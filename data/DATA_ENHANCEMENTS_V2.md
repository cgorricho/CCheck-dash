# Construction Check - Data Generation V2 Enhancements

**Date:** 2025-12-01  
**Builder:** Carlos Gorricho  
**Generator:** `data/generators/generate_data_v2.py`

## Overview

Enhanced synthetic data generation to support two critical customer-facing dashboard visualizations:
1. **Estimate Refinement Funnel/Cone** - Progressive estimates narrowing confidence intervals
2. **Regional Cost Localization** - Location-based cost multipliers for benchmarking

---

## Enhancement #1: AACE Estimate Classes

### Implementation
Added industry-standard AACE International estimate classification system with 5 classes:

| Class | Name | Confidence Interval | Engineering Complete | Contingency | Use Case |
|-------|------|---------------------|---------------------|-------------|----------|
| **Class 5** | Conceptual | -50% to +100% | 0-2% | 20% | Screening/Feasibility |
| **Class 4** | Study/Feasibility | -30% to +50% | 1-15% | 15% | Concept Study |
| **Class 3** | Budget/Authorization | -20% to +30% | 10-40% | 12% | Budget/Control |
| **Class 2** | Control/Bid | -15% to +20% | 30-100% | 8% | Bid/Tender |
| **Class 1** | Check/Bid | -10% to +15% | 50-100% | 5% | Final Bid |

### Database Schema Changes
**Table:** `estimates`

New fields:
```sql
estimate_sequence INTEGER DEFAULT 1            -- Sequential refinement number
aace_class TEXT                               -- class_5, class_4, class_3, class_2, class_1
engineering_completion_percent REAL            -- Design completion %
confidence_interval_low REAL                   -- Lower bound of estimate
confidence_interval_high REAL                  -- Upper bound of estimate
```

### Data Characteristics
- **40% of projects** receive progressive estimate refinement (2-5 estimates per project)
- **60% of projects** receive single/multiple estimates from different estimators
- Progressive refinements show:
  - Narrowing confidence intervals over time
  - Increasing engineering completion percentage
  - Decreasing contingency allowances
  - Class progression: 5 → 4 → 3 → 2 → 1

### Example: Progressive Estimate Refinement

Project ID: `000f23f6-7792-4c20-a67e-bffc9b362d9c`

| Seq | Class | Eng % | Estimate | Conf Low | Conf High | Date | Interval Width |
|-----|-------|-------|----------|----------|-----------|------|----------------|
| 1 | Class 5 | 11% | $95,761 | $27,092 | $108,370 | 2025-02-03 | **$81,278** |
| 2 | Class 4 | 16% | $46,406 | $37,929 | $81,277 | 2025-02-12 | **$43,348** |
| 3 | Class 3 | 26% | $69,374 | $43,348 | $70,440 | 2025-02-19 | **$27,092** |
| 4 | Class 2 | 67% | $55,332 | $46,057 | $65,022 | 2025-03-20 | **$18,965** |

**Notice:** Confidence interval narrows from $81K to $19K as project progresses!

---

## Enhancement #2: Progressive Estimate Refinement

### Concept
Same estimator provides multiple estimates for same project as engineering documentation progresses.

### Implementation
- **Selection Rate:** 40% of projects get progressive refinement
- **Refinement Count:** 2-5 estimates per selected project
- **Time Spacing:** 1-3 weeks between successive estimates
- **Estimator Consistency:** Same estimator for all refinements
- **Status Tracking:** Earlier estimates marked as `superseded`, final marked as `accepted`

### Key Metrics
- **Total Estimates Generated:** 2,108
- **Projects with Progressive Refinement:** 315 (40% of 800)
- **Single/Multi-Estimator Projects:** 485 (60% of 800)

### Visualization Opportunities
1. **Estimate Funnel Chart** - Show convergence to true cost
2. **Confidence Cone** - Narrowing prediction bands over time
3. **Engineering Progress Timeline** - Link design completion to accuracy
4. **Contingency Reduction Tracker** - Risk mitigation over project lifecycle

---

## Enhancement #3: Regional Cost Multipliers

### Concept
Construction costs vary significantly by location due to:
- Labor market differences
- Material availability/logistics
- Climate considerations (weather protection, insulation)
- Local regulations and permitting
- Union vs non-union markets

### Implementation

**Table:** `projects`

New field:
```sql
regional_cost_multiplier REAL DEFAULT 1.0     -- Location-based cost index
```

### Regional Multiplier Index

#### High-Cost Markets (1.20x - 2.00x)
```
HI (Hawaii)           2.00x    Island logistics, shipping
NY (New York)         1.35x    High labor, regulations
CA (California)       1.30x    Labor, regulations, seismic
MA (Massachusetts)    1.25x    Union labor, high COL
WA (Washington)       1.20x    Seattle metro premium
```

#### Above-Average Markets (1.08x - 1.50x)
```
MN (Minnesota)        1.50x    Winter construction challenges
IL (Illinois)         1.15x    Chicago metro, union labor
CO (Colorado)         1.12x    Denver metro growth
OR (Oregon)           1.10x    Portland metro premium
PA (Pennsylvania)     1.08x    Philadelphia regulations
```

#### Baseline Markets (0.96x - 1.00x)
```
TX (Texas)            1.00x    BASELINE reference
FL (Florida)          1.00x    Competitive market
NC (North Carolina)   0.98x
GA (Georgia)          0.97x
AZ (Arizona)          0.96x
```

