# BJT DC Bias Web App — Lab 03 (ENG29 2121)

Flask web application ที่คำนวณ **DC Operating Point** ของวงจร BJT Common-Emitter ได้ 3 แบบเลือกได้จากหน้าเว็บ:

- **Voltage-Divider Bias** (ของเดิมจาก Lab 2 — ผลยังคงเดิมทุกประการ)
- **Fixed Bias** (RB · RC)
- **Emitter Bias แบบแหล่งจ่ายเดียว** (RB · RC · RE)

เปิดผ่านเบราว์เซอร์ที่ `http://127.0.0.1:5000/`

**GitHub repo:** <https://github.com/tongchaichutikran0610867038-oss/BJT-DC-Bias-Web-App>  
**Commit SHA สำหรับส่งงาน:** ดูจาก GitHub หลัง push หรือรัน `git log -1 --format=%H`

## โครงสร้างไฟล์

```
├── app.py                # Flask route, เลือกโหมดด้วย if/elif, แปลงหน่วย, validation
├── dc_bias.py            # สมการวิศวกรรมล้วน 3 ฟังก์ชัน (ไม่รู้จัก Flask/HTML)
│   ├── solve_voltage_divider(...)  # เดิมจาก Lab 2 (ไม่แก้)
│   ├── solve_fixed_bias(...)
│   └── solve_emitter_bias(...)
├── templates/index.html  # ฟอร์มเลือกโหมด + ผล + วงจร SVG ตามโหมด (Jinja)
├── static/style.css
├── tests/
│   ├── test_dc_bias.py   # ทดสอบสมการวิศวกรรม รวมฟังก์ชันใหม่
│   └── test_web.py       # ทดสอบ route/ฟอร์ม/โหมด/validation
├── requirements.txt      # Flask>=3.1,<4 (ไม่เพิ่ม dependency)
├── README.md             # ไฟล์นี้
├── AGENTS.md             # กติกาสำหรับ AI agent
└── docs/
    ├── design-note.md    # mapping ข้อกำหนด Lab 03 → ไฟล์/ฟังก์ชัน
    ├── validation.md     # ตาราง A1–A5 + หลักฐานจาก browser + อธิบาย MCP
    ├── reflection.md     # คำตอบคำถามรายบุคคล (นักศึกษาเติมเอง)
    └── evidence-a1.png   # หลักฐานภาพหน้าจอกรณี A1
```

## ติดตั้งและรัน (PowerShell)

> ในเครื่องนี้คำสั่ง `python` เป็น alias ของ Microsoft Store และใช้ไม่ได้ ให้ใช้ `py -3.14` หรือ venv แทน

```powershell
# 1. สร้าง venv (ครั้งแรก)
py -3.14 -m venv .venv

# 2. ติดตั้ง dependencies
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 3. รันเซิร์ฟเวอร์ (เฉพาะ 127.0.0.1)
.\.venv\Scripts\python.exe -m flask --app app run --debug

# 4. เปิด http://127.0.0.1:5000/

# 5. รันเทสต์
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

ผลลัพธ์ตอนนี้: **28 tests ผ่านทั้งหมด**

## วิธีใช้หน้าเว็บ

1. เลือกวงจรในช่อง **วงจรที่เลือก** (Voltage-Divider / Fixed / Emitter)
2. กด **Calculate DC Bias** ครั้งหนึ่งเพื่อสลับช่องอินพุตให้ตรงโหมด (ไม่ต้องใช้ JavaScript)
3. กรอกเฉพาะช่องที่โผล่มาแล้วกด **Calculate DC Bias** อีกครั้ง

| โหมด | ช่องที่ใช้ |
|---|---|
| Voltage-Divider Bias | VCC, R1, R2, RC, RE, β, VBE |
| Fixed Bias | VCC, RB, RC, β, VBE (ไม่มี RE) |
| Emitter Bias | VCC, RB, RC, RE, β, VBE |

หน่วย resistance เลือกได้ Ω / kΩ / MΩ (ช่อง RB มี MΩ ให้เลือกโดยตรง 1 MΩ = 1,000 kΩ = 1,000,000 Ω)

## ค่าอ้างอิง (ตรวจแล้วผ่าน Browser — A1–A5)

ใช้ร่วม: `VCC = 12 V`, `RC = 2.2 kΩ`, `β = 100`, `VBE = 0.70 V`

### ค่าอ้างอิงอิสระของโหมดใหม่ (A3 — Emitter, RB = 1 MΩ, RE = 1 kΩ)

คำนวณมือจากสมการในใบงาน ไม่ได้อ่านค่าจากโปรแกรม:

```text
IB = (12 - 0.70) / (1,000,000 + 101×1,000)
   = 11.3 / 1,101,000 = 10.2634 µA
