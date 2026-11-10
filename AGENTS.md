# AGENTS.md — กติกาสำหรับ AI agent (Lab 02)

โปรเจกต์นี้สร้างขึ้นตามใบงาน `Lab02_BJT_Simulator_Brainstorm_2-2569.html`
ขอบเขต: Flask Web App คำนวณ DC Bias ของ BJT Common-Emitter (Voltage-Divider) เท่านั้น

## ข้อห้ามเด็ดขาด

- `dc_bias.py` **ห้าม import flask** หรือรู้จัก HTTP/HTML (แยกชั้นวิศวกรรมออกจากชั้นเว็บ)
- ตัวเลขผลลัพธ์ต้องมาจาก Python backend ทุกตัว **ห้าม hard-code ใน template**
- ห้ามเพิ่ม dependency นอกจาก `Flask>=3.1,<4` (ใช้ `unittest` จาก stdlib เท่านั้น)
- ห้าม commit `.venv/`, `.env`, API key หรือ credential ใด ๆ (ดู `.gitignore`)
- เซิร์ฟเวอร์เปิดเฉพาะ `127.0.0.1` (Flask dev server) ไม่ deploy สาธารณะ

## ขอบเขตที่ต้องรักษา (Week 2)

มีเฉพาะ: DC Bias, Voltage-Divider Bias, validation, region warning (Active/Cutoff/Saturation), automated tests
ไม่มี: AC, Bode, Transient, Signal Generator, Overlay, Bias type อื่น, FET, SPICE, Load Line, interactive schematic, ฐานข้อมูล, login

## คำสั่งที่ใช้ซ้ำ

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m flask --app app run --debug
python -m unittest discover -s tests -v
```

## เมื่อแก้สมการใน `dc_bias.py`

ต้องเพิ่ม/แก้เทสต์ใน `tests/test_dc_bias.py` ก่อนเสมอ (TDD) แก้ HTML **ไม่จำเป็น** เพราะ
สมการอยู่ใน Python ต่างหากจาก template — แก้ HTML เฉพาะเมื่อเปลี่ยนรูปแบบการแสดงผลเท่านั้น
