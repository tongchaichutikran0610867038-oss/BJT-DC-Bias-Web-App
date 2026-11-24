# Validation — Lab 03 (Fixed Bias / Emitter Bias / Divider)

## ค่าที่ใช้ร่วมทุกกรณี

`VCC = 12 V`, `RC = 2.2 kΩ`, `β = 100`, `VBE = 0.70 V`

แบบจำลอง Forward-Active (β และ VBE คงที่) ใช้ Ω และ A ในการคำนวณ แล้วแสดง
`VB/VE/VC/VCE` เป็น V, `IC` เป็น mA, `IB` เป็น µA

เกณฑ์เทียบผล: |ΔIC| ≤ 0.01 mA และ |ΔVCE| ≤ 0.02 V เทียบกับค่าอ้างอิงที่ยังไม่ปัดเศษ

## สมการอิสระที่ใช้คำนวณค่าคาดหมาย (ไม่ได้อ่านจากโปรแกรม)

```
Fixed   : IB = (VCC - VBE) / RB                         ; VE = 0
Emitter : IB = (VCC - VBE) / [RB + (β + 1)RE]
Divider : IB = (VTH - VBE) / [RTH + (β + 1)RE]
          VTH = VCC·R2/(R1+R2) , RTH = R1·R2/(R1+R2)

IC = β·IB , IE = (β+1)IB , VE = IE·RE (Fixed = 0)
VB = VE + VBE , VC = VCC - IC·RC , VCE = VC - VE
```

ตัวอย่างการคำนวณอิสระรอบ A3 (RB = 1 MΩ, RE = 1 kΩ):

```
IB = (12 - 0.70) / (1,000,000 + 101×1,000) = 11.3 / 1,101,000 = 10.2634 µA
IC = 100 × 10.2634 µA = 1.02634 mA
IE = 101 × 10.2634 µA = 1.03660 mA
VE = 1.03660 V , VB = 1.73660 V
VC = 12 - (1.02634 mA)(2.2 kΩ) = 9.74205 V
VCE = 9.74205 - 1.03660 = 8.70545 V
```

## ตารางตรวจรับ A1–A5 (ผลที่เห็นจริงจากหน้าเว็บ)

| กรณี | อินพุต | ค่าคาดหมาย (คำนวณอิสระ) | ผลที่เห็นจริง | วิธีตรวจ | สถานะ |
|---|---|---|---|---|---|
| **A1 · โหมดเดิม** | Divider · R1=100 kΩ, R2=22 kΩ, RE=1 kΩ | IC 1.230 mA · VCE 8.052 V · ACTIVE | IC **1.230 mA** · VCE **8.052 V** · ACTIVE · VB 1.942 V · VE 1.242 V · VC 9.294 V | OpenCode Browser | **PASS** |
| **A2 · Fixed** | Fixed · RB=1 MΩ (ไม่กรอก RE) | IC 1.130 mA · VCE 9.514 V · ACTIVE | IC **1.130 mA** · VCE **9.514 V** · ACTIVE · VE 0.000 V · VB 0.700 V · ไม่มีช่อง RE ปรากฏ | OpenCode Browser | **PASS** |
| **A3 · Emitter** | Emitter · RB=1 MΩ, RE=1 kΩ | IC 1.026 mA · VCE 8.705 V · ACTIVE | IC **1.026 mA** · VCE **8.705 V** · ACTIVE · VE 1.037 V · VB 1.737 V | OpenCode Browser | **PASS** |
| **A4 · เปลี่ยนค่าเดียว** | Emitter · เหมือน A3 แต่ RE=2 kΩ | ทำนายว่า **IC ลดลง** เพราะตัวหาร `RB+(β+1)RE` เพิ่ม → IB ลด | IC **0.940 mA** (ลดจาก 1.026) · VCE **8.033 V** · VE 1.899 V · ทิศทางตรงคำทำนาย | OpenCode Browser | **PASS** |
| **A5 · อินพุตผิด** | Fixed · RB=0 | มีข้อความให้แก้ RB, เว็บไม่ล่ม, ไม่แสดงผลรอบก่อน | ข้อความ: `ข้อผิดพลาด (โหมด Fixed Bias)` / `ค่า RB ต้องมากกว่า 0 Ω` · ไม่มีผลลัพธ์แสดง (`NO RESULTS`) | OpenCode Browser | **PASS** |

