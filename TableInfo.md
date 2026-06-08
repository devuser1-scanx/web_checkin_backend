-- =========================================================
-- ScanX Web Check-In / Check-Out App
-- Database Tables
-- All tables end with _web_checkin
-- =========================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- =========================================================
-- 1. Roles
-- =========================================================

CREATE TABLE IF NOT EXISTS roles_web_checkin (
    id BIGSERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_system_role BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
-- 2. Users
-- =========================================================

CREATE TABLE IF NOT EXISTS users_web_checkin (
    id BIGSERIAL PRIMARY KEY,

    full_name VARCHAR(150) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(150),
    phone VARCHAR(30),

    password_hash TEXT NOT NULL,

    role_id BIGINT NOT NULL REFERENCES roles_web_checkin(id),

    status VARCHAR(30) NOT NULL DEFAULT 'active',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    created_by BIGINT REFERENCES users_web_checkin(id),

    last_login_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_users_web_checkin_status
    CHECK (status IN ('active', 'inactive', 'banned', 'removed'))
);

CREATE INDEX IF NOT EXISTS idx_users_web_checkin_username
ON users_web_checkin(username);

CREATE INDEX IF NOT EXISTS idx_users_web_checkin_role_id
ON users_web_checkin(role_id);

CREATE INDEX IF NOT EXISTS idx_users_web_checkin_status
ON users_web_checkin(status);

-- =========================================================
-- 3. Staff Profiles
-- =========================================================

CREATE TABLE IF NOT EXISTS staff_profiles_web_checkin (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT UNIQUE NOT NULL REFERENCES users_web_checkin(id) ON DELETE CASCADE,

    employee_code VARCHAR(100),
    job_title VARCHAR(150),
    department VARCHAR(150),

    default_timezone VARCHAR(100) NOT NULL DEFAULT 'America/Chicago',

    joining_date DATE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_staff_profiles_web_checkin_user_id
ON staff_profiles_web_checkin(user_id);

CREATE INDEX IF NOT EXISTS idx_staff_profiles_web_checkin_employee_code
ON staff_profiles_web_checkin(employee_code);

-- =========================================================
-- 4. Clinics - future use
-- =========================================================

CREATE TABLE IF NOT EXISTS clinics_web_checkin (
    id BIGSERIAL PRIMARY KEY,

    clinic_name VARCHAR(150) NOT NULL,
    address_line_1 VARCHAR(255),
    address_line_2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100) DEFAULT 'USA',

    timezone VARCHAR(100) NOT NULL DEFAULT 'America/Chicago',

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_clinics_web_checkin_clinic_name
ON clinics_web_checkin(clinic_name);

-- =========================================================
-- 5. User Clinics - future use
-- =========================================================

CREATE TABLE IF NOT EXISTS user_clinics_web_checkin (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL REFERENCES users_web_checkin(id) ON DELETE CASCADE,
    clinic_id BIGINT NOT NULL REFERENCES clinics_web_checkin(id) ON DELETE CASCADE,

    is_primary BOOLEAN NOT NULL DEFAULT FALSE,

    assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_user_clinic_web_checkin UNIQUE (user_id, clinic_id)
);

CREATE INDEX IF NOT EXISTS idx_user_clinics_web_checkin_user_id
ON user_clinics_web_checkin(user_id);

CREATE INDEX IF NOT EXISTS idx_user_clinics_web_checkin_clinic_id
ON user_clinics_web_checkin(clinic_id);

-- =========================================================
-- 6. Attendance Sessions
-- One row = one check-in/check-out work session
-- =========================================================

CREATE TABLE IF NOT EXISTS attendance_sessions_web_checkin (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL REFERENCES users_web_checkin(id) ON DELETE CASCADE,

    check_in_at_utc TIMESTAMPTZ NOT NULL,
    check_out_at_utc TIMESTAMPTZ,

    display_timezone VARCHAR(100) NOT NULL DEFAULT 'America/Chicago',

    total_minutes INTEGER,

    status VARCHAR(30) NOT NULL DEFAULT 'open',

    check_in_source VARCHAR(50) NOT NULL DEFAULT 'web',
    check_out_source VARCHAR(50),

    check_in_ip VARCHAR(50),
    check_out_ip VARCHAR(50),

    check_in_user_agent TEXT,
    check_out_user_agent TEXT,

    notes TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_attendance_sessions_web_checkin_status
    CHECK (status IN ('open', 'closed', 'incomplete', 'admin_adjusted', 'voided'))
);

CREATE INDEX IF NOT EXISTS idx_attendance_sessions_web_checkin_user_id
ON attendance_sessions_web_checkin(user_id);

CREATE INDEX IF NOT EXISTS idx_attendance_sessions_web_checkin_status
ON attendance_sessions_web_checkin(status);

CREATE INDEX IF NOT EXISTS idx_attendance_sessions_web_checkin_check_in
ON attendance_sessions_web_checkin(check_in_at_utc);

-- Prevent multiple open sessions for same user
CREATE UNIQUE INDEX IF NOT EXISTS uq_one_open_session_per_user_web_checkin
ON attendance_sessions_web_checkin(user_id)
WHERE status = 'open' AND check_out_at_utc IS NULL;

-- =========================================================
-- 7. Attendance Events
-- Raw log of every check-in/check-out event
-- =========================================================

CREATE TABLE IF NOT EXISTS attendance_events_web_checkin (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL REFERENCES users_web_checkin(id) ON DELETE CASCADE,
    attendance_session_id BIGINT REFERENCES attendance_sessions_web_checkin(id) ON DELETE SET NULL,

    event_type VARCHAR(50) NOT NULL,
    event_time_utc TIMESTAMPTZ NOT NULL,

    display_timezone VARCHAR(100) NOT NULL DEFAULT 'America/Chicago',

    source VARCHAR(50) NOT NULL DEFAULT 'web',

    ip_address VARCHAR(50),
    user_agent TEXT,

    metadata_json JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_attendance_events_web_checkin_event_type
    CHECK (event_type IN ('check_in', 'check_out', 'admin_adjustment', 'auto_close', 'void'))
);

CREATE INDEX IF NOT EXISTS idx_attendance_events_web_checkin_user_id
ON attendance_events_web_checkin(user_id);

CREATE INDEX IF NOT EXISTS idx_attendance_events_web_checkin_session_id
ON attendance_events_web_checkin(attendance_session_id);

CREATE INDEX IF NOT EXISTS idx_attendance_events_web_checkin_event_type
ON attendance_events_web_checkin(event_type);

CREATE INDEX IF NOT EXISTS idx_attendance_events_web_checkin_event_time
ON attendance_events_web_checkin(event_time_utc);

-- =========================================================
-- 8. Login Sessions
-- =========================================================

CREATE TABLE IF NOT EXISTS login_sessions_web_checkin (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL REFERENCES users_web_checkin(id) ON DELETE CASCADE,

    token_id VARCHAR(255),

    login_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    logout_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,

    ip_address VARCHAR(50),
    user_agent TEXT,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_login_sessions_web_checkin_user_id
ON login_sessions_web_checkin(user_id);

CREATE INDEX IF NOT EXISTS idx_login_sessions_web_checkin_token_id
ON login_sessions_web_checkin(token_id);

-- =========================================================
-- 9. Audit Logs
-- =========================================================

CREATE TABLE IF NOT EXISTS audit_logs_web_checkin (
    id BIGSERIAL PRIMARY KEY,

    actor_user_id BIGINT,
    target_user_id BIGINT,

    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100),
    entity_id BIGINT,

    old_value JSONB,
    new_value JSONB,

    ip_address VARCHAR(50),
    user_agent TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_web_checkin_actor_user_id
ON audit_logs_web_checkin(actor_user_id);

CREATE INDEX IF NOT EXISTS idx_audit_logs_web_checkin_target_user_id
ON audit_logs_web_checkin(target_user_id);

CREATE INDEX IF NOT EXISTS idx_audit_logs_web_checkin_action
ON audit_logs_web_checkin(action);

CREATE INDEX IF NOT EXISTS idx_audit_logs_web_checkin_created_at
ON audit_logs_web_checkin(created_at);

-- =========================================================
-- 10. Attendance Adjustments - future use
-- =========================================================

CREATE TABLE IF NOT EXISTS attendance_adjustments_web_checkin (
    id BIGSERIAL PRIMARY KEY,

    attendance_session_id BIGINT NOT NULL REFERENCES attendance_sessions_web_checkin(id) ON DELETE CASCADE,

    adjusted_by BIGINT REFERENCES users_web_checkin(id),

    old_check_in_at_utc TIMESTAMPTZ,
    old_check_out_at_utc TIMESTAMPTZ,

    new_check_in_at_utc TIMESTAMPTZ,
    new_check_out_at_utc TIMESTAMPTZ,

    old_total_minutes INTEGER,
    new_total_minutes INTEGER,

    reason TEXT,

    approved_by BIGINT REFERENCES users_web_checkin(id),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_attendance_adjustments_web_checkin_session_id
ON attendance_adjustments_web_checkin(attendance_session_id);

CREATE INDEX IF NOT EXISTS idx_attendance_adjustments_web_checkin_adjusted_by
ON attendance_adjustments_web_checkin(adjusted_by);

-- =========================================================
-- 11. Password Reset Tokens - future use
-- =========================================================

CREATE TABLE IF NOT EXISTS password_reset_tokens_web_checkin (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL REFERENCES users_web_checkin(id) ON DELETE CASCADE,

    token_hash TEXT NOT NULL,

    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_web_checkin_user_id
ON password_reset_tokens_web_checkin(user_id);

CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_web_checkin_token_hash
ON password_reset_tokens_web_checkin(token_hash);