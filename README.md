# BJT DC Bias + CE Amplifier Simulator — Lab 03 → Lab 04 (ENG29 2121)

Flask web app เดิมจาก Lab 03 ยังใช้ได้ทุกประการ (Voltage-Divider / Fixed / Emitter Bias)
และต่อยอดเป็น **Common-Emitter Amplifier Simulator v1** ที่รันจริงด้วย **ngspice 47**
สำหรับวงจร CE Voltage-Divider อ้างอิงหนึ่งวงจร:

- **Lab 03 · Analytical DC Bias**: `dc_bias.py` (ไม่แตะสมการเดิม) + 3 โหมด + validation เดิม
- **Lab 04 · SPICE**: `.op` (DC), `.ac` (Bode gain/phase), `.tran` (Vin/Vout ตามเวลา)
- ผลทั้งหมดอ่านจาก `ngspice` ผ่าน `subprocess` → ไฟล์ `run.raw` → parser → SVG
- มีป้ายแยก `ENGINE / MODEL / STATUS` และแยกผล **SPICE** กับ **Analytical reference** ให้ชัด
- **ฟอร์มเดียว dropdown เดียว 6 ตัวเลือก** รวม LAB 03 (3 แบบ) + LAB 04 (3 analysis) — ปุ่มเดียวตามโหมด

**ลิงก์ในเครื่อง:** <http://127.0.0.1:5000/>  
**GitHub repo:** <https://github.com/tongchaichutikran0610867038-oss/BJT-DC-Bias-Web-App>  
**Commit SHA สำหรับส่งงาน:** ดูจาก GitHub หลัง push หรือรัน `git log -1 --format=%H`

---

## โครงสร้างไฟล์

```
├── app.py                # Flask route: action=analytical (Lab 03) หรือ action=spice (Lab 04)
├── dc_bias.py            # สมการ Lab 03 สามฟังก์ชัน — ไม่ import Flask และไม่เปลี่ยนผลเดิม
├── spice_engine.py       #Lab04: สร้าง netlist, เรียก ngspice, parse ASCII .raw, error handling
├── plots.py              #Lab04: วาด Bode/waveform SVG จาก array ที่ parse ได้ (stdlib ล้วน)
├── templates/index.html  # ฟอร์มเดียว 6 ตัวเลือก (Lab 03 ×3 + SPICE ×3) + ผล/status/หลักฐานรัน
├── static/style.css      # responsive layout, badge, plot container
├── tests/
│   ├── test_dc_bias.py   # 28 เทสต์เดิมของ Lab 03
│   ├── test_web.py       # route/ฟอร์ม/validation เดิม
│   └── test_spice_engine.py # netlist/parser/error path + รอบ ngspice จริง
├── requirements.txt      # Flask>=3.1,<4 (ไม่เพิ่ม dependency; ngspice ติดตั้งแยก)
├── AGENTS.md
├── docs/
│   ├── design-note.md
│   ├── validation.md     # A1–A5 + B1–B8 พร้อม screenshot และ tool status
│   ├── reflection.md     # คำตอบรายบุคคล (นักศึกษาเติมเอง)
│   ├── evidence-a1.png
│   └── captures/         # b2/b4/b5/b6/b7/b8 screenshots จาก OpenCode Browser
└── README.md
```

---

## ติดตั้งและรัน (PowerShell)

> ในเครื่องนี้คำสั่ง `python` เป็น Microsoft Store alias และใช้ไม่ได้ → ใช้ `py -3.14` หรือ venv โดยตรง

### 1. Python + Flask

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. ngspice (โปรแกรมภายนอก — ไม่ใช่ pip package)

Windows 64-bit: ดาวน์โหลด ngspice 47 จาก <https://ngspice.sourceforge.io/download.html>
(SourceForge `ngspice-47_64.7z`) → แตกไฟล์ → ใช้ executable ในโฟลเดอร์ `Spice64\bin`

เครื่องนี้ติดตั้งที่:

```
C:\Users\B6837228\AppData\Local\ngspice-47\Spice64\bin\ngspice_con.exe
```

เพิ่มโฟลเดอร์ `Spice64\bin` ลง user `PATH` หรือตั้ง environment variable:

```powershell
$env:NGSPICE_EXE = 'C:\Users\B6837228\AppData\Local\ngspice-47\Spice64\bin\ngspice_con.exe'
```

ตรวจเวอร์ชันก่อนรันเว็บ:

```powershell
ngspice_con.exe -v
# ควรเห็น ngspice-47
```

`spice_engine.find_engine()` หา **`NGSPICE_EXE` → PATH (`ngspice_con`, `ngspice`) → ตำแหน่งติดตั้งที่รู้จัก**
ตามลำดับ ถ้าไม่เจอจะแจ้ง error บนหน้าเว็บแทนการแสดงกราฟเก่า

