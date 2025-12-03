# Construction Check Database Schema Design
**Date**: 2025-11-30 23:00  
**Project**: Construction Check Dashboard Development  
**Builder**: Carlos Gorricho  
**Purpose**: Complete relational database schema for synthetic data generation

---

## Schema Overview

### Entity Relationship Diagram (Text Format)

```
┌─────────────────┐
│   businesses    │
└────────┬────────┘
         │ 1
         │
         │ N
┌────────▼────────┐      N ┌──────────────┐ 1     ┌──────────────┐
│    projects     │◄────────┤  estimates   │───────┤  estimators  │
└────────┬────────┘         └──────┬───────┘       └──────┬───────┘
         │ N                       │                      │
         │                         │ N                    │ 1
         │ 1                       │                      │
┌────────▼────────┐         ┌──────▼───────┐      ┌──────▼───────┐
│   milestones    │         │   reviews    │      │  expertise   │
└─────────────────┘         └──────────────┘      └──────────────┘

         ┌──────────────┐
         │   messages   │◄─── N:N between users
         └──────────────┘

         ┌──────────────┐
         │  activities  │◄─── Track all user actions
         └──────────────┘
```

---

## Core Entities

### 1. businesses

**Description**: Companies/organizations seeking cost estimating services

```sql
CREATE TABLE businesses (
    -- Primary Key
    business_id         VARCHAR(36) PRIMARY KEY,
    
    -- Business Information
    company_name        VARCHAR(255) NOT NULL,
    industry_sector     VARCHAR(100),  -- commercial, residential, infrastructure, industrial, mixed_use
    business_type       VARCHAR(50),   -- general_contractor, developer, owner, architect, engineer
    
    -- Location
    street_address      VARCHAR(255),
    city                VARCHAR(100),
    state               VARCHAR(2),
    zip_code            VARCHAR(10),
    country             VARCHAR(3) DEFAULT 'USA',
    
    -- Size & Scale
    company_size        VARCHAR(50),   -- small, medium, large, enterprise
    annual_revenue      DECIMAL(15,2),
    years_in_business   INTEGER,
    
    -- Platform Metrics
    registration_date   DATE NOT NULL,
    account_status      VARCHAR(20) DEFAULT 'active', -- active, suspended, closed
    verification_status VARCHAR(20) DEFAULT 'pending', -- pending, verified, rejected
    subscription_tier   VARCHAR(20) DEFAULT 'basic',   -- basic, professional, enterprise
    
    -- Contact
    primary_contact     VARCHAR(255),
    email               VARCHAR(255) UNIQUE NOT NULL,
    phone               VARCHAR(20),
    
    -- Reputation & Performance
    total_projects_posted    INTEGER DEFAULT 0,
    total_projects_completed INTEGER DEFAULT 0,
    average_project_value    DECIMAL(15,2),
    reputation_score         DECIMAL(3,2) DEFAULT 5.00, -- 1.00 to 5.00
    total_reviews_received   INTEGER DEFAULT 0,
    
    -- Metadata
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login          TIMESTAMP,
    
    -- Indexes
    INDEX idx_location (city, state),
    INDEX idx_sector (industry_sector),
    INDEX idx_status (account_status, verification_status)
);
```

---

### 2. estimators

**Description**: Consultants and freelance experts providing cost estimating services

