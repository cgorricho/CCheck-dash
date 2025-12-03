#!/usr/bin/env python3
"""
Construction Check - Enhanced Synthetic Data Generator V2
ENHANCEMENTS:
- AACE Estimate Classes (5 to 1) with proper confidence intervals
- Progressive estimate refinement (same project evolving over time)
- Regional cost multipliers (location-based pricing)

Builder: Carlos Gorricho
Date: 2025-12-01
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
Faker.seed(42)
np.random.seed(42)

# Configuration
DB_PATH = '../construction_check.db'
START_DATE = datetime(2023, 12, 1)
END_DATE = datetime(2025, 11, 30)

# Data volumes
NUM_BUSINESSES = 150
NUM_CONSULTANTS = 100
NUM_FREELANCERS = 250
NUM_PROJECTS = 800
PROGRESSIVE_ESTIMATE_RATE = 0.40  # 40% of projects get multiple progressive estimates
MAX_PROGRESSIVE_ESTIMATES = 5  # Maximum estimate refinements per project
REVIEW_RATE = 0.5

# ============================================================================
# NEW: AACE ESTIMATE CLASSES
# ============================================================================
# Based on AACE International standards
AACE_CLASSES = {
    'class_5': {
        'name': 'Class 5 - Conceptual',
        'confidence_low': -50,  # -50% to +100%
        'confidence_high': 100,
        'typical_contingency': 20.0,
        'engineering_completion': 2,  # 0-2% design complete
        'preparation_effort': 'minimal',
        'end_use': 'Screening/Feasibility'
    },
    'class_4': {
        'name': 'Class 4 - Study/Feasibility',
        'confidence_low': -30,  # -30% to +50%
        'confidence_high': 50,
        'typical_contingency': 15.0,
        'engineering_completion': 10,  # 1-15% design complete
        'preparation_effort': 'low',
        'end_use': 'Concept Study/Feasibility'
    },
    'class_3': {
        'name': 'Class 3 - Budget/Authorization',
        'confidence_low': -20,  # -20% to +30%
        'confidence_high': 30,
        'typical_contingency': 12.0,
        'engineering_completion': 30,  # 10-40% design complete
        'preparation_effort': 'medium',
        'end_use': 'Budget/Authorization/Control'
    },
    'class_2': {
        'name': 'Class 2 - Control/Bid',
        'confidence_low': -15,  # -15% to +20%
        'confidence_high': 20,
        'typical_contingency': 8.0,
        'engineering_completion': 65,  # 30-100% design complete
        'preparation_effort': 'high',
        'end_use': 'Control/Bid/Tender'
    },
    'class_1': {
        'name': 'Class 1 - Check/Bid',
        'confidence_low': -10,  # -10% to +15%
        'confidence_high': 15,
        'typical_contingency': 5.0,
        'engineering_completion': 95,  # 50-100% design complete
        'preparation_effort': 'very_high',
        'end_use': 'Check Estimate/Bid/Control'
    }
}

# ============================================================================
# NEW: REGIONAL COST MULTIPLIERS
# ============================================================================
# Based on construction cost indices by location
REGIONAL_COST_MULTIPLIERS = {
    # High-cost markets
    'NY': 1.35,  # New York
    'CA': 1.30,  # California (average - varies by city)
    'MA': 1.25,  # Boston area
    'WA': 1.20,  # Seattle area
    'HI': 2.00,  # Hawaii (highest - island logistics)
    
    # Above-average markets
    'IL': 1.15,  # Chicago
    'CO': 1.12,  # Denver
    'OR': 1.10,  # Portland
    'PA': 1.08,  # Philadelphia
    'MN': 1.50,  # Minneapolis (winter construction challenges)
    
    # Average markets
    'TX': 1.00,  # Texas (baseline)
    'FL': 1.00,  # Florida (baseline, but hurricane considerations)
    'NC': 0.98,
    'GA': 0.97,
    'AZ': 0.96,
    
    # Below-average markets
    'TN': 0.92,
    'OH': 0.90,
    'IN': 0.88,
    'NV': 0.95,
    'MI': 0.93
}

# Construction industry data (same as V1)
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
    'commercial': ['office_building', 'retail', 'restaurant', 'warehouse', 'hotel'],
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

ESTIMATION_METHODS = ['parametric', 'analogical', 'engineering', 'detailed_takeoff']

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


def get_regional_multiplier(state):
    """Get regional cost multiplier for state"""
    return REGIONAL_COST_MULTIPLIERS.get(state, 1.0)


def create_database():
    """Create SQLite database with enhanced schema"""
    print("Creating enhanced database schema...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS reviews")
    cursor.execute("DROP TABLE IF EXISTS estimates")
    cursor.execute("DROP TABLE IF EXISTS projects")
    cursor.execute("DROP TABLE IF EXISTS expertise")
    cursor.execute("DROP TABLE IF EXISTS estimators")
    cursor.execute("DROP TABLE IF EXISTS businesses")
    
    schema_sql = """
    -- BUSINESSES
    CREATE TABLE businesses (
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
    CREATE TABLE estimators (
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
    CREATE TABLE expertise (
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

    -- PROJECTS (enhanced with regional data)
    CREATE TABLE projects (
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
        regional_cost_multiplier REAL DEFAULT 1.0,
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

    -- ESTIMATES (enhanced with AACE classes)
    CREATE TABLE estimates (
        estimate_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        estimator_id TEXT NOT NULL,
        estimate_sequence INTEGER DEFAULT 1,
        aace_class TEXT,
        engineering_completion_percent REAL,
        estimated_total_cost REAL NOT NULL,
        confidence_interval_low REAL,
        confidence_interval_high REAL,
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
        FOREIGN KEY (estimator_id) REFERENCES estimators(estimator_id)
    );

    -- REVIEWS
    CREATE TABLE reviews (
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
    CREATE INDEX idx_projects_business ON projects(business_id);
    CREATE INDEX idx_projects_status ON projects(status);
    CREATE INDEX idx_projects_state ON projects(project_state);
    CREATE INDEX idx_estimates_project ON estimates(project_id);
    CREATE INDEX idx_estimates_estimator ON estimates(estimator_id);
    CREATE INDEX idx_estimates_class ON estimates(aace_class);
    CREATE INDEX idx_estimates_sequence ON estimates(project_id, estimate_sequence);
    CREATE INDEX idx_expertise_estimator ON expertise(estimator_id);
    """
    
    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()
    print("✓ Enhanced database schema created")


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
            'annual_revenue': round(np.random.lognormal(15, 1.5), 2),
            'years_in_business': random.randint(1, 50),
            'registration_date': reg_date.isoformat(),
            'verification_status': random.choices(['verified', 'pending'], weights=[0.85, 0.15])[0],
            'subscription_tier': random.choices(['basic', 'professional', 'enterprise'], weights=[0.5, 0.35, 0.15])[0],
            'primary_contact': fake.name(),
            'email': fake.company_email(),
            'phone': fake.phone_number(),
            'reputation_score': round(np.random.beta(8, 2) * 4 + 1, 2),
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
    """Generate estimator user data"""
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
            'estimate_accuracy_rate': round(np.random.beta(9, 2) * 100, 2),
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
    print(f"✓ {total} estimators created")
    return estimators


def generate_expertise(conn, estimators):
    """Generate expertise and certifications"""
    print("Generating expertise records...")
    
    cursor = conn.cursor()
    count = 0
    
    for estimator in estimators:
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
    """Generate construction projects with regional multipliers"""
    print(f"Generating {NUM_PROJECTS} projects...")
    
    cursor = conn.cursor()
    projects = []
    
    for i in range(NUM_PROJECTS):
        business = random.choice(businesses)
        city, state = random.choice(MAJOR_CITIES)
        
        posted_date = fake.date_time_between(start_date=START_DATE, end_date=END_DATE)
        
        sector = random.choice(list(PROJECT_SUBTYPES.keys()))
        subtype = random.choice(PROJECT_SUBTYPES[sector])
        
        # Base budget with regional multiplier
        base_budget = np.random.lognormal(13, 1.2)
        regional_multiplier = get_regional_multiplier(state)
        adjusted_budget = base_budget * regional_multiplier
        
        budget_min = round(adjusted_budget * 0.8, 2)
        budget_max = round(adjusted_budget * 1.2, 2)
        
        days_since_posted = (END_DATE - posted_date).days
        if days_since_posted > 300:
            status = random.choices(['completed', 'cancelled', 'in_progress'], weights=[0.6, 0.1, 0.3])[0]
        elif days_since_posted > 150:
            status = random.choices(['in_progress', 'estimate_delivered', 'completed'], weights=[0.5, 0.3, 0.2])[0]
        elif days_since_posted > 60:
            status = random.choices(['matched', 'estimate_in_progress', 'in_progress'], weights=[0.3, 0.4, 0.3])[0]
        else:
            status = random.choices(['posted', 'in_bidding', 'matched'], weights=[0.3, 0.5, 0.2])[0]
        
        project = {
            'project_id': str(uuid.uuid4()),
            'business_id': business['business_id'],
            'project_title': f"{random.choice(['New', 'Modern', 'Premium'])} {sector.title()} {subtype.replace('_', ' ').title()}",
            'project_description': fake.text(max_nb_chars=300),
            'project_type': random.choice(PROJECT_TYPES),
            'project_subtype': subtype,
            'project_city': city,
            'project_state': state,
            'project_zip': fake.zipcode(),
            'regional_cost_multiplier': regional_multiplier,
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
                project_zip, regional_cost_multiplier, square_footage, 
                estimated_budget_min, estimated_budget_max,
                estimate_needed_by, status, posted_date, urgency_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project['project_id'], project['business_id'], project['project_title'],
            project['project_description'], project['project_type'], project['project_subtype'],
            project['project_city'], project['project_state'], project['project_zip'],
            project['regional_cost_multiplier'], project['square_footage'],
            project['estimated_budget_min'], project['estimated_budget_max'],
            project['estimate_needed_by'], project['status'], project['posted_date'],
            project['urgency_level']
        ))
    
    conn.commit()
    print(f"✓ {NUM_PROJECTS} projects created")
    return projects


def generate_progressive_estimates(conn, project, estimators):
    """Generate progressive estimate refinement for a single project"""
    
    cursor = conn.cursor()
    
    # Select one estimator who will provide progressive estimates
    estimator = random.choice(estimators)
    
    # Number of progressive refinements (2-5)
    num_estimates = random.randint(2, MAX_PROGRESSIVE_ESTIMATES)
    
    # AACE class progression (5 -> 4 -> 3 -> 2 -> 1)
    class_progression = ['class_5', 'class_4', 'class_3', 'class_2', 'class_1']
    
    # Base cost (true value)
    base_cost = (project['estimated_budget_min'] + project['estimated_budget_max']) / 2
    
    posted_date = datetime.fromisoformat(project['posted_date'])
    
    for seq in range(num_estimates):
        # Get AACE class for this estimate
        class_index = min(seq, len(class_progression) - 1)
        aace_class = class_progression[class_index]
        class_info = AACE_CLASSES[aace_class]
        
        # Calculate estimate with decreasing variance
        variance_low = class_info['confidence_low'] / 100.0
        variance_high = class_info['confidence_high'] / 100.0
        
        # Random variance within confidence interval
        variance = random.uniform(variance_low, variance_high)
        estimated_cost = base_cost * (1 + variance)
        
        # Time progression (estimates submitted progressively)
        days_offset = seq * random.randint(7, 21)  # 1-3 weeks between estimates
        submitted_date = posted_date + timedelta(days=days_offset)
        
        # Engineering completion progresses
        engineering_pct = class_info['engineering_completion'] + random.randint(-5, 10)
        engineering_pct = max(0, min(100, engineering_pct))
        
        # Contingency decreases as confidence increases
        contingency_pct = class_info['typical_contingency'] + random.uniform(-2, 2)
        
        # Cost breakdown
        labor = estimated_cost * random.uniform(0.3, 0.45)
        materials = estimated_cost * random.uniform(0.25, 0.40)
        equipment = estimated_cost * random.uniform(0.05, 0.15)
        subcontractor = estimated_cost * random.uniform(0.10, 0.25)
        overhead = estimated_cost * random.uniform(0.08, 0.15)
        profit = estimated_cost * random.uniform(0.05, 0.12)
        
        estimate = {
            'estimate_id': str(uuid.uuid4()),
            'project_id': project['project_id'],
            'estimator_id': estimator['estimator_id'],
            'estimate_sequence': seq + 1,
            'aace_class': aace_class,
            'engineering_completion_percent': engineering_pct,
            'estimated_total_cost': round(estimated_cost, 2),
            'confidence_interval_low': round(base_cost * (1 + variance_low), 2),
            'confidence_interval_high': round(base_cost * (1 + variance_high), 2),
            'labor_cost': round(labor, 2),
            'materials_cost': round(materials, 2),
            'equipment_cost': round(equipment, 2),
            'subcontractor_cost': round(subcontractor, 2),
            'overhead_cost': round(overhead, 2),
            'profit_margin': round(profit, 2),
            'contingency_percent': round(contingency_pct, 2),
            'estimated_duration_days': random.randint(30, 720),
            'estimation_method': ESTIMATION_METHODS[class_index] if class_index < len(ESTIMATION_METHODS) else 'detailed_takeoff',
            'status': 'accepted' if seq == num_estimates - 1 else 'superseded',
            'submitted_date': submitted_date.isoformat()
        }
        
        cursor.execute("""
            INSERT INTO estimates (
                estimate_id, project_id, estimator_id, estimate_sequence,
                aace_class, engineering_completion_percent, estimated_total_cost,
                confidence_interval_low, confidence_interval_high,
                labor_cost, materials_cost, equipment_cost, subcontractor_cost,
                overhead_cost, profit_margin, contingency_percent,
                estimated_duration_days, estimation_method, status, submitted_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            estimate['estimate_id'], estimate['project_id'], estimate['estimator_id'],
            estimate['estimate_sequence'], estimate['aace_class'],
            estimate['engineering_completion_percent'], estimate['estimated_total_cost'],
            estimate['confidence_interval_low'], estimate['confidence_interval_high'],
            estimate['labor_cost'], estimate['materials_cost'], estimate['equipment_cost'],
            estimate['subcontractor_cost'], estimate['overhead_cost'], estimate['profit_margin'],
            estimate['contingency_percent'], estimate['estimated_duration_days'],
            estimate['estimation_method'], estimate['status'], estimate['submitted_date']
        ))
    
    return num_estimates


def generate_estimates(conn, projects, estimators):
    """Generate estimates (mix of progressive and single estimates)"""
    print("Generating estimates with AACE classes and progressive refinement...")
    
    cursor = conn.cursor()
    total_count = 0
    progressive_count = 0
    
    for project in projects:
        # Determine if this project gets progressive estimates
        if random.random() < PROGRESSIVE_ESTIMATE_RATE:
            # Progressive estimates from one estimator
            count = generate_progressive_estimates(conn, project, estimators)
            total_count += count
            progressive_count += 1
        else:
            # Standard single estimate(s) from multiple estimators
            num_estimates = random.randint(1, 3)
            selected_estimators = random.sample(estimators, min(num_estimates, len(estimators)))
            
            for estimator in selected_estimators:
                # Random AACE class
                aace_class = random.choice(list(AACE_CLASSES.keys()))
                class_info = AACE_CLASSES[aace_class]
                
                base_cost = (project['estimated_budget_min'] + project['estimated_budget_max']) / 2
                
                variance_low = class_info['confidence_low'] / 100.0
                variance_high = class_info['confidence_high'] / 100.0
                variance = random.uniform(variance_low, variance_high)
                
                estimated_cost = base_cost * (1 + variance)
                
                engineering_pct = class_info['engineering_completion'] + random.randint(-5, 10)
                engineering_pct = max(0, min(100, engineering_pct))
                
                contingency_pct = class_info['typical_contingency'] + random.uniform(-2, 2)
                
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
                    'estimate_sequence': 1,
                    'aace_class': aace_class,
                    'engineering_completion_percent': engineering_pct,
                    'estimated_total_cost': round(estimated_cost, 2),
                    'confidence_interval_low': round(base_cost * (1 + variance_low), 2),
                    'confidence_interval_high': round(base_cost * (1 + variance_high), 2),
                    'labor_cost': round(labor, 2),
                    'materials_cost': round(materials, 2),
                    'equipment_cost': round(equipment, 2),
                    'subcontractor_cost': round(subcontractor, 2),
                    'overhead_cost': round(overhead, 2),
                    'profit_margin': round(profit, 2),
                    'contingency_percent': round(contingency_pct, 2),
                    'estimated_duration_days': random.randint(30, 720),
                    'estimation_method': random.choice(ESTIMATION_METHODS),
                    'status': 'accepted' if random.random() > 0.7 else 'pending',
                    'submitted_date': submitted_date.isoformat()
                }
                
                cursor.execute("""
                    INSERT INTO estimates (
                        estimate_id, project_id, estimator_id, estimate_sequence,
                        aace_class, engineering_completion_percent, estimated_total_cost,
                        confidence_interval_low, confidence_interval_high,
                        labor_cost, materials_cost, equipment_cost, subcontractor_cost,
                        overhead_cost, profit_margin, contingency_percent,
                        estimated_duration_days, estimation_method, status, submitted_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    estimate['estimate_id'], estimate['project_id'], estimate['estimator_id'],
                    estimate['estimate_sequence'], estimate['aace_class'],
                    estimate['engineering_completion_percent'], estimate['estimated_total_cost'],
                    estimate['confidence_interval_low'], estimate['confidence_interval_high'],
                    estimate['labor_cost'], estimate['materials_cost'], estimate['equipment_cost'],
                    estimate['subcontractor_cost'], estimate['overhead_cost'], estimate['profit_margin'],
                    estimate['contingency_percent'], estimate['estimated_duration_days'],
                    estimate['estimation_method'], estimate['status'], estimate['submitted_date']
                ))
                
                total_count += 1
    
    conn.commit()
    print(f"✓ {total_count} estimates created ({progressive_count} projects with progressive refinement)")


def generate_reviews(conn, projects, businesses, estimators):
    """Generate reviews for completed projects"""
    print("Generating reviews...")
    
    cursor = conn.cursor()
    count = 0
    
    completed_projects = [p for p in projects if p['status'] == 'completed']
    
    for project in completed_projects:
        if random.random() > REVIEW_RATE:
            continue
        
        estimator = random.choice(estimators)
        business = next(b for b in businesses if b['business_id'] == project['business_id'])
        
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
    print("Construction Check - Enhanced Data Generator V2")
    print("="*60 + "\n")
    
    print("ENHANCEMENTS:")
    print("  • AACE Estimate Classes (5→1) with confidence intervals")
    print("  • Progressive estimate refinement (40% of projects)")
    print("  • Regional cost multipliers by state")
    print()
    
    create_database()
    
    conn = sqlite3.connect(DB_PATH)
    
    try:
        businesses = generate_businesses(conn)
        estimators = generate_estimators(conn)
        generate_expertise(conn, estimators)
        projects = generate_projects(conn, businesses)
        generate_estimates(conn, projects, estimators)
        generate_reviews(conn, projects, businesses, estimators)
        
        print("\n" + "="*60)
        print("✓ Enhanced data generation complete!")
        print(f"  Database: {DB_PATH}")
        print("\nKEY FEATURES:")
        print("  • Projects have regional cost multipliers")
        print("  • ~40% of projects have progressive estimate refinement")
        print("  • All estimates have AACE classes with confidence intervals")
        print("  • Estimate funnel/cone visualization ready")
        print("  • Location-based cost comparisons ready")
        print("="*60 + "\n")
        
    finally:
        conn.close()


if __name__ == '__main__':
    main()
