# BJT DC Bias Web App — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** สร้าง Flask web app หลายไฟล์ที่รับค่า VCC, R1, R2, RC, RE, β, VBE แล้วคำนวณ DC operating point ของ BJT Common-Emitter (Voltage-Divider Bias) พร้อม validation, region warning และ automated tests ภายในคาบ Lab 02

**Architecture:** แยกชั้นคำนวณ (`dc_bias.py`, ไม่รู้จัก Flask/HTML) ออกจากชั้น HTTP (`app.py` ที่ parse form, แปลงหน่วย, validate แล้วเรียก engine) และชั้นนำเสนอ (`templates/index.html` + `static/style.css`). ทุกอย่าง render ฝั่ง server ไม่มี JavaScript

**Tech Stack:** Python 3.14.2, Flask 3.x, `unittest` (stdlib), Jinja2 templates, PowerShell บน Windows

**Spec:** `docs/superpowers/specs/2026-11-10-bjt-dc-bias-webapp-design.md`

## Global Constraints

- Python 3.14.2 ที่ `C:\Program Files\Python314` — เรียกด้วย `python` (PATH แก้แล้ว)
- Flask `>=3.1,<4` เท่านั้น; ห้ามเพิ่ม dependency อื่น
- ใช้ `unittest` จาก stdlib — ห้ามใช้ pytest
- `dc_bias.py` **ห้าม import flask** หรือรู้จัก HTTP/HTML
- หน่วยภายใน engine เป็น SI: V, A, Ω — การแปลง kΩ → Ω เกิดใน `app.py` เท่านั้น
- เกณฑ์ saturation: `VCE <= 0.3` V; cutoff: `VTH <= VBE`
- ตัวเลขที่แสดง: แรงดัน 3 ตำแหน่งทศนิยม (V), IC/IE เป็น mA 3 ตำแหน่ง, IB เป็น µA 2 ตำแหน่ง
- UI เป็นภาษาไทย, ไม่มี JavaScript, ไม่มี framework CSS
- Serve เฉพาะ `127.0.0.1` ด้วย Flask dev server
- **Agent ห้ามรัน `git commit` / `git push` / สร้าง remote** — นักศึกษา commit ผ่าน GitHub Desktop
  ทุก task จบด้วยการเตรียม working tree + ข้อความ commit ที่แนะนำ
- ตัวเลขผลลัพธ์ต้องมาจาก Python ทุกตัว ห้าม hard-code ใน template

## Review Focus

| # | อินพุต/ภาวะที่เสี่ยง | พฤติกรรมที่คนใช้คาดหวัง | เทสต์ที่ผูกไว้ |
|---|---|---|---|
| 1 | กรอกตัวต้านทานเป็น kΩ แต่ระบบอ่านเป็น Ω (หรือกลับกัน) | ผลต่างกัน 1000 เท่า — ต้องแปลงตาม dropdown | Task 4: `test_kohm_and_ohm_give_same_result` |
| 2 | กรอก VBE ≥ VCC | ขึ้น error ไม่ใช่ค่าติดลบประหลาด | Task 5: `test_vbe_not_less_than_vcc_is_rejected` |
| 3 | กรอกช่องว่างหรือตัวอักษร | ขึ้น error อ่านรู้เรื่อง ไม่มี traceback | Task 5: `test_missing_field_is_rejected` |
| 4 | ค่าที่ทำให้ VCE ติดลบ/ใกล้ 0 | ต้องขึ้น Saturation ไม่ใช่รายงาน Active | Task 2: `test_saturation_when_vce_below_threshold` |
| 5 | เกิด error แล้วฟอร์มถูกล้าง | ค่าที่กรอกอยู่ต้องคงไว้ให้แก้ต่อ | Task 5: `test_entered_values_survive_validation_error` |

---

### Task 1: DC Bias engine — เคสอ้างอิง

**Files:**
- Create: `requirements.txt`
- Create: `dc_bias.py`
- Create: `tests/test_dc_bias.py`

**Interfaces:**
- Consumes: ไม่มี (task แรก)
- Produces: `solve_voltage_divider(vcc: float, r1: float, r2: float, rc: float, re: float, beta: float, vbe: float) -> dict` คืน dict มี key `vth, rth, ib, ic, ie, ve, vb, vc, vce` (SI ทั้งหมด) — task 2–5 เรียกใช้ signature นี้

