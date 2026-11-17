# Design — BJT Common-Emitter DC Bias Web App (Lab 02)

- **วันที่:** 2026-11-10
- **รายวิชา:** ENG29 2121 Computer Programming for Electrical Engineers (2/2569)
- **สถานะ:** อนุมัติแล้วโดยนักศึกษา (2026-11-10)
- **ที่มา:** ใบงาน `Lab02_BJT_Simulator_Brainstorm_2-2569.html`

## 1. เจตนาและเหตุผล (Intent & Why)

สร้าง Web Application จริง (ไม่ใช่ HTML ไฟล์เดียว) ที่รับพารามิเตอร์วงจร BJT Common-Emitter แบบ
Voltage-Divider Bias แล้วให้ **Python backend คำนวณ DC Operating Point** และแสดงผลใน Browser
เพื่อให้นักศึกษาเห็นครบวงจร Frontend → HTTP → Backend → Template และฝึกตรวจสอบผลทางวิศวกรรม
ด้วยการคำนวณอิสระของตนเอง ภายในคาบปฏิบัติการ 3 ชั่วโมง

## 2. เป้าหมาย (Goals)

- G1 เปิดเว็บผ่าน `http://127.0.0.1:5000/` ด้วย Flask ได้จริง (ไม่ใช่ `file://`)
- G2 รับ VCC, R1, R2, RC, RE, β, VBE และคำนวณ VB, VE, VC, VCE, IC (แสดง IB, IE เพิ่ม)
- G3 แสดงผลพร้อมหน่วย และระบุโหมดการทำงาน Active / Cutoff / Saturation
- G4 Validation: ค่าผิดหรือไม่ครบ → ข้อความ error ที่อ่านรู้เรื่อง หน้าเว็บไม่ล้ม
- G5 Automated tests: ≥3 ตัวตรวจสมการวิศวกรรม + ≥1 ตัวผ่าน Flask test client
- G6 Commit ผ่าน GitHub Desktop พร้อม README ที่ทำให้ clone แล้วรันได้

## 3. สิ่งที่ไม่ทำ (Non-goals)

ตัดตามขอบเขต Week 2 ของใบงานอย่างเคร่งครัด:

- ไม่มี AC analysis, Bode plot, Transient, Signal Generator, Overlay animation
- ไม่มี Bias type อื่น (Fixed, Emitter bias), ไม่มี FET
- ไม่มี SPICE/ngspice solver, ไม่มี DC Load Line
- ไม่มี interactive schematic editor, ไม่มีปุ่ม knob/สไลเดอร์
- ไม่มีฐานข้อมูล, ระบบ login, หรือ deploy ขึ้น cloud
- ไม่ใช้ JavaScript framework หรือ build tool

## 4. Anti-goals (ถือว่าล้มเหลวแม้โปรแกรมจะรัน)

- ตัวเลขผลลัพธ์ถูก hard-code ไว้ใน HTML หรือ JS
- `dc_bias.py` รู้จัก HTML/HTTP (ปนชั้นกัน)
- แสดงผลโดยไม่มีหน่วย หรือไม่แจ้ง warning เมื่อแบบจำลอง Forward-Active ใช้ไม่ได้
- มี test แต่ไม่เคยรันจริง แล้วอ้างว่าผ่าน
- Commit `.venv/`, `.env` หรือ credential ใด ๆ

## 5. ข้อจำกัด (Constraints)

- Python 3.14.2 (ติดตั้งที่ `C:\Program Files\Python314`), Flask 3.x, ใช้ `unittest` จาก stdlib
- Windows 11 + PowerShell, ไม่มี Node/npm (จึงไม่ใช้ frontend build tool)
- Serve เฉพาะ `127.0.0.1` ด้วย Flask development server
- งบเวลาสร้างจริง ~75 นาที ต้องจบในคาบ
- repo ปัจจุบันว่าง (มีเฉพาะ `.gitattributes`, `.gitignore`) และ **ยังไม่มี remote GitHub**
- การ commit ทำผ่าน GitHub Desktop (diff/commit/push ด้วย GUI)
- **เจ้าของ Git คือนักศึกษา:** ผู้สร้าง (agent) เตรียม working tree ให้พร้อมและรัน test ให้ผ่าน
  แต่ไม่ commit/push เอง และไม่สร้าง remote — นักศึกษาเป็นผู้ตรวจ diff, commit และ publish repo
  ผ่าน GitHub Desktop ตามที่ตกลงกันไว้

