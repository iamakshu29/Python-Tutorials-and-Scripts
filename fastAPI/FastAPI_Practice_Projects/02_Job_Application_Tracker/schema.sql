CREATE TYPE user_role AS ENUM (
    'Admin',
    'User'
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,

    email VARCHAR NOT NULL UNIQUE,

    -- NULL allowed for Google OAuth users
    hashed_password VARCHAR,

    google_id VARCHAR UNIQUE,

    role user_role NOT NULL,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

---------------------------------------------------------------------------

CREATE TYPE application_status AS ENUM (
    'Applied',
    'Interview',
    'Offer',
    'Rejected',
    'Ghosted'
);

CREATE TYPE role_status AS ENUM (
    'Devops',
    'Tester',
    'Developer'
);

CREATE TABLE applications (
    id SERIAL PRIMARY KEY,

    user_id INTEGER NOT NULL,

    company VARCHAR NOT NULL,
    role_title role_status NOT NULL,
    job_url VARCHAR,

    status application_status NOT NULL,

    applied_date DATE NOT NULL DEFAULT CURRENT_DATE,

    notes TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_applications_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
);