หลักฐานภาพหน้าจอ (กรณี A1): [`docs/evidence-a1.png`](evidence-a1.png)  
ข้อความผลที่คัดจากหน้าเว็บ A1: `IC 1.230 mA · VCE 8.052 V · ACTIVE · โหมด Voltage-Divider Bias`

> ตรวจซ้ำหลังปรับเกณฑ์ Saturation เป็น `VCE ≤ 0.2 V` และเพิ่มการ reject `NaN`/`Inf`:  
> A1–A5 ยังคง **PASS** และ unittest ผ่าน **28 tests**

## หมายเหตุเรื่องเครื่องมือตรวจ

- **Playwright MCP: NOT RUN** — เครื่องนี้ไม่มี Node.js / npx (`node --version`, `npx --version` ไม่พบ)
  จึงไม่สามารถสตาร์ท `@playwright/mcp` ได้ ตามใบงานจึงบันทึกเหตุผลและใช้ **OpenCode Browser**
  ที่มีอยู่ใน OpenCode Desktop แทน และยังใช้ตาราง A1–A5 กับเกณฑ์เดียวกัน
- ไม่ใช้ `curl` หรือการอ่านโค้ดแทนการรันเบราว์เซอร์ ทุกค่าข้างต้นอ่านจากหน้าเว็บหลังกดปุ่ม **Calculate DC Bias** จริง
- หลังเปลี่ยนโหมด ฟอร์มจะโหลดใหม่และอ่าน Snapshot ใหม่ทุกครั้ง ไม่นำผลรอบเก่ามาใช้
- ผล A3 (`RE = 1 kΩ`) และ A4 (`RE = 2 kΩ`) ถูกบันทึกไว้ในตารางเดียวกันเพื่อใช้เทียบทิศทางก่อน–หลัง

## การไล่ข้อมูลรอบ A4 (RE เดินทางถึงสมการอย่างไร)

```
ฟอร์ม <input name="re"> + <select name="re_unit">
  → request.form ใน app.py: values["re"], values["re_unit"]
  → parse_resistance(raw, unit) คูณ 1000 เมื่อ unit = kohm  → re (Ω)
  → kwargs["re"] = re
  → solve_emitter_bias(vcc, rb, rc, re, beta, vbe) ใน dc_bias.py
  → ib = (vcc - vbe) / (rb + (β+1)·re)
  → ie = (β+1)·ib  → ve = ie·re  → vce = vc - ve
  → format_results() แปลง A→mA, A→µA
  → {{ results.ic }} / {{ results.vce }} ใน templates/index.html
```

ถ้าเปลี่ยน RE แล้วผลไม่เปลี่ยน ให้ตรวจตามลำดับนี้: ชื่อ `name="re"` ในฟอร์ม → ค่าที่ `request.form` ได้ →
ผล `parse_resistance` → `kwargs["re"]` → บรรทัด `ib = ...` ใน `solve_emitter_bias` → ค่าที่แสดงใน template

## บทบาท MCP (อธิบายตามใบงาน)

```
OpenCode (MCP Client) ──MCP──▶ Playwright MCP (MCP Server) ──▶ Browser ──HTTP──▶ Flask + Python
        ▲                                                        │
        └──────────────── MCP snapshot ◀── Browser ◀── หน้าเว็บ ◀──┘
```

