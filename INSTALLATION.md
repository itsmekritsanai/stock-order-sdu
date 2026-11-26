# คู่มือการติดตั้งและนำระบบขึ้นใช้งาน (Installation & Deployment Guide)
### ระบบขอเบิกพัสดุและคลังพัสดุดิจิทัล มหาวิทยาลัยสวนดุสิต (Stock Order SDU v3.8.3)

คู่มือนี้รองรับการนำไปติดตั้งและ Deploy ได้ทั้งบนเซิร์ฟเวอร์จริง (Linux / Windows Server) และเครื่องพัฒนา

---

## วิธีที่ 1: Deploy แบบ 1 คำสั่งด้วย Docker (แนะนำที่สุด — ง่ายที่สุด)

วิธีนี้ไม่จำเป็นต้องติดตั้ง Python หรือ PostgreSQL บนเครื่องเป้าหมาย ใช้แค่ **Docker** อย่างเดียว:

1. **โคลนโปรเจกต์ลงเครื่องปลายทาง:**
   ```bash
   git clone https://github.com/itsmekritsanai/stock-order-sdu.git
   cd stock-order-sdu
   ```

2. **(แนะนำสำหรับ Production) คัดลอกไฟล์ตั้งค่า `.env` และเปลี่ยนรหัสผ่าน/คีย์ลับ:**
   ```bash
   cp .env.example .env
   ```
   แก้ไขค่าสำคัญใน `.env` ก่อนเปิดใช้งานจริง:
   - `DB_PASSWORD` — เปลี่ยนรหัสผ่านฐานข้อมูลจากค่าเริ่มต้น
   - `STAFF_PASSWORD`, `DEFAULT_USER_PASSWORD` — ตั้งรหัสผ่านเจ้าหน้าที่และผู้ใช้
   - `STAFF_AUTH_SECRET`, `REQUESTER_AUTH_SECRET` — ตั้งสตริงสุ่มความยาว >= 32 ตัวอักษร
   - `AUTH_BYPASS="false"` — บังคับให้ระบบยืนยันตัวตน Login เสมอ
   - `ALLOWED_ORIGINS` / `BASE_URL` — ใส่ URL หรือโดเมนจริงที่ใช้เข้างาน (หากมี)

3. **สั่งสร้างและเปิดใช้งานครบทั้งเว็บ + ฐานข้อมูลในคำสั่งเดียว:**
   ```bash
   docker compose up -d --build
   ```

4. **ตรวจสอบสถานะความพร้อม:**
   ```bash
   docker compose ps
   ```
   ระบบจะรันคอนเทนเนอร์ทั้ง 2 ตัวให้โดยอัตโนมัติ:
   - `sdu_stock_postgres`: ฐานข้อมูล PostgreSQL 17 (อิมพอร์ต `backend/schema_postgres.sql` + ข้อมูลตั้งต้น 34 รายการให้อัตโนมัติ)
   - `sdu_stock_app`: เว็บพอร์ทัล + REST API บนพอร์ต `8080`

5. **เข้าใช้งานผ่านเว็บเบราว์เซอร์:**
   - ศูนย์กลางพอร์ทัล: `http://localhost:8080/portal.html`
   - หน้าผู้ขอเบิก: `http://localhost:8080/index.html`
   - หน้าเจ้าหน้าที่/ผู้ดูแล: `http://localhost:8080/staff.html`
   - ตรวจสอบ Health API: `http://localhost:8080/api?action=health`

---

## วิธีที่ 2: ติดตั้งแบบรัน Python บนเครื่อง Host (พัฒนา / ไม่มี Docker สำหรับ App)

1. คัดลอกโปรเจกต์และสร้างไฟล์ `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```
2. สร้าง Virtual Environment และติดตั้งแพ็กเกจ:
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
   *(บน macOS/Linux ใช้ `source .venv/bin/activate`)*
3. สตาร์ทเฉพาะฐานข้อมูล PostgreSQL ด้วย Docker Compose:
   ```powershell
   docker compose up -d postgres
   ```
4. เปิดใช้งานเว็บเซิร์ฟเวอร์:
   - บน Windows ดับเบิลคลิก `start.bat` หรือรัน:
     ```powershell
     .venv\Scripts\python.exe backend\server.py
     ```

---

## การตั้งค่า HTTPS (Reverse Proxy สำหรับขึ้นเซิร์ฟเวอร์จริง)

หากเปิดใช้งานผ่านโดเมนมหาลัยหรืออินเทอร์เน็ต แนะนำให้วาง Nginx หรือ Caddy ไว้ด้านหน้าแล้ว Proxy มายังพอร์ต `8080`:

```nginx
server {
    listen 443 ssl http2;
    server_name stock.example.ac.th;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## การทดสอบระบบ (Automated Tests & Rules Verification)

```powershell
.venv\Scripts\python .agents/skills/stock-order-rules/scripts/verify_rules.py
.venv\Scripts\python -m pytest tests -v
```

---

## การสำรองข้อมูลและการกู้คืน (Database Backup & Restore)

- **สำรองข้อมูล PostgreSQL เป็นไฟล์ SQL:**
  ```bash
  docker exec -t sdu_stock_postgres pg_dump -U postgres sdu_inventory > backup_sdu_inventory.sql
  ```
- **กู้คืนข้อมูลจากไฟล์สำรอง:**
  ```bash
  docker exec -i sdu_stock_postgres psql -U postgres sdu_inventory < backup_sdu_inventory.sql
  ```

---

## การแก้ปัญหาที่พบบ่อย (Troubleshooting)

1. **พอร์ต 8080 หรือ 5433 ชนกับบริการอื่นในเครื่อง:**
   แก้ค่า `PORT` หรือ `DB_PORT` ในไฟล์ `.env` แล้วรัน `docker compose up -d` ใหม่
2. **ต้องการอัปเดตโค้ดเวอร์ชันใหม่หลัง `git pull`:**
   ```bash
   git pull origin main
   docker compose up -d --build
   ```
   *(ข้อมูลในโฟลเดอร์ `./postgres-data` จะยังคงอยู่ครบ และ `backend/server.py` จะทำ Schema Auto-Migration ให้อัตโนมัติ)*
