"""Flask application for the BJT DC Bias web app.

Handles HTTP GET/POST, parses the form, validates inputs, converts units,
and calls the dc_bias engine. The engine module knows nothing about Flask.
"""

from flask import Flask, render_template, request

from dc_bias import solve_voltage_divider

app = Flask(__name__)

DEFAULTS = {
    "vcc": "12",
    "r1": "100",
    "r1_unit": "kohm",
    "r2": "22",
    "r2_unit": "kohm",
    "rc": "2.2",
    "rc_unit": "kohm",
    "re": "1",
    "re_unit": "kohm",
    "beta": "100",
    "vbe": "0.70",
}


def parse_resistance(raw, unit):
    """Convert a resistance input to ohms (float). Raw is a number string;
    unit is either 'ohm' or 'kohm'."""
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    if unit == "kohm":
        value *= 1000.0
    return value


@app.route("/", methods=["GET", "POST"])
def index():
    values = dict(DEFAULTS)
    results = None
    errors = []

    if request.method == "POST":
        for name in ("vcc", "r1", "r2", "rc", "re", "beta", "vbe"):
            values[name] = request.form.get(name, "")
        for name in ("r1_unit", "r2_unit", "rc_unit", "re_unit"):
            values[name] = request.form.get(name, "kohm")

        try:
            vcc = float(values["vcc"])
        except (TypeError, ValueError):
            vcc = None

        r1 = parse_resistance(values["r1"], values["r1_unit"])
        r2 = parse_resistance(values["r2"], values["r2_unit"])
        rc = parse_resistance(values["rc"], values["rc_unit"])
        re_ = parse_resistance(values["re"], values["re_unit"])

        try:
            beta = float(values["beta"])
        except (TypeError, ValueError):
            beta = None

        try:
            vbe = float(values["vbe"])
        except (TypeError, ValueError):
            vbe = None

        errors = validate_inputs(vcc, r1, r2, rc, re_, beta, vbe)

        if not errors:
            results = solve_voltage_divider(vcc, r1, r2, rc, re_, beta, vbe)
            results = format_results(results)

    return render_template(
        "index.html",
        results=results,
        errors=errors,
        values=values,
    )


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

def validate_inputs(vcc, r1, r2, rc, re_, beta, vbe):
    """Return a list of Thai error messages (empty = all valid)."""
    errors = []

    def bad(name, msg):
        errors.append(msg)

    if vcc is None:
        bad("VCC", "กรุณากรอก VCC เป็นตัวเลข")
    elif vcc <= 0:
        bad("VCC", "VCC ต้องมากกว่า 0 V")

    for name, value in (("R1", r1), ("R2", r2), ("RC", rc), ("RE", re_)):
        if value is None:
            bad(name, f"กรุณากรอก {name} เป็นตัวเลข")
        elif value <= 0:
            bad(name, f"ค่า {name} ต้องมากกว่า 0 Ω")

    if beta is None:
        bad("β", "กรุณากรอก β เป็นตัวเลข")
    elif beta <= 0:
        bad("β", "β ต้องมากกว่า 0")

    if vbe is None:
        bad("VBE", "กรุณากรอก VBE เป็นตัวเลข")
    elif vbe <= 0:
        bad("VBE", "VBE ต้องมากกว่า 0 V")
    elif vcc is not None and vbe >= vcc:
        bad("VBE", "VBE ต้องน้อยกว่า VCC")

    return errors
