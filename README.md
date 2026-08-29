<div align="center">
  <img src="docs/architecture-diagram.svg" width="880" alt="Architecture diagram" />
  <h1>Senior Full-Stack Developer / Data Scientist Portfolio</h1>
  <p>
    <strong>Full-Stack • Data Science • Dashboard • AI Prototyping</strong>
  </p>
  <p>
    โปรเจคนี้สะท้อนความสามารถในการสร้างระบบ end-to-end ตั้งแต่ข้อมูล การวิเคราะห์ การพยากรณ์ ไปจนถึงการแสดงผลบนหน้า Dashboard
    ที่พร้อมสำหรับนำเสนอผลงานในเชิงธุรกิจและงานวิจัย
  </p>
</div>

## Highlights

- FastAPI backend สำหรับ API และการประมวลผลข้อมูล
- React dashboard สำหรับการแสดงข้อมูลแบบ interactive
- Machine Learning workflow สำหรับพยากรณ์และประเมินความเสี่ยง
- PostgreSQL integration สำหรับระบบข้อมูลเชิง production-like
- โครงสร้างโปรเจคที่จัดระเบียบและพร้อมนำเสนอต่อผู้ชม

## Project Showcase

<div align="center">
  <table>
    <tr>
      <td width="50%"><img src="docs/dashboard-preview-1.svg" width="100%" alt="Dashboard preview 1" /></td>
      <td width="50%"><img src="docs/dashboard-preview-2.svg" width="100%" alt="Dashboard preview 2" /></td>
    </tr>
  </table>
</div>

## Projects Included

### 1) Chonburi Dengue Watch
- ระบบเฝ้าระวังและพยากรณ์โรคไข้เลือดออกจังหวัดชลบุรี
- ผสาน FastAPI, React, SQLite และ Machine Learning
- เหมาะสำหรับการนำเสนอเชิง data-driven และสาธารณสุขดิจิทัล

### 2) PostgreSQL + FastAPI
- ตัวอย่าง API ที่เชื่อมต่อ PostgreSQL อย่างมีโครงสร้าง
- สะท้อนความสามารถด้าน backend architecture, database design และ API service

### 3) React Dashboard District Filter
- ตัวอย่าง dashboard สำหรับข้อมูลภาคพื้นที่แบบรายอำเภอ
- เน้นการกรองข้อมูลและการสรุปสถานการณ์เพื่อดูแนวโน้มได้เร็ว

## Architecture Overview

![Architecture diagram](docs/architecture-diagram.svg)

## Tech Stack

- Python / FastAPI / SQLAlchemy
- React / Vite / Recharts
- PostgreSQL / SQLite
- Machine Learning / Random Forest
- Docker Compose / API Design

## Presentation Page

คุณสามารถเปิดหน้า presentation แบบสั้น ๆ ได้ที่:

- [docs/portfolio-landing.html](docs/portfolio-landing.html)

## Quick Start

### 1) Clone Repository

```bash
git clone https://github.com/prapan34-hue/senior-full-stack-developer-data-scientist.git
cd senior-full-stack-developer-data-scientist
```

### 2) Run Chonburi Dengue Watch

```powershell
cd chonburi-dengue-watch/backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.ml.train
uvicorn app.main:app --reload --port 8000
```

```powershell
cd ../frontend
pnpm install
pnpm dev
```

### 3) Run PostgreSQL Sample

```powershell
cd ../postgresql-fastapi/postgresql
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
docker compose up -d
uvicorn app.main:app --reload --port 8000
```

## Notes

ข้อมูลในโครงการหลักเป็นข้อมูลจำลองเพื่อการสาธิต การทดลอง และการนำเสนอเท่านั้น
ไม่ควรใช้เป็นฐานข้อมูลเชิงปฏิบัติจริงสำหรับตัดสินใจทางสุขภาพหรือสาธารณสุขโดยตรง หากต้องใช้งานจริงควรมีข้อมูลจริง การตรวจสอบทางวิชาการ และการร่วมมือกับผู้เชี่ยวชาญที่เกี่ยวข้อง

## Summary

Repository นี้แสดงให้เห็นถึงความสามารถต่อเนื่องใน 4 ด้านสำคัญ:

- Backend Engineering
- Frontend Development
- Data Science / ML
- Product Presentation

ซึ่งเหมาะสำหรับใช้เป็น portfolio project ในการสมัครงาน หรือการนำเสนอผลงานต่อผู้ชม
