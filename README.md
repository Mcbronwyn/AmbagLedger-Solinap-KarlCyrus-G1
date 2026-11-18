# AmbagLedger: Transparent Class Fund and Micro-Contribution Tracker

- **Developer:** Karl Cyrus P. Solinap
- **Course & Section:** CSIT327 – Information Management 2 (Section G1)
- **Institution:** Cebu Institute of Technology – University
- **Tech Stack:** Full-Stack Django (`Django >= 5.2, < 6.0`, Django Templates, HTML/CSS) & Supabase PostgreSQL (`psycopg`, `python-dotenv`)

---

## Project Overview

AmbagLedger is a centralized, database-driven financial tracking web application designed for university class sections and student organizations to manage collective micro-contributions ("ambagan")[cite: 1]. Backed by a normalized **Supabase PostgreSQL** database, the system replaces error-prone single-entry paper notebooks with role-segregated administrative controls for **Class Treasurers** and real-time read-only transparency workspaces for **Class Members**[cite: 1].

---

## Implemented Increments

### Project Development 1 (PD1) — Authentication, RBAC & Profile Management (`F-01`)
- Custom `CustomUser` model (`users` table) using institutional email authentication and PBKDF2-SHA256 password hashing[cite: 1].
- Database-level role enforcement (`TREASURER` vs. `MEMBER` via `CheckConstraint`) and `@treasurer_required` / `@member_required` decorators returning HTTP `403` on unauthorized cross-role access (`BR-01`, `BR-02`)[cite: 1].
- Role-based dashboards, `POST`-enforced logout, and self-service profile viewing and editing[cite: 1].

### Project Development 2 (PD2) — Core Feature Vertical Slice (`F-02` & `F-03`)
- **Class Section Workspaces (`F-02`):** Full Treasurer CRUD (`Create`, `Read`, `Update`, `Delete`) for the `sections` table with automatic generation of a unique 8-character alphanumeric `invite_code` (`BR-03`) and strict ownership isolation[cite: 1].
- **Member Onboarding & Roster Moderation (`F-03`):** Student self-enrollment into class sections (`section_members` table) using a valid `invite_code` and institutional `student_id_number`[cite: 1].
- **Business Rule Enforcement:**
  - `BR-03`: Unique, non-null alphanumeric invite code per section[cite: 1].
  - `BR-04`: Composite uniqueness constraint (`UNIQUE (section_id, user_id)`) preventing duplicate enrollment in the same section[cite: 1].
  - `BR-05`: Maximum roster capacity of **50 active students** per section enforced on join and reactivation[cite: 1].

---

## Local Development Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/Mcbronwyn/AmbagLedger-Solinap-KarlCyrus-G1.git](https://github.com/Mcbronwyn/AmbagLedger-Solinap-KarlCyrus-G1.git)
cd AmbagLedger-Solinap-KarlCyrus-G1