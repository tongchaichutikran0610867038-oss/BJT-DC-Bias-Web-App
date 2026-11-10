import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app


class TestGetIndex(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_returns_form_with_all_inputs(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        for name in ("vcc", "r1", "r2", "rc", "re", "beta", "vbe"):
            self.assertIn(f'name="{name}"', html)


VALID = dict(vcc="12", r1="100", r1_unit="kohm", r2="22", r2_unit="kohm",
             rc="2.2", rc_unit="kohm", re="1", re_unit="kohm",
             beta="100", vbe="0.70")


class TestPostCalculate(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_valid_input_shows_computed_values(self):
        html = self.client.post("/", data=VALID).get_data(as_text=True)
        self.assertEqual(self.client.post("/", data=VALID).status_code, 200)
        self.assertIn("1.230", html)   # IC [mA]
        self.assertIn("8.052", html)   # VCE [V]
        self.assertIn("ACTIVE", html)

    def test_kohm_and_ohm_give_same_result(self):
        ohm = dict(VALID, r1="100000", r1_unit="ohm", r2="22000", r2_unit="ohm",
                   rc="2200", rc_unit="ohm", re="1000", re_unit="ohm")
        a = self.client.post("/", data=VALID).get_data(as_text=True)
        b = self.client.post("/", data=ohm).get_data(as_text=True)
        self.assertIn("1.230", a)
        self.assertIn("1.230", b)


class TestValidation(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_zero_beta_is_rejected(self):
        resp = self.client.post("/", data=dict(VALID, beta="0"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("β ต้องมากกว่า 0", resp.get_data(as_text=True))

    def test_zero_vcc_is_rejected(self):
        html = self.client.post("/", data=dict(VALID, vcc="0")).get_data(as_text=True)
        self.assertIn("VCC ต้องมากกว่า 0 V", html)

    def test_missing_field_is_rejected(self):
        bad = dict(VALID)
        del bad["vbe"]
        html = self.client.post("/", data=bad).get_data(as_text=True)
        self.assertIn("VBE", html)
        self.assertIn("ตัวเลข", html)

    def test_negative_resistance_is_rejected(self):
        html = self.client.post("/", data=dict(VALID, rc="-2")).get_data(as_text=True)
        self.assertIn("RC", html)
        self.assertIn("มากกว่า 0", html)

    def test_vbe_not_less_than_vcc_is_rejected(self):
        html = self.client.post("/", data=dict(VALID, vbe="12")).get_data(as_text=True)
        self.assertIn("VBE ต้องน้อยกว่า VCC", html)

    def test_entered_values_survive_validation_error(self):
        html = self.client.post("/", data=dict(VALID, beta="0")).get_data(as_text=True)
        self.assertIn('value="100"', html)   # ค่า β เดิมยังอยู่ ไม่ถูกล้าง


class TestRegionBadge(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_active_badge_class(self):
        html = self.client.post("/", data=VALID).get_data(as_text=True)
        self.assertIn("badge-active", html)

    def test_saturation_badge_class(self):
        sat = dict(VALID, rc="20")
        html = self.client.post("/", data=sat).get_data(as_text=True)
        self.assertIn("badge-saturation", html)


if __name__ == "__main__":
    unittest.main()
