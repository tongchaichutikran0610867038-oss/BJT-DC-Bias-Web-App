"""DC bias calculations for an NPN BJT in Common-Emitter circuits.

Supports three circuits: voltage-divider bias, fixed bias, and single-supply
emitter bias. Forward-Active approximation with constant beta and constant VBE.
All parameters and results use SI units: volts (V), amperes (A), ohms (Ohm).

This module must not import Flask or know anything about HTTP/HTML.
"""


def solve_voltage_divider(vcc, r1, r2, rc, re, beta, vbe):
    """Return the DC operating point of a voltage-divider biased NPN BJT.

    Args:
        vcc: Supply voltage [V].
        r1: Base-to-VCC resistor [Ohm].
        r2: Base-to-ground resistor [Ohm].
        rc: Collector resistor [Ohm].
        re: Emitter resistor [Ohm].
        beta: Forward current gain (dimensionless).
        vbe: Base-emitter voltage [V].

    Returns:
        dict with keys vth, rth, ib, ic, ie, ve, vb, vc, vce in SI units.
    """
    vth = vcc * r2 / (r1 + r2)
    rth = r1 * r2 / (r1 + r2)

    if vth <= vbe:
        return {
            "vth": vth,
            "rth": rth,
            "ib": 0.0,
            "ic": 0.0,
            "ie": 0.0,
            "ve": 0.0,
            "vb": vth,
            "vc": vcc,
            "vce": vcc,
            "region": "cutoff",
            "message": "Cutoff: VTH <= VBE, the forward-active equations do not apply.",
        }

    ib = (vth - vbe) / (rth + (beta + 1) * re)
    ic = beta * ib
    ie = (beta + 1) * ib

    ve = ie * re
    vb = ve + vbe
    vc = vcc - ic * rc
    vce = vc - ve

    if vce <= 0.2:
        region = "saturation"
        message = "Saturation: VCE <= 0.2 V, the calculated forward-active values are not reliable."
    else:
        region = "active"
        message = "Forward-Active approximation (VTH > VBE and VCE > 0.2 V)."

    return {
        "vth": vth,
        "rth": rth,
        "ib": ib,
        "ic": ic,
        "ie": ie,
        "ve": ve,
        "vb": vb,
        "vc": vc,
        "vce": vce,
        "region": region,
        "message": message,
    }


def solve_fixed_bias(vcc, rb, rc, beta, vbe):
    """Return the DC operating point of a fixed-biased NPN BJT.

    RB connects VCC to the base; the emitter is connected directly to ground.
    IB = (VCC - VBE) / RB. VE is therefore always 0 V.

    Args use SI units: V, Ohm, dimensionless, V.
    Returns a dict with the same result keys/units as the other solvers.
    """
    if vcc <= vbe:
        return {
            "ib": 0.0,
            "ic": 0.0,
            "ie": 0.0,
            "ve": 0.0,
            "vb": vcc,
            "vc": vcc,
            "vce": vcc,
            "region": "cutoff",
            "message": "Cutoff: VCC <= VBE, the forward-active equations do not apply.",
        }

    ib = (vcc - vbe) / rb
    ic = beta * ib
    ie = (beta + 1) * ib

    ve = 0.0
    vb = ve + vbe
    vc = vcc - ic * rc
    vce = vc - ve

    if vce <= 0.2:
        region = "saturation"
        message = "Saturation: VCE <= 0.2 V, the calculated forward-active values are not reliable."
    else:
        region = "active"
        message = "Forward-Active approximation (VCC > VBE and VCE > 0.2 V)."

    return {
        "ib": ib,
        "ic": ic,
        "ie": ie,
        "ve": ve,
        "vb": vb,
        "vc": vc,
        "vce": vce,
        "region": region,
        "message": message,
    }


def solve_emitter_bias(vcc, rb, rc, re, beta, vbe):
    """Return the DC operating point of a single-supply emitter-biased NPN BJT.

    RB connects VCC to the base; RE connects the emitter to ground.
    IB = (VCC - VBE) / [RB + (beta + 1) * RE].

    Args use SI units: V, Ohm, dimensionless, V.
    Returns a dict with the same result keys/units as the other solvers.
    """
    if vcc <= vbe:
        return {
            "ib": 0.0,
            "ic": 0.0,
            "ie": 0.0,
            "ve": 0.0,
            "vb": vcc,
            "vc": vcc,
            "vce": vcc,
            "region": "cutoff",
            "message": "Cutoff: VCC <= VBE, the forward-active equations do not apply.",
        }

    ib = (vcc - vbe) / (rb + (beta + 1) * re)
    ic = beta * ib
    ie = (beta + 1) * ib

    ve = ie * re
    vb = ve + vbe
    vc = vcc - ic * rc
    vce = vc - ve

    if vce <= 0.2:
        region = "saturation"
        message = "Saturation: VCE <= 0.2 V, the calculated forward-active values are not reliable."
    else:
        region = "active"
        message = "Forward-Active approximation (VCC > VBE and VCE > 0.2 V)."

    return {
        "ib": ib,
        "ic": ic,
        "ie": ie,
        "ve": ve,
        "vb": vb,
        "vc": vc,
        "vce": vce,
        "region": region,
        "message": message,
    }