```sql
CREATE TABLE estimators (
    -- Primary Key
    estimator_id        VARCHAR(36) PRIMARY KEY,
    
    -- Personal Information
    first_name          VARCHAR(100) NOT NULL,
    last_name           VARCHAR(100) NOT NULL,
    display_name        VARCHAR(200),
    profile_headline    VARCHAR(255),
    bio                 TEXT,
    
    -- Estimator Type
    estimator_type      VARCHAR(20) NOT NULL, -- consultant, freelance_expert
    
    -- Location
    city                VARCHAR(100),
    state               VARCHAR(2),
    zip_code            VARCHAR(10),
    country             VARCHAR(3) DEFAULT 'USA',
    willing_to_travel   BOOLEAN DEFAULT FALSE,
    remote_available    BOOLEAN DEFAULT TRUE,
    
    -- Professional Background
    years_experience    INTEGER,
    education_level     VARCHAR(50), -- bachelors, masters, phd, professional
    
    -- Pricing
    hourly_rate         DECIMAL(10,2),
    minimum_project_fee DECIMAL(10,2),
    currency            VARCHAR(3) DEFAULT 'USD',
    
    -- Availability
    availability_status VARCHAR(20) DEFAULT 'available', -- available, busy, unavailable
    max_concurrent_projects INTEGER DEFAULT 3,
    current_project_count   INTEGER DEFAULT 0,
    
    -- Platform Metrics
    registration_date   DATE NOT NULL,
    account_status      VARCHAR(20) DEFAULT 'active',
    verification_status VARCHAR(20) DEFAULT 'pending',
    background_check    BOOLEAN DEFAULT FALSE,
    insurance_verified  BOOLEAN DEFAULT FALSE,
    
    -- Contact
    email               VARCHAR(255) UNIQUE NOT NULL,
    phone               VARCHAR(20),
    linkedin_url        VARCHAR(255),
    website_url         VARCHAR(255),
    
    -- Performance Metrics
    total_estimates_delivered    INTEGER DEFAULT 0,
    total_estimates_accepted     INTEGER DEFAULT 0,
    total_estimates_rejected     INTEGER DEFAULT 0,
    win_rate                     DECIMAL(5,2) DEFAULT 0.00, -- percentage
    average_turnaround_hours     DECIMAL(8,2),
    average_response_hours       DECIMAL(8,2),
    estimate_accuracy_rate       DECIMAL(5,2), -- percentage (how close to actual)
    
    -- Reputation
    client_satisfaction_score    DECIMAL(3,2) DEFAULT 5.00,
    total_reviews_received       INTEGER DEFAULT 0,
    repeat_client_rate           DECIMAL(5,2) DEFAULT 0.00,
    
    -- Diversity Classification (for Construction Check's diverse network)
    diversity_classification     VARCHAR(50), -- minority_owned, women_owned, veteran_owned, lgbtq_owned, none
    
    -- Metadata
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login          TIMESTAMP,
    last_active         TIMESTAMP,
    
    -- Indexes
    INDEX idx_type (estimator_type),
    INDEX idx_location (city, state),
    INDEX idx_availability (availability_status),
    INDEX idx_verification (verification_status, background_check)
);
```

---

### 3. expertise

**Description**: Estimator specializations and certifications

```sql
CREATE TABLE expertise (
    -- Primary Key
    expertise_id        VARCHAR(36) PRIMARY KEY,
    
    -- Foreign Key
    estimator_id        VARCHAR(36) NOT NULL,
    
    -- Specialization
    specialization_type VARCHAR(50) NOT NULL, -- cost_estimating, quantity_surveying, value_engineering, forensic_estimating
    project_types       JSON, -- ["commercial", "residential", "infrastructure"]
    
    -- Certifications
    certification_name  VARCHAR(255), -- AACE, ASPE, CCP, etc.
    certification_number VARCHAR(100),
    issuing_organization VARCHAR(255),
    issue_date          DATE,
    expiry_date         DATE,
    
    -- Skills & Tools
    software_proficiency JSON, -- ["Sage Estimating", "Bluebeam", "PlanSwift"]
    years_in_specialty  INTEGER,
    
    -- Verification
    verified            BOOLEAN DEFAULT FALSE,
    verification_date   DATE,
    
    -- Metadata
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (estimator_id) REFERENCES estimators(estimator_id) ON DELETE CASCADE,
    INDEX idx_estimator (estimator_id),
    INDEX idx_specialization (specialization_type)
);
```

---

### 4. projects

**Description**: Construction projects posted by businesses

