-- Supabase PostgreSQL schema and functions for logbook
-- This script is idempotent where practical and aligns table/function references.

SET TIME ZONE 'Asia/Manila';

-- =============================
-- TABLES
-- =============================

CREATE TABLE IF NOT EXISTS role (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS person (
    person_id SERIAL PRIMARY KEY,
    lastname VARCHAR(100) NOT NULL,
    firstname VARCHAR(100) NOT NULL,
    middle_initial VARCHAR(5),
    suffix VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role_id INT NOT NULL,
    person_id INT NOT NULL,
    profile_pic TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_tempPassword BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_users_role FOREIGN KEY (role_id)
        REFERENCES role(role_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_users_person FOREIGN KEY (person_id)
        REFERENCES person(person_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS guest (
    guest_id SERIAL PRIMARY KEY,
    lastname VARCHAR(100) NOT NULL,
    firstname VARCHAR(100) NOT NULL,
    middle_initial VARCHAR(5),
    suffix VARCHAR(10),
    contact_number VARCHAR(20),
    email VARCHAR(150)
);

CREATE TABLE IF NOT EXISTS visitor_company (
    company_id SERIAL PRIMARY KEY,
    company_name VARCHAR(150) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS employee (
    contact_id SERIAL PRIMARY KEY,
    full_name VARCHAR(150) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS visit_purpose (
    purpose_id SERIAL PRIMARY KEY,
    purpose_name VARCHAR(150) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS visit_log (
    visit_id SERIAL PRIMARY KEY,
    date_of_visit DATE NOT NULL DEFAULT CURRENT_DATE,
    time_in TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    time_out TIMESTAMPTZ,
    guest_id INT NOT NULL,
    company_id INT NOT NULL,
    contact_id INT NOT NULL,
    purpose_id INT NOT NULL,
    user_id INT NOT NULL,
    CONSTRAINT fk_visit_guest FOREIGN KEY (guest_id)
        REFERENCES guest(guest_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_visit_company FOREIGN KEY (company_id)
        REFERENCES visitor_company(company_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_visit_contact FOREIGN KEY (contact_id)
        REFERENCES employee(contact_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_visit_purpose FOREIGN KEY (purpose_id)
        REFERENCES visit_purpose(purpose_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_visit_user FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE RESTRICT
);

-- =============================
-- SEED DATA
-- =============================

INSERT INTO role (role_name) VALUES
('admin'),
('guard')
ON CONFLICT (role_name) DO NOTHING;

INSERT INTO visitor_company (company_name) VALUES
('Accenture'),
('PLDT'),
('Globe'),
('Personal')
ON CONFLICT (company_name) DO NOTHING;

INSERT INTO employee (full_name) VALUES
('Maria Santos'),
('Juan Dela Cruz'),
('Mark Reyes')
ON CONFLICT (full_name) DO NOTHING;

INSERT INTO visit_purpose (purpose_name) VALUES
('Meeting'),
('Interview'),
('Delivery'),
('Maintenance'),
('Training')
ON CONFLICT (purpose_name) DO NOTHING;

-- =============================
-- FUNCTIONS
-- =============================

CREATE OR REPLACE FUNCTION create_user_account(
    p_username VARCHAR,
    p_password_hash TEXT,
    p_role_id INT,
    p_lastname VARCHAR,
    p_firstname VARCHAR,
    p_middle_initial VARCHAR,
    p_suffix VARCHAR
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    new_person_id INT;
BEGIN
    INSERT INTO person(lastname, firstname, middle_initial, suffix)
    VALUES (p_lastname, p_firstname, p_middle_initial, p_suffix)
    RETURNING person_id INTO new_person_id;

    INSERT INTO users(
        username,
        password_hash,
        role_id,
        person_id,
        is_active,
        is_tempPassword
    )
    VALUES (
        p_username,
        p_password_hash,
        p_role_id,
        new_person_id,
        TRUE,
        TRUE
    );
END;
$$;

CREATE OR REPLACE FUNCTION login_user(
    p_username VARCHAR
)
RETURNS TABLE(
    user_id INT,
    username VARCHAR,
    password_hash TEXT,
    role_name VARCHAR,
    is_active BOOLEAN,
    is_tempPassword BOOLEAN
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        u.user_id,
        u.username,
        u.password_hash,
        r.role_name,
        u.is_active,
        u.is_tempPassword
    FROM users u
    JOIN role r ON u.role_id = r.role_id
    WHERE u.username = p_username;
END;
$$;

CREATE OR REPLACE FUNCTION change_user_password(
    p_user_id INT,
    p_new_password TEXT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE users
    SET password_hash = p_new_password,
        is_tempPassword = FALSE
    WHERE user_id = p_user_id;
END;
$$;

CREATE OR REPLACE FUNCTION create_guest_visit(
    -- Guest info
    p_lastname VARCHAR,
    p_firstname VARCHAR, 
    p_middle_initial VARCHAR,
    p_suffix VARCHAR,
    p_contact VARCHAR,
    p_email VARCHAR,

    -- Company
    p_company_name VARCHAR,

    -- Employee
    p_contact_name VARCHAR,

    -- Purpose
    p_purpose_name VARCHAR
)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    new_guest_id INT;
    new_company_id INT;
    new_contact_id INT;
    new_purpose_id INT;
    new_visit_id INT;
BEGIN

-- Insert guest
INSERT INTO guest(
    lastname,
    firstname,
    middle_initial,
    suffix,
    contact_number,
    email
)
VALUES (
    p_lastname,
    p_firstname,
    p_middle_initial,
    p_suffix,
    p_contact,
    p_email
)
RETURNING guest_id INTO new_guest_id;

-- Insert company (always new)
IF p_company_name IS NULL THEN
    RAISE EXCEPTION 'Company is required';
END IF;

INSERT INTO visitor_company(company_name)
VALUES (p_company_name)
RETURNING company_id INTO new_company_id;

-- Insert employee (always new)
IF p_contact_name IS NULL THEN
    RAISE EXCEPTION 'Employee is required';
END IF;

INSERT INTO employee(full_name)
VALUES (p_contact_name)
RETURNING contact_id INTO new_contact_id;

-- Insert purpose (always new)
IF p_purpose_name IS NULL THEN
    RAISE EXCEPTION 'Purpose is required';
END IF;

INSERT INTO visit_purpose(purpose_name)
VALUES (p_purpose_name)
RETURNING purpose_id INTO new_purpose_id;

--  Insert visit log
INSERT INTO visit_log(
    date_of_visit,
    time_in,
    guest_id,
    company_id,
    contact_id,
    purpose_id
)
VALUES(
    CURRENT_DATE,
    CURRENT_TIMESTAMP,
    new_guest_id,
    new_company_id,
    new_contact_id,
    new_purpose_id
)
RETURNING visit_id INTO new_visit_id;

--  Return visit_id
RETURN new_visit_id;

END;
$$;


CREATE OR REPLACE FUNCTION add_guest_timeout(
    p_visit_id INT,
    p_user_id INT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN

UPDATE visit_log
SET 
    time_out = CURRENT_TIMESTAMP,
    user_id = p_user_id
WHERE visit_id = p_visit_id
AND time_out IS NULL;

IF NOT FOUND THEN
    RAISE EXCEPTION 'Visit already timed out or does not exist';
END IF;

END;
$$;


CREATE OR REPLACE FUNCTION delete_guest_log(
    p_visit_id INT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM visit_log
    WHERE visit_id = p_visit_id;
END;
$$;

CREATE OR REPLACE FUNCTION view_guest_logs()
RETURNS TABLE(
    visit_id INT,
    guest_name TEXT,
    contact_number VARCHAR,
    company_name VARCHAR,
    contact_person VARCHAR,
    purpose_name VARCHAR,
    time_in TIMESTAMP,
    time_out TIMESTAMP
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        v.visit_id,
        g.firstname
        || CASE
            WHEN g.middle_initial IS NOT NULL AND g.middle_initial <> ''
            THEN ' ' || g.middle_initial || '.'
            ELSE ''
           END
        || ' ' || g.lastname
        || CASE
            WHEN g.suffix IS NOT NULL AND g.suffix <> ''
            THEN ' ' || g.suffix
            ELSE ''
           END AS guest_name,
        g.contact_number,
        vc.company_name,
        e.full_name,
        vp.purpose_name,
        v.time_in AT TIME ZONE 'Asia/Manila' AS time_in,
        v.time_out AT TIME ZONE 'Asia/Manila' AS time_out
    FROM visit_log v
    JOIN guest g ON v.guest_id = g.guest_id
    JOIN visitor_company vc ON v.company_id = vc.company_id
    JOIN employee e ON v.contact_id = e.contact_id
    JOIN visit_purpose vp ON v.purpose_id = vp.purpose_id
    ORDER BY v.time_in DESC;
END;
$$;

CREATE OR REPLACE FUNCTION generate_report_by_date(
    p_start DATE,
    p_end DATE
)
RETURNS TABLE(
    visit_id INT,
    guest_name TEXT,
    company_name VARCHAR,
    purpose_name VARCHAR,
    time_in TIMESTAMPTZ,
    time_out TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        v.visit_id,
        g.firstname || ' ' || g.lastname,
        vc.company_name,
        vp.purpose_name,
        v.time_in,
        v.time_out
    FROM visit_log v
    JOIN guest g ON v.guest_id = g.guest_id
    JOIN visitor_company vc ON v.company_id = vc.company_id
    JOIN visit_purpose vp ON v.purpose_id = vp.purpose_id
    WHERE v.date_of_visit BETWEEN p_start AND p_end
    ORDER BY v.time_in DESC;
END;
$$;

CREATE OR REPLACE FUNCTION update_user_account(
    p_user_id INT,
    p_username VARCHAR
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE users
    SET username = p_username
    WHERE user_id = p_user_id;
END;
$$;

CREATE OR REPLACE FUNCTION set_user_status(
    p_user_id INT,
    p_status BOOLEAN
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE users
    SET is_active = p_status
    WHERE user_id = p_user_id;
END;
$$;

CREATE OR REPLACE FUNCTION search_guest_logs(
    p_search TEXT
)
RETURNS TABLE(
    visit_id INT,
    guest_name TEXT,
    company_name VARCHAR,
    contact_person VARCHAR,
    contact_number VARCHAR,
    purpose_name VARCHAR,
    date_of_visit DATE,
    time_in TIMESTAMPTZ,
    time_out TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        v.visit_id,
        g.firstname
        || CASE
            WHEN g.middle_initial IS NOT NULL AND g.middle_initial <> ''
            THEN ' ' || g.middle_initial || '.'
            ELSE ''
           END
        || ' ' || g.lastname
        || CASE
            WHEN g.suffix IS NOT NULL AND g.suffix <> ''
            THEN ' ' || g.suffix
            ELSE ''
           END AS guest_name,
        vc.company_name,
        e.full_name AS contact_person,
        g.contact_number,
        vp.purpose_name,
        v.date_of_visit,
        v.time_in,
        v.time_out
    FROM visit_log v
    JOIN guest g ON v.guest_id = g.guest_id
    JOIN visitor_company vc ON v.company_id = vc.company_id
    JOIN employee e ON v.contact_id = e.contact_id
    JOIN visit_purpose vp ON v.purpose_id = vp.purpose_id
    WHERE
        g.firstname ILIKE '%' || p_search || '%'
        OR g.lastname ILIKE '%' || p_search || '%'
        OR COALESCE(g.middle_initial, '') ILIKE '%' || p_search || '%'
        OR COALESCE(g.suffix, '') ILIKE '%' || p_search || '%'
        OR vc.company_name ILIKE '%' || p_search || '%'
        OR e.full_name ILIKE '%' || p_search || '%'
        OR vp.purpose_name ILIKE '%' || p_search || '%'
    ORDER BY v.time_in DESC;
END;
$$;