### 3. รันเซิร์ฟเวอร์

```powershell
.\.venv\Scripts\python.exe -m flask --app app run --debug --host 127.0.0.1 --port 5000
```

เปิด <http://127.0.0.1:5000/> (เฉพาะเครื่องนี้ — ไม่ deploy สาธารณะ)

### 4. รันเทสต์

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

ผลล่าสุด: **34 tests ผ่าน** (28 เทสต์เดิม + 6 เทสต์ Lab 04)
เทสต์ที่ต้องใช้ engine จะ `skip` อัตโนมัติถ้าไม่พบ ngspice

---

## วิธีใช้หน้าเว็บ — ฟอร์มเดียว 6 ตัวเลือก

หน้าเว็บมี **ฟอร์มเดียว** และ dropdown **Analysis / Bias Mode** ที่มี 6 ตัวเลือก
(ไม่ต้องสลับฟอร์ม Lab 03 / Lab 04):

| # | ตัวเลือกใน dropdown | ทางเดิน | ปุ่ม |
|---|---|---|---|
| 1 | Voltage-Divider Bias (Lab 03) | `dc_bias.solve_voltage_divider` | Calculate DC Bias |
| 2 | Fixed Bias (Lab 03) | `dc_bias.solve_fixed_bias` | Calculate DC Bias |
| 3 | Emitter Bias (Lab 03) | `dc_bias.solve_emitter_bias` | Calculate DC Bias |
| 4 | CE SPICE · DC (.op) | `ngspice .op` | Run ngspice Simulation |
| 5 | CE SPICE · AC (.ac) | `ngspice .ac` | Run ngspice Simulation |
| 6 | CE SPICE · Transient (.tran) | `ngspice .tran` | Run ngspice Simulation |

เลือกตัวเลือก → กรอกเฉพาะช่องที่โผล่มา → กดปุ่มเดียว ระบบจะสลับ
hidden field `action=analytical|spice` ให้เอง (JS ทำเฉพาะ UI; server validate ใหม่ทุกครั้ง)

**Lab 03 (1–3):** ใช้ VCC, R1/R2/RC/RE หรือ RB, β, VBE; หน่วย resistance เลือก Ω / kΩ / MΩ ได้ตามเดิม

**Lab 04 (4–6):** ใช้ช่อง CE โดยเฉพาะ; ระหว่างรันจะเห็น `STATUS: RUNNING` (UI-only JS),
เสร็จแล้วเป็น `ENGINE: ngspice 47 · MODEL: QNPN · STATUS: SUCCESS` หรือหน้า ERROR
ที่ไม่มีกราฟ/ตัวเลขเก่า

| ช่อง | หน่วยที่แสดง | หมายเหตุ |
|---|---|---|
| VCC | V | ใช้ทุกโหมด |
| R1, R2, RC, RE, RL | kΩ | แปลงเป็น Ω ก่อนเขียน netlist |
| Cin, Cout | µF | coupling capacitor (ไม่มี bypass capacitor) |
| Source amplitude | mV peak | AC magnitude หรือ `SIN` amplitude |
| Source frequency | Hz | ใช้กับ `.tran`; `.ac` sweep 1 Hz–10 MHz แบบคงที่ |

Fixture เริ่มต้นตรงใบงาน: `12 V / 100 kΩ / 22 kΩ / 2.2 kΩ / 1 kΩ / 10 kΩ / 10 µF / 10 µF / 10 mV / 1 kHz`

**BJT model ที่ใช้ (documented, ไม่เดารุ่นการค้า):**

```spice
.MODEL QNPN NPN(IS=1e-14 BF=100 VAF=100 RB=10)
```

**จุดวัด:** AC gain = `|V(OUT)/V(IN)|` โดย `V(IN)` อยู่ก่อน `Cin` และ `V(OUT)` ที่ `RL`;
DC `IC` คำนวณจาก `(VCC−VC)/RC` หลังอ่าน node voltage จาก `ngspice .op`

ค่าอ้างอิงLab 03 (ตรวจแล้ว A1–A5 ใน [`docs/validation.md`](docs/validation.md)):

| กรณี | IC | VCE |
|---|---|---|
| A1 Divider | 1.230 mA | 8.052 V |
| A2 Fixed | 1.130 mA | 9.514 V |
| A3 Emitter (RE=1 kΩ) | 1.026 mA | 8.705 V |
| A4 Emitter (RE=2 kΩ) | 0.940 mA | 8.033 V |
| A5 Fixed RB=0 | error `ค่า RB ต้องมากกว่า 0 Ω` | — |

