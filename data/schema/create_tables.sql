-- Construction Check Database Schema
-- PostgreSQL DDL Script
-- Date: 2025-11-30
-- Builder: Carlos Gorricho

-- Drop existing tables (in correct order due to foreign keys)
DROP TABLE IF EXISTS activities CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS milestones CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS estimates CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS expertise CASCADE;
DROP TABLE IF EXISTS estimators CASCADE;
DROP TABLE IF EXISTS businesses CASCADE;
DROP TABLE IF EXISTS platform_metrics CASCADE;
DROP TABLE IF EXISTS project_types_lookup CASCADE;
DROP TABLE IF EXISTS certifications_lookup CASCADE;

-- ============================================================================
-- CORE ENTITIES
-- ============================================================================

-- 1. BUSINESSES
CREATE TABLE businesses (
    business_id         VARCHAR(36) PRIMARY KEY,
    company_name        VARCHAR(255) NOT NULL,
    industry_sector     VARCHAR(100),
    business_type       VARCHAR(50),
    street_address      VARCHAR(255),
    city                VARCHAR(100),
    state               VARCHAR(2),
    zip_code            VARCHAR(10),
    country             VARCHAR(3) DEFAULT 'USA',
    company_size        VARCHAR(50),
    annual_revenue      DECIMAL(15,2),
    years_in_business   INTEGER,
    registration_date   DATE NOT NULL,
    account_status      VARCHAR(20) DEFAULT 'active',
    verification_status VARCHAR(20) DEFAULT 'pending',
    subscription_tier   VARCHAR(20) DEFAULT 'basic',
    primary_contact     VARCHAR(255),
    email               VARCHAR(255) UNIQUE NOT NULL,
    phone               VARCHAR(20),
    total_projects_posted    INTEGER DEFAULT 0,
    total_projects_completed INTEGER DEFAULT 0,
    average_project_value    DECIMAL(15,2),
    reputation_score         DECIMAL(3,2) DEFAULT 5.00,
    total_reviews_received   INTEGER DEFAULT 0,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login          TIMESTAMP
);

CREATE INDEX idx_businesses_location ON businesses(city, state);
CREATE INDEX idx_businesses_sector ON businesses(industry_sector);
CREATE INDEX idx_businesses_status ON businesses(account_status, verification_status);

-- 2. ESTIMATORS
CREATE TABLE estimators (
    estimator_id        VARCHAR(36) PRIMARY KEY,
    first_name          VARCHAR(100) NOT NULL,
    last_name           VARCHAR(100) NOT NULL,
    display_name        VARCHAR(200),
    profile_headline    VARCHAR(255),
    bio                 TEXT,
    estimator_type      VARCHAR(20) NOT NULL,
    city                VARCHAR(100),
    state               VARCHAR(2),
    zip_code            VARCHAR(10),
    country             VARCHAR(3) DEFAULT 'USA',
    willing_to_travel   BOOLEAN DEFAULT FALSE,
    remote_available    BOOLEAN DEFAULT TRUE,
    years_experience    INTEGER,
    education_level     VARCHAR(50),
    hourly_rate         DECIMAL(10,2),
    minimum_project_fee DECIMAL(10,2),
    currency            VARCHAR(3) DEFAULT 'USD',
    availability_status VARCHAR(20) DEFAULT 'available',
    max_concurrent_projects INTEGER DEFAULT 3,
    current_project_count   INTEGER DEFAULT 0,
    registration_date   DATE NOT NULL,
    account_status      VARCHAR(20) DEFAULT 'active',
    verification_status VARCHAR(20) DEFAULT 'pending',
    background_check    BOOLEAN DEFAULT FALSE,
    insurance_verified  BOOLEAN DEFAULT FALSE,
    email               VARCHAR(255) UNIQUE NOT NULL,
    phone               VARCHAR(20),
    linkedin_url        VARCHAR(255),
    website_url         VARCHAR(255),
    total_estimates_delivered    INTEGER DEFAULT 0,
    total_estimates_accepted     INTEGER DEFAULT 0,
    total_estimates_rejected     INTEGER DEFAULT 0,
    win_rate                     DECIMAL(5,2) DEFAULT 0.00,
    average_turnaround_hours     DECIMAL(8,2),
    average_response_hours       DECIMAL(8,2),
    estimate_accuracy_rate       DECIMAL(5,2),
    client_satisfaction_score    DECIMAL(3,2) DEFAULT 5.00,
    total_reviews_received       INTEGER DEFAULT 0,
    repeat_client_rate           DECIMAL(5,2) DEFAULT 0.00,
    diversity_classification     VARCHAR(50),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login          TIMESTAMP,
    last_active         TIMESTAMP
);