- **Skill** `browser-acceptance-check` บอกว่าต้องตรวจกรณีไหนและรายงานหลักฐานอะไร (ไม่ได้เปิดเว็บเอง)
- **MCP** ทำให้เอเจนต์เรียกเครื่องมือเบราว์เซอร์ได้จริง (เปิด URL, กรอกฟอร์ม, อ่าน snapshot)
- **Flask** ยังทำงานเหมือนเดิม เบราว์เซอร์คุย HTTP ตามปกติ ไม่ต้องลง Playwright ใน `requirements.txt`
- งานนี้ใช้ OpenCode Browser แทนเพราะเครื่องไม่มี Node/npx และได้คะแนนตรวจผลเท่ากันตามใบงาน

## ข้อจำกัดของแบบจำลอง

- ทั้งสามโหมดใช้เกณฑ์เตือน `VCE ≤ 0.2 V` ตามใบงาน Lab 03 (A1 ยังได้ `VCE = 8.052 V` จึงไม่กระทบผลเดิม)
- ถ้า `VCC ≤ VBE` หรือ `IB ≤ 0` จะรายงาน `CUTOFF` โดยไม่คำนวณค่าที่เชื่อถือได้
- `to_float()` ใช้ `math.isfinite()` จึง reject ค่า `NaN` และ `Inf` เป็นอินพุตผิด พร้อมข้อความให้แก้ไข (ทดสอบใน `tests/test_web.py`)
- ไม่ใช่ SPICE ไม่มี AC/Transient/Load Line และไม่คำนวณโหมด Cutoff/Saturation แบบละเอียด
- เซิร์ฟเวอร์เปิดเฉพาะ `127.0.0.1` เท่านั้น

---

# Lab 04 — CE Amplifier Simulator (ngspice)

## Engine และ Model ที่ใช้จริง

| รายการ | ค่าที่ตรวจได้ |
|---|---|
| Engine | `ngspice_con.exe` (console build) |
| Version | **ngspice 47** (อ่านจาก `ngspice_con.exe -v` และแสดงในหน้าเว็บ) |
| Batch command | `ngspice_con.exe -b -o run.log -r run.raw circuit.cir` |
| BJT model | `.MODEL QNPN NPN(IS=1e-14 BF=100 VAF=100 RB=10)` |
| ที่มาของ model | Generic NPN ที่ประกาศใน netlist ทุกครั้ง — ไม่มี Instructor Starter Kit ในเครื่องนี้ จึงไม่เดาว่าเป็น transistor รุ่นการค้ารุ่นใด |
| ผลลัพธ์ | อ่านจาก `run.raw` (ASCII) ด้วย `spice_engine.parse_raw_ascii()` แล้วส่งให้ `plots.py` วาด SVG — ไม่มีค่ากราฟ hard-code |
| Analytical comparison | `dc_bias.py` (β=100, VBE=0.70 V) ใช้เป็น reference เฉพาะ DC และแยกป้ายให้ชัด |

Fixture ตามใบงาน: `VCC=12 V`, `R1=100 kΩ`, `R2=22 kΩ`, `RC=2.2 kΩ`, `RE=1 kΩ`, `RL=10 kΩ`, `Cin=Cout=10 µF`, source `10 mV peak / 1 kHz`
(ไม่มี emitter bypass capacitor ตาม baseline)

**UI รวมฟอร์ม (หลัง approve จากผู้ใช้):** dropdown `Analysis / Bias Mode` มี 6 ค่า
`divider / fixed / emitter / spice_dc / spice_ac / spice_tran`; `app.py` แยกทางเดินด้วยค่า `mode`
ที่ส่งจากฟอร์ม (hidden `action` ถูกตั้งตามโหมดโดย JS แต่ server เป็นคนตรวจ/คำนวณ) —
ผล Lab 03 ทั้ง 3 แบบยังเท่าเดิมทุกตัวเลข และ B2–B7 ผ่านเหมือนตอนแยกฟอร์ม

## ตัวอย่าง netlist ที่ส่งจริง (Transient)