## 6. แนวทางที่พิจารณา (Approaches)

| # | แนวทาง | ข้อดี | ข้อเสีย | สรุป |
|---|--------|-------|---------|------|
| A | ฟอร์มเรียบหน้าเดียว + ตารางผล | เร็วที่สุด เหลือเวลาไปทำ validation/tests | ดูจืด ไม่ได้สื่อ "งานวิศวกรรม" | ไม่เลือก — เสียดายโอกาส演示 |
| B | **หน้าเดียว + แผนผังวงจร SVG + ป้ายโหมดมีสี** | เวลาขึ้นจอดี ต้นทุนเวลาเพิ่มเล็กน้อย ยังทำ tests ครบได้ | ต้องเขียน SVG/ CSS เพิ่มราว 10–15 นาที | **เลือก** |
| C | แยกหน้า input → results | แยกความรับผิดชอบสวยงาม | เพิ่ม route/template/เทสต์ โดยได้ประโยชน์ไม่คุ้มเวลา | ไม่เลือก — เกินจำเป็นต่อขอบเขต |

**ที่เลือก: B** — เพราะใบงานให้น้ำหนักกับ "Web App ที่แสดงผล DC Bias พร้อมหน่วยและ warning"
การเห็นวงจร+ป้ายโหมดช่วยให้ตรวจรับ A3/A5 ได้ด้วยตาเปล่า และยังอยู่ในขอบเขต DC Bias เท่านั้น

## 7. การออกแบบ (The Design)

### 7.1 โครงสร้างไฟล์

```
BJT DC Bias Web App/
├── app.py                  # Flask routes + form parsing + unit conversion
├── dc_bias.py              # สมการวิศวกรรมล้วน (ไม่ import flask)
├── templates/index.html    # ฟอร์ม + ผลลัพธ์ (Jinja)
├── static/style.css        # layout + สีป้ายโหมด
├── tests/test_dc_bias.py   # สมการ, ช่วงโหมด, unit conversion
├── tests/test_web.py       # GET /, POST / (valid, invalid)
├── requirements.txt        # Flask>=3.1,<4
├── README.md               # วิธีติดตั้ง/รัน/ทดสอบ (PowerShell)
├── AGENTS.md               # convention สำหรับ AI agent
└── docs/
    ├── design-note.md      # สรุปดีไซน์ + mapping A1–A7
    ├── validation.md       # ผลตรวจสอบกับค่าคำนวณอิสระ
    └── reflection.md       # นักศึกษาเขียนเอง
```

### 7.2 เส้นทาง HTTP

| Route | Method | พฤติกรรม |
|---|---|---|
| `/` | GET | แสดงฟอร์มว่าง (ค่าเริ่มต้นตามใบงาน) + HTTP 200 |
| `/` | POST | parse → validate → คำนวณ → render หน้าเดิมพร้อมผลหรือ error |

เหตุผลที่ใช้ `POST /` แทน `/calculate`: ใบงานอนุญาตทั้งสองแบบ และการ render หน้าเดิม
ทำให้ผู้ใช้เห็นค่าที่กรอกกับผลลัพธ์พร้อมกัน ลดจำนวน template/route ที่ต้องทดสอบ

### 7.3 ชั้นคำนวณ (`dc_bias.py`)

ฟังก์ชันเดียวที่เปิดให้ใช้:

```python
def solve_voltage_divider(vcc, r1, r2, rc, re, beta, vbe) -> dict
```

คืนค่า dict: `vth, rth, ib, ic, ie, ve, vb, vc, vce, region, message`
หน่วยภายในเป็น SI (V, A, Ω) ทั้งหมด — **การแปลง kΩ → Ω เกิดที่ `app.py` ก่อนเรียกฟังก์ชันนี้**

สมการ (Forward-Active, β คงที่, VBE คงที่):

```
VTH = VCC * R2 / (R1 + R2)
RTH = R1 * R2 / (R1 + R2)
IB  = (VTH - VBE) / (RTH + (beta + 1) * RE)
IC  = beta * IB
IE  = (beta + 1) * IB
VE  = IE * RE
VB  = VE + VBE
VC  = VCC - IC * RC
VCE = VC - VE
```

**การจำแนกโหมด (ลำดับความสำคัญ):**