- [ ] **Step 1: สร้าง venv และติดตั้ง Flask**

Run (จาก root ของ repo):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install "Flask>=3.1,<4"
python -c "import flask; print(flask.__version__)"
```
Expected: พิมพ์เลขเวอร์ชัน 3.x และไม่มี error
จากนั้นเขียน `requirements.txt` บรรทัดเดียว: `Flask>=3.1,<4`

- [ ] **Step 2: เขียนเทสต์ที่ยังไม่ผ่าน**

`tests/test_dc_bias.py` — ต้องมี bootstrap นี้บนสุดของไฟล์ เพื่อให้รันได้ทั้ง `discover -s tests` และ `-t .`:
```python
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
```

- [ ] **Step 3: รันเทสต์ให้เห็นว่า fail**

Run: `python -m unittest discover -s tests -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'dc_bias'`

- [ ] **Step 4: implement `solve_voltage_divider` ใน `dc_bias.py`**

ฟังก์ชันเดียว รับ 7 พารามิเตอร์ตาม Interfaces ใช้สมการ:
```
VTH = vcc*r2/(r1+r2)   RTH = r1*r2/(r1+r2)
IB  = (VTH-vbe)/(RTH+(beta+1)*re)
IC  = beta*IB          IE = (beta+1)*IB
VE  = IE*re            VB = VE+vbe
VC  = vcc-IC*rc        VCE = VC-VE
```
ห้าม import flask; ห้าม print

- [ ] **Step 5: รันเทสต์ให้ผ่าน**

Run: `python -m unittest discover -s tests -v`
Expected: `OK` 2 tests

- [ ] **Step 6: เตรียม commit (นักศึกษาทำผ่าน GitHub Desktop)**

ไฟล์ที่ควรปรากฏในแท็บ Changes: `requirements.txt`, `dc_bias.py`, `tests/test_dc_bias.py`
ข้อความ commit แนะนำ: `Add DC bias engine with reference-point test`

---

### Task 2: จำแนกโหมด Active / Cutoff / Saturation

**Files:**
- Modify: `dc_bias.py`
- Modify: `tests/test_dc_bias.py`

**Interfaces:**
- Consumes: `solve_voltage_divider(...)` จาก Task 1
- Produces: dict เดิม + key `region: str` (`"active" | "cutoff" | "saturation"`) และ `message: str`

- [ ] **Step 1: เขียนเทสต์โหมดที่ยังไม่ผ่าน**

เพิ่มใน `tests/test_dc_bias.py`:
```python
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
```

- [ ] **Step 2: รันให้เห็นว่า fail**

Run: `python -m unittest discover -s tests -v`
Expected: FAIL — `KeyError: 'region'`

- [ ] **Step 3: เพิ่มการจำแนกโหมดใน `dc_bias.py`**

ลำดับ: (1) ถ้า `vth <= vbe` → region `"cutoff"`, ตั้ง `ib=ic=ie=0.0, ve=0.0, vb=vth, vc=vcc, vce=vcc`, message มีคำว่า `Cutoff` (2) ไม่งั้นคำนวณตามสมการ แล้วถ้า `vce <= 0.3` → `"saturation"` พร้อม message มีคำว่า `Saturation` และระบุว่าค่าไม่น่าเชื่อถือ (3) นอกนั้น `"active"`

- [ ] **Step 4: รันให้ผ่าน**

Run: `python -m unittest discover -s tests -v`
Expected: `OK` 5 tests

- [ ] **Step 5: เตรียม commit**

ข้อความ commit แนะนำ: `Classify operating region with cutoff and saturation warnings`

---

### Task 3: Flask skeleton + GET /

**Files:**
- Create: `app.py`
- Create: `templates/index.html`
- Create: `static/style.css`
- Create: `tests/test_web.py`

**Interfaces:**
- Consumes: ไม่มี
- Produces: `app` (โมดูล-level `Flask` instance) ให้ `tests/test_web.py` import; route `/` ที่รับ GET/POST

- [ ] **Step 1: เขียนเทสต์ GET ที่ยังไม่ผ่าน**

`tests/test_web.py` (bootstrap แบบเดียวกับ Task 1 แล้ว):
```python
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
        for name in ("vcc", "r1", "r2", "rc", "re", "beta", "vbe"):
            self.assertIn(f'name="{name}"', resp.get_data(as_text=True))