CREATE INDEX idx_estimators_type ON estimators(estimator_type);
CREATE INDEX idx_estimators_location ON estimators(city, state);
CREATE INDEX idx_estimators_availability ON estimators(availability_status);
CREATE INDEX idx_estimators_verification ON estimators(verification_status, background_check);

-- 3. EXPERTISE
CREATE TABLE expertise (
    expertise_id        VARCHAR(36) PRIMARY KEY,
    estimator_id        VARCHAR(36) NOT NULL,
    specialization_type VARCHAR(50) NOT NULL,
    project_types       JSONB,
    certification_name  VARCHAR(255),
    certification_number VARCHAR(100),
    issuing_organization VARCHAR(255),
    issue_date          DATE,
    expiry_date         DATE,
    software_proficiency JSONB,
    years_in_specialty  INTEGER,
    verified            BOOLEAN DEFAULT FALSE,
    verification_date   DATE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (estimator_id) REFERENCES estimators(estimator_id) ON DELETE CASCADE
);

CREATE INDEX idx_expertise_estimator ON expertise(estimator_id);
CREATE INDEX idx_expertise_specialization ON expertise(specialization_type);

-- 4. PROJECTS
CREATE TABLE projects (
    project_id          VARCHAR(36) PRIMARY KEY,
    business_id         VARCHAR(36) NOT NULL,
    matched_estimator_id VARCHAR(36),
    project_title       VARCHAR(255) NOT NULL,
    project_description TEXT,
    project_type        VARCHAR(100),
    project_subtype     VARCHAR(100),
    project_city        VARCHAR(100),
    project_state       VARCHAR(2),
    project_zip         VARCHAR(10),
    project_country     VARCHAR(3) DEFAULT 'USA',
    square_footage      INTEGER,
    number_of_units     INTEGER,
    number_of_stories   INTEGER,
    estimated_budget_min DECIMAL(15,2),
    estimated_budget_max DECIMAL(15,2),
    desired_start_date  DATE,
    desired_completion_date DATE,
    estimate_needed_by  DATE NOT NULL,
    status              VARCHAR(20) DEFAULT 'posted',
    posted_date         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    matched_date        TIMESTAMP,
    estimate_delivered_date TIMESTAMP,
    project_start_date  DATE,
    project_completion_date DATE,
    number_of_bids      INTEGER DEFAULT 0,
    bid_deadline        TIMESTAMP,
    final_estimated_cost DECIMAL(15,2),
    actual_cost         DECIMAL(15,2),
    cost_variance_percent DECIMAL(6,2),
    insurance_required  BOOLEAN DEFAULT TRUE,
    bond_required       BOOLEAN DEFAULT FALSE,
    security_clearance  BOOLEAN DEFAULT FALSE,
    prevailing_wage     BOOLEAN DEFAULT FALSE,
    urgency_level       VARCHAR(20) DEFAULT 'normal',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_id) REFERENCES businesses(business_id) ON DELETE CASCADE,
    FOREIGN KEY (matched_estimator_id) REFERENCES estimators(estimator_id) ON DELETE SET NULL
);

