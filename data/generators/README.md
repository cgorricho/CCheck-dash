# Data Generator

**Simple one-command data generation for dashboard development**

## Quick Start

```bash
cd /home/cgorricho/apps/CCheck/data/generators
pip install faker numpy
python3 generate_data.py
```

That's it! The database will be created at `/home/cgorricho/apps/CCheck/data/construction_check.db`

## What It Creates

- **150** businesses
- **350** estimators (100 consultants, 250 freelancers)
- **800** projects (24 months historical)
- **~1,600** estimates
- **~200** reviews
- **~700** expertise/certification records

## Data Features

✓ Realistic distributions (log-normal budgets, beta ratings)  
✓ Geographic spread (27 major US cities)  
✓ Industry-specific terminology  
✓ Proper relationships and integrity  
✓ Ready for dashboard queries

## Output

```
============================================================
Construction Check - Synthetic Data Generator
============================================================

Creating database schema...
✓ Database schema created
Generating 150 businesses...
✓ 150 businesses created
Generating 350 estimators...
✓ 350 estimators created (100 consultants, 250 freelancers)
Generating expertise records...
✓ 700 expertise records created
Generating 800 projects...
✓ 800 projects created
Generating estimates...
✓ 1600 estimates created
Generating reviews...
✓ 200 reviews created

============================================================
✓ Data generation complete!
  Database: ../construction_check.db
============================================================
```

## Next Step

Build the dashboard! The data is ready for Plotly Dash to query and visualize.
