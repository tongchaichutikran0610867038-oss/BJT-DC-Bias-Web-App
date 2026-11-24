# AGENTS.md — กติกาสำหรับ AI agent (Lab 03 + Lab 04)

โปรเจกต์นี้สร้างขึ้นตามใบงาน `ENG29_2121_Lab03_BJT_Bias_Web_App` แล้วต่อยอดตาม
`Lab04_BJT_Amplifier_Simulator` (อนุมัติโดยเจ้าของ repo แล้ว)

## ขอบเขตที่ต้องรักษา

**Lab 03 (ห้ามเปลี่ยนผลเดิม)**

1. Voltage-Divider Bias (ของเดิมจาก Lab 02 — ผลต้องเหมือนเดิมทุกประการ)
2. Fixed Bias
3. Emitter Bias แบบแหล่งจ่ายเดียว
4. validation, region warning (Active/Cutoff/Saturation), unittest เดิม 28 ตัว

**Lab 04 (เพิ่มเฉพาะที่อนุมัติ)**

5. วงจร CE Voltage-Divider อ้างอิง **หนึ่งวงจร** ผ่าน `spice_engine.py`
5b. **ฟอร์มเดียว dropdown เดียว 6 ตัวเลือก** (1–3 Lab 03, 4–6 Lab 04) — ทางเดินเลือกตาม `mode` ใน POST; ห้ามแยกฟอร์มอีก
6. SPICE ได้จริง 3 analysis: `.op`, `.ac`, `.tran` ด้วย `ngspice_con.exe`
7. กราฟ Bode (gain dB + phase °) และ waveform (V vs time ms) ที่สร้างจาก `run.raw` ที่ parse ได้
8. ฟอร์ม Amplitude/Frequency, status/provenance, หลักฐาน netlist/log และ error state

## ข้อห้ามเด็ดขาด

- `dc_bias.py` **ห้าม import flask** หรือรู้จัก HTTP/HTML — และ **ห้ามแก้สมการ/ผล Lab 03**
- ตัวเลขผลลัพธ์ต้องมาจาก Python backend ทุกตัว **ห้าม hard-code ใน template**
- ผลกราฟต้องมาจาก ngspice run จริง; ห้าม mock trace, ห้ามแสดงกราฟ/STATUS: SUCCESS ค้างเมื่อ engine fail
- ห้ามเพิ่ม Python dependency นอกจาก `Flask>=3.1,<4` (`unittest`, `subprocess`, `math`, `tempfile` เป็น stdlib)
- ngspice เป็น executable ภายนอก → ห้าม/pip จำลอง และต้องตรวจ missing engine / nonzero rc / timeout / empty raw
- ห้าม commit `.venv/`, `.env`, API key หรือ credential ใด ๆ (ดู `.gitignore`)
- เซิร์ฟเวอร์เปิดเฉพาะ `127.0.0.1` (Flask dev server) ไม่ deploy สาธารณะ
- ห้ามย้ายสมการ Lab 03 ไปไว้ใน HTML หรือสร้างระบบใหม่ทับโปรเจกต์เดิม
- JS ที่เพิ่มได้เฉพาะ UI status (`STATUS: RUNNING`) — ห้ามคำนวณค่าทางวิศวกรรมใน browser

## โครงสร้างที่เพิ่ม

- `spice_engine.py` — สร้าง netlist, เรียก `ngspice_con.exe` ด้วย `subprocess.run([...], shell=False)`, parse ASCII `.raw`
- `plots.py` — วาด SVG จาก array ของ engine (stdlib ล้วน)
- `tests/test_spice_engine.py` — ตรวจ directive/source/parser/error path และรอบจริง (skip ถ้าไม่มี engine)
- `docs/validation.md` — ตาราง A1–A5 **และ** B1–B8 พร้อม status ของ Playwright MCP / OpenCode Browser / Impeccable
- `docs/captures/` — screenshot จาก browser จริง

## คำสั่งที่ใช้ซ้ำ

ในเครื่องนี้ `python` เป็น alias ของ Microsoft Store ให้ใช้ `py -3.14` หรือ venv โดยตรง

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app app run --debug --host 127.0.0.1 --port 5000
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

ngspice 47 (Windows 64-bit): `ngspice_con.exe -v` ต้องขึ้น `ngspice-47`;
ถ้าไม่ได้อยู่ใน PATH ให้ตั้ง `NGSPICE_EXE` ตาม README

## เมื่อแก้สมการใน `dc_bias.py`

ต้องเพิ่ม/แก้เทสต์ใน `tests/test_dc_bias.py` ก่อนเสมอ (TDD)
แต่สำหรับ Lab 04 **ไม่ควรแก้ `dc_bias.py` เลย** เพราะใช้เป็น analytical reference เทียบกับ SPICE

## เกณฑ์ตรวจรับ

**Lab 03:** A1 Divider เดิม · A2 Fixed ใช้ RB ได้โดยไม่กรอก RE · A3 Emitter ใช้ RB+RE ·
A4 RE 1→2 kΩ แล้ว IC ลด · A5 RB=0 แจ้ง error และไม่แสดงผลเก่า

**Lab 04:** B1 Regression · B2 DC SPICE พร้อม model/status · B3 เปลี่ยน RE แล้วผลเปลี่ยน ·
B4 AC Bode มี frequency/gain/phase พร้อมหน่วย · B5 transient 10 mV/1 kHz เห็นกลับเฟส ·
B6 เปลี่ยน source แล้ว waveform เปลี่ยน · B7 invalid/engine fail ไม่โชว์ success ปลอม ·
B8 desktop/phone viewport ไม่ตัดปุ่มและกราฟ

ทุกกรณีต้องบันทึกว่ารันด้วย tool อะไรจริง — **ห้ามอ้าง Playwright MCP หรือ Impeccable ถ้าไม่ได้รัน**