#### Below-Average Markets (0.88x - 0.95x)
```
NV (Nevada)           0.95x
MI (Michigan)         0.93x
TN (Tennessee)        0.92x
OH (Ohio)             0.90x
IN (Indiana)          0.88x
```

### Verification: School Projects by Location

| State | Multiplier | Avg Budget | Projects |
|-------|------------|------------|----------|
| NY | 1.35x | $160,294 | 2 |
| CA | 1.30x | $1,363,864 | 2 |
| MA | 1.25x | $1,975,531 | 3 |
| IL | 1.15x | $424,704 | 2 |
| CO | 1.12x | $698,611 | 5 |
| TX | 1.00x | $1,268,978 | 4 |
| FL | 1.00x | $1,325,627 | 7 |
| AZ | 0.96x | $1,314,843 | 3 |

**Example:** Building identical high school:
- Florida (baseline): $1,000,000
- Minnesota (winter challenges): $1,500,000 (+50%)
- Hawaii (island logistics): $2,000,000 (+100%)

### Visualization Opportunities
1. **Cost Localization Map** - Heat map showing regional variations
2. **Project Type Benchmarking** - Compare costs for same building type across states
3. **Cost Normalization** - Adjust customer's projects to baseline for fair comparison
4. **Location Recommendation** - Identify cost-effective regions for expansion

---

## Dashboard Integration

### Customer Dashboard Requirements

#### 1. Estimate Refinement Funnel
**Chart Type:** Line chart with confidence bands

**Data Query:**
```sql
SELECT 
    e.estimate_sequence,
    e.aace_class,
    e.engineering_completion_percent,
    e.estimated_total_cost,
    e.confidence_interval_low,
    e.confidence_interval_high,
    e.submitted_date
FROM estimates e
WHERE e.project_id = ?
ORDER BY e.estimate_sequence
```

**Visual Elements:**
- X-axis: Time (submitted_date) or Engineering % Complete
- Y-axis: Cost ($)
- Center line: Estimated total cost
- Shaded area: Confidence interval (high to low)
- Annotations: AACE class labels
- Final line: Actual cost (if completed)

#### 2. Regional Cost Comparison
**Chart Type:** Horizontal bar chart or map

**Data Query:**
```sql
-- Customer's projects normalized to baseline
SELECT 
    p.project_id,
    p.project_title,
    p.project_state,
    p.regional_cost_multiplier,
    (p.estimated_budget_min + p.estimated_budget_max) / 2 as budget,
    ((p.estimated_budget_min + p.estimated_budget_max) / 2) / p.regional_cost_multiplier as normalized_budget
FROM projects p
WHERE p.business_id = ?

-- Industry benchmark for same project type
SELECT 
    project_state,
    regional_cost_multiplier,
    AVG((estimated_budget_min + estimated_budget_max) / 2) as avg_cost
FROM projects
WHERE project_subtype = ?
GROUP BY project_state, regional_cost_multiplier
```

**Visual Elements:**
- Show customer's project costs vs industry average
- Normalize all costs to baseline (TX = 1.0x)
- Color-code by cost variance (above/below average)
- Interactive: click state to see comparable projects

---

## Data Statistics

### Summary
```
Businesses:              150
Estimators:             350 (100 consultants, 250 freelancers)
Projects:               800
Estimates:            2,108
  - Progressive:      1,033 (from 315 projects)
  - Single/Multi:     1,075 (from 485 projects)
Reviews:               164
```

### AACE Class Distribution
```sql
SELECT aace_class, COUNT(*) as count
FROM estimates
GROUP BY aace_class;
```

Expected distribution:
- Class 5: ~20% (conceptual phase)
- Class 4: ~20% (feasibility)
- Class 3: ~20% (budget)
- Class 2: ~20% (bid prep)
- Class 1: ~20% (final bid)

### Progressive Refinement Stats
```sql
-- Projects with multiple progressive estimates
SELECT 
    COUNT(DISTINCT project_id) as progressive_projects,
    AVG(estimate_count) as avg_refinements
FROM (
    SELECT project_id, COUNT(*) as estimate_count
    FROM estimates
    GROUP BY project_id
    HAVING estimate_count > 1
);
```

---

## Next Steps

### Dashboard Development
1. **Rename** `business_dashboard_v2.py` → `platform_admin_dashboard.py`
2. **Build Customer Dashboard** with:
   - Estimate refinement funnel for customer's projects
   - Regional cost comparison vs industry benchmarks
   - Filter by business_id
3. **Build Estimator Dashboards** (Consultant & Freelancer)

### Additional Visualizations
- **Cost Confidence Over Time** - Track estimate accuracy improvement
- **Regional Cost Index Trends** - Historical multiplier changes
- **Project Complexity Scoring** - Link engineering % to cost variance
- **Estimator Performance by AACE Class** - Accuracy by estimate type

---

## Files Modified

### Created
- `data/generators/generate_data_v2.py` - Enhanced generator (1,016 lines)
- `data/DATA_ENHANCEMENTS_V2.md` - This documentation

### Database
- `data/construction_check.db` - Regenerated with enhancements

### Next to Update
- `dashboards/platform_admin_dashboard.py` (rename from business_dashboard_v2.py)
- `dashboards/customer_dashboard.py` (new - to be created)

---

**Generated:** 2025-12-01  
**Database Ready:** ✓  
**Dashboard Ready:** Pending customer dashboard development