1. `VTH <= VBE` → `region = "cutoff"`
   รายงาน IB = IC = IE = 0, VE = 0, VB = VTH, VC = VCC, VCE = VCC
   message: "VTH ≤ VBE: ทรานซิสเตอร์อยู่ในช่วง Cutoff — สมการ Forward-Active ใช้ไม่ได้"
2. คำนวณตามสมการ แล้วถ้า `VCE <= 0.3` → `region = "saturation"`
   แสดงค่าที่คำนวณได้ แต่กำกับว่า "VCE ใกล้/เข้าสู่ Saturation — ค่าที่ได้ไม่ใช่ผลที่เชื่อถือได้"
3. นอกนั้น → `region = "active"`, message: "Forward-Active approximation"

> 0.3 V เป็นเกณฑ์เตือนเชิงวิศวกรรม (ไม่ใช่ 0.2 V แบบ SPICE) และระบุไว้ใน `validation.md`

### 7.4 อินพุตและหน่วย

| Field | อินพุต | ค่าเริ่มต้น | หมายเหตุ |
|---|---|---|---|
| VCC | ตัวเลข + หน่วย V (คงที่) | 12 | ต้อง > 0 |
| R1, R2, RC, RE | ตัวเลข + dropdown Ω / kΩ | 100 k, 22 k, 2.2 k, 1 k | ต้อง > 0 หลังแปลงเป็น Ω |
| β | ตัวเลข | 100 | ต้อง > 0 |
| VBE | ตัวเลข V | 0.70 | ต้อง > 0 |

เหตุผลที่มี dropdown หน่วย: ใบงานระบุชัดว่า "ต้องแปลง kΩ เป็น Ω ให้สอดคล้องก่อนคำนวณ"
การให้ผู้ใช้เลือกหน่วยแล้วระบบแปลงเองลดความผิดพลาด และทดสอบได้ตรงจุด

### 7.5 Validation

ตรวจที่ `app.py` ก่อนเรียกชั้นคำนวณ ทุกกรณีรวบเป็น list แล้วแสดงพร้อมกัน:

| เงื่อนไข | ข้อความ |
|---|---|
| ช่องว่าง / ไม่ใช่ตัวเลข | "กรุณากรอก {field} เป็นตัวเลข" |
| VCC ≤ 0 | "VCC ต้องมากกว่า 0 V" |
| R ใด ๆ ≤ 0 (หลังแปลงหน่วย) | "ค่า {field} ต้องมากกว่า 0 Ω" |
| β ≤ 0 | "β ต้องมากกว่า 0" |
| VBE ≤ 0 | "VBE ต้องมากกว่า 0 V" |
| VBE ≥ VCC | "VBE ต้องน้อยกว่า VCC" |

เมื่อมี error: HTTP 200, แสดง error ทุกข้อ, คงค่าที่ผู้ใช้กรอกไว้ในฟอร์ม, ไม่เรียก `solve_`

### 7.6 หน้าจอ (ข้อความสเก็ตช์)

```
┌─ BJT DC Bias Calculator ─────────────────────────────┐
│ [ Voltage-Divider Bias · NPN · Forward-Active ]      │
│                                                      │
│  VCC [12] V      β [100]      VBE [0.70] V           │
│  R1 [100][kΩ▾]   R2 [22][kΩ▾]                        │
│  RC [2.2][kΩ▾]   RE [1][kΩ▾]                         │
│                    [ Calculate DC Bias ]             │
│                                                      │
│  ┌ วงจร (SVG) ─────┐  ┌ ผลลัพธ์ ────────────┐        │
│  │ VCC ─R1─┬─RC─   │  │ VB  1.942 V         │        │
│  │        B│C      │  │ VE  1.242 V         │        │
│  │        NPN      │  │ VC  9.294 V         │        │
│  │      R2 │ RE    │  │ VCE 8.052 V         │        │
│  └─────────────────┘  │ IC  1.230 mA        │        │
│                       │ IB  12.30 µA        │        │
│                       │ [● ACTIVE]          │        │
│                       └─────────────────────┘        │
└──────────────────────────────────────────────────────┘
```

- ป้ายโหมด: Active = เขียว, Cutoff = เทา, Saturation = ส้ม/แดง
- ค่าตัวเลข: แรงดัน 3 ตำแหน่งทศนิยม (V), กระแส mA 3 ตำแหน่ง, IB แสดงเป็น µA
- ไม่มี JavaScript; ทั้งหมด render ฝั่ง server

### 7.7 แผนการทดสอบ

`tests/test_dc_bias.py` (unittest):