```

- [ ] **Step 2: รันให้เห็นว่า fail**

Run: `python -m unittest discover -s tests -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app'`

- [ ] **Step 3: สร้าง `app.py`**

`app.py`: สร้าง `app = Flask(__name__)`, route `@app.route("/", methods=["GET"])` คืน `render_template("index.html", ...)` โดยส่งค่าเริ่มต้นตาม spec (VCC 12, R1 100k, R2 22k, RC 2.2k, RE 1k, β 100, VBE 0.70) และ `results=None`, `errors=[]`, `values={...}`

- [ ] **Step 4: สร้าง `templates/index.html`**

ฟอร์ม `method="post" action="/"` ที่มี `<input name="...">` ครบ 7 ชื่อ และลิงก์ `static/style.css` ผ่าน `url_for`

- [ ] **Step 5: สร้าง `static/style.css`**

layout พื้นฐานเท่านั้น (ตาราง ผลลัพธ์ ยังไม่ต้องสวย) — การตกแต่งจริงอยู่ Task 6

- [ ] **Step 6: รันให้ผ่าน**

Run: `python -m unittest discover -s tests -v`
Expected: `OK` 6 tests

- [ ] **Step 7: ตรวจด้วยตาเปล่า**

Run: `python -m flask --app app run --debug` แล้วเปิด `http://127.0.0.1:5000/`
Expected: เห็นฟอร์ม 7 ช่อง; กด Ctrl+C เพื่อหยุด server

- [ ] **Step 8: เตรียม commit**

ข้อความ commit แนะนำ: `Add Flask app skeleton serving the DC bias form`

---

### Task 4: POST / คำนวณจริง + แปลงหน่วย kΩ

**Files:**
- Modify: `app.py`
- Modify: `templates/index.html`
- Modify: `tests/test_web.py`

**Interfaces:**
- Consumes: `solve_voltage_divider(...)` จาก Task 1–2
- Produces: `parse_resistance(raw: str, unit: str) -> float` (คืน Ω, unit เป็น `"ohm"` หรือ `"kohm"`), `format_results(results: dict) -> dict` (คืน dict ของสตริงพร้อมหน่วยสำหรับ template)

- [ ] **Step 1: เขียนเทสต์ POST ที่ยังไม่ผ่าน**

เพิ่มใน `tests/test_web.py`:
```python
VALID = dict(vcc="12", r1="100", r1_unit="kohm", r2="22", r2_unit="kohm",
             rc="2.2", rc_unit="kohm", re="1", re_unit="kohm",
             beta="100", vbe="0.70")

class TestPostCalculate(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_valid_input_shows_computed_values(self):
        html = self.client.post("/", data=VALID).get_data(as_text=True)
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
```

- [ ] **Step 2: รันให้เห็นว่า fail**

Run: `python -m unittest discover -s tests -v`
Expected: FAIL — ไม่พบ `1.230` ใน response (ยังไม่มี POST)

- [ ] **Step 3: implement POST + helper ใน `app.py` และแสดงผลใน template**

`parse_resistance`: คูณ 1000 เมื่อ `unit == "kohm"`, ไม่งั้นคืนค่าตามที่รับ (แปลงเป็น float แล้ว)
route POST: เรียก `parse_resistance` ทั้ง 4 ตัว → `solve_voltage_divider` → `format_results` → `render_template(..., results=..., values=form)`; ยังไม่ทำ validation (Task 5)
`format_results`: ใช้ f-string 3 ตำแหน่ง (`f"{v:.3f}"`) กับแรงดัน/IC/IE และ 2 ตำแหน่งกับ IB ที่คูณ 1e6 เป็น µA; **คง `region` เป็นตัวพิมพ์เล็กใน dict** (`"active"`) เพราะ template ใช้เป็นชื่อคลาส CSS `badge-active` และแสดงข้อความด้วย `{{ results.region|upper }}`
`templates/index.html`: เพิ่ม dropdown `<select name="r1_unit">` (ค่า `ohm`/`kohm`, default `kohm`) ทั้ง 4 ตัว และบล็อก `{% if results %}` แสดงตารางผล

- [ ] **Step 4: รันให้ผ่าน**

Run: `python -m unittest discover -s tests -v`
Expected: `OK` 8 tests

