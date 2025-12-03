#!/usr/bin/env python3
"""
Construction Check - Synthetic Data Generator
Generates realistic construction marketplace data for dashboard prototypes

Builder: Carlos Gorricho
Date: 2025-11-30
"""

import sqlite3
import uuid
from datetime import datetime, timedelta
from faker import Faker
import numpy as np
import random
import json

# Initialize Faker
fake = Faker('en_US')
Faker.seed(42)  # Reproducible data
np.random.seed(42)

# Configuration
DB_PATH = '../construction_check.db'
START_DATE = datetime(2023, 12, 1)  # 24 months of data
END_DATE = datetime(2025, 11, 30)

# Data volumes
NUM_BUSINESSES = 150
NUM_CONSULTANTS = 100
NUM_FREELANCERS = 250
NUM_PROJECTS = 800
NUM_ESTIMATES_PER_PROJECT_AVG = 2  # ~1,600 estimates total
REVIEW_RATE = 0.5  # 50% of completed projects get reviews
MILESTONES_PER_PROJECT_AVG = 3
MESSAGES_TOTAL = 3000
ACTIVITIES_TOTAL = 10000

# Construction industry data
INDUSTRY_SECTORS = [
    'commercial', 'residential', 'infrastructure', 
    'industrial', 'mixed_use', 'institutional'
]

BUSINESS_TYPES = [
    'general_contractor', 'developer', 'owner', 
    'architect', 'engineer', 'property_manager'
]

COMPANY_SIZES = ['small', 'medium', 'large', 'enterprise']

PROJECT_TYPES = [
    'new_construction', 'renovation', 'addition', 
    'infrastructure', 'demolition', 'tenant_improvement'
]

PROJECT_SUBTYPES = {
    'commercial': ['office', 'retail', 'restaurant', 'warehouse', 'hotel'],
    'residential': ['single_family', 'multi_family', 'townhome', 'condo', 'apartment'],
    'infrastructure': ['road', 'bridge', 'utility', 'parking', 'site_work'],
    'industrial': ['manufacturing', 'distribution', 'processing', 'research'],
    'institutional': ['school', 'hospital', 'government', 'religious', 'civic']
}

PROJECT_STATUSES = [
    'posted', 'in_bidding', 'matched', 'estimate_in_progress', 
    'estimate_delivered', 'in_progress', 'completed', 'cancelled'
]

SPECIALIZATIONS = [
    'cost_estimating', 'quantity_surveying', 'value_engineering', 
    'forensic_estimating', 'conceptual_estimating', 'detailed_estimating'
]

CERTIFICATIONS = [
    ('CCP', 'Certified Cost Professional', 'AACE International'),
    ('PSP', 'Planning and Scheduling Professional', 'AACE International'),
    ('CPE', 'Certified Professional Estimator', 'ASPE'),
    ('MRICS', 'Member Royal Institution of Chartered Surveyors', 'RICS'),
    ('PMP', 'Project Management Professional', 'PMI'),
    ('LEED AP', 'Leadership in Energy and Environmental Design', 'USGBC')
]

ESTIMATION_METHODS = ['unit_cost', 'square_foot', 'assembly', 'detailed_takeoff']
CONFIDENCE_LEVELS = ['low', 'medium', 'high', 'very_high']

# Major US cities for geographic distribution
MAJOR_CITIES = [
    ('New York', 'NY'), ('Los Angeles', 'CA'), ('Chicago', 'IL'),
    ('Houston', 'TX'), ('Phoenix', 'AZ'), ('Philadelphia', 'PA'),
    ('San Antonio', 'TX'), ('San Diego', 'CA'), ('Dallas', 'TX'),
    ('Austin', 'TX'), ('Jacksonville', 'FL'), ('San Jose', 'CA'),
    ('Fort Worth', 'TX'), ('Columbus', 'OH'), ('Charlotte', 'NC'),
    ('Indianapolis', 'IN'), ('Seattle', 'WA'), ('Denver', 'CO'),
    ('Boston', 'MA'), ('Portland', 'OR'), ('Atlanta', 'GA'),
    ('Miami', 'FL'), ('Las Vegas', 'NV'), ('Detroit', 'MI'),
    ('Nashville', 'TN'), ('Minneapolis', 'MN'), ('Tampa', 'FL')
]