ผล SPICE ตัวอย่าง (fixture เดิม): `VB 1.949 V · VE 1.289 V · VC 9.190 V · VCE 7.900 V · IC 1.277 mA`;
AC 141 จุด, ที่ 1 kHz gain ≈ 4.859 dB / phase ≈ −179.87°;
transient 10 mV/1 kHz ได้ Vout peak ≈ 17.50 mV และกลับเฟส (~180°)
(ตัวเลขเหล่านี้เป็นหลักฐานจากรันจริง ไม่ได้เป็นค่าที่โปรแกรมใช้ตอบทุกครั้ง — -change input แล้วผลเปลี่ยน)

---

## วิธีตรวจซ้ำ / Reproducibility

```powershell
# 1) รัน ngspice ด้วย netlist ที่เว็บสร้างให้ (ดูใน <details> บนหน้าเว็บ)
ngspice_con.exe -b -o run.log -r run.raw circuit.cir

# 2) หรือเรียก adapter โดยตรง
.\.venv\Scripts\python.exe -c "import spice_engine as s; p=dict(vcc=12,r1=100e3,r2=22e3,rc=2.2e3,re=1e3,rl=10e3,cin=10e-6,cout=10e-6,amp=0.010,freq=1000); print(s.run_analysis(dict(p,analysis='dc'))['readings'])"

# 3) เปิด browser แล้วทำ B1–B8 ตามตารางใน docs/validation.md
```

รายละเอียด B1–B8, screenshot desktop/mobile, log excerpt, ความคลาดเคลื่อน และ tool status อยู่ใน
[`docs/validation.md`](docs/validation.md)

---

## หมายเหตุเรื่อง MCP / Browser / Impeccable

- **Playwright MCP: NOT RUN** — เครื่องนี้ไม่มี Node.js / npx และไม่มี MCP server ที่เปิดอยู่
- **Impeccable Skill: NOT RUN** — ไม่มี skill นี้ใน session; ปรับ UI ด้วย HTML/CSS ทั่วไป
- ใช้ **OpenCode Browser** ที่มากับ OpenCode Desktop แทนในการตรวจ B1–B8 และบันทึกตามความจริง
- ถ้าต้องการ Playwright MCP จริง ให้ติดตั้ง Node.js 18+ แล้วเพิ่มใน `opencode.json` (OpenCode V2):

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

---

## ข้อจำกัด

- Lab 03 ยังเป็น Forward-Active approximation เท่านั้น (β, VBE คงที่) และเตือน saturation ที่ `VCE ≤ 0.2 V`
- Lab 04 มี **เฉพาะ** CE Voltage-Divider reference เดียว — ไม่มี editor วงจร, Emitter bypass, FET, overlay animated, AC ทุก bias mode หรือ deploy สาธารณะ
- `.ac` sweep ถูกกำหนด `1 Hz–10 MHz`; โมเดลไม่มี high-frequency pole → ไม่รายงาน `fH` (ถือว่า *not determined in sweep range*) และยังไม่คำนวณ `-3 dB fL` อัตโนมัติ
- SVG วาดฝั่งเซิร์ฟเวอร์ด้วย stdlib → มีแกน/หน่วย/legend แต่ไม่มี hover tooltip
- ตรวจ B8 ด้วย iframe กว้าง 390 px แทน viewport resize API ของ browser tool; ไม่ใช่อุปกรณ์จริง
- ห้าม commit `.venv/`, `.env`, API key, credential หรือไฟล์ run ชั่วคราว (`.gitignore` มีอยู่แล้ว)

---

## ส่งงาน

ก่อน commit ตรวจ `git diff` และ `git diff --staged`

ในเครื่องนี้ `git` ไม่ได้อยู่ใน PATH แต่มี Git ที่มากับ GitHub Desktop:

```
C:\Users\B6837228\AppData\Local\GitHubDesktop\app-3.7.0\resources\app\git\cmd\git.exe
```

หรือใช้ GitHub Desktop กด **Commit** แล้ว **Push** ได้ตามปกติ  
ต้องส่ง **GitHub URL + Commit SHA** ของ commit ล่าสุดพร้อมงาน Lab 04

### AI ช่วยอะไร / นักศึกษาตรวจอะไร

- AI เขียน adapter/plot/dispatch/UI/tests และร่างเอกสารจากผลรันจริง
- นักศึกษาตรวจ netlist ใน `<details>`, log `.raw`, ทิศทางกลับเฟส และความต่าง SPICE/Analytical เอง
- ถ้าเปลี่ยน amplitude แต่กราฟไม่เปลี่ยน → ไล่ `sp_amp → spice_params → build_netlist → run.raw → plots.py`

*อ้างอิงเพิ่มเติม:* [ngspice docs](https://ngspice.sourceforge.io/docs.html) ·
[batch mode manual](https://nmg.gitlab.io/ngspice-manual/startingngspice/startingoptions/batchmode.html)