- [ ] **Step 5: เตรียม commit**

ข้อความ commit แนะนำ: `Calculate DC bias on form submit with kOhm unit conversion`

---

### Task 5: Validation

**Files:**
- Modify: `app.py`
- Modify: `templates/index.html`
- Modify: `tests/test_web.py`

**Interfaces:**
- Consumes: `parse_resistance(...)` จาก Task 4
- Produces: `validate_inputs(values: dict) -> list[str]` — คืน list ข้อความ error ภาษาไทย (ว่าง = ผ่าน); route POST ต้อง **ไม่เรียก** `solve_voltage_divider` เมื่อ list ไม่ว่าง

- [ ] **Step 1: เขียนเทสต์ validation ที่ยังไม่ผ่าน**

เพิ่มใน `tests/test_web.py`:
```python
class TestValidation(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_zero_beta_is_rejected(self):
        resp = self.client.post("/", data=dict(VALID, beta="0"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("β ต้องมากกว่า 0", resp.get_data(as_text=True))

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

    def test_zero_vcc_is_rejected(self):
        html = self.client.post("/", data=dict(VALID, vcc="0")).get_data(as_text=True)
        self.assertIn("VCC ต้องมากกว่า 0 V", html)

    def test_entered_values_survive_validation_error(self):
        html = self.client.post("/", data=dict(VALID, beta="0")).get_data(as_text=True)
        self.assertIn('value="100"', html)   # ค่า β เดิมยังอยู่ ไม่ถูกล้าง
```

- [ ] **Step 2: รันให้เห็นว่า fail**

Run: `python -m unittest discover -s tests -v`
Expected: FAIL — ไม่พบข้อความ error ภาษาไทย

- [ ] **Step 3: implement `validate_inputs` และแสดง error ใน template**

กฎตาม spec §7.5 (ข้อความต้องตรง): ค่าที่แปลงไม่ได้ → `"กรุณากรอก {FIELD} เป็นตัวเลข"`; `VCC ต้องมากกว่า 0 V`; `ค่า {FIELD} ต้องมากกว่า 0 Ω`; `β ต้องมากกว่า 0`; `VBE ต้องมากกว่า 0 V`; `VBE ต้องน้อยกว่า VCC`
เมื่อมี error: HTTP 200, แสดงทุกข้อในบล็อก error, `results=None`, คง `values` ที่ผู้ใช้กรอกกลับไปใน value ของ input/select

- [ ] **Step 4: รันให้ผ่าน**

Run: `python -m unittest discover -s tests -v`
Expected: `OK` 14 tests

- [ ] **Step 5: เตรียม commit**

ข้อความ commit แนะนำ: `Validate inputs and keep entered values on error`

---

### Task 6: หน้าตา — แผนผังวงจร SVG และป้ายโหมดมีสี

**Files:**
- Modify: `templates/index.html`
- Modify: `static/style.css`
- Modify: `tests/test_web.py`

**Interfaces:**
- Consumes: `results` dict จาก Task 4
- Produces: คลาส CSS `badge-active`, `badge-cutoff`, `badge-saturation` ที่ template ใส่ตามค่า `region`

- [ ] **Step 1: เขียนเทสต์ป้ายโหมดที่ยังไม่ผ่าน**

เพิ่มใน `tests/test_web.py`:
```python
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
```

- [ ] **Step 2: รันให้เห็นว่า fail**

Run: `python -m unittest discover -s tests -v`
Expected: FAIL — ไม่พบ `badge-active`

- [ ] **Step 3: เพิ่ม SVG, ป้ายโหมด และ CSS**

template: วาง `<svg>` วงจร NPN voltage-divider (VCC–R1–base, R2–ground, RC–collector, RE–emitter) ไว้ข้างตารางผล, ใส่ `<span class="badge badge-{{ results.region }}">` แสดงชื่อโหมดตัวพิมพ์ใหญ่
CSS: `.badge-active` เขียว, `.badge-cutoff` เทา, `.badge-saturation` ส้ม/แดง; จัด layout สองคอลัมน์ด้วย flex และยุบเป็นคอลัมน์เดียวใต้ 640px

- [ ] **Step 4: รันให้ผ่าน**

Run: `python -m unittest discover -s tests -v`
Expected: `OK` 16 tests

