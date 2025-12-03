# Construction Check Dashboard Prototype

[![Dashboard](https://img.shields.io/badge/Dashboard-Construction%20Check-FF9900)](https://www.constructioncheck.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Plotly Dash](https://img.shields.io/badge/Plotly-Dash-3F4F75.svg)](https://plotly.com/dash/)

> **Interactive multi-user dashboard prototype for Construction Check** - A construction cost estimating marketplace connecting businesses with professional estimators.

## 🎯 Project Overview

This project showcases technical expertise through the development of comprehensive, interactive dashboards for [Construction Check](https://www.constructioncheck.io/), demonstrating proficiency in data visualization, UI/UX design, and full-stack development for the construction industry.

### Key Features

- **5 Integrated Dashboard Views**: Customer, Consultant, Freelancer, Platform Admin, and Data Schema
- **AACE Estimate Refinement Tracking**: Progressive estimate convergence visualization (Classes 5→1)
- **Regional Cost Analysis**: Comparison of project costs vs national averages with regional multipliers
- **Synthetic Data Generation**: Realistic dataset with 150 businesses, 350 estimators, 800 projects, 2,108 estimates
- **Construction Check Branding**: Professional design using authentic brand colors (Orange #FF9900, Navy, Gray)

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/cgorricho/CCheck-dash.git
cd CCheck-dash

# Install dependencies
pip install dash plotly pandas
```

### Running the Dashboard

**Option 1: Using the launch script (recommended) - Background Mode**

The dashboard runs in a background tmux session, so you can close the terminal and it keeps running.

```bash
# Start dashboard in background
./run_dashboard.sh

# View dashboard logs (optional)
tmux attach -t ccheck-dashboard
# (Press Ctrl+B then D to detach from tmux)

# Stop dashboard
./stop_dashboard.sh
```

**Option 2: Direct Python execution - Foreground Mode**
```bash
# From the project root directory
cd dashboards
python unified_dashboard.py
# Press Ctrl+C to stop
```

Open your browser to `http://127.0.0.1:8050`

**Note**: Option 1 requires tmux. Install with: `sudo apt install tmux`

## 📊 Dashboard Views

### 1. Customer Dashboard
- **Project portfolio overview** with metrics (Total Projects, Active Projects, Investment, Estimate Precision)
- **Estimate Refinement Funnel**: Track progressive estimate convergence by AACE class
- **Regional Cost Analysis**: Compare project costs with national averages
- **Complete project table** with status, budgets, and estimate counts
- **Dropdown selector**: Choose from 5 random customers

### 2. Consultant Dashboard
- **Business metrics**: Total estimates delivered, revenue (5% platform fee), unique clients, win rate
- **Performance analytics**: AACE class distribution bar chart
- **Key metrics**: Estimate accuracy rate, client satisfaction scores
- **Dropdown selector**: Choose from 5 random consulting firms

### 3. Freelancer Dashboard
- **Freelancer metrics**: Active projects, earnings (3% platform fee), estimates delivered, hourly rate
- **Work distribution**: AACE class breakdown (pie chart)
- **Reputation tracking**: Accuracy rate and client ratings
- **Dropdown selector**: Choose from 5 random freelance estimators

### 4. Platform Admin Dashboard
- **Platform-wide KPIs**: Total businesses, estimators, projects, active projects, estimates
- **Geographic visualization**: Estimator network distribution by state (choropleth map)
- **Project analytics**: Status distribution and top project types
- **Network insights**: Real-time platform health monitoring

### 5. Data Schema View
- **Database overview infographic**: Visual representation of all tables and relationships
- **Schema details**: Table structures, record counts, foreign key relationships
- **Progressive refinement explanation**: AACE estimate class progression
- **Data statistics**: 800 projects, 2,108 estimates, 350 estimators, 150 businesses

## 🗄️ Database Structure

SQLite database (`data/construction_check.db`) with the following schema:

- **businesses** (150 records): Customer companies
- **estimators** (350 records): 100 consultants, 250 freelancers
- **projects** (800 records): Construction projects with regional cost multipliers
- **estimates** (2,108 records): Progressive estimates with AACE classes
- **reviews** (164 records): Client feedback
- **expertise** (692 records): Estimator specializations

### Key Features of Data
- **AACE Estimate Classes**: 5 (Conceptual, ±50-100%) → 1 (Final Bid, ±10-15%)
- **Progressive Refinement**: 40% of projects have 2-5 estimates showing convergence
- **Regional Multipliers**: 0.88x (Indiana) to 2.00x (Hawaii)
- **Realistic Distribution**: Proper status distribution, bid counts, satisfaction scores

## 🎨 Design & Branding

### Color Scheme (Construction Check Brand)
```python
Orange (Primary):  #FF9900  # Brand signature color
Navy (Secondary):  #1a1f36  # Text and headers
Gray (Neutral):    #64748b  # Supporting elements
White/Light Gray:  #f8fafc  # Clean backgrounds
```

### Design Principles
- Clean, professional Construction Check website-inspired layout
- Responsive card-based design with shadows and rounded corners
- Side-by-side chart layouts for better comparison
- Status badges with color coding
- Interactive dropdowns with default values

## 📁 Project Structure

```
CCheck-dash/
├── dashboards/
│   ├── unified_dashboard.py          # Main multi-user dashboard
│   ├── customer_dashboard.py         # Standalone customer view
│   ├── platform_admin_dashboard.py   # Standalone admin view
│   └── README.md
├── data/
│   ├── construction_check.db         # SQLite database
│   ├── generators/
│   │   ├── generate_data.py          # Initial data generator
│   │   └── generate_data_v2.py       # Enhanced with AACE & regional data
│   └── schema/
│       └── create_tables.sql         # Database schema
├── research/
│   └── 20251130-2149_construction_estimating_dashboard_research.md
└── README.md
```

## 🔧 Technical Stack

- **Framework**: Plotly Dash (Python)
- **Visualization**: Plotly Express & Graph Objects
- **Database**: SQLite3
- **Data Processing**: Pandas
- **UI Components**: Dash Core Components, Dash HTML Components

## 📈 Data Generation

Two versions of data generators included:

### V1 - Basic Data Generator
- Initial dataset with standard fields
- Simple random data generation

### V2 - Enhanced Data Generator
- **AACE Estimate Classes**: Industry-standard classification (5→1)
- **Progressive Refinement**: Multiple estimates per project showing convergence
- **Regional Cost Multipliers**: Geographic cost variations
- **Confidence Intervals**: Accuracy ranges by estimate class
- **Engineering Completion %**: Project maturity tracking

## 🎯 Use Cases

This prototype demonstrates capabilities for:
- **Construction marketplaces**: Multi-sided platform dashboards
- **Project management tools**: Progress tracking and analytics
- **Cost estimation software**: AACE-compliant estimate refinement
- **Professional networks**: Consultant/freelancer performance metrics
- **Data visualization**: Complex construction industry data

## 👨‍💻 Development

**Built by**: Carlos Gorricho  
**Purpose**: Technical demonstration for Construction Check CEO interview  
**Date**: November-December 2024  
**Status**: Prototype - Fully functional demo

### Development Highlights
- Researched Construction Check's business model and user needs
- Designed comprehensive database schema with industry standards
- Generated realistic synthetic data (2,100+ estimates)
- Built 5 integrated dashboard views with shared navigation
- Applied authentic Construction Check branding
- Implemented progressive estimate refinement visualization
- Created regional cost comparison features

## 🚀 Future Enhancements

Potential additions for production deployment:
- User authentication and role-based access control
- Real-time data updates and websocket integration
- Advanced filtering and search functionality
- Export capabilities (PDF reports, CSV data)
- Mobile-responsive design optimization
- Integration with Construction Check's existing platform
- AI-powered matching algorithm visualization
- Payment processing dashboard
- Messaging/communication features

## 📝 Documentation

Additional documentation available in the repository:
- `dashboards/DASHBOARD_SUMMARY.md`: Detailed dashboard feature descriptions
- `data/DATA_ENHANCEMENTS_V2.md`: Database enhancement documentation
- `research/`: Construction Check research and requirements
- `data/schema/`: Database design documentation

## 📄 License

This is a prototype project created for demonstration purposes.

## 🔗 Links

- **Construction Check Website**: https://www.constructioncheck.io/
- **Repository**: https://github.com/cgorricho/CCheck-dash

---

**Note**: This is a prototype dashboard created for demonstration purposes. It uses synthetic data and is not connected to Construction Check's production systems.