```sql
CREATE TABLE projects (
    -- Primary Key
    project_id          VARCHAR(36) PRIMARY KEY,
    
    -- Foreign Keys
    business_id         VARCHAR(36) NOT NULL,
    matched_estimator_id VARCHAR(36), -- NULL until matched
    
    -- Project Information
    project_title       VARCHAR(255) NOT NULL,
    project_description TEXT,
    project_type        VARCHAR(100), -- new_construction, renovation, addition, infrastructure, demolition
    project_subtype     VARCHAR(100), -- commercial_office, retail, residential_single, multi_family, etc.
    
    -- Location
    project_city        VARCHAR(100),
    project_state       VARCHAR(2),
    project_zip         VARCHAR(10),
    project_country     VARCHAR(3) DEFAULT 'USA',
    
    -- Scope & Size
    square_footage      INTEGER,
    number_of_units     INTEGER,
    number_of_stories   INTEGER,
    estimated_budget_min DECIMAL(15,2),
    estimated_budget_max DECIMAL(15,2),
    
    -- Timeline
    desired_start_date  DATE,
    desired_completion_date DATE,
    estimate_needed_by  DATE NOT NULL,
    
    -- Status Tracking
    status              VARCHAR(20) DEFAULT 'posted', -- posted, in_bidding, matched, estimate_in_progress, estimate_delivered, in_progress, completed, cancelled
    posted_date         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    matched_date        TIMESTAMP,
    estimate_delivered_date TIMESTAMP,
    project_start_date  DATE,
    project_completion_date DATE,
    
    -- Bidding
    number_of_bids      INTEGER DEFAULT 0,
    bid_deadline        TIMESTAMP,
    
    -- Cost Tracking (after project completion)
    final_estimated_cost DECIMAL(15,2), -- from accepted estimate
    actual_cost         DECIMAL(15,2),  -- actual project cost
    cost_variance_percent DECIMAL(6,2),  -- (actual - estimated) / estimated * 100
    
    -- Requirements
    insurance_required  BOOLEAN DEFAULT TRUE,
    bond_required       BOOLEAN DEFAULT FALSE,
    security_clearance  BOOLEAN DEFAULT FALSE,
    prevailing_wage     BOOLEAN DEFAULT FALSE,
    
    -- Urgency
    urgency_level       VARCHAR(20) DEFAULT 'normal', -- low, normal, high, urgent
    
    -- Metadata
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (business_id) REFERENCES businesses(business_id) ON DELETE CASCADE,
    FOREIGN KEY (matched_estimator_id) REFERENCES estimators(estimator_id) ON DELETE SET NULL,
    
    INDEX idx_business (business_id),
    INDEX idx_status (status),
    INDEX idx_type (project_type, project_subtype),
    INDEX idx_location (project_state, project_city),
    INDEX idx_posted_date (posted_date),
    INDEX idx_urgency (urgency_level, estimate_needed_by)
);
```

---

### 5. estimates

**Description**: Cost estimates submitted by estimators for projects

```sql
CREATE TABLE estimates (
    -- Primary Key
    estimate_id         VARCHAR(36) PRIMARY KEY,
    
    -- Foreign Keys
    project_id          VARCHAR(36) NOT NULL,
    estimator_id        VARCHAR(36) NOT NULL,
    
    -- Estimate Information
    estimated_total_cost DECIMAL(15,2) NOT NULL,
    
    -- Cost Breakdown
    labor_cost          DECIMAL(15,2),
    materials_cost      DECIMAL(15,2),
    equipment_cost      DECIMAL(15,2),
    subcontractor_cost  DECIMAL(15,2),
    overhead_cost       DECIMAL(15,2),
    profit_margin       DECIMAL(15,2),
    contingency_percent DECIMAL(5,2),
    contingency_amount  DECIMAL(15,2),
    
    -- Timeline Estimate
    estimated_duration_days INTEGER,
    estimated_start_date    DATE,
    estimated_completion_date DATE,
    
    -- Methodology
    estimation_method   VARCHAR(50), -- unit_cost, square_foot, assembly, detailed_takeoff
    confidence_level    VARCHAR(20), -- low, medium, high, very_high
    assumptions         TEXT,
    exclusions          TEXT,
    notes               TEXT,
    
    -- Status
    status              VARCHAR(20) DEFAULT 'pending', -- pending, accepted, rejected, withdrawn
    submitted_date      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_date       TIMESTAMP,
    accepted_date       TIMESTAMP,
    
    -- Documents
    detailed_breakdown_url VARCHAR(500), -- link to full estimate document
    supporting_docs_urls   JSON,         -- array of document URLs
    
    -- Accuracy Tracking (populated after project completion)
    actual_cost         DECIMAL(15,2),
    variance_amount     DECIMAL(15,2),
    variance_percent    DECIMAL(6,2),
    accuracy_rating     VARCHAR(20), -- excellent, good, fair, poor
    
    -- Metadata
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (estimator_id) REFERENCES estimators(estimator_id) ON DELETE CASCADE,
    
    INDEX idx_project (project_id),
    INDEX idx_estimator (estimator_id),
    INDEX idx_status (status),
    INDEX idx_submitted_date (submitted_date),
    
    UNIQUE KEY unique_estimate (project_id, estimator_id) -- one estimate per estimator per project
);
```