- [ ] **Step 5: ดูผลจริงในเบราว์เซอร์**

Run: `python -m flask --app app run --debug` แล้วเปิด `http://127.0.0.1:5000/` กรอกค่าตัวอย่าง กด Calculate
Expected: เห็นวงจร, ตารางผลพร้อมหน่วย, ป้าย ACTIVE สีเขียว; ลองแก้ RC เป็น 20 kΩ → ป้ายเปลี่ยนเป็น SATURATION

- [ ] **Step 6: เตรียม commit**

ข้อความ commit แนะนำ: `Style results with circuit diagram and region badge`

---

### Task 7: เอกสาร + ตรวจรับครบ A1–A7

**Files:**
- Create: `README.md`
- Create: `AGENTS.md`
- Create: `docs/design-note.md`
- Create: `docs/validation.md`
- Create: `docs/reflection.md`

**Interfaces:**
- Consumes: ทุกอย่างจาก Task 1–6
- Produces: เอกสารที่ทำให้ clone แล้วรันได้ (A7)

- [ ] **Step 1: เขียน `README.md`**

ต้องมี: ภาพรวมสั้น ๆ, วิธีติดตั้ง/รัน/ทดสอบด้วย PowerShell (`python -m venv .venv`, `.\.venv\Scripts\Activate.ps1`, `python -m pip install -r requirements.txt`, `python -m flask --app app run --debug`, `python -m unittest discover -s tests -v`), ระบุ URL `http://127.0.0.1:5000/`, URL repo เป็น `<YOUR_REPO_URL>` (ห้ามเดา), และหมายเหตุว่าเป็นแบบจำลอง Forward-Active

- [ ] **Step 2: เขียน `docs/validation.md`**

ตารางเทียบค่าจากเว็บกับค่าคำนวณมือของเคสอ้างอิง (VTH 2.164 V, RTH 18.03 kΩ, IB 12.30 µA, IC 1.230 mA, IE 1.242 mA, VE 1.242 V, VB 1.942 V, VC 9.294 V, VCE 8.052 V) พร้อมระบุสมมติฐานและเกณฑ์ 0.3 V

- [ ] **Step 3: เขียน `docs/design-note.md`**

ตาราง A1–A7 → ไฟล์/route ที่รองรับ (คัดลอกจาก spec §7.9)

- [ ] **Step 4: เขียน `docs/reflection.md`**

scaffold คำถาม 4 ข้อท้ายใบงานเป็นหัวข้อ พร้อมช่องคำตอบว่าง — **ห้ามเติมคำตอบแทนนักศึกษา**

- [ ] **Step 5: เขียน `AGENTS.md`**

กติกา: `dc_bias.py` ห้าม import flask; แก้สมการต้องแก้เทสต์; ห้าม commit `.venv`; ใช้ `unittest`; ข้อความ UI ภาษาไทย

- [ ] **Step 6: รันชุดทดสอบทั้งหมด**

Run: `python -m unittest discover -s tests -v`
Expected: `OK` 16 tests, ไม่มี skipped

- [ ] **Step 7: ตรวจรับด้วยมือตาม A1–A7**

| ตรวจ | วิธี |
|---|---|
| A1 | GET `/` → 200 + เห็นฟอร์ม |
| A2 | กรอกค่าตัวอย่าง → เห็นผลที่คำนวณจาก Python |
| A3 | เทียบค่ากับ `docs/validation.md` |
| A4 | กรอก β=0 และช่องว่าง → เห็น error, หน้าไม่ล้ม |
| A5 | RC=20 kΩ → SATURATION; R2=1 kΩ → CUTOFF |
| A6 | 16 tests ผ่าน |
| A7 | README ทำตามได้จริงบนเครื่องนี้ |

- [ ] **Step 8: เตรียม commit**

ข้อความ commit แนะนำ: `Add README, validation notes and reflection scaffold`

---

## หลังจบแผน (นักศึกษาทำเองผ่าน GitHub Desktop)

1. Publish repository (ถ้ายังไม่มี remote) แล้วอัปเดต URL ใน `README.md`
2. ตรวจ diff ของแต่ละชุด แล้ว commit ตามข้อความที่แนะนำในแต่ละ task
3. Push origin
4. ส่ง Repository URL + Commit SHA + ภาพหน้าจอผลคำนวณ + Test log ทาง Moodle
