# ScanX Web Check-In Backend

This is the backend API for the **ScanX Employee Check-In / Check-Out Web Application**.

The application allows ScanX staff members to check in and check out, while admins can manage staff users, roles, access status, and attendance reports.

---

## 1. Tech Stack

The backend is built using:

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* JWT authentication
* bcrypt password hashing
* Google Cloud SQL
* Google Cloud Run

---

## 2. Main Features

Current MVP features:

* Admin login
* Staff login
* JWT-based authentication
* Swagger authorization support
* Role-based authorization
* Admin can create staff users
* Admin can change user roles
* Admin can change user status
* Admin can ban/remove users
* Admin can reset staff password
* Staff can check in
* Staff can check out
* Duplicate check-in prevention
* Checkout without check-in prevention
* Admin can view attendance records
* Admin can view currently checked-in staff
* Admin can view attendance summary
* Audit logs for important actions

---

## 3. Project Structure

```txt
web_checkin_backend/
  app/
    __init__.py
    main.py
    config.py
    database.py

    models/
      __init__.py
      role.py
      user.py
      staff_profile.py
      attendance_session.py
      attendance_event.py
      audit_log.py
      login_session.py

    schemas/
      __init__.py
      auth_schema.py
      user_schema.py
      attendance_schema.py

    routes/
      __init__.py
      auth_routes.py
      admin_user_routes.py
      staff_routes.py
      admin_attendance_routes.py

    services/
      __init__.py
      auth_service.py
      attendance_service.py
      audit_service.py

    utils/
      __init__.py
      security.py
      dependencies.py

    seed.py

  alembic/
  alembic.ini
  requirements.txt
  .env
  .env.example
  .gcloudignore
  Dockerfile
  README.md
```

---

## 4. File Usage Explanation

### `app/main.py`

This is the main FastAPI entry point.

It is responsible for:

* Creating the FastAPI app
* Adding CORS middleware
* Registering all API routers
* Providing the `/health` endpoint

Main routers included:

* Auth routes
* Staff routes
* Admin user routes
* Admin attendance routes

Run command uses this file:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

### `app/config.py`

This file loads application settings from `.env`.

It contains:

* App name
* App environment
* Database URL
* JWT settings
* Default timezone
* CORS allowed origins

Important environment variables loaded here:

```env
DATABASE_URL
JWT_SECRET_KEY
JWT_ALGORITHM
JWT_ACCESS_TOKEN_EXPIRE_MINUTES
DEFAULT_TIMEZONE
CORS_ALLOWED_ORIGINS
```

---

### `app/database.py`

This file handles database connection setup.

It contains:

* SQLAlchemy engine
* Database session factory
* Base model class
* `get_db()` dependency

`get_db()` is used in routes to safely open and close DB sessions.

---

## 5. Models

Models define database table structures.

All table names end with `_web_checkin` to avoid conflict with existing ScanX tables.

---

### `app/models/role.py`

Table:

```txt
roles_web_checkin
```

Purpose:

Stores system roles.

Default roles:

* admin
* staff

Used for role-based access control.

---

### `app/models/user.py`

Table:

```txt
users_web_checkin
```

Purpose:

Stores all admin and staff users.

Important fields:

* full_name
* username
* email
* phone
* password_hash
* role_id
* status
* is_active
* is_deleted
* created_by
* last_login_at

This table is used for login and access control.

---

### `app/models/staff_profile.py`

Table:

```txt
staff_profiles_web_checkin
```

Purpose:

Stores additional staff details.

Important fields:

* employee_code
* job_title
* department
* default_timezone
* joining_date

This keeps staff-specific information separate from login information.

---

### `app/models/attendance_session.py`

Table:

```txt
attendance_sessions_web_checkin
```

Purpose:

Stores each complete or open work session.

One row represents one check-in/check-out cycle.

Important fields:

* user_id
* check_in_at_utc
* check_out_at_utc
* display_timezone
* total_minutes
* status
* check_in_ip
* check_out_ip
* check_in_user_agent
* check_out_user_agent

Status values:

```txt
open
closed
incomplete
admin_adjusted
voided
```

For MVP, mostly used statuses are:

```txt
open
closed
```

---

### `app/models/attendance_event.py`

Table:

```txt
attendance_events_web_checkin
```

Purpose:

Stores raw attendance events.

Examples:

