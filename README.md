# AmbagLedger: Transparent Class Fund and Micro-Contribution Tracker

- **Developer:** Karl Cyrus P. Solinap
- **Course & Section:** CSIT327 – Information Management 2 (Section G1)
- **Institution:** Cebu Institute of Technology – University
- **Tech Stack:** Full-Stack Django (`Django >= 5.2, < 6.0`, Django Templates, HTML/CSS) & Supabase PostgreSQL (`psycopg`, `python-dotenv`)

---

## Project Overview

AmbagLedger is a centralized, database-driven financial tracking web application designed for university class sections and student organizations to manage collective micro-contributions ("ambagan"). Backed by a normalized **Supabase PostgreSQL** database, the system replaces error-prone single-entry paper notebooks with role-segregated administrative controls for **Class Treasurers** and real-time read-only transparency workspaces for **Class Members**.

---

## Implemented Increments

### Project Development 1 (PD1) — Authentication, RBAC & Profile Management (`F-01`)
- Custom `CustomUser` model (`users` table) using institutional email authentication and PBKDF2-SHA256 password hashing.
- Database-level role enforcement (`TREASURER` vs. `MEMBER` via `CheckConstraint`) and `@treasurer_required` / `@member_required` decorators returning HTTP `403` on unauthorized cross-role access (`BR-01`, `BR-02`).
- Role-based dashboards, `POST`-enforced logout, and self-service profile viewing and editing.

### Project Development 2 (PD2) — Core Feature Vertical Slice (`F-02` & `F-03`)
- **Class Section Workspaces (`F-02`):** Full Treasurer CRUD (`Create`, `Read`, `Update`, `Delete`) for the `sections` table with automatic generation of a unique 8-character alphanumeric `invite_code` (`BR-03`) and strict ownership isolation.
- **Member Onboarding & Roster Moderation (`F-03`):** Student self-enrollment into class sections (`section_members` table) using a valid `invite_code` and institutional `student_id_number`.
- **Business Rule Enforcement:**
  - `BR-03`: Unique, non-null alphanumeric invite code per section.
  - `BR-04`: Composite uniqueness constraint (`UNIQUE (section_id, user_id)`) preventing duplicate enrollment in the same section.
  - `BR-05`: Maximum roster capacity of **50 active students** per section enforced on join and reactivation.

---

## Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Mcbronwyn/AmbagLedger-Solinap-KarlCyrus-G1.git
cd AmbagLedger-Solinap-KarlCyrus-G1
```

### 2. Create and Activate a Virtual Environment

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (`.env`)
Create a `.env` file in the project root with your Supabase PostgreSQL credentials:
```env
SECRET_KEY=your-django-secret-key
DEBUG=True

DB_NAME=postgres
DB_USER=postgres.<your-project-ref>
DB_PASSWORD=<your-supabase-db-password>
DB_HOST=<your-supabase-pooler-host>
DB_PORT=5432
DB_SSLMODE=require
```

### 5. Apply Database Migrations & Run the Server
```bash
python manage.py migrate
python manage.py runserver
```
Open `http://127.0.0.1:8000/` in your browser.

### 6. Run Automated Tests
```bash
python manage.py test accounts sections --keepdb
```