CREATE INDEX idx_projects_business ON projects(business_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_type ON projects(project_type, project_subtype);
CREATE INDEX idx_projects_location ON projects(project_state, project_city);
CREATE INDEX idx_projects_posted_date ON projects(posted_date);
CREATE INDEX idx_projects_urgency ON projects(urgency_level, estimate_needed_by);

-- 5. ESTIMATES
CREATE TABLE estimates (
    estimate_id         VARCHAR(36) PRIMARY KEY,
    project_id          VARCHAR(36) NOT NULL,
    estimator_id        VARCHAR(36) NOT NULL,
    estimated_total_cost DECIMAL(15,2) NOT NULL,
    labor_cost          DECIMAL(15,2),
    materials_cost      DECIMAL(15,2),
    equipment_cost      DECIMAL(15,2),
    subcontractor_cost  DECIMAL(15,2),
    overhead_cost       DECIMAL(15,2),
    profit_margin       DECIMAL(15,2),
    contingency_percent DECIMAL(5,2),
    contingency_amount  DECIMAL(15,2),
    estimated_duration_days INTEGER,
    estimated_start_date    DATE,
    estimated_completion_date DATE,
    estimation_method   VARCHAR(50),
    confidence_level    VARCHAR(20),
    assumptions         TEXT,
    exclusions          TEXT,
    notes               TEXT,
    status              VARCHAR(20) DEFAULT 'pending',
    submitted_date      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_date       TIMESTAMP,
    accepted_date       TIMESTAMP,
    detailed_breakdown_url VARCHAR(500),
    supporting_docs_urls   JSONB,
    actual_cost         DECIMAL(15,2),
    variance_amount     DECIMAL(15,2),
    variance_percent    DECIMAL(6,2),
    accuracy_rating     VARCHAR(20),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (estimator_id) REFERENCES estimators(estimator_id) ON DELETE CASCADE,
    UNIQUE (project_id, estimator_id)
);

CREATE INDEX idx_estimates_project ON estimates(project_id);
CREATE INDEX idx_estimates_estimator ON estimates(estimator_id);
CREATE INDEX idx_estimates_status ON estimates(status);
CREATE INDEX idx_estimates_submitted_date ON estimates(submitted_date);

-- 6. REVIEWS
CREATE TABLE reviews (
    review_id           VARCHAR(36) PRIMARY KEY,
    project_id          VARCHAR(36) NOT NULL,
    reviewer_id         VARCHAR(36) NOT NULL,
    reviewer_type       VARCHAR(20) NOT NULL,
    reviewee_id         VARCHAR(36) NOT NULL,
    reviewee_type       VARCHAR(20) NOT NULL,
    overall_rating      DECIMAL(2,1) NOT NULL CHECK (overall_rating BETWEEN 1.0 AND 5.0),
    communication_rating DECIMAL(2,1) CHECK (communication_rating BETWEEN 1.0 AND 5.0),
    professionalism_rating DECIMAL(2,1) CHECK (professionalism_rating BETWEEN 1.0 AND 5.0),
    accuracy_rating     DECIMAL(2,1) CHECK (accuracy_rating BETWEEN 1.0 AND 5.0),
    timeliness_rating   DECIMAL(2,1) CHECK (timeliness_rating BETWEEN 1.0 AND 5.0),
    value_rating        DECIMAL(2,1) CHECK (value_rating BETWEEN 1.0 AND 5.0),
    review_title        VARCHAR(255),
    review_text         TEXT,
    would_recommend     BOOLEAN,
    would_work_again    BOOLEAN,
    verified_review     BOOLEAN DEFAULT FALSE,
    status              VARCHAR(20) DEFAULT 'published',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);

CREATE INDEX idx_reviews_reviewee ON reviews(reviewee_id, reviewee_type);
CREATE INDEX idx_reviews_reviewer ON reviews(reviewer_id, reviewer_type);
CREATE INDEX idx_reviews_project ON reviews(project_id);
CREATE INDEX idx_reviews_rating ON reviews(overall_rating);

-- 7. MILESTONES
CREATE TABLE milestones (
    milestone_id        VARCHAR(36) PRIMARY KEY,
    project_id          VARCHAR(36) NOT NULL,
    milestone_name      VARCHAR(255) NOT NULL,
    milestone_description TEXT,
    sequence_order      INTEGER,
    planned_start_date  DATE,
    planned_end_date    DATE,
    actual_start_date   DATE,
    actual_end_date     DATE,
    planned_cost        DECIMAL(15,2),
    actual_cost         DECIMAL(15,2),
    status              VARCHAR(20) DEFAULT 'not_started',
    completion_percent  INTEGER DEFAULT 0 CHECK (completion_percent BETWEEN 0 AND 100),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);

CREATE INDEX idx_milestones_project ON milestones(project_id);
CREATE INDEX idx_milestones_status ON milestones(status);

-- 8. MESSAGES
CREATE TABLE messages (
    message_id          VARCHAR(36) PRIMARY KEY,
    project_id          VARCHAR(36),
    sender_id           VARCHAR(36) NOT NULL,
    sender_type         VARCHAR(20) NOT NULL,
    recipient_id        VARCHAR(36) NOT NULL,
    recipient_type      VARCHAR(20) NOT NULL,
    thread_id           VARCHAR(36),
    parent_message_id   VARCHAR(36),
    subject             VARCHAR(255),
    message_body        TEXT NOT NULL,
    attachments         JSONB,
    is_read             BOOLEAN DEFAULT FALSE,
    read_at             TIMESTAMP,
    is_archived         BOOLEAN DEFAULT FALSE,
    is_flagged          BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE SET NULL,
    FOREIGN KEY (parent_message_id) REFERENCES messages(message_id) ON DELETE CASCADE
);

CREATE INDEX idx_messages_thread ON messages(thread_id);
CREATE INDEX idx_messages_project ON messages(project_id);
CREATE INDEX idx_messages_sender ON messages(sender_id, sender_type);
CREATE INDEX idx_messages_recipient ON messages(recipient_id, recipient_type);
CREATE INDEX idx_messages_unread ON messages(recipient_id, is_read);

-- 9. ACTIVITIES
CREATE TABLE activities (
    activity_id         VARCHAR(36) PRIMARY KEY,
    user_id             VARCHAR(36) NOT NULL,
    user_type           VARCHAR(20) NOT NULL,
    activity_type       VARCHAR(50) NOT NULL,
    activity_category   VARCHAR(50),
    related_project_id  VARCHAR(36),
    related_estimate_id VARCHAR(36),
    activity_data       JSONB,
    session_id          VARCHAR(36),
    ip_address          VARCHAR(45),
    user_agent          VARCHAR(500),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_activities_user ON activities(user_id, user_type);
CREATE INDEX idx_activities_type ON activities(activity_type);
CREATE INDEX idx_activities_created_at ON activities(created_at);
CREATE INDEX idx_activities_session ON activities(session_id);

-- 10. PLATFORM METRICS
CREATE TABLE platform_metrics (
    metric_id           VARCHAR(36) PRIMARY KEY,
    date                DATE NOT NULL,
    period_type         VARCHAR(20) NOT NULL,
    total_businesses    INTEGER DEFAULT 0,
    active_businesses   INTEGER DEFAULT 0,
    new_businesses      INTEGER DEFAULT 0,
    total_estimators    INTEGER DEFAULT 0,
    active_estimators   INTEGER DEFAULT 0,
    new_estimators      INTEGER DEFAULT 0,
    projects_posted     INTEGER DEFAULT 0,
    projects_matched    INTEGER DEFAULT 0,
    projects_completed  INTEGER DEFAULT 0,
    projects_cancelled  INTEGER DEFAULT 0,
    estimates_submitted INTEGER DEFAULT 0,
    estimates_accepted  INTEGER DEFAULT 0,
    average_bids_per_project DECIMAL(5,2),
    total_project_value DECIMAL(15,2) DEFAULT 0.00,
    average_project_value DECIMAL(15,2) DEFAULT 0.00,
    total_estimate_value DECIMAL(15,2) DEFAULT 0.00,
    average_match_time_hours DECIMAL(8,2),
    average_estimate_turnaround_hours DECIMAL(8,2),
    average_estimate_accuracy DECIMAL(5,2),
    total_messages_sent INTEGER DEFAULT 0,
    total_reviews_posted INTEGER DEFAULT 0,
    average_satisfaction_score DECIMAL(3,2),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (date, period_type)
);

CREATE INDEX idx_platform_metrics_date_period ON platform_metrics(date, period_type);

-- ============================================================================
-- LOOKUP/REFERENCE TABLES
-- ============================================================================

-- 11. PROJECT TYPES LOOKUP
CREATE TABLE project_types_lookup (
    type_id             VARCHAR(36) PRIMARY KEY,
    type_name           VARCHAR(100) UNIQUE NOT NULL,
    category            VARCHAR(50),
    description         TEXT,
    typical_size_range  VARCHAR(100),
    active              BOOLEAN DEFAULT TRUE
);

-- 12. CERTIFICATIONS LOOKUP
CREATE TABLE certifications_lookup (
    certification_id    VARCHAR(36) PRIMARY KEY,
    certification_code  VARCHAR(20) UNIQUE NOT NULL,
    certification_name  VARCHAR(255) NOT NULL,
    issuing_org         VARCHAR(255),
    description         TEXT,
    website_url         VARCHAR(255),
    active              BOOLEAN DEFAULT TRUE
);

-- ============================================================================
-- GRANT PERMISSIONS (adjust as needed)
-- ============================================================================

-- Example: GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ccheck_app_user;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
