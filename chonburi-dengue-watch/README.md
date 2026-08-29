# Chonburi Dengue Watch

ระบบต้นแบบสำหรับบันทึกข้อมูล เฝ้าระวัง และพยากรณ์ผู้ป่วยไข้เลือดออกใน 11 อำเภอของจังหวัดชลบุรี

## Architecture

```text
React + Tailwind + Recharts
          │ REST/JSON
          ▼
FastAPI ──┬── SQLite (observations + predictions)
          └── RandomForestRegressor (joblib artifact)
                    ▲
              Pandas training pipeline
```

- Frontend มีหน้า Dashboard และ Data Entry Form
- Backend ตรวจสอบข้อมูลด้วย Pydantic, บันทึกข้อมูลใน SQLite และเรียกโมเดลพยากรณ์
- Training pipeline สร้าง mock data แบบ reproducible สำหรับ 11 อำเภอ แล้ว train/test แบบแบ่งตามเวลา
- Risk level ใช้ทั้งจำนวนผู้ป่วยที่คาดการณ์และอัตราเพิ่มขึ้นจากค่าครั้งก่อน

## Run locally

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.ml.train
uvicorn app.main:app --reload --port 8000
```

เปิด API docs ที่ `http://localhost:8000/docs`

### Frontend

```powershell
cd frontend
pnpm install
pnpm dev
```

Frontend ใช้ `http://localhost:8000` เป็นค่าเริ่มต้น เปลี่ยนได้ด้วย `VITE_API_URL`.

> Mock data ใช้เพื่อสาธิตเท่านั้น ก่อนใช้จริงควร train ด้วยข้อมูลระบาดวิทยาและอากาศที่ผ่านการตรวจสอบ พร้อมปรับ threshold ร่วมกับนักระบาดวิทยา
