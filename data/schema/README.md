# Construction Check - Data Schema Design

**Status**: ✅ Complete  
**Date**: 2025-11-30  
**Builder**: Carlos Gorricho

---

## Overview

Complete database schema designed for the Construction Check marketplace platform. The schema supports all three user types (Businesses, Consultants, Freelance Experts) and provides comprehensive data tracking for dashboards and analytics.

---

## Files in This Directory

### 1. `20251130-2300_database_schema_design.md`
**Purpose**: Comprehensive schema documentation  
**Contents**:
- Entity relationship diagrams
- Detailed table specifications
- Business rules and constraints
- Data integrity requirements
- Index strategies
- Privacy and security considerations

### 2. `create_tables.sql`
**Purpose**: PostgreSQL DDL script  
**Contents**:
- DROP statements for clean setup
- CREATE TABLE statements for all 12 tables
- Index definitions
- Foreign key constraints
- Default values and checks

---

## Database Schema Summary

### Core Tables (10)

| Table | Purpose | Est. Records |
|-------|---------|--------------|
| **businesses** | Companies seeking estimates | 150 |
| **estimators** | Consultants & freelance experts | 350 |
| **expertise** | Estimator specializations/certs | 500-700 |
| **projects** | Construction projects | 800 |
| **estimates** | Cost estimates submitted | 1,500 |
| **reviews** | User ratings & feedback | 400 |
| **milestones** | Project progress tracking | 2,000 |
| **messages** | User communications | 3,000 |
| **activities** | User action logs | 10,000+ |
| **platform_metrics** | Daily aggregated KPIs | 365-730 |

### Lookup Tables (2)

| Table | Purpose |
|-------|---------|
| **project_types_lookup** | Standard project classifications |
| **certifications_lookup** | Valid certifications registry |

---

## Key Relationships

```
businesses (1) → (N) projects
estimators (1) → (N) estimates
estimators (1) → (N) expertise
projects (1) → (N) estimates
projects (1) → (N) milestones
projects (1) → (N) reviews
```

---

## Key Features

### 1. Multi-User Support
- Separate tables for businesses and estimators
- Flexible reviewer/reviewee relationships
- User-type aware messaging system

### 2. Performance Optimized
- Strategic indexes on frequently queried fields
- Composite indexes for complex queries
- JSONB for flexible data storage

### 3. Data Integrity
- Foreign key constraints with cascading rules
- CHECK constraints on ratings (1.0-5.0)
- Unique constraints prevent duplicates
- Default values for critical fields

### 4. Analytics Ready
- Pre-aggregated metrics table
- Comprehensive activity logging
- Historical data tracking
- Time-series friendly structure

### 5. Scalability
- UUID primary keys (VARCHAR(36))
- JSONB for extensible attributes
- Separate tables for high-volume data (activities)
- Optimized for read-heavy dashboards

---

## Usage Instructions

### 1. Database Setup

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE construction_check;

# Connect to new database
\c construction_check

# Execute schema
\i /home/cgorricho/apps/CCheck/data/schema/create_tables.sql
```

### 2. Verify Installation

```sql
-- Check all tables created
\dt

-- View table structure
\d businesses
\d estimators
\d projects

-- Verify indexes
\di
```

### 3. Test Relationships

```sql
-- Insert test business
INSERT INTO businesses (
    business_id, company_name, email, registration_date
) VALUES (
    'test-business-001', 'Test Construction Co', 'test@example.com', CURRENT_DATE
);