---

### 6. reviews

**Description**: Reviews and ratings between businesses and estimators

```sql
CREATE TABLE reviews (
    -- Primary Key
    review_id           VARCHAR(36) PRIMARY KEY,
    
    -- Relationships
    project_id          VARCHAR(36) NOT NULL,
    reviewer_id         VARCHAR(36) NOT NULL,  -- business_id or estimator_id
    reviewer_type       VARCHAR(20) NOT NULL,  -- business, estimator
    reviewee_id         VARCHAR(36) NOT NULL,  -- estimator_id or business_id
    reviewee_type       VARCHAR(20) NOT NULL,  -- estimator, business
    
    -- Rating (1-5 scale)
    overall_rating      DECIMAL(2,1) NOT NULL CHECK (overall_rating BETWEEN 1.0 AND 5.0),
    
    -- Sub-ratings
    communication_rating DECIMAL(2,1) CHECK (communication_rating BETWEEN 1.0 AND 5.0),
    professionalism_rating DECIMAL(2,1) CHECK (professionalism_rating BETWEEN 1.0 AND 5.0),
    accuracy_rating     DECIMAL(2,1) CHECK (accuracy_rating BETWEEN 1.0 AND 5.0), -- for estimators
    timeliness_rating   DECIMAL(2,1) CHECK (timeliness_rating BETWEEN 1.0 AND 5.0),
    value_rating        DECIMAL(2,1) CHECK (value_rating BETWEEN 1.0 AND 5.0),
    
    -- Review Content
    review_title        VARCHAR(255),
    review_text         TEXT,
    
    -- Recommendation
    would_recommend     BOOLEAN,
    would_work_again    BOOLEAN,
    
    -- Verification
    verified_review     BOOLEAN DEFAULT FALSE, -- verified that project actually happened
    
    -- Status
    status              VARCHAR(20) DEFAULT 'published', -- published, flagged, removed
    
    -- Metadata
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    INDEX idx_reviewee (reviewee_id, reviewee_type),
    INDEX idx_reviewer (reviewer_id, reviewer_type),
    INDEX idx_project (project_id),
    INDEX idx_rating (overall_rating)
);
```

---

### 7. milestones

**Description**: Project milestones and progress tracking

```sql
CREATE TABLE milestones (
    -- Primary Key
    milestone_id        VARCHAR(36) PRIMARY KEY,
    
    -- Foreign Key
    project_id          VARCHAR(36) NOT NULL,
    
    -- Milestone Information
    milestone_name      VARCHAR(255) NOT NULL,
    milestone_description TEXT,
    sequence_order      INTEGER,
    
    -- Dates
    planned_start_date  DATE,
    planned_end_date    DATE,
    actual_start_date   DATE,
    actual_end_date     DATE,
    
    -- Cost
    planned_cost        DECIMAL(15,2),
    actual_cost         DECIMAL(15,2),
    
    -- Status
    status              VARCHAR(20) DEFAULT 'not_started', -- not_started, in_progress, completed, delayed, cancelled
    completion_percent  INTEGER DEFAULT 0 CHECK (completion_percent BETWEEN 0 AND 100),
    
    -- Metadata
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    INDEX idx_project (project_id),
    INDEX idx_status (status)
);
```

