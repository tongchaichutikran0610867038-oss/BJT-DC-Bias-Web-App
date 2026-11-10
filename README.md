# BJT DC Bias Web App — Lab 02 (ENG29 2121)

Flask web application ที่คำนวณ **DC Operating Point** ของวงจร BJT Common-Emitter แบบ
Voltage-Divider Bias บน Python backend แสดงผลผ่านเบราว์เซอร์ที่ `http://127.0.0.1:5000/`

## โครงสร้างไฟล์

```
├── app.py              # Flask routes, ฟอร์ม, validation, หน่วย
├── dc_bias.py          # สมการวิศวกรรมล้วน (ไม่รู้จัก Flask/HTML)
├── templates/index.html  # ฟอร์ม + ตารางผล + วงจร SVG (Jinja)
├── static/style.css    # รูปลักษณ์หน้าเว็บ
├── tests/test_dc_bias.py # テストสมการวิศวกรรม
├── tests/test_web.py   # テスト Flask route / ฟอร์ม
├── requirements.txt    # Flask>=3.1,<4
├── README.md           # ไฟล์นี้
├── AGENTS.md           # กติกาสำหรับ AI agent
└── docs/
    ├── design-note.md  # mapping เกณฑ์ตรวจรับ A1–A7
    ├── validation.md   # ตรวจสอบกับค่าคำนวณอิสระ
    └── reflection.md   # คำตอบคำถามรายบุคคล (นักศึกษาเติมเอง)
```

## ติดตั้งและรัน (PowerShell)

```powershell
# 1. สร้างและเปิด venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. ติดตั้ง dependencies
python -m pip install -r requirements.txt

# 3. รันเซิร์ฟเวอร์ (เฉพาะเครื่องพัฒนา)
python -m flask --app app run --debug

# 4. เปิดเบราว์เซอร์ที่ http://127.0.0.1:5000/

# 5. รันแบบทดสอบ (จากอีก terminal เดียวกันหรือหลังหยุดเซิร์ฟเวอร์)
python -m unittest discover -s tests -v
```

## ค่าตัวอย่างอ้างอิง

ใส่ตามใบงานแล้วกด **Calculate DC Bias**:

| ค่า | ค่าเริ่มต้น |
|---|---|
| VCC | 12 V |
| R1 | 100 kΩ |
| R2 | 22 kΩ |
| RC | 2.2 kΩ |
| RE | 1 kΩ |
| β | 100 |
| VBE | 0.70 V |

ผลที่คาดหวัง (ผ่านการคำนวณมือแล้ว):

| ปริมาณ | ค่า |
|---|---|
| VB | 1.942 V |
| VE | 1.242 V |
| VC | 9.294 V |
| VCE | 8.052 V |
| IC | 1.230 mA |
| IB | 12.30 µA |
| โหมด | ACTIVE |

## เงื่อนไขและข้อจำกัด

- แบบจำลอง **Forward-Active** (β คงที่, VBE คงที่) เฉพาะ DC Bias เท่านั้น
- ไม่มี AC analysis, Bode plot, Transient, SPICE solver, หรือ Bias type อื่น
- เซิร์ฟเวอร์ Flask development server ใช้เฉพาะบน `127.0.0.1` ไม่เปิดสู่เครือข่ายสาธารณะ
- ห้าม commit `.venv/`, `.env`, API key หรือ credential ใด ๆ (มี `.gitignore` แล้ว)

## เกณฑ์ตรวจรับ (A1–A7)

ดูรายละเอียดใน `docs/design-note.md`

## สร้าง repo บน GitHub

หลังจาก commit แล้ว ให้สร้าง remote repository บน GitHub ผ่าน **GitHub Desktop**
(**Publish repository**) แล้วอัปเดต URL ตัวแปล `<YOUR_REPO_URL>` ในไฟล์นี้ให้นักศึกษาที่จะ clone ต่อใช้ได้