* check_in
* check_out
* admin_adjustment
* auto_close
* void

This table helps with audit and future debugging.

---

### `app/models/audit_log.py`

Table:

```txt
audit_logs_web_checkin
```

Purpose:

Tracks important system and admin actions.

Example actions:

* login_success
* login_failed
* user_created
* role_changed
* status_changed
* password_reset

This table is useful for accountability and security.

---

### `app/models/login_session.py`

Table:

```txt
login_sessions_web_checkin
```

Purpose:

Stores login session information.

This is currently available for future use.

It can later support:

* Force logout
* Device/session tracking
* Active session list
* Token revocation

---

### `app/models/__init__.py`

This file imports all models.

It is useful for Alembic migrations and model registration.

---

## 6. Schemas

Schemas define request and response validation using Pydantic.

---

### `app/schemas/auth_schema.py`

Contains authentication-related schemas.

Main schemas:

* `LoginRequest`
* `LoginResponse`
* `CurrentUserResponse`

Used by:

* `/api/web-checkin/auth/login`
* `/api/web-checkin/auth/token`
* `/api/web-checkin/auth/me`

---

### `app/schemas/user_schema.py`

Contains user management schemas.

Main schemas:

* `CreateUserRequest`
* `UserResponse`
* `ChangeRoleRequest`
* `ChangeStatusRequest`
* `ResetPasswordRequest`

Used by admin user APIs.

---

### `app/schemas/attendance_schema.py`

Contains attendance-related schemas.

Main schemas:

* `AttendanceStatusResponse`
* `AttendanceSessionResponse`

Used by staff check-in/check-out APIs.

---

## 7. Routes

Routes define the API endpoints.

---

### `app/routes/auth_routes.py`

Base path:

```txt
/api/web-checkin/auth
```

Endpoints:

```txt
POST /login
POST /token
GET  /me
```

Usage:

* `/login` is JSON-based login for frontend.
* `/token` is form-data login for Swagger Authorize.
* `/me` returns current logged-in user details.

---

### `app/routes/staff_routes.py`

Base path:

```txt
/api/web-checkin/staff
```

Endpoints:

```txt
GET  /status
POST /check-in
POST /check-out
```

Usage:

Staff uses these APIs to check current status, check in, and check out.

---

### `app/routes/admin_user_routes.py`

Base path:

```txt
/api/web-checkin/admin/users
```

Endpoints:

```txt
POST   /
GET    /
PATCH  /{user_id}/role
PATCH  /{user_id}/status
PATCH  /{user_id}/password
```

Usage:

Admin uses these APIs to manage users.

Admin can:

* Create staff user
* List users
* Change role
* Change status
* Reset password

---

### `app/routes/admin_attendance_routes.py`

Base path:

```txt
/api/web-checkin/admin/attendance
```

Endpoints:

```txt
GET /
GET /currently-checked-in
GET /summary
```

Usage:

Admin uses these APIs to view attendance records and summary.

---

## 8. Services

Services contain reusable business logic.

---

### `app/services/auth_service.py`

Handles authentication logic.

Responsibilities:

* Find user by username
* Verify password
* Check active/banned status
* Update last login time
* Create JWT access token

---

### `app/services/attendance_service.py`

Handles attendance logic.

Responsibilities:

* Get active attendance session
* Get current attendance status
* Check in user
* Check out user
* Calculate total minutes
* Create attendance event records

Important validation:

* User cannot check in twice.
* User cannot check out without active check-in.

---

### `app/services/audit_service.py`

Handles audit logging.

Responsibilities:

* Create audit log entries
* Track admin/system actions

---

## 9. Utilities

---

### `app/utils/security.py`

Handles password hashing and JWT token creation.

Functions:

```txt
hash_password()
verify_password()
create_access_token()
```

Uses:

* bcrypt
* passlib
* python-jose

---

### `app/utils/dependencies.py`

Contains FastAPI dependencies.

Important dependencies:

```txt
get_current_user()
require_admin()
```

Usage:

* `get_current_user()` protects logged-in APIs.
* `require_admin()` protects admin-only APIs.

---

## 10. Seed File

### `app/seed.py`

This file creates default data.

It creates:

* admin role
* staff role
* first admin user

Default admin credentials:

```txt
Username: admin
Password: Admin@123
```

After first login, change the admin password.

Run seed:

```bash
python -m app.seed
```

---