---

### 8. messages

**Description**: Communication between businesses and estimators

```sql
CREATE TABLE messages (
    -- Primary Key
    message_id          VARCHAR(36) PRIMARY KEY,
    
    -- Relationships
    project_id          VARCHAR(36), -- nullable for general inquiries
    sender_id           VARCHAR(36) NOT NULL,
    sender_type         VARCHAR(20) NOT NULL, -- business, estimator
    recipient_id        VARCHAR(36) NOT NULL,
    recipient_type      VARCHAR(20) NOT NULL, -- business, estimator
    
    -- Thread Management
    thread_id           VARCHAR(36), -- groups related messages
    parent_message_id   VARCHAR(36), -- for replies
    
    -- Message Content
    subject             VARCHAR(255),
    message_body        TEXT NOT NULL,
    
    -- Attachments
    attachments         JSON, -- array of file URLs
    
    -- Status
    is_read             BOOLEAN DEFAULT FALSE,
    read_at             TIMESTAMP,
    is_archived         BOOLEAN DEFAULT FALSE,
    is_flagged          BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE SET NULL,
    FOREIGN KEY (parent_message_id) REFERENCES messages(message_id) ON DELETE CASCADE,
    
    INDEX idx_thread (thread_id),
    INDEX idx_project (project_id),
    INDEX idx_sender (sender_id, sender_type),
    INDEX idx_recipient (recipient_id, recipient_type),
    INDEX idx_unread (recipient_id, is_read)
);
```

---

### 9. activities

**Description**: User activity log for analytics and engagement tracking

```sql
CREATE TABLE activities (
    -- Primary Key
    activity_id         VARCHAR(36) PRIMARY KEY,
    
    -- User Information
    user_id             VARCHAR(36) NOT NULL,
    user_type           VARCHAR(20) NOT NULL, -- business, estimator
    
    -- Activity Details
    activity_type       VARCHAR(50) NOT NULL, -- login, search, view_project, submit_estimate, etc.
    activity_category   VARCHAR(50), -- engagement, transaction, profile, messaging
    
    -- Related Entities
    related_project_id  VARCHAR(36),
    related_estimate_id VARCHAR(36),
    
    -- Activity Data
    activity_data       JSON, -- flexible storage for activity-specific data
    
    -- Session
    session_id          VARCHAR(36),
    ip_address          VARCHAR(45),
    user_agent          VARCHAR(500),
    
    -- Metadata
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user (user_id, user_type),
    INDEX idx_activity_type (activity_type),
    INDEX idx_created_at (created_at),
    INDEX idx_session (session_id)
);
```

---

### 10. platform_metrics

**Description**: Aggregated platform-level KPIs and metrics (for dashboard performance)

```sql
CREATE TABLE platform_metrics (
    -- Primary Key
    metric_id           VARCHAR(36) PRIMARY KEY,
    
    -- Time Period
    date                DATE NOT NULL,
    period_type         VARCHAR(20) NOT NULL, -- daily, weekly, monthly, quarterly, yearly
    
    -- User Metrics
    total_businesses    INTEGER DEFAULT 0,
    active_businesses   INTEGER DEFAULT 0,
    new_businesses      INTEGER DEFAULT 0,
    total_estimators    INTEGER DEFAULT 0,
    active_estimators   INTEGER DEFAULT 0,
    new_estimators      INTEGER DEFAULT 0,
    
    -- Project Metrics
    projects_posted     INTEGER DEFAULT 0,
    projects_matched    INTEGER DEFAULT 0,
    projects_completed  INTEGER DEFAULT 0,
    projects_cancelled  INTEGER DEFAULT 0,
    
    -- Estimate Metrics
    estimates_submitted INTEGER DEFAULT 0,
    estimates_accepted  INTEGER DEFAULT 0,
    average_bids_per_project DECIMAL(5,2),
    
    -- Financial Metrics
    total_project_value DECIMAL(15,2) DEFAULT 0.00,
    average_project_value DECIMAL(15,2) DEFAULT 0.00,
    total_estimate_value DECIMAL(15,2) DEFAULT 0.00,
    
    -- Performance Metrics
    average_match_time_hours DECIMAL(8,2),
    average_estimate_turnaround_hours DECIMAL(8,2),
    average_estimate_accuracy DECIMAL(5,2),
    
    -- Engagement Metrics
    total_messages_sent INTEGER DEFAULT 0,
    total_reviews_posted INTEGER DEFAULT 0,
    average_satisfaction_score DECIMAL(3,2),
    
    -- Metadata
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_date_period (date, period_type),
    UNIQUE KEY unique_metric (date, period_type)
);
```

