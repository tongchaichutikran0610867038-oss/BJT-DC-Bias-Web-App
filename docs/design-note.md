# Design Note — Mapping เกณฑ์ตรวจรับ A1–A7

อ้างอิงใบงาน Lab 02 ข้อ 09 (Acceptance Tests)

| เกณฑ์ตรวจรับ | องค์ประกอบในโปรเจกต์ที่รองรับ |
|---|---|
| **A1** GET `/` เปิดเว็บผ่าน localhost ได้ เห็นหน้า Input Form; HTTP 200 | `app.py` route `/` methods `["GET"]` + `templates/index.html` |
| **A2** POST `/` กรอกค่าตัวอย่างแล้ว Server เรียก Python คำนวณ แสดงผล DC Bias ใน HTML (ไม่ใช้ค่าฮาร์ดโค้ด) | `app.py` route `POST` → `solve_voltage_divider()` (ใน `dc_bias.py`) → render |
| **A3** Engineering Reference: VB, VE, VC, VCE, IC สอดคล้องกับการคำนวณอิสระภายใต้แบบจำลองเดียวกัน | `dc_bias.py` สมการตามใบงาน + `docs/validation.md` ตารางเทียบค่า |
| **A4** Validation: R≤0, β≤0 หรือข้อมูลไม่ใช่ตัวเลข → แสดง Error ชัดเจน หน้าเว็บไม่ล้ม | `app.py` `validate_inputs()` 6 กฎ + ข้อความภาษาไทย + HTTP 200 |
| **A5** Outside Active Region: คำเตือนกรณี Cutoff / Saturation; ไม่รายงานว่า approximation ใช้ได้ | `dc_bias.py` `region` ("cutoff"/"saturation"/"active") + `message` + ป้ายสีใน template |
| **A6** Unit + HTTP Tests: ≥3 เทสต์สมการ + ≥1 เทสต์ Flask test client | `tests/test_dc_bias.py` 5 ตัว + `tests/test_web.py` 9 ตัว (รวม 16) |
| **A7** GitHub Reproducibility: คลอนแล้วติดตั้ง dependencies / รันเว็บ / รันเทสต์ตาม README ได้ | `README.md` คำสั่ง PowerShell ครบ + `requirements.txt` + `.gitignore` |

## สมการอ้างอิง (ใน `dc_bias.py`)

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

เกณฑ์โหมด: `VTH <= VBE` → Cutoff · `VCE <= 0.3 V` → Saturation (ค่าไม่น่าเชื่อถือ) · นอกนั้น → Active
