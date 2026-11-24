"""Flask application for the BJT DC Bias web app (Lab 03).

Handles HTTP GET/POST, parses the form, validates inputs, converts units,
selects the bias circuit, and calls the matching dc_bias engine function.
The engine module knows nothing about Flask.
"""

import math

from flask import Flask, render_template, request

from dc_bias import solve_voltage_divider, solve_fixed_bias, solve_emitter_bias
from plots import bode_svg, waveform_svg
from spice_engine import SpiceEngineError, run_analysis

app = Flask(__name__)

MODE_DIVIDER = "divider"
MODE_FIXED = "fixed"
MODE_EMITTER = "emitter"

MODE_LABELS = {
    MODE_DIVIDER: "Voltage-Divider Bias",
    MODE_FIXED: "Fixed Bias",
    MODE_EMITTER: "Emitter Bias (แหล่งจ่ายเดียว)",
}

SOLVERS = {
    MODE_DIVIDER: solve_voltage_divider,
    MODE_FIXED: solve_fixed_bias,
    MODE_EMITTER: solve_emitter_bias,
}

ALL_INPUTS = (
    "vcc", "r1", "r1_unit", "r2", "r2_unit",
    "rb", "rb_unit", "rc", "rc_unit", "re", "re_unit",
    "beta", "vbe",
)

DEFAULTS = {
    "mode": MODE_DIVIDER,
    "vcc": "12",
    "r1": "100",
    "r1_unit": "kohm",
    "r2": "22",
    "r2_unit": "kohm",
    "rb": "1",
    "rb_unit": "mohm",
    "rc": "2.2",
    "rc_unit": "kohm",
    "re": "1",
    "re_unit": "kohm",
    "beta": "100",
    "vbe": "0.70",
}

# Lab 04: one fixed CE voltage-divider reference fed to ngspice.
# Form values are strings so the user's entries survive a validation error.
SPICE_DEFAULTS = {
    "sp_analysis": "dc",
    "sp_vcc": "12",
    "sp_r1": "100",      # kΩ
    "sp_r2": "22",       # kΩ
    "sp_rc": "2.2",      # kΩ
    "sp_re": "1",        # kΩ
    "sp_rl": "10",       # kΩ
    "sp_cin": "10",      # µF
    "sp_cout": "10",     # µF
    "sp_amp": "10",      # mV peak
    "sp_freq": "1000",   # Hz
}
SPICE_INPUT_NAMES = tuple(SPICE_DEFAULTS)
ANALYSIS_LABELS = {
    "dc": "DC · .op",
    "ac": "AC · .ac",
    "tran": "Transient · .tran",
}


def required_fields(mode):
    """Input names that must be present for a given circuit mode."""
    common = {"vcc", "rc", "rc_unit", "beta", "vbe"}
    extra = {
        MODE_DIVIDER: {"r1", "r1_unit", "r2", "r2_unit", "re", "re_unit"},
        MODE_FIXED: {"rb", "rb_unit"},
        MODE_EMITTER: {"rb", "rb_unit", "re", "re_unit"},
    }.get(mode, set())
    return common | extra


def to_float(raw):
    """Parse a finite number string, returning None when missing or invalid."""
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def parse_resistance(raw, unit):
    """Convert a resistance input to ohms. Unit: 'ohm', 'kohm' or 'mohm'."""
    value = to_float(raw)
    if value is None:
        return None
    if unit == "kohm":
        value *= 1000.0
    elif unit == "mohm":
        value *= 1_000_000.0
    return value


def validate_inputs(vcc, beta, vbe, resistors):
    """Return Thai error messages; resistors is a list of (label, ohms)."""
    errors = []

    if vcc is None:
        errors.append("กรุณากรอก VCC เป็นตัวเลข")
    elif vcc <= 0:
        errors.append("VCC ต้องมากกว่า 0 V")

    for label, value in resistors:
        if value is None:
            errors.append(f"กรุณากรอก {label} เป็นตัวเลข")
        elif value <= 0:
            errors.append(f"ค่า {label} ต้องมากกว่า 0 Ω")

    if beta is None:
        errors.append("กรุณากรอก β เป็นตัวเลข")
    elif beta <= 0:
        errors.append("β ต้องมากกว่า 0")

    if vbe is None:
        errors.append("กรุณากรอก VBE เป็นตัวเลข")
    elif vbe <= 0:
        errors.append("VBE ต้องมากกว่า 0 V")
    elif vcc is not None and vbe >= vcc:
        errors.append("VBE ต้องน้อยกว่า VCC")

    return errors


def format_results(results):
    """แปลงผลลัพธ์หน่วย SI เป็นสตริงพร้อมหน่วยสำหรับแสดงใน template."""
    return {
        "vb": f"{results['vb']:.3f}",
        "ve": f"{results['ve']:.3f}",
        "vc": f"{results['vc']:.3f}",
        "vce": f"{results['vce']:.3f}",
        "ic": f"{results['ic'] * 1000:.3f}",   # A → mA
        "ie": f"{results['ie'] * 1000:.3f}",   # A → mA
        "ib": f"{results['ib'] * 1e6:.2f}",    # A → µA
        "region": results["region"],
        "message": results["message"],
    }