-- Verify insert
SELECT * FROM businesses WHERE business_id = 'test-business-001';
```

---

## Next Steps

### Phase 1: Data Generation (In Progress)
- [ ] Create Python data generation scripts
- [ ] Define realistic distributions
- [ ] Generate lookup table data
- [ ] Generate user data (businesses, estimators)
- [ ] Generate transactional data (projects, estimates)
- [ ] Generate engagement data (reviews, messages, activities)

### Phase 2: Data Validation
- [ ] Verify referential integrity
- [ ] Check data distributions
- [ ] Validate business rules
- [ ] Test query performance
- [ ] Review data quality

### Phase 3: Dashboard Development
- [ ] Connect dashboard to database
- [ ] Build data transformation layer
- [ ] Create visualization components
- [ ] Test with real queries

---

## Data Generation Strategy

### Approach
1. **Lookup Tables First**: Reference data (project types, certifications)
2. **Users Second**: Businesses and estimators with profiles
3. **Transactional Third**: Projects and estimates with realistic relationships
4. **Engagement Fourth**: Reviews, messages, activities
5. **Metrics Last**: Aggregate platform_metrics from transactional data

### Synthetic Data Requirements
- **Realism**: Use construction industry terminology and patterns
- **Distributions**: Log-normal for project sizes, beta for ratings
- **Seasonality**: Construction industry follows seasonal patterns
- **Relationships**: Maintain referential integrity throughout
- **Time Series**: 12-24 months historical data for trend analysis

---

## Technical Specifications

### Database Engine
- **Primary**: PostgreSQL 12+
- **Alternative**: MySQL 8.0+ (with modifications to JSONB → JSON)

### Data Types
- **IDs**: VARCHAR(36) for UUID storage
- **Money**: DECIMAL(15,2) for precision
- **Ratings**: DECIMAL(2,1) or DECIMAL(3,2) with CHECK constraints
- **JSON**: JSONB for flexible attributes (PostgreSQL specific)
- **Dates**: TIMESTAMP for precision, DATE where time not needed

### Constraints
- **Primary Keys**: All tables have UUID primary keys
- **Foreign Keys**: Proper cascading (CASCADE or SET NULL)
- **Unique**: Email addresses, estimate per project per estimator
- **Checks**: Ratings between 1.0-5.0, completion 0-100%

---

## Performance Considerations

### Indexing Strategy
1. **Primary Keys**: Automatic B-tree indexes
2. **Foreign Keys**: Indexed for join performance
3. **Filter Fields**: Status, type, location fields
4. **Date Fields**: For time-series queries
5. **Composite**: Multi-column indexes for complex queries

### Query Optimization
- Use composite indexes for common filter combinations
- JSONB GIN indexes for JSON field queries
- Avoid SELECT * in production queries
- Use pagination for large result sets
- Leverage platform_metrics for dashboard performance

---

## Security & Privacy

### PII Fields
These fields contain personally identifiable information:
- email addresses
- phone numbers
- street addresses
- names

### Recommendations
1. Encrypt PII fields at rest
2. Hash/mask data in non-production environments
3. Implement row-level security (RLS) in PostgreSQL
4. Audit trail for PII access
5. GDPR/CCPA compliance considerations

---

## Schema Version Control

### Current Version
- **Version**: 1.0.0
- **Date**: 2025-11-30
- **Status**: Initial design complete

### Future Enhancements
Potential additions for v2.0:
- Payment transactions table
- Document storage metadata
- Notification preferences
- Audit trail table
- User sessions table
- API access logs

---

## Testing Checklist

### Schema Validation
- [ ] All tables created successfully
- [ ] All foreign keys working
- [ ] All indexes created
- [ ] Default values applied correctly
- [ ] CHECK constraints enforced

### Data Integrity
- [ ] Cannot insert orphaned records
- [ ] Cascading deletes work correctly
- [ ] Unique constraints prevent duplicates
- [ ] Date validations work
- [ ] Numeric ranges enforced

### Performance
- [ ] Indexes improve query speed
- [ ] Large table queries acceptable (<1s)
- [ ] Join queries optimized
- [ ] Aggregation queries fast

---

## Support & Documentation

### Additional Resources
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- UUID Best Practices: Standard UUID v4 format
- JSONB Performance: https://www.postgresql.org/docs/current/datatype-json.html

### Questions or Issues
Document any schema-related questions in project notes for team review.

---

**End of Schema Documentation**  
**Next Phase**: Synthetic Data Generation Scripts  
**Builder**: Carlos Gorricho