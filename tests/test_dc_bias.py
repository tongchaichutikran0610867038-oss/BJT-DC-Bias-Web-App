import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dc_bias import solve_voltage_divider

REFERENCE = dict(vcc=12.0, r1=100_000.0, r2=22_000.0, rc=2_200.0, re=1_000.0, beta=100.0, vbe=0.70)


class TestReferencePoint(unittest.TestCase):
    def test_matches_hand_calculation(self):
        r = solve_voltage_divider(**REFERENCE)
        self.assertAlmostEqual(r["vth"], 2.164, delta=0.001)
        self.assertAlmostEqual(r["rth"], 18_033.0, delta=1.0)
        self.assertAlmostEqual(r["ib"], 1.2299e-05, delta=1e-8)
        self.assertAlmostEqual(r["ic"], 1.2299e-03, delta=1e-6)
        self.assertAlmostEqual(r["ie"], 1.2422e-03, delta=1e-6)
        self.assertAlmostEqual(r["ve"], 1.242, delta=0.001)
        self.assertAlmostEqual(r["vb"], 1.942, delta=0.001)
        self.assertAlmostEqual(r["vc"], 9.294, delta=0.001)
        self.assertAlmostEqual(r["vce"], 8.052, delta=0.001)

    def test_beta_change_increases_collector_current(self):
        stronger = solve_voltage_divider(**dict(REFERENCE, beta=200.0))
        self.assertAlmostEqual(stronger["ic"], 1.3368e-03, delta=1e-6)
        self.assertGreater(stronger["ic"], solve_voltage_divider(**REFERENCE)["ic"])


class TestRegion(unittest.TestCase):
    def test_active_for_reference_case(self):
        r = solve_voltage_divider(**REFERENCE)
        self.assertEqual(r["region"], "active")

    def test_cutoff_when_vth_below_vbe(self):
        r = solve_voltage_divider(vcc=12.0, r1=100_000.0, r2=1_000.0,
                                  rc=2_200.0, re=1_000.0, beta=100.0, vbe=0.70)
        self.assertEqual(r["region"], "cutoff")
        self.assertEqual(r["ic"], 0.0)
        self.assertEqual(r["vce"], 12.0)
        self.assertIn("Cutoff", r["message"])

    def test_saturation_when_vce_below_threshold(self):
        r = solve_voltage_divider(vcc=12.0, r1=100_000.0, r2=22_000.0,
                                  rc=20_000.0, re=1_000.0, beta=100.0, vbe=0.70)
        self.assertEqual(r["region"], "saturation")
        self.assertIn("Saturation", r["message"])


if __name__ == "__main__":
    unittest.main()