```spice
* CE voltage-divider amplifier - generated by spice_engine.py
VCC VCC 0 DC 12
R1 VCC BASE 100000
R2 BASE 0 22000
RC VCC COLL 2200
RE EMIT 0 1000
RL OUT 0 10000
Q1 COLL BASE EMIT QNPN
CIN IN BASE 1e-05
COUT COLL OUT 1e-05
VS IN 0 SIN(0 0.01 1000)
.MODEL QNPN NPN(IS=1e-14 BF=100 VAF=100 RB=10)
.TRAN 6e-06 0.006 0 6e-06
.END
```

DC ใช้ `.OP`, AC ใช้ `.AC DEC 20 1 10MEG`; ตัวเลข amplitude/frequency ในบรรทัด `VS` มาจากฟอร์มทุกครั้ง

## ตัวอย่าง ngspice log (รันเดียวกับตารางด้านล่าง)

```text
Note: No compatibility mode selected!
Circuit: * ce voltage-divider amplifier - generated by spice_engine.py
ASCII raw file "run.raw"
Doing analysis at TEMP = 27.000000 and TNOM = 27.000000
Using SPARSE 1.3 as Direct Linear Solver
No. of Data Columns : 9
No. of Data Rows : 1008
Total analysis time (seconds) = 0.0073324
```

รอบ DC ได้ `No. of Data Rows : 1`, รอบ AC ได้ `No. of Data Rows : 141` (สอดคล้องกับ `141 จุดความถี่` ที่หน้าเว็บแสดง)

## ตารางตรวจรับ B1–B8 (ผลที่เห็นจริงจาก OpenCode Browser)