def spice_form_values(form):
    """Keep every Lab 04 field as the user typed it, including on error."""
    return {name: form.get(name, SPICE_DEFAULTS[name]) for name in SPICE_INPUT_NAMES}


def _scaled(raw, factor):
    value = to_float(raw)
    return None if value is None else value * factor


def spice_params(values):
    """Convert displayed kΩ/µF/mV inputs into SI units for the engine."""
    return {
        "analysis": values["sp_analysis"],
        "vcc": to_float(values["sp_vcc"]),
        "r1": parse_resistance(values["sp_r1"], "kohm"),
        "r2": parse_resistance(values["sp_r2"], "kohm"),
        "rc": parse_resistance(values["sp_rc"], "kohm"),
        "re": parse_resistance(values["sp_re"], "kohm"),
        "rl": parse_resistance(values["sp_rl"], "kohm"),
        "cin": _scaled(values["sp_cin"], 1e-6),
        "cout": _scaled(values["sp_cout"], 1e-6),
        "amp": _scaled(values["sp_amp"], 1e-3),
        "freq": to_float(values["sp_freq"]),
    }


def plot_for(analysis, series):
    """Build presentation SVG from parsed engine data only."""
    if analysis == "ac":
        return bode_svg(series)
    if analysis == "tran":
        return waveform_svg(series)
    return ""


@app.route("/", methods=["GET", "POST"])
def index():
    values = dict(DEFAULTS)
    mode = DEFAULTS["mode"]
    results = None
    errors = []

    spice_values = dict(SPICE_DEFAULTS)
    spice_result = None
    spice_error = None
    spice_plot = ""
    analytical_reference = None

    if request.method == "POST":
        action = request.form.get("action", "analytical")

        if action == "spice":
            # Lab 04 path: one CE reference circuit, three real ngspice analyses.
            spice_values = spice_form_values(request.form)
            analysis = spice_values["sp_analysis"]
            try:
                params = spice_params(spice_values)
                spice_result = run_analysis(params)
                spice_plot = plot_for(analysis, spice_result["series"])

                if analysis == "dc" and not any(item is None for item in params.values()):
                    try:
                        reference = solve_voltage_divider(
                            vcc=params["vcc"],
                            r1=params["r1"],
                            r2=params["r2"],
                            rc=params["rc"],
                            re=params["re"],
                            beta=float(DEFAULTS["beta"]),
                            vbe=float(DEFAULTS["vbe"]),
                        )
                        analytical_reference = format_results(reference)
                    except (ValueError, ZeroDivisionError):
                        analytical_reference = None
            except SpiceEngineError as exc:
                # Never keep a previous success plot when the current run failed.
                spice_error = str(exc)
                spice_result = None
                spice_plot = ""
                analytical_reference = None
        else:
            # Lab 03 path is untouched: same form fields, same three solvers.
            # Missing mode keeps the Lab 2 default; an explicit bad value is an error.
            mode = request.form.get("mode") or MODE_DIVIDER
            values["mode"] = mode

            required = required_fields(mode)
            for name in ALL_INPUTS:
                fallback = "" if name in required else DEFAULTS[name]
                values[name] = request.form.get(name, fallback)

            if mode not in SOLVERS:
                errors = [
                    f"โหมดวงจรไม่รู้จัก: {mode} "
                    "(เลือกได้เฉพาะ divider, fixed หรือ emitter)"
                ]
            else:
                vcc = to_float(values["vcc"])
                beta = to_float(values["beta"])
                vbe = to_float(values["vbe"])
                rc = parse_resistance(values["rc"], values["rc_unit"])

                resistors = [("RC", rc)]
                kwargs = {"vcc": vcc, "rc": rc, "beta": beta, "vbe": vbe}

                if mode == MODE_DIVIDER:
                    r1 = parse_resistance(values["r1"], values["r1_unit"])
                    r2 = parse_resistance(values["r2"], values["r2_unit"])
                    re_ = parse_resistance(values["re"], values["re_unit"])
                    resistors[1:1] = [("R1", r1), ("R2", r2), ("RE", re_)]
                    kwargs.update(r1=r1, r2=r2, re=re_)
                elif mode == MODE_FIXED:
                    rb = parse_resistance(values["rb"], values["rb_unit"])
                    resistors.insert(0, ("RB", rb))
                    kwargs["rb"] = rb
                elif mode == MODE_EMITTER:
                    rb = parse_resistance(values["rb"], values["rb_unit"])
                    re_ = parse_resistance(values["re"], values["re_unit"])
                    resistors[0:0] = [("RB", rb), ("RE", re_)]
                    kwargs.update(rb=rb, re=re_)

                errors = validate_inputs(vcc, beta, vbe, resistors)

                if not errors:
                    results = format_results(SOLVERS[mode](**kwargs))

    return render_template(
        "index.html",
        results=results,
        errors=errors,
        values=values,
        mode=mode,
        mode_label=MODE_LABELS.get(mode, mode),
        spice_values=spice_values,
        spice_result=spice_result,
        spice_error=spice_error,
        spice_plot=spice_plot,
        analytical_reference=analytical_reference,
        analysis_label=ANALYSIS_LABELS.get(
            spice_values["sp_analysis"], spice_values["sp_analysis"]
        ),
    )