IC = 100 × 10.2634 µA = 1.02634 mA
IE = 101 × 10.2634 µA = 1.03660 mA
VE = 1.03660 × 1,000 = 1.03660 V
VB = 1.03660 + 0.70 = 1.73660 V
VC = 12 - (1.02634 mA × 2.2 kΩ) = 9.74205 V
VCE = 9.74205 - 1.03660 = 8.70545 V
```

| กรณี | อินพุต | IC | VCE |
|---|---|---|---|
| A1 Divider | R1=100 kΩ, R2=22 kΩ, RE=1 kΩ | 1.230 mA | 8.052 V |
| A2 Fixed | RB=1 MΩ | 1.130 mA | 9.514 V |
| A3 Emitter | RB=1 MΩ, RE=1 kΩ | 1.026 mA | 8.705 V |
| A4 Emitter | RB=1 MΩ, RE=2 kΩ | 0.940 mA | 8.033 V |
| A5 Fixed | RB=0 | แจ้ง error `ค่า RB ต้องมากกว่า 0 Ω` ไม่แสดงผลเก่า | — |

รายละเอียด ค่าคำนวณอิสระ วิธีตรวจ และหลักฐานอยู่ใน [`docs/validation.md`](docs/validation.md)

## หมายเหตุเรื่อง MCP / Browser

- เครื่องนี้ไม่มี Node.js / npx จึง **Playwright MCP: NOT RUN** และใช้ **OpenCode Browser** ที่มาพร้อม OpenCode Desktop แทน (ใบงานให้คะแนนตรวจผลเท่ากันทุกวิธี)
- ถ้าต้องการใช้ Playwright MCP จริง ให้ติดตั้ง Node.js 18+ แล้วเพิ่มใน `opencode.json` (OpenCode V2):

```json
{
  "mcp": {
    "servers": {
      "playwright": {
        "type": "local",
        "command": ["npx", "-y", "@playwright/mcp@latest", "--browser", "chrome", "--isolated"]
      }
    }
  }
}
```

ปิด–เปิด OpenCode แล้วตรวจด้วย `/mcps` หรือ `opencode mcp list`

## เงื่อนไขและข้อจำกัด

- แบบจำลอง **Forward-Active** (β คงที่, VBE คงที่) เฉพาะ DC Bias เท่านั้น
- ทั้งสามโหมดเตือน saturation ที่ `VCE ≤ 0.2 V` ตามใบงาน Lab 03 (กรณี A1 ยังได้ `VCE = 8.052 V` จึงไม่กระทบผลเดิม)
- ไม่มี AC, Bode, Transient, SPICE, Load Line, หรือ Bias type อื่นนอกจาก 3 แบบนี้
- เซิร์ฟเวอร์ Flask development ใช้เฉพาะบน `127.0.0.1` ไม่เปิดสู่เครือข่ายสาธารณะ
- ห้าม commit `.venv/`, `.env`, API key หรือ credential ใด ๆ (มี `.gitignore` แล้ว)

## ส่งงาน

ก่อน Commit ให้ตรวจ `git diff` และ `git diff --staged` แล้ว Commit/Push ตาม Lab 1–2  
**หมายเหตุ**: เครื่องนี้ไม่มี `git` ใน `PATH` แต่มี Git ที่มากับ GitHub Desktop ที่  
`C:\Users\b6837228\AppData\Local\GitHubDesktop\app-3.6.11\resources\app\git\cmd\git.exe`  
หรือใช้ GitHub Desktop กด **Commit** แล้ว **Push** ได้ตามปกติ

ต้องส่ง **GitHub URL + Commit SHA** ของ commit ล่าสุดพร้อมงาน Lab 03

### AI ช่วยอะไร และนักศึกษาตรวจอะไร

- **AI ช่วย**: เขียน `solve_fixed_bias`, `solve_emitter_bias`, ปรับ `app.py`/template ให้เลือกโหมด, เพิ่มเทสต์, รันตรวจ Browser และร่าง `docs/validation.md`
- **นักศึกษาตรวจ**: สมการและหน่วยเทียบกับค่าคำนวณมือ, ผล A1–A5 จากหน้าเว็บจริง, ทิศทาง A3→A4
- **จุดเลือกฟังก์ชัน**: `SOLVERS[mode]` และ `if/elif` ใน `app.py`
- **จุดแปลงหน่วย**: `parse_resistance()` ใน `app.py` (Ω / kΩ / MΩ → Ω)
- **จุดตรวจอินพุต**: `required_fields()` + `validate_inputs()` ใน `app.py` (รวมการ reject `NaN`/`Inf` ด้วย `math.isfinite`)
- **จุดคำนวณ**: `dc_bias.py` ทั้งสามฟังก์ชัน (ไม่ import Flask และไม่รู้จัก HTML)