DIVERSITY_CLASSIFICATIONS = [
    'minority_owned', 'women_owned', 'veteran_owned', 
    'lgbtq_owned', 'disabled_owned', None
]


def create_database():
    """Create SQLite database with schema"""
    print("Creating database schema...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Read and execute schema (simplified for SQLite)
    schema_sql = """
    -- BUSINESSES
    CREATE TABLE IF NOT EXISTS businesses (
        business_id TEXT PRIMARY KEY,
        company_name TEXT NOT NULL,
        industry_sector TEXT,
        business_type TEXT,
        street_address TEXT,
        city TEXT,
        state TEXT,
        zip_code TEXT,
        country TEXT DEFAULT 'USA',
        company_size TEXT,
        annual_revenue REAL,
        years_in_business INTEGER,
        registration_date TEXT NOT NULL,
        account_status TEXT DEFAULT 'active',
        verification_status TEXT DEFAULT 'verified',
        subscription_tier TEXT DEFAULT 'basic',
        primary_contact TEXT,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        total_projects_posted INTEGER DEFAULT 0,
        total_projects_completed INTEGER DEFAULT 0,
        average_project_value REAL,
        reputation_score REAL DEFAULT 5.00,
        total_reviews_received INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        last_login TEXT
    );

    -- ESTIMATORS
    CREATE TABLE IF NOT EXISTS estimators (
        estimator_id TEXT PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        display_name TEXT,
        profile_headline TEXT,
        bio TEXT,
        estimator_type TEXT NOT NULL,
        city TEXT,
        state TEXT,
        zip_code TEXT,
        country TEXT DEFAULT 'USA',
        willing_to_travel INTEGER DEFAULT 0,
        remote_available INTEGER DEFAULT 1,
        years_experience INTEGER,
        education_level TEXT,
        hourly_rate REAL,
        minimum_project_fee REAL,
        currency TEXT DEFAULT 'USD',
        availability_status TEXT DEFAULT 'available',
        max_concurrent_projects INTEGER DEFAULT 3,
        current_project_count INTEGER DEFAULT 0,
        registration_date TEXT NOT NULL,
        account_status TEXT DEFAULT 'active',
        verification_status TEXT DEFAULT 'verified',
        background_check INTEGER DEFAULT 0,
        insurance_verified INTEGER DEFAULT 0,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        linkedin_url TEXT,
        website_url TEXT,
        total_estimates_delivered INTEGER DEFAULT 0,
        total_estimates_accepted INTEGER DEFAULT 0,
        total_estimates_rejected INTEGER DEFAULT 0,
        win_rate REAL DEFAULT 0.00,
        average_turnaround_hours REAL,
        average_response_hours REAL,
        estimate_accuracy_rate REAL,
        client_satisfaction_score REAL DEFAULT 5.00,
        total_reviews_received INTEGER DEFAULT 0,
        repeat_client_rate REAL DEFAULT 0.00,
        diversity_classification TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        last_login TEXT,
        last_active TEXT
    );

    -- EXPERTISE
    CREATE TABLE IF NOT EXISTS expertise (
        expertise_id TEXT PRIMARY KEY,
        estimator_id TEXT NOT NULL,
        specialization_type TEXT NOT NULL,
        project_types TEXT,
        certification_name TEXT,
        certification_number TEXT,
        issuing_organization TEXT,
        issue_date TEXT,
        expiry_date TEXT,
        software_proficiency TEXT,
        years_in_specialty INTEGER,
        verified INTEGER DEFAULT 0,
        verification_date TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (estimator_id) REFERENCES estimators(estimator_id)
    );

    -- PROJECTS
    CREATE TABLE IF NOT EXISTS projects (
        project_id TEXT PRIMARY KEY,
        business_id TEXT NOT NULL,
        matched_estimator_id TEXT,
        project_title TEXT NOT NULL,
        project_description TEXT,
        project_type TEXT,
        project_subtype TEXT,
        project_city TEXT,
        project_state TEXT,
        project_zip TEXT,
        project_country TEXT DEFAULT 'USA',
        square_footage INTEGER,
        number_of_units INTEGER,
        number_of_stories INTEGER,
        estimated_budget_min REAL,
        estimated_budget_max REAL,
        desired_start_date TEXT,
        desired_completion_date TEXT,
        estimate_needed_by TEXT NOT NULL,
        status TEXT DEFAULT 'posted',
        posted_date TEXT DEFAULT CURRENT_TIMESTAMP,
        matched_date TEXT,
        estimate_delivered_date TEXT,
        project_start_date TEXT,
        project_completion_date TEXT,
        number_of_bids INTEGER DEFAULT 0,
        bid_deadline TEXT,
        final_estimated_cost REAL,
        actual_cost REAL,
        cost_variance_percent REAL,
        insurance_required INTEGER DEFAULT 1,
        bond_required INTEGER DEFAULT 0,
        security_clearance INTEGER DEFAULT 0,
        prevailing_wage INTEGER DEFAULT 0,
        urgency_level TEXT DEFAULT 'normal',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (business_id) REFERENCES businesses(business_id),
        FOREIGN KEY (matched_estimator_id) REFERENCES estimators(estimator_id)
    );

    -- ESTIMATES
    CREATE TABLE IF NOT EXISTS estimates (
        estimate_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        estimator_id TEXT NOT NULL,
        estimated_total_cost REAL NOT NULL,
        labor_cost REAL,
        materials_cost REAL,
        equipment_cost REAL,
        subcontractor_cost REAL,
        overhead_cost REAL,
        profit_margin REAL,
        contingency_percent REAL,
        contingency_amount REAL,
        estimated_duration_days INTEGER,
        estimated_start_date TEXT,
        estimated_completion_date TEXT,
        estimation_method TEXT,
        confidence_level TEXT,
        assumptions TEXT,
        exclusions TEXT,
        notes TEXT,
        status TEXT DEFAULT 'pending',
        submitted_date TEXT DEFAULT CURRENT_TIMESTAMP,
        reviewed_date TEXT,
        accepted_date TEXT,
        detailed_breakdown_url TEXT,
        supporting_docs_urls TEXT,
        actual_cost REAL,
        variance_amount REAL,
        variance_percent REAL,
        accuracy_rating TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(project_id),
        FOREIGN KEY (estimator_id) REFERENCES estimators(estimator_id),
        UNIQUE(project_id, estimator_id)
    );

    -- REVIEWS
    CREATE TABLE IF NOT EXISTS reviews (
        review_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        reviewer_id TEXT NOT NULL,
        reviewer_type TEXT NOT NULL,
        reviewee_id TEXT NOT NULL,
        reviewee_type TEXT NOT NULL,
        overall_rating REAL NOT NULL CHECK (overall_rating BETWEEN 1.0 AND 5.0),
        communication_rating REAL CHECK (communication_rating BETWEEN 1.0 AND 5.0),
        professionalism_rating REAL CHECK (professionalism_rating BETWEEN 1.0 AND 5.0),
        accuracy_rating REAL CHECK (accuracy_rating BETWEEN 1.0 AND 5.0),
        timeliness_rating REAL CHECK (timeliness_rating BETWEEN 1.0 AND 5.0),
        value_rating REAL CHECK (value_rating BETWEEN 1.0 AND 5.0),
        review_title TEXT,
        review_text TEXT,
        would_recommend INTEGER,
        would_work_again INTEGER,
        verified_review INTEGER DEFAULT 0,
        status TEXT DEFAULT 'published',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(project_id)
    );

    -- Create indexes
    CREATE INDEX IF NOT EXISTS idx_projects_business ON projects(business_id);
    CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
    CREATE INDEX IF NOT EXISTS idx_estimates_project ON estimates(project_id);
    CREATE INDEX IF NOT EXISTS idx_estimates_estimator ON estimates(estimator_id);
    CREATE INDEX IF NOT EXISTS idx_expertise_estimator ON expertise(estimator_id);
    """
    
    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()
    print("✓ Database schema created")


def generate_businesses(conn):
    """Generate business user data"""
    print(f"Generating {NUM_BUSINESSES} businesses...")
    
    cursor = conn.cursor()
    businesses = []
    
    for i in range(NUM_BUSINESSES):
        city, state = random.choice(MAJOR_CITIES)
        reg_date = fake.date_between(start_date=START_DATE, end_date=END_DATE - timedelta(days=180))
        
        business = {
            'business_id': str(uuid.uuid4()),
            'company_name': fake.company(),
            'industry_sector': random.choice(INDUSTRY_SECTORS),
            'business_type': random.choice(BUSINESS_TYPES),
            'street_address': fake.street_address(),
            'city': city,
            'state': state,
            'zip_code': fake.zipcode(),
            'company_size': random.choice(COMPANY_SIZES),
            'annual_revenue': round(np.random.lognormal(15, 1.5), 2),  # Log-normal distribution
            'years_in_business': random.randint(1, 50),
            'registration_date': reg_date.isoformat(),
            'verification_status': random.choices(['verified', 'pending'], weights=[0.85, 0.15])[0],
            'subscription_tier': random.choices(['basic', 'professional', 'enterprise'], weights=[0.5, 0.35, 0.15])[0],
            'primary_contact': fake.name(),
            'email': fake.company_email(),
            'phone': fake.phone_number(),
            'reputation_score': round(np.random.beta(8, 2) * 4 + 1, 2),  # Beta distribution skewed positive
            'last_login': (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
        }
        
        businesses.append(business)
        
        cursor.execute("""
            INSERT INTO businesses (
                business_id, company_name, industry_sector, business_type,
                street_address, city, state, zip_code, company_size, annual_revenue,
                years_in_business, registration_date, verification_status,
                subscription_tier, primary_contact, email, phone, reputation_score, last_login
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            business['business_id'], business['company_name'], business['industry_sector'],
            business['business_type'], business['street_address'], business['city'],
            business['state'], business['zip_code'], business['company_size'],
            business['annual_revenue'], business['years_in_business'],
            business['registration_date'], business['verification_status'],
            business['subscription_tier'], business['primary_contact'],
            business['email'], business['phone'], business['reputation_score'],
            business['last_login']
        ))
    
    conn.commit()
    print(f"✓ {NUM_BUSINESSES} businesses created")
    return businesses


def generate_estimators(conn):
    """Generate estimator user data (consultants and freelancers)"""
    print(f"Generating {NUM_CONSULTANTS + NUM_FREELANCERS} estimators...")
    
    cursor = conn.cursor()
    estimators = []
    
    total = NUM_CONSULTANTS + NUM_FREELANCERS
    
    for i in range(total):
        estimator_type = 'consultant' if i < NUM_CONSULTANTS else 'freelance_expert'
        city, state = random.choice(MAJOR_CITIES)
        reg_date = fake.date_between(start_date=START_DATE, end_date=END_DATE - timedelta(days=90))
        
        first_name = fake.first_name()
        last_name = fake.last_name()
        
        # Consultants tend to have higher rates and more experience
        if estimator_type == 'consultant':
            years_exp = random.randint(8, 35)
            hourly_rate = round(random.uniform(125, 350), 2)
            min_fee = round(random.uniform(5000, 25000), 2)
        else:
            years_exp = random.randint(3, 25)
            hourly_rate = round(random.uniform(75, 200), 2)
            min_fee = round(random.uniform(2000, 10000), 2)
        
        estimator = {
            'estimator_id': str(uuid.uuid4()),
            'first_name': first_name,
            'last_name': last_name,
            'display_name': f"{first_name} {last_name}",
            'profile_headline': f"{random.choice(['Senior', 'Professional', 'Expert', 'Certified'])} Cost Estimator",
            'bio': fake.text(max_nb_chars=200),
            'estimator_type': estimator_type,
            'city': city,
            'state': state,
            'zip_code': fake.zipcode(),
            'willing_to_travel': random.choice([0, 1]),
            'remote_available': 1,
            'years_experience': years_exp,
            'education_level': random.choice(['bachelors', 'masters', 'professional']),
            'hourly_rate': hourly_rate,
            'minimum_project_fee': min_fee,
            'registration_date': reg_date.isoformat(),
            'verification_status': random.choices(['verified', 'pending'], weights=[0.9, 0.1])[0],
            'background_check': random.choice([0, 1]),
            'insurance_verified': random.choice([0, 1]),
            'email': fake.email(),
            'phone': fake.phone_number(),
            'linkedin_url': f"https://linkedin.com/in/{first_name.lower()}{last_name.lower()}",
            'average_turnaround_hours': round(random.uniform(24, 120), 2),
            'average_response_hours': round(random.uniform(1, 24), 2),
            'estimate_accuracy_rate': round(np.random.beta(9, 2) * 100, 2),  # High accuracy
            'client_satisfaction_score': round(np.random.beta(8, 2) * 4 + 1, 2),
            'diversity_classification': random.choice(DIVERSITY_CLASSIFICATIONS),
            'last_login': (datetime.now() - timedelta(days=random.randint(0, 14))).isoformat(),
            'last_active': (datetime.now() - timedelta(hours=random.randint(1, 168))).isoformat()
        }
        
        estimators.append(estimator)
        
        cursor.execute("""
            INSERT INTO estimators (
                estimator_id, first_name, last_name, display_name, profile_headline,
                bio, estimator_type, city, state, zip_code, willing_to_travel,
                remote_available, years_experience, education_level, hourly_rate,
                minimum_project_fee, registration_date, verification_status,
                background_check, insurance_verified, email, phone, linkedin_url,
                average_turnaround_hours, average_response_hours, estimate_accuracy_rate,
                client_satisfaction_score, diversity_classification, last_login, last_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            estimator['estimator_id'], estimator['first_name'], estimator['last_name'],
            estimator['display_name'], estimator['profile_headline'], estimator['bio'],
            estimator['estimator_type'], estimator['city'], estimator['state'],
            estimator['zip_code'], estimator['willing_to_travel'], estimator['remote_available'],
            estimator['years_experience'], estimator['education_level'], estimator['hourly_rate'],
            estimator['minimum_project_fee'], estimator['registration_date'],
            estimator['verification_status'], estimator['background_check'],
            estimator['insurance_verified'], estimator['email'], estimator['phone'],
            estimator['linkedin_url'], estimator['average_turnaround_hours'],
            estimator['average_response_hours'], estimator['estimate_accuracy_rate'],
            estimator['client_satisfaction_score'], estimator['diversity_classification'],
            estimator['last_login'], estimator['last_active']
        ))
    
    conn.commit()
    print(f"✓ {total} estimators created ({NUM_CONSULTANTS} consultants, {NUM_FREELANCERS} freelancers)")
    return estimators


def generate_expertise(conn, estimators):
    """Generate expertise and certifications for estimators"""
    print("Generating expertise records...")
    
    cursor = conn.cursor()
    count = 0
    
    for estimator in estimators:
        # Each estimator gets 1-3 specializations
        num_specializations = random.randint(1, 3)
        
        for _ in range(num_specializations):
            cert = random.choice(CERTIFICATIONS) if random.random() > 0.5 else None
            
            expertise = {
                'expertise_id': str(uuid.uuid4()),
                'estimator_id': estimator['estimator_id'],
                'specialization_type': random.choice(SPECIALIZATIONS),
                'project_types': json.dumps(random.sample(INDUSTRY_SECTORS, random.randint(2, 4))),
                'certification_name': cert[0] if cert else None,
                'issuing_organization': cert[2] if cert else None,
                'issue_date': (datetime.now() - timedelta(days=random.randint(365, 3650))).date().isoformat() if cert else None,
                'expiry_date': (datetime.now() + timedelta(days=random.randint(365, 1825))).date().isoformat() if cert else None,
                'software_proficiency': json.dumps(random.sample(['Sage Estimating', 'Bluebeam', 'PlanSwift', 'CostX', 'ProEst'], random.randint(2, 4))),
                'years_in_specialty': random.randint(2, estimator['years_experience']),
                'verified': 1 if cert else 0
            }
            
            cursor.execute("""
                INSERT INTO expertise (
                    expertise_id, estimator_id, specialization_type, project_types,
                    certification_name, issuing_organization, issue_date, expiry_date,
                    software_proficiency, years_in_specialty, verified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                expertise['expertise_id'], expertise['estimator_id'],
                expertise['specialization_type'], expertise['project_types'],
                expertise['certification_name'], expertise['issuing_organization'],
                expertise['issue_date'], expertise['expiry_date'],
                expertise['software_proficiency'], expertise['years_in_specialty'],
                expertise['verified']
            ))
            
            count += 1
    
    conn.commit()
    print(f"✓ {count} expertise records created")


def generate_projects(conn, businesses):
    """Generate construction projects"""
    print(f"Generating {NUM_PROJECTS} projects...")
    
    cursor = conn.cursor()
    projects = []
    
    for i in range(NUM_PROJECTS):
        business = random.choice(businesses)
        city, state = random.choice(MAJOR_CITIES)
        
        # Posted date spread over 24 months
        posted_date = fake.date_time_between(start_date=START_DATE, end_date=END_DATE)
        
        # Project type and subtype
        sector = random.choice(list(PROJECT_SUBTYPES.keys()))
        subtype = random.choice(PROJECT_SUBTYPES[sector])
        
        # Budget (log-normal distribution)
        budget_median = np.random.lognormal(13, 1.2)  # Wide range
        budget_min = round(budget_median * 0.8, 2)
        budget_max = round(budget_median * 1.2, 2)
        
        # Status based on time (older projects more likely to be completed)
        days_since_posted = (END_DATE - posted_date).days
        if days_since_posted > 300:
            status = random.choices(
                ['completed', 'cancelled', 'in_progress'],
                weights=[0.6, 0.1, 0.3]
            )[0]
        elif days_since_posted > 150:
            status = random.choices(
                ['in_progress', 'estimate_delivered', 'completed'],
                weights=[0.5, 0.3, 0.2]
            )[0]
        elif days_since_posted > 60:
            status = random.choices(
                ['matched', 'estimate_in_progress', 'in_progress'],
                weights=[0.3, 0.4, 0.3]
            )[0]
        else:
            status = random.choices(
                ['posted', 'in_bidding', 'matched'],
                weights=[0.3, 0.5, 0.2]
            )[0]
        
        project = {
            'project_id': str(uuid.uuid4()),
            'business_id': business['business_id'],
            'project_title': f"{random.choice(['New', 'Modern', 'Premium', 'Downtown', 'Luxury'])} {sector.title()} {subtype.replace('_', ' ').title()}",
            'project_description': fake.text(max_nb_chars=300),
            'project_type': random.choice(PROJECT_TYPES),
            'project_subtype': subtype,
            'project_city': city,
            'project_state': state,
            'project_zip': fake.zipcode(),
            'square_footage': random.randint(1000, 500000),
            'estimated_budget_min': budget_min,
            'estimated_budget_max': budget_max,
            'estimate_needed_by': (posted_date + timedelta(days=random.randint(7, 30))).date().isoformat(),
            'status': status,
            'posted_date': posted_date.isoformat(),
            'urgency_level': random.choices(['low', 'normal', 'high', 'urgent'], weights=[0.2, 0.5, 0.2, 0.1])[0],
        }
        
        projects.append(project)
        
        cursor.execute("""
            INSERT INTO projects (
                project_id, business_id, project_title, project_description,
                project_type, project_subtype, project_city, project_state,
                project_zip, square_footage, estimated_budget_min, estimated_budget_max,
                estimate_needed_by, status, posted_date, urgency_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project['project_id'], project['business_id'], project['project_title'],
            project['project_description'], project['project_type'], project['project_subtype'],
            project['project_city'], project['project_state'], project['project_zip'],
            project['square_footage'], project['estimated_budget_min'],
            project['estimated_budget_max'], project['estimate_needed_by'],
            project['status'], project['posted_date'], project['urgency_level']
        ))
    
    conn.commit()
    print(f"✓ {NUM_PROJECTS} projects created")
    return projects


def generate_estimates(conn, projects, estimators):
    """Generate cost estimates for projects"""
    print("Generating estimates...")
    
    cursor = conn.cursor()
    count = 0
    
    for project in projects:
        # Number of estimates per project
        num_estimates = max(1, int(np.random.poisson(NUM_ESTIMATES_PER_PROJECT_AVG)))
        
        selected_estimators = random.sample(estimators, min(num_estimates, len(estimators)))
        
        for estimator in selected_estimators:
            # Base cost around project budget with variance
            base_cost = (project['estimated_budget_min'] + project['estimated_budget_max']) / 2
            estimated_cost = base_cost * random.uniform(0.85, 1.15)
            
            # Cost breakdown
            labor = estimated_cost * random.uniform(0.3, 0.45)
            materials = estimated_cost * random.uniform(0.25, 0.40)
            equipment = estimated_cost * random.uniform(0.05, 0.15)
            subcontractor = estimated_cost * random.uniform(0.10, 0.25)
            overhead = estimated_cost * random.uniform(0.08, 0.15)
            profit = estimated_cost * random.uniform(0.05, 0.12)
            
            submitted_date = datetime.fromisoformat(project['posted_date']) + timedelta(days=random.randint(1, 14))
            
            estimate = {
                'estimate_id': str(uuid.uuid4()),
                'project_id': project['project_id'],
                'estimator_id': estimator['estimator_id'],
                'estimated_total_cost': round(estimated_cost, 2),
                'labor_cost': round(labor, 2),
                'materials_cost': round(materials, 2),
                'equipment_cost': round(equipment, 2),
                'subcontractor_cost': round(subcontractor, 2),
                'overhead_cost': round(overhead, 2),
                'profit_margin': round(profit, 2),
                'contingency_percent': round(random.uniform(5, 15), 2),
                'estimated_duration_days': random.randint(30, 720),
                'estimation_method': random.choice(ESTIMATION_METHODS),
                'confidence_level': random.choice(CONFIDENCE_LEVELS),
                'status': 'accepted' if random.random() > 0.7 else 'pending',
                'submitted_date': submitted_date.isoformat()
            }
            
            cursor.execute("""
                INSERT INTO estimates (
                    estimate_id, project_id, estimator_id, estimated_total_cost,
                    labor_cost, materials_cost, equipment_cost, subcontractor_cost,
                    overhead_cost, profit_margin, contingency_percent,
                    estimated_duration_days, estimation_method, confidence_level,
                    status, submitted_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                estimate['estimate_id'], estimate['project_id'], estimate['estimator_id'],
                estimate['estimated_total_cost'], estimate['labor_cost'],
                estimate['materials_cost'], estimate['equipment_cost'],
                estimate['subcontractor_cost'], estimate['overhead_cost'],
                estimate['profit_margin'], estimate['contingency_percent'],
                estimate['estimated_duration_days'], estimate['estimation_method'],
                estimate['confidence_level'], estimate['status'], estimate['submitted_date']
            ))
            
            count += 1
    
    conn.commit()
    print(f"✓ {count} estimates created")


def generate_reviews(conn, projects, businesses, estimators):
    """Generate reviews for completed projects"""
    print("Generating reviews...")
    
    cursor = conn.cursor()
    count = 0
    
    completed_projects = [p for p in projects if p['status'] == 'completed']
    
    for project in completed_projects:
        if random.random() > REVIEW_RATE:
            continue
        
        # Business reviews estimator
        estimator = random.choice(estimators)
        business = next(b for b in businesses if b['business_id'] == project['business_id'])
        
        # Generate realistic ratings (beta distribution, skewed positive)
        overall_rating = round(np.random.beta(8, 2) * 4 + 1, 1)
        
        review = {
            'review_id': str(uuid.uuid4()),
            'project_id': project['project_id'],
            'reviewer_id': business['business_id'],
            'reviewer_type': 'business',
            'reviewee_id': estimator['estimator_id'],
            'reviewee_type': 'estimator',
            'overall_rating': overall_rating,
            'communication_rating': round(min(5.0, max(1.0, overall_rating + random.uniform(-0.5, 0.5))), 1),
            'professionalism_rating': round(min(5.0, max(1.0, overall_rating + random.uniform(-0.5, 0.5))), 1),
            'accuracy_rating': round(min(5.0, max(1.0, overall_rating + random.uniform(-0.5, 0.5))), 1),
            'timeliness_rating': round(min(5.0, max(1.0, overall_rating + random.uniform(-0.5, 0.5))), 1),
            'value_rating': round(min(5.0, max(1.0, overall_rating + random.uniform(-0.5, 0.5))), 1),
            'review_title': random.choice([
                'Excellent work', 'Great experience', 'Professional service',
                'Highly recommend', 'Outstanding estimator', 'Will work with again'
            ]),
            'review_text': fake.text(max_nb_chars=200),
            'would_recommend': 1 if overall_rating >= 4.0 else 0,
            'would_work_again': 1 if overall_rating >= 4.5 else 0,
            'verified_review': 1
        }
        
        cursor.execute("""
            INSERT INTO reviews (
                review_id, project_id, reviewer_id, reviewer_type,
                reviewee_id, reviewee_type, overall_rating, communication_rating,
                professionalism_rating, accuracy_rating, timeliness_rating,
                value_rating, review_title, review_text, would_recommend,
                would_work_again, verified_review
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            review['review_id'], review['project_id'], review['reviewer_id'],
            review['reviewer_type'], review['reviewee_id'], review['reviewee_type'],
            review['overall_rating'], review['communication_rating'],
            review['professionalism_rating'], review['accuracy_rating'],
            review['timeliness_rating'], review['value_rating'],
            review['review_title'], review['review_text'],
            review['would_recommend'], review['would_work_again'],
            review['verified_review']
        ))
        
        count += 1
    
    conn.commit()
    print(f"✓ {count} reviews created")


def main():
    """Main execution"""
    print("\n" + "="*60)
    print("Construction Check - Synthetic Data Generator")
    print("="*60 + "\n")
    
    # Create database
    create_database()
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Generate data in order
        businesses = generate_businesses(conn)
        estimators = generate_estimators(conn)
        generate_expertise(conn, estimators)
        projects = generate_projects(conn, businesses)
        generate_estimates(conn, projects, estimators)
        generate_reviews(conn, projects, businesses, estimators)
        
        print("\n" + "="*60)
        print("✓ Data generation complete!")
        print(f"  Database: {DB_PATH}")
        print("="*60 + "\n")
        
    finally:
        conn.close()


if __name__ == '__main__':
    main()