| Case | Method | Input | Expected/Reference | Observed | Evidence | Status |
|---|---|---|---|---|---|---|
| **B1 · Regression** | OpenCode Browser — dropdown เดียว 6 ตัวเลือก: select/submit 1–3 (Lab 03) และ 4–6 (Lab 04) | Divider `R1=100k,R2=22k,RE=1k`; Fixed `RB=1M`; Emitter `RB=1M,RE=1k→2k` | ค่า Lab 03 เดิม: Divider 1.230 mA / 8.052 V; Fixed 1.130 mA / 9.514 V; Emitter 1.026 mA / 8.705 V; A4 0.940 mA / 8.033 V; RB=0 ต้อง error | Divider **1.230 mA / 8.052 V / ACTIVE**; Fixed **1.130 mA / 9.514 V / ACTIVE**; Emitter **1.026 mA / 8.705 V / ACTIVE**; เปลี่ยน RE=2k → **0.940 mA / 8.033 V**; RB=0 → `ค่า RB ต้องมากกว่า 0 Ω`, ไม่แสดงผลเก่า | [`b1_fixed.png`](captures/b1_fixed.png) · [`b1_emitter.png`](captures/b1_emitter.png) · [`b1_divider.png`](captures/b1_divider.png) (OpenCode Browser, กดปุ่มจริง) + ตาราง A1–A5 ข้างบน | **PASS** |
| **B2 · DC SPICE** | OpenCode Browser — dropdown ตัวเลือก **4 · CE SPICE · DC (.op)**, กด **Run ngspice Simulation** | Fixture ด้านบน, RE=1 kΩ | VB/VE/VC/VCE/IC จาก `ngspice .op` พร้อม Model และ Run Status | `VB 1.949 V · VE 1.289 V · VC 9.190 V · VCE 7.900 V · IC 1.277 mA`; badge `ENGINE: ngspice 47` `MODEL: QNPN` `STATUS: SUCCESS`; Analytical แยกต่างหาก `IC 1.230 mA · VCE 8.052 V · active` | [`b2_dc_desktop.png`](captures/b2_dc_desktop.png) + log ตัวอย่างด้านบน + `<details>` netlist/log ในหน้าเว็บ | **PASS** |
| **B3 · Change RE** | OpenCode Browser — แก้เฉพาะ `RE (kΩ)` 1 → 2 แล้ว Run DC ซ้ำ | เหมือน B2 แต่ `RE=2` | Operating Point ต้องเปลี่ยน ไม่ใช่ค่าค้าง | `VB 2.048 V · VE 1.404 V · VC 10.469 V · VCE 9.065 V · IC 0.696 mA` (จาก 1.277 mA); ทิศทางสอดคล้อง RE เพิ่ม → IC ลด | [`b3_before.png`](captures/b3_before.png) → [`b3_after.png`](captures/b3_after.png) (session เดียวกัน, RE 1→2 kΩ); ค่าใหม่ตรงกับ log/run.raw รอบใหม่ | **PASS** |
| **B4 · AC** | OpenCode Browser — dropdown ตัวเลือก **5 · CE SPICE · AC (.ac)**, กด Run | Fixture, source amplitude 10 mV peak | Frequency axis, Gain magnitude (dB), Phase (degree) พร้อมหน่วย และข้อมูลจาก run จริง | `141 จุดความถี่จาก .ac DEC 20 1 10MEG`; SVG มีแกน `Frequency (Hz, log scale)`, `Gain |Vout/Vin| (dB)`, `Phase (degree)`; ที่ ~1 kHz อ่านได้ gain **4.859 dB**, phase **-179.87°**; gain ตกถึง **-2.606 dB** ที่ 1 Hz | [`b4_ac_desktop.png`](captures/b4_ac_desktop.png); log `No. of Data Rows : 141`; คำนวณ gain จาก `v(out)/v(in)` ใน `spice_engine.frequency_response()` | **PASS** |
| **B5 · Transient** | OpenCode Browser — dropdown ตัวเลือก **6 · CE SPICE · Transient (.tran)**, 10 mV peak / 1 kHz | `VS IN 0 SIN(0 0.01 1000)`, 6 periods | เห็น Vin/Vout ตามเวลา มีป้าย Volt/ms และสัญญาณกลับเฟส | `Vin peak 10.00 mV`, `Vout peak 17.50 mV`, `Phase direction กลับเฟส (~180°)`, `Samples 1008`; SVG แกน `Voltage (V)` / `Time (ms)` และ legend Vin/Vout | [`b5_tran_desktop.png`](captures/b5_tran_desktop.png); log `No. of Data Rows : 1008` | **PASS** |
| **B6 · Change Source** | OpenCode Browser — เปลี่ยน amplitude 10→20 mV และ frequency 1→2 kHz แล้ว Run ซ้ำ | `VS IN 0 SIN(0 0.02 2000)` | Waveform/ค่าต้องเปลี่ยนตาม input ไม่ใช่กราฟ hard-code | `Vin peak 20.00 mV`, `Vout peak 34.99 mV`, ยังกลับเฟส; แกนเวลาเปลี่ยนจาก `0–6 ms` เป็น `0–3 ms` (6 periods ของ 2 kHz) | [`b6_tran_changed.png`](captures/b6_tran_changed.png) เทียบกับ B5; netlist ใน `<details>` แสดงบรรทัด `SIN(0 0.02 2000)` | **PASS** |
| **B7 · Invalid / Fail** | OpenCode Browser — ใส่ `RE=0` แล้ว Run | `RE = 0 kΩ` | แจ้ง error, ไม่ค้าง, ไม่แสดง STATUS SUCCESS หรือกราฟเก่าปลอม | ข้อความจริง: `Simulation failed — engine status: ERROR` / `RE ต้องมากกว่าหรือเท่ากับ 1e-06` / `ไม่มีกราฟหรือตัวเลขจากรอบก่อนหน้าแสดงร่วมกับข้อความผิดพลาด`; ตรวจ DOM ไม่มี `.plot` และไม่มี `STATUS: SUCCESS` | [`b7_invalid.png`](captures/b7_invalid.png) + `tests/test_spice_engine.py` ตรวจ path เดียวกัน | **PASS** |
| **B8 · UI** | OpenCode Browser — desktop viewport ~1296 px และ iframe 390 px (จำลอง phone viewport เพราะ browser tool ไม่มี viewport-resize API) + เปลี่ยนโหมด | Desktop: เปิด DC/AC/Tran; Phone: เปิด AC แล้วสลับ Fixed→Emitter | ปุ่ม/หน่วย/กราฟอ่านง่าย ไม่ตัดเนื้อหาสำคัญ | Desktop: buttons visible, `console error = 0`, document/CSS 200–304. Phone: `innerWidth=390`, `document.scrollWidth=390` (**ไม่มี horizontal overflow**), ปุ่มเดียวของฟอร์มรวมอยู่ในจอ; dropdown แสดงครบ 6 ตัวเลือก; `.plot-wrap` กว้าง 348 px และเลื่อนได้เพื่อเห็นกราฟ `min-width=560 px`; สลับ Fixed → RB โผล่/RE ซ่อน, Emitter → RB+RE โผล่ | [`b2_dc_desktop.png`](captures/b2_dc_desktop.png), [`b8_ac_mobile.png`](captures/b8_ac_mobile.png) (390×2700 px), browser evaluate audit | **PASS** (ด้วยข้อจำกัด iframe — ไม่ใช่อุปกรณ์จริง) |