## 11. Environment Variables

Create `.env` in the project root.

Example:

```env
APP_NAME=scanx-web-checkin
APP_ENV=development
APP_DEBUG=true

DATABASE_URL=postgresql://postgres:your_encoded_password@127.0.0.1:5432/scanx_app

JWT_SECRET_KEY=replace-this-with-random-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

DEFAULT_TIMEZONE=America/Chicago

CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 12. JWT Secret Key

`JWT_SECRET_KEY` is used to sign JWT tokens.

Do not use:

```env
JWT_SECRET_KEY=change-this-secret-key
```

Generate a secure random key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Then copy the output into `.env`:

```env
JWT_SECRET_KEY=paste-generated-secret-here
```

Important:

* Use one secret for local development.
* Use a different secret for production.
* Never commit `.env` to GitHub.
* In production, store this in Google Secret Manager.

If the JWT secret is changed, all existing login tokens become invalid and users need to log in again.

---

## 13. Database Password with Special Characters

If DB password contains special characters, URL encode them in `DATABASE_URL`.

Example:

Actual password:

```txt
ScanX@123
```

Use:

```env
DATABASE_URL=postgresql://postgres:ScanX%40123@127.0.0.1:5432/scanx_app
```

Common encodings:

```txt
@  = %40
#  = %23
$  = %24
%  = %25
&  = %26
+  = %2B
/  = %2F
:  = %3A
?  = %3F
=  = %3D
```

---

## 14. Installation Instructions

### Step 1: Clone or open the backend project

```bash
cd C:\Latitude_Projects\ScanX\web_checkin_backend
```

---

### Step 2: Create virtual environment

```bash
python -m venv venv
```

---

### Step 3: Activate virtual environment

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

---

### Step 4: Install dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not ready yet, install manually:

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic python-dotenv passlib[bcrypt] bcrypt==4.0.1 python-jose pydantic-settings email-validator python-multipart
```

Then generate requirements:

```bash
pip freeze > requirements.txt
```

---

## 15. Required Python Packages

Important packages:

```txt
fastapi
uvicorn
sqlalchemy
psycopg2-binary
alembic
python-dotenv
pydantic-settings
python-jose
passlib
bcrypt==4.0.1
email-validator
python-multipart
```

Important note:

Use:

```txt
bcrypt==4.0.1
```

This avoids compatibility issues with passlib.

If bcrypt issue occurs, run:

```bash
pip uninstall bcrypt -y
pip install bcrypt==4.0.1
```

---

## 16. Running Locally

### Step 1: Start Cloud SQL Auth Proxy

Run this in a separate terminal:

```bash
cloud-sql-proxy vernal-maker-473121-k4:us-central1:scanx-postgres-db --port 5432
```

Keep this terminal open.

---

### Step 2: Start FastAPI backend

In backend terminal:

```bash
venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run at:

```txt
http://localhost:8000
```

Swagger docs:

```txt
http://localhost:8000/docs
```

Health check:

```txt
http://localhost:8000/health
```

---

## 17. Swagger Authentication

Open:

```txt
http://localhost:8000/docs
```

Click **Authorize**.

Enter:

```txt
username: admin
password: Admin@123
```

Leave these blank:

```txt
client_id
client_secret
```

Click **Authorize**.

Now protected APIs can be tested from Swagger.

---

## 18. API Testing Flow

### 1. Login as admin

Endpoint:

```txt
POST /api/web-checkin/auth/login
```

Body:

```json
{
  "username": "admin",
  "password": "Admin@123"
}
```

---

### 2. Create dummy staff user

Endpoint:

```txt
POST /api/web-checkin/admin/users
```

Body:

```json
{
  "full_name": "John Staff",
  "username": "john",
  "password": "John@123",
  "role_name": "staff",
  "email": "john@example.com",
  "phone": "1234567890",
  "employee_code": "EMP001",
  "job_title": "Front Desk Staff",
  "department": "Operations"
}
```

---

### 3. Login as staff

Endpoint:

```txt
POST /api/web-checkin/auth/login
```

Body:

```json
{
  "username": "john",
  "password": "John@123"
}
```

---

### 4. Check staff status

Endpoint:

```txt
GET /api/web-checkin/staff/status
```

---

### 5. Staff check in

Endpoint:

```txt
POST /api/web-checkin/staff/check-in
```

---

### 6. Staff check out

Endpoint:

```txt
POST /api/web-checkin/staff/check-out
```

---

### 7. Admin view attendance

Endpoint:

```txt
GET /api/web-checkin/admin/attendance
```

Optional filters:

```txt
staff_user_id
status
start_date
end_date
```

Example:

```txt
/api/web-checkin/admin/attendance?status=closed
```

---

## 19. Database Tables

This backend uses the following tables:

```txt
roles_web_checkin
users_web_checkin
staff_profiles_web_checkin
clinics_web_checkin
user_clinics_web_checkin
attendance_sessions_web_checkin
attendance_events_web_checkin
login_sessions_web_checkin
audit_logs_web_checkin
attendance_adjustments_web_checkin
password_reset_tokens_web_checkin
```

The MVP mainly uses:

```txt
roles_web_checkin
users_web_checkin
staff_profiles_web_checkin
attendance_sessions_web_checkin
attendance_events_web_checkin
audit_logs_web_checkin
```

---

## 20. Useful SQL Checks

Check users:

```sql
SELECT id, full_name, username, status, is_active
FROM users_web_checkin;
```

Check roles:

```sql
SELECT id, role_name
FROM roles_web_checkin;
```

Check attendance sessions:

```sql
SELECT *
FROM attendance_sessions_web_checkin
ORDER BY created_at DESC;
```

Check audit logs:

```sql
SELECT action, actor_user_id, target_user_id, created_at
FROM audit_logs_web_checkin
ORDER BY created_at DESC;
```

---

## 21. Cloud SQL Connection

For local development, use Cloud SQL Auth Proxy.

Instance connection name:

```txt
vernal-maker-473121-k4:us-central1:scanx-postgres-db
```

Proxy command:

```bash
cloud-sql-proxy vernal-maker-473121-k4:us-central1:scanx-postgres-db --port 5432
```

Then `.env` database URL should use:

```env
DATABASE_URL=postgresql://postgres:your_password@127.0.0.1:5432/scanx_app
```

Do not use the instance connection name directly as database host.

Wrong:

```env
DATABASE_URL=postgresql://postgres:password@vernal-maker-473121-k4:us-central1:scanx-postgres-db:5432/scanx_app
```

Correct with proxy:

```env
DATABASE_URL=postgresql://postgres:password@127.0.0.1:5432/scanx_app
```

---

## 22. Alembic Notes

Alembic is used for future database migrations.

Current database tables were created manually from Cloud SQL SQL script.

For future development, Alembic should be fixed and used properly.

Common Alembic commands:

```bash
alembic revision --autogenerate -m "message"
alembic upgrade head
```

If `alembic.ini` is invalid, ensure it has proper sections like:

```ini
[alembic]
script_location = alembic

sqlalchemy.url = postgresql://postgres:password@localhost:5432/scanx_app
```

Do not keep only this line in `alembic.ini`:

```ini
sqlalchemy.url = postgresql://postgres:password@localhost:5432/scanx_app
```

That will break Alembic.

---

## 23. Deployment Notes

For Cloud Run deployment, do not upload:

* `.env`
* `venv/`
* `.git/`
* local cache files

Use `.gcloudignore`.

Production secrets should be stored in:

```txt
Google Secret Manager
```

Recommended production variables:

```env
APP_ENV=production
APP_DEBUG=false
DATABASE_URL=production-database-url
JWT_SECRET_KEY=production-secret-from-secret-manager
DEFAULT_TIMEZONE=America/Chicago
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

---

## 24. Current MVP Status

Backend MVP is functionally complete.

Completed:

* Authentication
* Authorization
* Admin user management
* Staff check-in/check-out
* Attendance reports
* Audit logging
* Cloud SQL database connection
* Swagger API testing

Pending for production readiness:

* Dockerfile finalization
* Cloud Run deployment
* Alembic migration cleanup
* Production secret setup
* Frontend integration
* Production CORS domain
* Admin password change

---

## 25. Security Notes

Important security rules:

* Do not commit `.env`
* Do not expose database publicly
* Use Cloud SQL Auth Proxy locally
* Use Secret Manager in production
* Use strong JWT secret
* Change default admin password
* Keep bcrypt pinned to compatible version
* Use HTTPS in production

---

## 26. Default Admin

Default admin created during seed:

```txt
Username: admin
Password: Admin@123
```

Change this password after first successful login.
