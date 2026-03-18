# Construction Check — Analytics Dashboard Platform

Interactive multi-stakeholder dashboard prototype for [Construction Check](https://www.constructioncheck.io/), a construction cost estimating marketplace connecting businesses with professional estimators.

## What This Demonstrates

Five integrated dashboard views, each tailored to a different stakeholder in the construction cost estimation workflow — from the business requesting an estimate to the platform administrator monitoring marketplace health.

## Dashboard Views

### 1. Customer Dashboard
- Project portfolio overview with status tracking
- Estimate comparison across multiple estimators
- Cost variance analysis against budget
- AACE estimate class progression (Class 5 → Class 1)

### 2. Consultant Dashboard
- Active engagement pipeline
- Estimator team performance metrics
- Revenue tracking and forecasting
- Client satisfaction trends

### 3. Freelancer Dashboard
- Available project opportunities
- Personal performance metrics
- Earnings tracker with billing status
- Skill-based project matching

### 4. Platform Admin Dashboard
- Marketplace health metrics
- User acquisition and retention
- Transaction volume and revenue
- Quality assurance monitoring

### 5. Data Schema Explorer
- Interactive entity relationship visualization
- Table statistics and data quality metrics
- Schema documentation

## Technical Highlights

### AACE Estimate Refinement Tracking
Visualizes the progressive convergence of cost estimates through the AACE (Association for the Advancement of Cost Engineering) classification system — from Class 5 (conceptual, -50%/+100% accuracy) to Class 1 (definitive, -5%/+10% accuracy).

### Regional Cost Analysis
Comparison of project costs against national averages with regional multipliers — critical for construction estimating where labor and material costs vary significantly by geography.

### Synthetic Data Generation
Realistic dataset powering all dashboards:
- 150 businesses
- 350 estimators
- 800 projects
- 2,108 estimates
- Regional distribution across US markets

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Framework | Plotly Dash |
| Language | Python 3.8+ |
| Visualization | Plotly.js |
| Styling | Construction Check branding (Orange #FF9900, Navy, Gray) |

## Quick Start

```bash
pip install -r requirements.txt
python app.py
```

Open `http://localhost:8050` in your browser.
