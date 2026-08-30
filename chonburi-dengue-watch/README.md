# Chonburi Dengue Watch

ผลงานนี้เป็นโปรเจคต้นแบบที่ผสานความสามารถด้าน Full-Stack Development, Data Science และ Business Intelligence เพื่อแสดงกระบวนการเฝ้าระวังและพยากรณ์โรคไข้เลือดออกในจังหวัดชลบุรีแบบ end-to-end โดยใช้ข้อมูลจำลองที่มีโครงสร้างใกล้เคียงกับการใช้งานจริง

## วัตถุประสงค์ของโปรเจค

- บันทึกและตรวจสอบข้อมูลผู้ป่วยรายอำเภอรายสัปดาห์
- แสดงภาพรวมสถานการณ์ผ่าน Dashboard ที่เข้าใจง่าย
- คำนวณและแสดงระดับความเสี่ยงในแต่ละพื้นที่
- ใช้โมเดล Machine Learning ในการพยากรณ์จำนวนผู้ป่วยที่อาจเกิดขึ้น
- สร้างสภาพแวดล้อมที่เหมาะสำหรับการนำเสนองานและการทดลองแนวคิด

## สถาปัตยกรรมระบบ

```text
ผู้ใช้งาน
   │
   ▼
React Frontend
   │
   ▼
FastAPI Backend
   ├── SQLite Database
   ├── Predict API
   ├── Dashboard API
   └── Pydantic Validation
   │
   ▼
Machine Learning Pipeline
   ├── Synthetic data generation
   ├── Feature preparation
   └── RandomForest model (joblib)
```

## ฟีเจอร์หลัก

- Dashboard ที่แสดงสถิติเบื้องต้นและข้อมูลเสี่ยงเชิงพื้นที่
- แบบฟอร์มบันทึกข้อมูลผู้ป่วยและสภาพอากาศ
- API สำหรับการทำนายจำนวนผู้ป่วยได้ทันที
- การใช้ข้อมูลจำลองที่สามารถทำซ้ำได้เพื่อการทดลองและสาธิต
- การจัดระดับความเสี่ยงตามจำนวนผู้ป่วยและแนวโน้มการเปลี่ยนแปลง

## โครงสร้างโฟลเดอร์

```text
chonburi-dengue-watch/
├── backend/
│   ├── app/
│   │   ├── ml/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   └── schemas.py
│   ├── data/
│   ├── models/
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/
│   ├── index.html
│   ├── package.json
│   ├── pnpm-lock.yaml
│   └── vite.config.js
├── README.md
├── generate_chonburi_dengue_mock.py
└── .gitignore
```

## เริ่มต้นใช้งาน

### วิธีง่าย: ใช้ launcher

จากโฟลเดอร์ root ให้เปิดไฟล์:

```powershell
.\run-dengue-dashboard.bat
```

ซคริปต์นี้จะ:
- ตรวจหา Node.js และติดตั้งอัตโนมัติถ้ายังไม่มี
- ติดตั้ง dependency ของ backend และ frontend
- เริ่ม backend และ frontend พร้อมกันใน terminal เดียว
- แสดง URL สำหรับ dashboard และ API

### ปิดโปรเจค

กด:

```text
Ctrl + C
```

บน terminal ที่เปิด script อยู่ เพื่อปิด backend และ frontend ให้หยุดพร้อมกัน

### 1) Backend (manual)

```powershell
cd chonburi-dengue-watch/backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.ml.train
uvicorn app.main:app --reload --port 8000
```

เปิด Swagger API ได้ที่:

http://localhost:8000/docs

### 2) Frontend (manual)

```powershell
cd chonburi-dengue-watch/frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

Frontend จะเชื่อมต่อกับ Backend ที่ http://localhost:8000 เป็นค่าเริ่มต้น

## ข้อมูลและโมเดล

- ข้อมูลในโปรเจคนี้เป็นข้อมูลจำลองที่ถูกสร้างขึ้นโดย script ที่สามารถทำซ้ำได้
- โมเดลถูกฝึกด้วยข้อมูลเชิงพื้นที่และสภาพอากาศแบบรายสัปดาห์
- ระดับความเสี่ยงถูกกำหนดจากจำนวนผู้ป่วยที่พยากรณ์ได้และอัตราการเพิ่มขึ้นเมื่อเทียบกับค่าในรอบก่อนหน้า

> โปรเจคนี้เหมาะสำหรับการสาธิต การทดลอง และการนำเสนอในเชิงผลงานนักพัฒนาและนักวิเคราะห์ข้อมูลเท่านั้น ไม่ควรใช้เป็นฐานข้อมูลจริงสำหรับการตัดสินใจด้านสาธารณสุขโดยตรง

## มุมมองสำหรับการนำเสนองาน

โปรเจคนี้สะท้อนกระบวนการทำงานแบบจริงจังและครบวงจร:

1. สร้างและปรับปรุงข้อมูล
2. เตรียมฟีเจอร์และฝึกโมเดล
3. เปิด API สำหรับการใช้งาน
4. สร้าง Dashboard สำหรับการสรุปผลและติดตามสถานการณ์
5. จัดวางโครงสร้างโปรเจคที่พร้อมใช้งานสำหรับ presentation
