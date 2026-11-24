"""Lab 04 checks: netlist generation, parsing, validation and error paths."""

import unittest

from app import app
from spice_engine import (
    SpiceEngineError,
    build_netlist,
    find_engine,
    parse_raw_ascii,
    run_analysis,
    validate_params,
)

PARAMS = {
    "analysis": "dc",
    "vcc": 12.0,
    "r1": 100000.0,
    "r2": 22000.0,
    "rc": 2200.0,
    "re": 1000.0,
    "rl": 10000.0,
    "cin": 10e-6,
    "cout": 10e-6,
    "amp": 0.010,
    "freq": 1000.0,
}


def engine_available():
    try:
        find_engine()
    except SpiceEngineError:
        return False
    return True


class TestNetlist(unittest.TestCase):
    def test_directives_match_analysis(self):
        self.assertIn(".OP", build_netlist(PARAMS, "dc"))
        self.assertIn(".AC DEC 20 1 10MEG", build_netlist(PARAMS, "ac"))
        self.assertIn(".TRAN", build_netlist(PARAMS, "tran"))

    def test_source_reflects_amplitude_and_frequency(self):
        netlist = build_netlist(PARAMS, "tran")
        self.assertIn("SIN(0 0.01 1000)", netlist)
        self.assertIn("Q1 COLL BASE EMIT QNPN", netlist)

    def test_zero_re_is_rejected_before_any_process(self):
        bad = dict(PARAMS, re=0.0)
        with self.assertRaises(SpiceEngineError):
            validate_params(bad)


class TestRawParser(unittest.TestCase):
    def test_parses_ascii_raw_header_and_values(self):
        text = """Title: sample
Plotname: Operating Point
Flags: real
No. Variables: 2
No. Points: 1
Variables:
\t0\tv(base)\tvoltage
\t1\tv(emit)\tvoltage
Values:
0\t1.500000000000000e+00
\t5.000000000000000e-01
"""
        points, variables, meta = parse_raw_ascii(text)
        self.assertEqual(variables, ["v(base)", "v(emit)"])
        self.assertEqual(meta["flags"], "real")
        self.assertAlmostEqual(points[0][0], 1.5)
        self.assertAlmostEqual(points[0][1], 0.5)


@unittest.skipUnless(engine_available(), "ngspice not installed on this machine")
class TestRealRun(unittest.TestCase):
    def test_dc_readings_come_from_engine(self):
        result = run_analysis(PARAMS)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["engine"], "ngspice")
        readings = result["readings"]
        self.assertAlmostEqual(readings["vb"], 1.949, places=2)
        self.assertGreater(readings["ic"], 0.0011)
        self.assertLess(readings["ic"], 0.0015)


class TestWebErrorPath(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_invalid_spice_input_does_not_show_success_or_plot(self):
        payload = {
            "action": "spice",
            "sp_analysis": "dc",
            "sp_vcc": "12",
            "sp_r1": "100",
            "sp_r2": "22",
            "sp_rc": "2.2",
            "sp_re": "0",
            "sp_rl": "10",
            "sp_cin": "10",
            "sp_cout": "10",
            "sp_amp": "10",
            "sp_freq": "1000",
        }
        html = self.client.post("/", data=payload).get_data(as_text=True)
        self.assertIn("RE ต้องมากกว่าหรือเท่ากับ", html)
        self.assertNotIn("STATUS: SUCCESS", html)
        self.assertNotIn('<svg class="plot"', html)


if __name__ == "__main__":
    unittest.main()
