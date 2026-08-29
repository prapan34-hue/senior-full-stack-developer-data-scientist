# Senior Full-Stack Developer / Data Scientist Portfolio

โปรเจคนี้จัดทำขึ้นเพื่อแสดงความสามารถด้าน Full-Stack Development, Data Science, Machine Learning, API Design และ Dashboard Development ผ่านผลงานที่สามารถใช้งานได้จริงและเหมาะสำหรับการนำเสนอผลงานในเชิงธุรกิจหรืองานวิจัย

## ภาพรวมของโครงการ

Repository นี้ประกอบด้วยผลงาน 3 ส่วนหลัก:

1. Chonburi Dengue Watch
   - ระบบเฝ้าระวังและพยากรณ์โรคไข้เลือดออกในจังหวัดชลบุรี
   - ใช้ FastAPI + React + Machine Learning
2. PostgreSQL + FastAPI
   - ตัวอย่างระบบ API ที่เชื่อมต่อฐานข้อมูล PostgreSQL
   - เหมาะสำหรับการแสดงแนวทางการออกแบบ backend และ database service
3. React Dashboard District Filter
   - Dashboards สำหรับนำเสนอข้อมูลแบบรายอำเภอและตัวกรองข้อมูล

## สถาปัตยกรรมระบบ

![สถาปัตยกรรมระบบ](docs/architecture-diagram.svg)

## โครงสร้างโปรเจค

```text
senior-full-stack-developer-data-scientist/
├── README.md
├── .gitignore
├── generate_chonburi_dengue_mock.py
├── docs/
│   └── architecture-diagram.svg
├── chonburi-dengue-watch/
│   ├── README.md
│   ├── backend/
│   └── frontend/
├── postgresql-fastapi/
│   └── postgresql/
└── react-dashboard-district-filter/
    └── frontend/
```

## ความสามารถที่แสดงผ่านโปรเจค

- Backend Development: FastAPI, REST API, Validation, Error Handling
- Frontend Development: React, Vite, UI Components, Dashboard
- Data Engineering: Synthetic dataset generation, data cleaning, feature preparation
- Machine Learning: Random Forest, model training, prediction workflow
- Database Design: SQLite และ PostgreSQL
- Presentation Ready: โครงสร้างโปรเจค, README ที่อ่านง่าย, ระบบที่สามารถทดลองได้

## โครงการหลัก: Chonburi Dengue Watch

โครงการนี้เป็นส่วนสำคัญที่สุดของ repository โดยมีวัตถุประสงค์เพื่อจำลองกระบวนการทำงานแบบ end-to-end ดังนี้:

- สร้างชุดข้อมูลสมมุติสำหรับสภาพแวดล้อมทางสาธารณสุข
- จัดการข้อมูลเชิงพื้นที่และสภาพอากาศ
- ฝึกโมเดลเพื่อพยากรณ์จำนวนผู้ป่วยในแต่ละอำเภอ
- สร้าง REST API สำหรับส่งข้อมูลและผลการพยากรณ์
- แสดงผลบน Dashboard เพื่อให้เห็นความเสี่ยงและแนวโน้ม

## วิธีเริ่มต้นใช้งาน

### 1) Clone และเปิดโปรเจค

```bash
git clone https://github.com/prapan34-hue/senior-full-stack-developer-data-scientist.git
cd senior-full-stack-developer-data-scientist
```

### 2) เริ่มต้นโครงการ Chonburi Dengue Watch

```powershell
cd chonburi-dengue-watch/backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.ml.train
uvicorn app.main:app --reload --port 8000
```

เปิด Frontend:

```powershell
cd ../frontend
pnpm install
pnpm dev
```

### 3) เริ่มต้น PostgreSQL Demo

```powershell
cd ../postgresql-fastapi/postgresql
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
docker compose up -d
uvicorn app.main:app --reload --port 8000
```

## ข้อควรทราบ

ข้อมูลในโครงการหลักเป็นข้อมูลที่สร้างขึ้นเพื่อการสาธิตและการนำเสนอเท่านั้น ไม่ควรใช้สำหรับตัดสินใจทางด้านสาธารณสุขจริงโดยตรง หากต้องใช้งานในเชิงจริงควรมีข้อมูลจริง การตรวจสอบทางวิชาการ และการร่วมมือกับผู้เชี่ยวชาญด้านสุขภาพและสาธารณสุข

## สรุป

Repository นี้สะท้อนถึงแนวทางการทำงานแบบ multidisciplinary ที่ผสานระหว่าง:

- Data Science
- Full-Stack Engineering
- Frontend Design
- API Architecture
- Business Intelligence และ Presentation

เหมาะอย่างยิ่งสำหรับการใช้เป็น portfolio project หรือเอกสารประกอบการนำเสนอในระดับนักพัฒนาหรือผู้เชี่ยวชาญด้านข้อมูล
