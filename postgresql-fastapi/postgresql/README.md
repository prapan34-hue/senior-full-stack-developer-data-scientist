# PostgreSQL + FastAPI

โปรเจคนี้เป็นตัวอย่างระบบ API ที่ใช้ FastAPI ร่วมกับ PostgreSQL เพื่อแสดงความสามารถด้าน Backend Architecture, Database Integration และ Data Service Design ที่พร้อมใช้งานจริง

## ภาพรวมของโปรเจค

โครงการนี้มีจุดประสงค์หลักเพื่อแสดงกระบวนการทำงานดังนี้:

- เชื่อมต่อ FastAPI กับ PostgreSQL
- จัดการข้อมูลเชิงพื้นที่และสถิติรายสัปดาห์
- ใช้ SQL schema ที่ชัดเจนและสามารถบำรุงรักษาได้
- ให้ API endpoint สำหรับการเรียกข้อมูลและบันทึกข้อมูล
- สร้างสภาพแวดล้อมที่สามารถขยายและพัฒนาต่อได้

## Stack ที่ใช้

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Docker Compose
- Pydantic

## โครงสร้างโปรเจค

```text
postgresql-fastapi/
└── postgresql/
    ├── app/
    │   ├── database.py
    │   ├── main.py
    │   ├── models.py
    │   └── schemas.py
    ├── docker-compose.yml
    ├── .env.example
    ├── requirements.txt
    ├── schema.sql
    └── README.md
```

## วิธีเริ่มต้นใช้งาน

```powershell
docker compose up -d
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

หลังจากรันแล้ว สามารถเข้าถึง API ได้ที่:

http://localhost:8000/docs

และตรวจสอบ endpoint:

- GET /api/health
- GET /api/districts
- GET /api/surveillance
- POST /api/surveillance

## ข้อควรระวังด้านความปลอดภัย

- เก็บค่า DATABASE_URL หรือ credentials ในไฟล์ .env เท่านั้น
- ไม่ควร commit credentials ลง repository
- ควรใช้ secret management ในสภาพแวดล้อมจริง

## แนวทางในการพัฒนาเพิ่มเติม

- เพิ่มระบบ migration ด้วย Alembic
- ใช้ JWT หรือ OAuth สำหรับ Authentication
- เพิ่มการ validate และ logging ให้ครบขึ้น
- ปรับให้รองรับการใช้งานแบบ Production-ready

> โปรเจคนี้เหมาะสำหรับแสดงภาพรวมของ backend architecture และการผสานฐานข้อมูลแบบ production-like ให้เห็นถึงความสามารถในการทำงานกับข้อมูลจริงในระดับระบบ