---

## Lookup/Reference Tables

### 11. project_types_lookup

```sql
CREATE TABLE project_types_lookup (
    type_id             VARCHAR(36) PRIMARY KEY,
    type_name           VARCHAR(100) UNIQUE NOT NULL,
    category            VARCHAR(50), -- commercial, residential, infrastructure, industrial
    description         TEXT,
    typical_size_range  VARCHAR(100),
    active              BOOLEAN DEFAULT TRUE
);
```

### 12. certifications_lookup

```sql
CREATE TABLE certifications_lookup (
    certification_id    VARCHAR(36) PRIMARY KEY,
    certification_code  VARCHAR(20) UNIQUE NOT NULL,
    certification_name  VARCHAR(255) NOT NULL,
    issuing_org         VARCHAR(255),
    description         TEXT,
    website_url         VARCHAR(255),
    active              BOOLEAN DEFAULT TRUE
);
```

---

## Data Volume Targets

Based on research requirements:

| Entity | Target Records | Notes |
|--------|---------------|-------|
| businesses | 150 | Mix of small to enterprise |
| estimators | 350 | 100 consultants, 250 freelancers |
| expertise | 500-700 | Multiple per estimator |
| projects | 800 | 12-24 months historical |
| estimates | 1,500 | ~2-3 per project average |
| reviews | 400 | ~50% of completed projects |
| milestones | 2,000 | ~2-5 per project |
| messages | 3,000 | Active communication |
| activities | 10,000+ | High-volume tracking |
| platform_metrics | 365-730 | Daily for 1-2 years |

---

## Data Integrity Rules

### Business Rules

1. **Estimate Submission**:
   - Estimator must be verified to submit estimates
   - Cannot submit estimate after project deadline
   - Only one estimate per estimator per project

2. **Project Matching**:
   - Project must be in 'in_bidding' status
   - Estimator must have submitted an estimate
   - Business accepts estimate → project status changes to 'matched'

3. **Reviews**:
   - Can only review after project reaches 'completed' status
   - Each party can only review once per project
   - Review must be within 90 days of project completion

4. **Cost Variance Calculation**:
   - Only populated when project status = 'completed'
   - Requires both estimated_cost and actual_cost
   - Formula: ((actual_cost - estimated_cost) / estimated_cost) * 100

5. **Reputation Scores**:
   - Recalculated on each new review
   - Average of all reviews weighted by recency
   - Cached in user table for performance

---

## Indexes Strategy

### Performance Optimization

1. **High-Traffic Queries**:
   - Dashboard data pulls (date ranges, aggregations)
   - Estimator search and filtering
   - Project discovery feeds
   - Message threads

2. **Composite Indexes**:
   - (user_id, user_type, created_at) for activity tracking
   - (project_id, status) for project queries
   - (estimator_id, availability_status) for matching

3. **Full-Text Indexes**:
   - project_description, project_title
   - estimator bio, profile_headline
   - review_text

---

## Data Privacy & Security

### PII Fields

Sensitive data requiring encryption/masking:
- email addresses
- phone numbers
- street addresses
- social security numbers (if added)
- payment information (if added)

### Access Control

- Business users: can only see their own projects and estimates
- Estimators: can see all projects, own estimates and reviews
- Admin: full access with audit trail

---

**Schema Status**: Design Complete  
**Next Steps**: 
1. Generate SQL DDL scripts
2. Create synthetic data generation scripts
3. Populate database with realistic data

**Builder**: Carlos Gorricho  
**Date**: 2025-11-30