### ผลตรวจซ้ำหลังรวมเป็นฟอร์มเดียว 6 ตัวเลือก (OpenCode Browser)

| Dropdown | ผลที่เห็น | Status |
|---|---|---|
| 1 Divider | `IC 1.230 mA · VCE 8.052 V · ACTIVE` | PASS |
| 2 Fixed | `IC 1.130 mA · VCE 9.514 V · ACTIVE` | PASS |
| 3 Emitter | `IC 1.026 mA · VCE 8.705 V · ACTIVE` | PASS |
| 4 CE SPICE DC | `VB 1.949 · VE 1.289 · VC 9.190 · IC 1.277 mA` + Analytical `1.230 mA` | PASS |
| 5 CE SPICE AC | `141 จุดความถี่`, SVG แกน Gain/Phase, `STATUS: SUCCESS` | PASS |
| 6 CE SPICE TRAN | `Vin 10.00 mV · Vout 17.50 mV · 1008 samples`; เปลี่ยนเป็น 20 mV/2 kHz → `34.99 mV`, แกน 0–3 ms | PASS |
| RE=0 ในตัวเลือก 4 | `Simulation failed — engine status: ERROR`, ไม่มี `STATUS: SUCCESS` และไม่มี `<svg class="plot">` | PASS |
| Mobile 390 px (iframe) | `innerWidth=390`, `scrollWidth=390`, `.plot-wrap` client 348/scroll 560, `console error = 0` | PASS |

## การพิสูจน์ว่ากราฟไม่ใช่ Mock Data

1. `app.py` แยก action `spice` ออกจาก action `analytical`; ทุกการกด Run เรียก `spice_engine.run_analysis(params)` ใหม่เสมอ
2. `spice_engine.build_netlist()` เขียนค่า VCC/R1/R2/RC/RE/RL/Cin/Cout/amplitude/frequency จากฟอร์มลง netlist — B6 เห็นบรรทัด `SIN(0 0.02 2000)` เปลี่ยนจริง
3. `ngspice_con.exe -b -o run.log -r run.raw circuit.cir` ทำงานใน `TemporaryDirectory`; ตรวจ return code, ขนาดไฟล์, timeout 30 s และ `No. Variables` ก่อน parse
4. `parse_raw_ascii()` อ่าน `Values:` จาก `run.raw`; `frequency_response()` / `transient_response()` คำนวณ array จาก complex/real numbers ก่อนส่งให้ `plots.py` วาด SVG
5. `plot_for()` ไม่มี branch สำหรับข้อมูลตัวอย่างหรือค่าเฉลี่ยล่วงหน้า; ถ้า engine fail `spice_plot` ถูกล้างเป็น `""` และหน้า error ไม่มี `<svg class="plot">` (B7)
6. `unittest` ตรวจ directive, source string, raw parser, error path และรอบ ngspice จริงรวม 34 tests

