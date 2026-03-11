# Construction Check Dashboards

**Modern, Interactive Dashboards with Drill-Down Capabilities**

## Quick Start

```bash
cd /home/cgorricho/apps/CCheck-dash/dashboards
pip install --user dash plotly pandas
python3 business_dashboard.py
```

Open browser to: **http://127.0.0.1:8050**

---

## Business Dashboard Features

### 📊 Key Metrics Cards
- Active Projects
- Pending Estimates  
- Total Projects
- Average Response Time

### 📈 Interactive Charts
1. **Project Status Distribution** (Horizontal Bar)
   - **CLICK TO DRILL DOWN** → Filters project table below
   - Color-coded by status type
   
2. **Top Project Types** (Vertical Bar)
   - Shows average budget on hover
   - Top 10 project subtypes
   
3. **Project Activity Timeline** (Line Chart)
   - Last 6 months trend
   - Area fill for visual impact

### 🔍 Drill-Down Capability

**Interactive Filtering Flow:**
```
Click any bar in "Project Status" chart
  ↓
Projects table automatically filters
  ↓
Shows only projects with that status
  ↓
"Clear Filter" button appears to reset
```

### 📋 Projects Table
- 20 most recent projects
- Filterable by status (via chart click)
- Color-coded status badges
- Formatted budget values

---

## Design Principles

✅ **Modern Minimalist** - Clean, professional aesthetic  
✅ **Card-Based Layout** - Scannable information hierarchy  
✅ **Responsive** - Works on different screen sizes  
✅ **Interactive** - Click-driven drill-down  
✅ **No Clutter** - Hidden toolbars, clean charts  

### Color Scheme
- **Primary**: Blue (#2563eb) - Actions, headers
- **Success**: Green (#10b981) - Positive metrics
- **Warning**: Amber (#f59e0b) - Attention needed
- **Danger**: Red (#ef4444) - Critical issues

---

## Technical Stack

- **Framework**: Plotly Dash
- **Charting**: Plotly Graph Objects
- **Data**: Pandas + SQLite
- **Styling**: Inline CSS (production-ready)

---

## Next Dashboards

Coming soon:
- Consultant Dashboard (track revenue, clients, performance)
- Freelancer Dashboard (find projects, earnings, ratings)

---

Press **Ctrl+C** in terminal to stop the server.