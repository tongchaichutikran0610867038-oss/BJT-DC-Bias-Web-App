# AGENTS.md — กติกาสำหรับ AI agent (Lab 03)

โปรเจกต์นี้สร้างขึ้นตามใบงาน `ENG29_2121_Lab03_BJT_Bias_Web_App` และต่อยอดจาก Lab 02
ขอบเขต: Flask Web App คำนวณ DC Bias ของ BJT Common-Emitter แบบ Forward-Active จำนวน 3 วงจร

1. Voltage-Divider Bias (ของเดิมจาก Lab 02 — ต้องให้ผลเดิม)
2. Fixed Bias
3. Emitter Bias แบบแหล่งจ่ายเดียว

## ข้อห้ามเด็ดขาด

- `dc_bias.py` **ห้าม import flask** หรือรู้จัก HTTP/HTML (แยกชั้นวิศวกรรมออกจากชั้นเว็บ)
- ตัวเลขผลลัพธ์ต้องมาจาก Python backend ทุกตัว **ห้าม hard-code ใน template**
- ห้ามเพิ่ม dependency นอกจาก `Flask>=3.1,<4` (ใช้ `unittest` จาก stdlib เท่านั้น)
- ห้าม commit `.venv/`, `.env`, API key หรือ credential ใด ๆ (ดู `.gitignore`)
- เซิร์ฟเวอร์เปิดเฉพาะ `127.0.0.1` (Flask dev server) ไม่ deploy สาธารณะ
- ห้ามย้ายสมการไปไว้ใน HTML หรือสร้างระบบใหม่ทั้งโปรเจกต์

## ขอบเขตที่ต้องรักษา (Lab 03)

มีเฉพาะ: DC Bias, 3 วงจรไบอัส, validation, region warning (Active/Cutoff/Saturation), automated tests  
ไม่มี: AC, Bode, Transient, Signal Generator, Overlay, FET, SPICE, Load Line, interactive schematic, ฐานข้อมูล, login

## คำสั่งที่ใช้ซ้ำ

ในเครื่องนี้ `python` เป็น alias ของ Microsoft Store ให้ใช้ `py -3.14` หรือ venv โดยตรง

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app app run --debug
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## เมื่อแก้สมการใน `dc_bias.py`

ต้องเพิ่ม/แก้เทสต์ใน `tests/test_dc_bias.py` ก่อนเสมอ (TDD) แม้ใบงาน Lab 03
จะไม่ได้บังคับให้เขียน unittest ใหม่ แต่เทสต์เดิมใช้ป้องกันไม่ให้ผล Lab 02 เปลี่ยน

แก้ HTML **ไม่จำเป็น** เพราะสมการอยู่ใน Python ต่างหากจาก template — แก้ HTML
เฉพาะเมื่อเปลี่ยนรูปแบบการแสดงผลเท่านั้น

## เกณฑ์ตรวจรับ Lab 03

- A1: Voltage-Divider เดิมต้องได้ผลเดิม
- A2: Fixed Bias ใช้ RB ได้โดยไม่ต้องกรอก RE
- A3: Emitter Bias ใช้ RB + RE
- A4: เปลี่ยน RE จาก 1 kΩ เป็น 2 kΩ แล้ว IC ต้องลดลง
- A5: อินพุตผิด (เช่น RB = 0) ต้องแจ้ง error และไม่แสดงผลรอบเก่า
- ต้องมีหลักฐานจาก Browser และบันทึกวิธีตรวจจริง (Playwright MCP / OpenCode Browser / Manual)