## ความคลาดเคลื่อนและข้อจำกัดที่ยังเหลือ

- SPICE กับ Analytical ไม่ตรงทุกหลัก: DC SPICE `IC 1.277 mA / VCE 7.900 V` เทียบ Analytical `1.230 mA / 8.052 V` เพราะโมเดล NPN ใช้ `IS/BF/VAF/RB` ไม่ใช่ β+VBE คงที่ — หน้าเว็บแยกป้ายและอธิบายไว้แล้ว
- Sweep AC เป็น `1 Hz–10 MHz` แบบ fixed; gain ไม่ตัดที่ความถี่สูงในช่วงนี้เพราะโมเดลไม่มี high-frequency pole จึง **ไม่รายงาน fH** และถือว่า `not determined in sweep range` แทนการสร้างตัวเลข
- สำหรับ fL: กราฟมีสาขาความถี่ต่ำแต่หน้าเว็บไม่ได้คำนวณ `-3 dB` อัตโนมัติ จึงยังไม่รายงานค่าตัวเลข fL ที่ “คำนวณจากจุดตัด” — เป็นงานต่อยอด
- รอบ AC ใช้ amplitude เป็น AC magnitude และใช้ frequency input เพื่อให้ฟอร์มครบถ้วน แต่การ sweep ถูกกำหนดโดย `.ac DEC 20 1 10MEG` ไม่ได้ sweep รอบ `sp_freq` เดี่ยว ๆ
- B8 ใช้ iframe 390 px ไม่ใช่โทรศัพท์จริงหรือ Playwright device emulation; หน้าเว็บ nevertheless ไม่มี horizontal overflow และกราฟเลื่อนใน container ได้
- กราฟ SVG วาดฝั่งเซิร์ฟเวอร์ด้วย Python stdlib (ไม่เพิ่ม dependency) — รองรับ axes/units แต่ยังไม่มี hover tooltip แบบ chart library

## สถานะเครื่องมือตรวจ (ต้องอ่านตรง ๆ)

| เครื่องมือ | สถานะ | เหตุผล/หมายเหตุ |
|---|---|---|
| **OpenCode Browser** | **RUN · PASS** | ใช้ Navigate/Snapshot/Select/Fill/Click/Evaluate/Screenshot จริงกับ `http://127.0.0.1:5000/` |
| **Playwright MCP** | **NOT RUN** | เครื่องนี้ไม่มี Node.js/npx และไม่พบ MCP server ที่เปิดอยู่ จึงไม่สามารถอ้างผล Playwright MCP ได้ — ใบงานอนุญาตให้ใช้ Browser Tool อื่นพร้อมบันทึกเหตุผล |
| **Impeccable Skill** | **NOT RUN** | ไม่มี skill นี้ใน OpenCode session นี้; UI ปรับด้วย CSS/HTML ทั่วไปและตรวจด้วย OpenCode Browser แทน |
| **Manual UI review** | RUN | ตรวจอ่านได้จาก snapshot/evaluate และ screenshots ด้านบน ไม่ได้ใช้ curl แทน browser |

## AI ที่ช่วย และสิ่งที่ต้องตรวจเอง

- AI เขียน `spice_engine.py`, `plots.py`, ส่วน dispatch ใน `app.py`,ฟอร์ม/กราฟใน template, CSS และเทสต์เพิ่ม; ปรับ README/AGENTS/validation ตามผลรันจริง
- นักศึกษาควรตรวจเองว่า netlist ใน `<details>` ตรงกับ fixture, ตัวเลข VB/VE/VC/VCE/IC สอดคล้อง log, ทิศทางกลับเฟสของ CE และความต่าง SPICE/Analytical มีคำอธิบาย
- ถ้าเปลี่ยน amplitude แต่กราฟไม่เปลี่ยน ให้ดูตามลำดับ: `sp_amp` ในฟอร์ม → `spice_params()` → `build_netlist()` บรรทัด `VS` → `run.raw` → `frequency_response()`/`transient_response()` → `plots.py`
