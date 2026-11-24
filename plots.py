"""Server-side SVG plots built only from ngspice data (no chart dependency)."""

import math


def _polyline(points):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in points)


def _nice_ticks(low, high, count=4):
    if high <= low:
        return [low]
    return [low + (high - low) * i / (count - 1) for i in range(count)]


def bode_svg(series, width=720, height=380):
    """Return a Bode SVG with gain (dB) and phase (deg) versus log frequency."""
    if not series:
        return '<p class="muted">ไม่มีข้อมูล .ac ที่จะสร้างกราฟ</p>'

    left, right = 62, width - 18
    top, panel_gap = 28, 24
    panel_height = 132
    gain_top = top
    phase_top = top + panel_height + panel_gap

    freqs = [max(item["freq_hz"], 1e-30) for item in series]
    log_min, log_max = math.log10(min(freqs)), math.log10(max(freqs))
    if log_max <= log_min:
        log_max = log_min + 1.0

    gains = [item["gain_db"] for item in series]
    phases = [item["phase_deg"] for item in series]
    gain_low, gain_high = min(gains), max(gains)
    pad = max(0.5, (gain_high - gain_low) * 0.12)
    gain_low, gain_high = gain_low - pad, gain_high + pad
    phase_low, phase_high = min(-180.0, min(phases)) - 5.0, max(0.0, max(phases)) + 5.0

    def x_pos(freq):
        fraction = (math.log10(max(freq, 1e-30)) - log_min) / (log_max - log_min)
        return left + fraction * (right - left)

    def y_pos(value, low, high, panel_top):
        fraction = (value - low) / (high - low)
        return panel_top + panel_height - fraction * panel_height

    gain_points = [
        (x_pos(item["freq_hz"]), y_pos(item["gain_db"], gain_low, gain_high, gain_top))
        for item in series
    ]
    phase_points = [
        (x_pos(item["freq_hz"]), y_pos(item["phase_deg"], phase_low, phase_high, phase_top))
        for item in series
    ]

    parts = [
        f'<svg class="plot" viewBox="0 0 {width} {height}" role="img" '
        'aria-labelledby="bode-title bode-desc" xmlns="http://www.w3.org/2000/svg">',
        '<title id="bode-title">AC frequency response from ngspice</title>',
        '<desc id="bode-desc">Gain in decibels and phase in degrees versus frequency, '
        'plotted from parsed ngspice AC output.</desc>',
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#f9fcfd" '
        'stroke="#dce7ee" rx="6"/>',
    ]

    for panel_top, low, high, label, colour, data_points in (
        (gain_top, gain_low, gain_high, "Gain |Vout/Vin| (dB)", "#167e93", gain_points),
        (phase_top, phase_low, phase_high, "Phase (degree)", "#a65a2c", phase_points),
    ):
        parts.append(
            f'<text x="{left}" y="{panel_top + 12}" font-size="11" fill="#486275">{label}</text>'
        )
        for tick in _nice_ticks(low, high):
            y = y_pos(tick, low, high, panel_top)
            parts.append(
                f'<line x1="{left}" y1="{y:.2f}" x2="{right}" y2="{y:.2f}" '
                'stroke="#dce7ee" stroke-width="1"/>'
            )
            parts.append(
                f'<text x="{left - 6}" y="{y + 4:.2f}" font-size="9" fill="#486275" '
                f'text-anchor="end">{tick:.1f}</text>'
            )
        parts.append(
            f'<line x1="{left}" y1="{panel_top + panel_height}" x2="{right}" '
            f'y2="{panel_top + panel_height}" stroke="#9cb2c2" stroke-width="1.2"/>'
        )
        parts.append(
            f'<polyline points="{_polyline(data_points)}" fill="none" stroke="{colour}" '
            'stroke-width="2.2" stroke-linejoin="round"/>'
        )

    for frequency in _nice_ticks(min(freqs), max(freqs)):
        x = x_pos(frequency)
        parts.append(
            f'<line x1="{x:.2f}" y1="{gain_top}" x2="{x:.2f}" '
            f'y2="{phase_top + panel_height}" stroke="#e7eef3" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{x:.2f}" y="{phase_top + panel_height + 16}" font-size="9" '
            f'fill="#486275" text-anchor="middle">{frequency:.3g}</text>'
        )
    parts.append(
        f'<text x="{(left + right) / 2:.1f}" y="{height - 6}" font-size="11" '
        'fill="#486275" text-anchor="middle">Frequency (Hz, log scale)</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


def waveform_svg(series, width=720, height=330):
    """Return Vin/Vout versus time SVG from parsed ngspice transient output."""
    if not series:
        return '<p class="muted">ไม่มีข้อมูล .tran ที่จะสร้างกราฟ</p>'

    left, right = 62, width - 18
    top, bottom = 28, height - 46
    plot_height = bottom - top

    times = [item["time_s"] for item in series]
    values = [item["vin_v"] for item in series] + [item["vout_v"] for item in series]
    time_min, time_max = min(times), max(times)
    if time_max <= time_min:
        time_max = time_min + 1e-9
    span = max(max(values) - min(values), 1e-6)
    value_low = min(values) - span * 0.12
    value_high = max(values) + span * 0.12

    stride = max(1, len(series) // 700)
    samples = series[::stride]
    if samples[-1] is not series[-1]:
        samples.append(series[-1])

    def x_pos(seconds):
        return left + (seconds - time_min) / (time_max - time_min) * (right - left)

    def y_pos(volts):
        return bottom - (volts - value_low) / (value_high - value_low) * plot_height

    vin_points = [(x_pos(item["time_s"]), y_pos(item["vin_v"])) for item in samples]
    vout_points = [(x_pos(item["time_s"]), y_pos(item["vout_v"])) for item in samples]

    parts = [
        f'<svg class="plot" viewBox="0 0 {width} {height}" role="img" '
        'aria-labelledby="wave-title wave-desc" xmlns="http://www.w3.org/2000/svg">',
        '<title id="wave-title">Transient waveforms from ngspice</title>',
        '<desc id="wave-desc">Input and output voltage versus time from parsed '
        'ngspice transient output.</desc>',
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#f9fcfd" '
        'stroke="#dce7ee" rx="6"/>',
        f'<text x="{left}" y="{top - 8}" font-size="11" fill="#486275">Voltage (V)</text>',
    ]

    for tick in _nice_ticks(value_low, value_high):
        y = y_pos(tick)
        parts.append(
            f'<line x1="{left}" y1="{y:.2f}" x2="{right}" y2="{y:.2f}" '
            'stroke="#dce7ee" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{left - 6}" y="{y + 4:.2f}" font-size="9" fill="#486275" '
            f'text-anchor="end">{tick:.3f}</text>'
        )
    parts.append(
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" '
        'stroke="#9cb2c2" stroke-width="1.2"/>'
    )
    parts.append(
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" '
        'stroke="#9cb2c2" stroke-width="1.2"/>'
    )

    for seconds in _nice_ticks(time_min, time_max):
        x = x_pos(seconds)
        parts.append(
            f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{bottom}" '
            'stroke="#e7eef3" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{x:.2f}" y="{bottom + 16}" font-size="9" fill="#486275" '
            f'text-anchor="middle">{seconds * 1000:.2f}</text>'
        )

    parts.append(
        f'<polyline points="{_polyline(vin_points)}" fill="none" stroke="#0c8e83" '
        'stroke-width="2.2" stroke-linejoin="round"/>'
    )
    parts.append(
        f'<polyline points="{_polyline(vout_points)}" fill="none" stroke="#c77a35" '
        'stroke-width="2.2" stroke-linejoin="round"/>'
    )
    parts.append(
        f'<text x="{(left + right) / 2:.1f}" y="{height - 6}" font-size="11" '
        'fill="#486275" text-anchor="middle">Time (ms)</text>'
    )
    parts.append(
        f'<rect x="{right - 168}" y="{top + 4}" width="164" height="20" rx="3" '
        'fill="#ffffff" stroke="#dce7ee"/>'
    )
    parts.append(
        f'<line x1="{right - 160}" y1="{top + 14}" x2="{right - 138}" y2="{top + 14}" '
        'stroke="#0c8e83" stroke-width="2.2"/>'
    )
    parts.append(
        f'<text x="{right - 132}" y="{top + 18}" font-size="10" fill="#17344b">Vin</text>'
    )
    parts.append(
        f'<line x1="{right - 96}" y1="{top + 14}" x2="{right - 74}" y2="{top + 14}" '
        'stroke="#c77a35" stroke-width="2.2"/>'
    )
    parts.append(
        f'<text x="{right - 68}" y="{top + 18}" font-size="10" fill="#17344b">Vout</text>'
    )
    parts.append("</svg>")
    return "".join(parts)
