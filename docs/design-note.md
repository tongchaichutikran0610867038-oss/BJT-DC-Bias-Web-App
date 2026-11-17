# Design Note — Lab 03 (BJT DC Bias Web App)

อ้างอิงใบงาน `ENG29_2121_Lab03_BJT_Bias_Web_App`  
ต่อยอดจาก Lab 02 โดยคงผลของ Voltage-Divider Bias เดิมไว้ และเพิ่ม Fixed Bias กับ Emitter Bias

## Mapping ข้อกำหนด → องค์ประกอบในโปรเจกต์

| ข้อกำหนดจากใบงาน | องค์ประกอบที่รองรับ |
|---|---|
| เลือกได้ 3 วงจรจากหน้าเว็บ | `templates/index.html` dropdown `name="mode"` + `MODE_LABELS` |
| Fixed Bias ใช้ `RB`, `RC` | `solve_fixed_bias()` ใน `dc_bias.py` |
| Emitter Bias ใช้ `RB`, `RC`, `RE` | `solve_emitter_bias()` ใน `dc_bias.py` |
| Voltage-Divider เดิมต้องได้ผลเดิม | `solve_voltage_divider()` ไม่เปลี่ยนสูตร + `tests/test_dc_bias.py` |
| Flask เลือกฟังก์ชันตามโหมด | `SOLVERS` และ `if/elif` ใน `app.py` |
| แปลงหน่วย Ω / kΩ / MΩ | `parse_resistance()` ใน `app.py` |
| ตรวจเฉพาะช่องที่โหมดต้องใช้ | `required_fields()` + `validate_inputs()` |
| โหมดไม่รู้จักต้องแจ้ง error | `if mode not in SOLVERS` ใน `app.py` |
| แสดงผลและ error ระบุโหมด | `mode_label` ส่งเข้า template |
| ไม่แสดงผลรอบเก่าเมื่ออินพุตผิด | `results = None` เมื่อ validation ไม่ผ่าน |
| ตรวจผลผ่าน Browser A1–A5 | `docs/validation.md` + `docs/evidence-a1.png` |

## สมการที่ใช้ใน `dc_bias.py`

```text
Fixed   : IB = (VCC - VBE) / RB
Emitter : IB = (VCC - VBE) / [RB + (beta + 1) * RE]
Divider : IB = (VTH - VBE) / [RTH + (beta + 1) * RE]
          VTH = VCC * R2 / (R1 + R2)
          RTH = R1 * R2 / (R1 + R2)

ทุกโหมด:
IC  = beta * IB
IE  = (beta + 1) * IB
VE  = IE * RE          (Fixed: VE = 0)
VB  = VE + VBE
VC  = VCC - IC * RC
VCE = VC - VE
```

หน่วยภายใน: `V`, `A`, `Ω`  
หน่วยที่แสดง: `VB/VE/VC/VCE` เป็น V, `IC/IE` เป็น mA, `IB` เป็น µA

## การแบ่งชั้น

- `dc_bias.py` — สมการวิศวกรรมล้วน ไม่ import Flask และไม่รู้จัก HTTP/HTML
- `app.py` — route, parse form, validation, unit conversion, dispatch ไปยัง solver
- `templates/index.html` — แสดงฟอร์ม/ผล/error ด้วย Jinja ไม่มีตัวเลข hard-code
- `tests/` — regression tests ของสมการและ Flask route

## เกณฑ์ Region

- `VCC <= VBE` หรือ `VTH <= VBE` → `CUTOFF`
- `VCE <= 0.2 V` → `SATURATION` (ทั้งสามโหมดตาม Lab 03)
- นอกนั้น → `ACTIVE`

## Validation ที่ต้องมี

- ช่องที่โหมดต้องใช้ต้องมีค่า
- ต้องเป็นตัวเลขจำกัด (`math.isfinite`) — reject `NaN` / `Inf`
- ค่าที่ต้องเป็นบวกต้อง `> 0`
- `VBE < VCC`
- อินพุตผิดต้อง HTTP 200, แสดงข้อความภาษาไทย และไม่แสดงผลรอบเก่า

## ชุดทดสอบ

รันด้วย:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

ผลปัจจุบัน: **28 tests ผ่านทั้งหมด** (สมการ 3 วงจร, region, validation, unit conversion, mode dispatch)