1. เคสอ้างอิงใบงาน (VCC 12, R1 100k, R2 22k, RC 2.2k, RE 1k, β 100, VBE 0.7)
   → VTH ≈ 2.164 V, RTH ≈ 18.033 kΩ, IC ≈ 1.230 mA, VE ≈ 1.242 V, VCE ≈ 8.052 V (±0.01)
2. เปลี่ยน β → IC เปลี่ยนตามสัดส่วนที่คาดหมาย (ยืนยันว่า β ถูกใช้จริง)
3. Cutoff: VTH < VBE → region == "cutoff", IC == 0
4. Saturation: RE/RC ทำให้ VCE ≤ 0.3 → region == "saturation"
5. การแปลงหน่วย kΩ → Ω ทำงานถูก (100 kΩ ให้ผลเท่ากับ 100000 Ω)

`tests/test_web.py` (Flask test client):

6. GET / → 200 และมีช่อง input ครบ 7 ตัว
7. POST / ค่าถูกต้อง → 200 และ HTML มี "1.230" (ค่ามาจาก Python)
8. POST / ค่า β = 0 → 200, มีข้อความ error, ไม่มี traceback

### 7.8 เอกสารและ Git

- `README.md`: PowerShell commands (`python -m venv .venv`, activate, `pip install -r requirements.txt`,
  `python -m flask --app app run --debug`, `python -m unittest discover -s tests -v`)
  ส่วน URL ของ repo ใช้ placeholder `<YOUR_REPO_URL>` จนกว่านักศึกษาจะ publish บน GitHub
  (ห้ามใส่ URL ที่คาดเดาเอง)
- `docs/validation.md`: ตารางเทียบค่าที่เว็บคำนวณกับค่าคำนวณมือ พร้อมระบุว่าใช้แบบจำลองใด
- `docs/design-note.md`: mapping A1–A7 แบบหนึ่งบรรทัดต่อข้อ ตามตาราง §7.9
- `docs/reflection.md`:  scaffold คำถาม 4 ข้อจากท้ายใบงาน พร้อมช่องคำตอบว่าง
  (นักศึกษาเติมเอง ห้ามให้ AI เขียนคำตอบ):
  1. เหตุใดการเปิด `templates/index.html` ตรง ๆ จึงไม่เท่ากับการรัน Flask?
  2. ฟอร์มส่งข้อมูลไป Python อย่างไร?
  3. แก้สมการใน `dc_bias.py` แล้วต้องแก้ HTML หรือไม่?
  4. ทำไมผลใน Region ที่แบบจำลองใช้ไม่ได้จึงต้องมี Warning?
- **ผู้สร้างเตรียมของให้ commit-ready เท่านั้น** — แบ่งชุดการเปลี่ยนแปลงให้ตรงกับ 4 commit
  ที่นักศึกษาจะทำใน GitHub Desktop: (1) design doc, (2) `dc_bias.py` + tests,
  (3) `app.py` + templates + CSS, (4) README/AGENTS/docs ที่เหลือ
  แต่ **ไม่รัน `git commit` เอง** และไม่ push

### 7.9 การแมปกับเกณฑ์ตรวจรับ

| เกณฑ์ | องค์ประกอบที่รองรับ |
|---|---|
| A1 GET / | route `/` + `templates/index.html` |
| A2 POST / | parse form → `solve_voltage_divider` → render |
| A3 Engineering Reference | `dc_bias.py` + `docs/validation.md` |
| A4 Validation | §7.5 |
| A5 Outside Active Region | §7.3 การจำแนกโหมด + ป้ายสี |
| A6 Unit + HTTP tests | `tests/test_dc_bias.py` 5 ตัว + `tests/test_web.py` 3 ตัว |
| A7 GitHub Reproducibility | README + `requirements.txt` + `.gitignore` |

## 8. สิ่งที่เหลือให้ผู้สร้างตัดสินใจ (Left to the builder)

- โทนสี/ระยะห่าง/ฟอนต์ และรายละเอียด SVG ของวงจร
- ถ้อยคำภาษาไทยของข้อความ error และ label (ความหมายต้องตรง §7.5)
- ลำดับการแสดงผล IB/IE และการจัดกลุ่มตัวเลข
- จำนวนทศนิยมของ VTH/RTH ที่แสดง (ถ้าจะแสดง)
- การแบ่ง commit ย่อยที่ละเอียดกว่าระดับ §7.8
