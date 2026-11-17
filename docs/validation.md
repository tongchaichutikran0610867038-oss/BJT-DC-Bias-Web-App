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
- ก่อนแก้โค้ด รายงานรอบแรกถูกบันทึกไว้ในตารางนี้แล้ว (ดูผลก่อน–หลังใน A4)

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
