import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dc_bias import solve_voltage_divider, solve_fixed_bias, solve_emitter_bias

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

    def test_vce_just_above_lab03_threshold_is_active(self):
        # VCE ~= 0.243 V: above the Lab 03 0.2 V warning threshold.
        r = solve_voltage_divider(vcc=12.0, r1=100_000.0, r2=22_000.0,
                                  rc=8_550.0, re=1_000.0, beta=100.0, vbe=0.70)
        self.assertAlmostEqual(r["vce"], 0.2426, delta=0.001)
        self.assertEqual(r["region"], "active")


class TestFixedBias(unittest.TestCase):
    def test_matches_hand_calculation(self):
        r = solve_fixed_bias(vcc=12.0, rb=1_000_000.0, rc=2_200.0,
                             beta=100.0, vbe=0.70)
        self.assertAlmostEqual(r["ib"], 11.3e-6, delta=1e-9)
        self.assertAlmostEqual(r["ic"], 1.130e-3, delta=1e-6)
        self.assertAlmostEqual(r["ve"], 0.0, delta=1e-12)
        self.assertAlmostEqual(r["vb"], 0.70, delta=1e-9)
        self.assertAlmostEqual(r["vce"], 9.514, delta=0.001)
        self.assertEqual(r["region"], "active")

    def test_cutoff_when_vcc_not_above_vbe(self):
        r = solve_fixed_bias(vcc=0.60, rb=1_000_000.0, rc=2_200.0,
                             beta=100.0, vbe=0.70)
        self.assertEqual(r["region"], "cutoff")
        self.assertEqual(r["ic"], 0.0)


class TestEmitterBias(unittest.TestCase):
    def test_matches_hand_calculation(self):
        r = solve_emitter_bias(vcc=12.0, rb=1_000_000.0, rc=2_200.0,
                               re=1_000.0, beta=100.0, vbe=0.70)
        self.assertAlmostEqual(r["ib"], 1.02634e-5, delta=1e-9)
        self.assertAlmostEqual(r["ic"], 1.02634e-3, delta=1e-6)
        self.assertAlmostEqual(r["ve"], 1.0366, delta=0.001)
        self.assertAlmostEqual(r["vce"], 8.705, delta=0.001)
        self.assertEqual(r["region"], "active")

    def test_larger_re_reduces_ic(self):
        small = solve_emitter_bias(vcc=12.0, rb=1_000_000.0, rc=2_200.0,
                                   re=1_000.0, beta=100.0, vbe=0.70)
        large = solve_emitter_bias(vcc=12.0, rb=1_000_000.0, rc=2_200.0,
                                   re=2_000.0, beta=100.0, vbe=0.70)
        self.assertAlmostEqual(large["ic"], 0.9401e-3, delta=1e-6)
        self.assertLess(large["ic"], small["ic"])


if __name__ == "__main__":
    unittest.main()
