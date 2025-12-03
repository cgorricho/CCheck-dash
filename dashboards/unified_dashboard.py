#!/usr/bin/env python3
"""
Construction Check - Unified Multi-User Dashboard
Integrated showcase with tabs for all user perspectives

Builder: Carlos Gorricho
Date: 2025-12-01
"""

import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import pandas as pd
import sqlite3
from datetime import datetime

# Database connection
DB_PATH = '../data/construction_check.db'

# Demo IDs
DEMO_BUSINESS_ID = '0f65e92e-878d-4d7f-90c2-4d47773c7c7a'  # Blanchard, Taylor and Porter (default)
DEMO_CONSULTANT_ID = None  # To be selected
DEMO_FREELANCER_ID = None  # To be selected

def load_random_customers(limit=5):
    """Load random customers for selector"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        """
        SELECT b.business_id, b.company_name, b.city, b.state, COUNT(p.project_id) as project_count
        FROM businesses b
        LEFT JOIN projects p ON b.business_id = p.business_id
        GROUP BY b.business_id
        HAVING project_count >= 3
        ORDER BY RANDOM()
        LIMIT ?
        """,
        conn,
        params=[limit]
    )
    conn.close()
    return df

def load_random_consultants(limit=5):
    """Load random consultants for selector"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        """
        SELECT estimator_id, display_name, city, state, years_experience,
               estimate_accuracy_rate, client_satisfaction_score,
               total_estimates_delivered, win_rate
        FROM estimators
        WHERE estimator_type = 'consultant'
        ORDER BY RANDOM()
        LIMIT ?
        """,
        conn,
        params=[limit]
    )
    conn.close()
    return df

def load_random_freelancers(limit=5):
    """Load random freelancers for selector"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        """
        SELECT estimator_id, display_name, city, state, years_experience,
               estimate_accuracy_rate, client_satisfaction_score,
               total_estimates_delivered, hourly_rate
        FROM estimators
        WHERE estimator_type = 'freelance_expert'
        ORDER BY RANDOM()
        LIMIT ?
        """,
        conn,
        params=[limit]
    )
    conn.close()
    return df

def load_consultant_overview(estimator_id):
    """Load consultant-specific metrics"""
    conn = get_db_connection()
    
    estimator = pd.read_sql_query(
        "SELECT * FROM estimators WHERE estimator_id = ?",
        conn,
        params=[estimator_id]
    ).iloc[0] if pd.read_sql_query("SELECT COUNT(*) as c FROM estimators WHERE estimator_id = ?", conn, params=[estimator_id])['c'][0] > 0 else None
    
    if estimator is None:
        conn.close()
        return None
    
    # Total estimates delivered
    total_estimates = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM estimates WHERE estimator_id = ?",
        conn,
        params=[estimator_id]
    )['count'][0]
    
    # Revenue (simulated from estimates)
    total_revenue = pd.read_sql_query(
        "SELECT SUM(estimated_total_cost * 0.05) as revenue FROM estimates WHERE estimator_id = ?",
        conn,
        params=[estimator_id]
    )['revenue'][0]
    
    # Unique clients
    unique_clients = pd.read_sql_query(
        """
        SELECT COUNT(DISTINCT p.business_id) as count
        FROM estimates e
        JOIN projects p ON e.project_id = p.project_id
        WHERE e.estimator_id = ?
        """,
        conn,
        params=[estimator_id]
    )['count'][0]
    
    conn.close()
    
    return {
        'total_estimates': total_estimates,
        'total_revenue': total_revenue if total_revenue else 0,
        'unique_clients': unique_clients,
        'win_rate': estimator['win_rate'] if 'win_rate' in estimator else 0,
        'accuracy_rate': estimator['estimate_accuracy_rate'] if 'estimate_accuracy_rate' in estimator else 0,
        'satisfaction': estimator['client_satisfaction_score'] if 'client_satisfaction_score' in estimator else 0
    }

def load_freelancer_overview(estimator_id):
    """Load freelancer-specific metrics"""
    conn = get_db_connection()
    
    estimator = pd.read_sql_query(
        "SELECT * FROM estimators WHERE estimator_id = ?",
        conn,
        params=[estimator_id]
    ).iloc[0] if pd.read_sql_query("SELECT COUNT(*) as c FROM estimators WHERE estimator_id = ?", conn, params=[estimator_id])['c'][0] > 0 else None
    
    if estimator is None:
        conn.close()
        return None
    
    # Active projects
    active_projects = pd.read_sql_query(
        """
        SELECT COUNT(DISTINCT e.project_id) as count
        FROM estimates e
        JOIN projects p ON e.project_id = p.project_id
        WHERE e.estimator_id = ? AND e.status = 'accepted' AND p.status NOT IN ('completed', 'cancelled')
        """,
        conn,
        params=[estimator_id]
    )['count'][0]
    
    # Total earnings
    total_earnings = pd.read_sql_query(
        "SELECT SUM(estimated_total_cost * 0.03) as earnings FROM estimates WHERE estimator_id = ? AND status = 'accepted'",
        conn,
        params=[estimator_id]
    )['earnings'][0]
    
    # Total estimates
    total_estimates = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM estimates WHERE estimator_id = ?",
        conn,
        params=[estimator_id]
    )['count'][0]
    
    conn.close()
    
    return {
        'active_projects': active_projects,
        'total_earnings': total_earnings if total_earnings else 0,
        'total_estimates': total_estimates,
        'accuracy_rate': estimator['estimate_accuracy_rate'] if 'estimate_accuracy_rate' in estimator else 0,
        'satisfaction': estimator['client_satisfaction_score'] if 'client_satisfaction_score' in estimator else 0,
        'hourly_rate': estimator['hourly_rate'] if 'hourly_rate' in estimator else 0
    }

def load_estimator_info(estimator_id):
    """Load estimator information"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        "SELECT * FROM estimators WHERE estimator_id = ?",
        conn,
        params=[estimator_id]
    )
    conn.close()
    return df.iloc[0] if len(df) > 0 else None

def load_estimator_estimates_by_class(estimator_id):
    """Load estimate distribution by AACE class"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        """
        SELECT aace_class, COUNT(*) as count
        FROM estimates
        WHERE estimator_id = ?
        GROUP BY aace_class
        ORDER BY aace_class
        """,
        conn,
        params=[estimator_id]
    )
    conn.close()
    return df

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Construction Check - Platform Demo"

# Color scheme - Construction Check ACTUAL website branding
# Based on https://www.constructioncheck.io/ screenshot
COLORS = {
    # Primary - Construction Check Orange (brand signature color)
    'primary': '#FF9900',      # Vibrant orange ("Time & Money")
    'primary_light': '#FFB347', # Lighter orange
    'primary_dark': '#CC7A00',  # Darker orange
    
    # Secondary - Navy/Dark Blue
    'secondary': '#1a1f36',    # Dark navy blue (text and headers)
    'secondary_light': '#2d3748',
    
    # Success - Gray (matching bar chart)
    'success': '#64748b',      # Gray instead of green
    'success_light': '#94a3b8',
    
    # Warning/Accent - Use orange as primary accent
    'warning': '#FF9900',      # Orange
    'accent': '#FF9900',       # Orange accent
    
    # Danger - Red
    'danger': '#ef4444',
    
    # Neutral - Clean grays
    'neutral': '#64748b',
    'neutral_light': '#94a3b8',
    'neutral_dark': '#475569',
    
    # Background - Clean white with subtle grays
    'background': '#f8fafc',    # Very light gray (Construction Check style)
    'background_alt': '#f1f5f9', # Slightly darker gray
    'card': '#ffffff',          # Pure white for cards
    'text': '#1a1f36',         # Dark navy for text
    'text_light': '#64748b',   # Gray for secondary text
    'border': '#e2e8f0',       # Light border
    
    # Gradients - Navy to Orange
    'gradient_start': '#1a1f36',  # Navy
    'gradient_end': '#FF9900',     # Orange
    
    # AACE Class colors
    'class_5': '#ef4444',   # Red - Conceptual
    'class_4': '#FF9900',   # Orange - Feasibility (brand color)
    'class_3': '#fbbf24',   # Yellow - Budget
    'class_2': '#94a3b8',   # Light Gray - Bid Prep
    'class_1': '#64748b'    # Gray - Final Bid
}

# ============================================================================
# SHARED DATA LOADING FUNCTIONS
# ============================================================================

def get_db_connection():
    """Create database connection"""
    return sqlite3.connect(DB_PATH)

# Import data loading functions from individual dashboards
# (We'll use the same functions but consolidated here)

def load_customer_info(business_id):
    """Load customer business information"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        "SELECT * FROM businesses WHERE business_id = ?",
        conn,
        params=[business_id]
    )
    conn.close()
    return df.iloc[0] if len(df) > 0 else None

def load_customer_overview(business_id):
    """Load customer-specific metrics"""
    conn = get_db_connection()
    
    total_projects = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM projects WHERE business_id = ?",
        conn,
        params=[business_id]
    )['count'][0]
    
    active_projects = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM projects WHERE business_id = ? AND status NOT IN ('completed', 'cancelled')",
        conn,
        params=[business_id]
    )['count'][0]
    
    total_spent = pd.read_sql_query(
        "SELECT SUM((estimated_budget_min + estimated_budget_max) / 2) as total FROM projects WHERE business_id = ?",
        conn,
        params=[business_id]
    )['total'][0]
    
    avg_estimate_accuracy = pd.read_sql_query(
        """
        SELECT AVG(ABS(e.confidence_interval_high - e.confidence_interval_low)) as avg_interval
        FROM estimates e
        JOIN projects p ON e.project_id = p.project_id
        WHERE p.business_id = ? AND e.aace_class IN ('class_1', 'class_2')
        """,
        conn,
        params=[business_id]
    )['avg_interval'][0]
    
    conn.close()
    
    return {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'total_spent': total_spent if total_spent else 0,
        'avg_accuracy': avg_estimate_accuracy if avg_estimate_accuracy else 0
    }

def load_customer_projects(business_id):
    """Load all projects for customer"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        """
        SELECT 
            p.project_id,
            p.project_title,
            p.project_type,
            p.project_subtype,
            p.project_city || ', ' || p.project_state as location,
            p.status,
            (p.estimated_budget_min + p.estimated_budget_max) / 2 as budget,
            COUNT(e.estimate_id) as estimate_count,
            p.posted_date
        FROM projects p
        LEFT JOIN estimates e ON p.project_id = e.project_id
        WHERE p.business_id = ?
        GROUP BY p.project_id
        ORDER BY p.posted_date DESC
        """,
        conn,
        params=[business_id]
    )
    conn.close()
    return df

def load_estimate_funnel(project_id):
    """Load progressive estimates for funnel visualization"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        """
        SELECT 
            e.estimate_sequence,
            e.aace_class,
            e.engineering_completion_percent,
            e.estimated_total_cost,
            e.confidence_interval_low,
            e.confidence_interval_high,
            e.contingency_percent,
            e.submitted_date
        FROM estimates e
        WHERE e.project_id = ?
        ORDER BY e.estimate_sequence
        """,
        conn,
        params=[project_id]
    )
    conn.close()
    return df

def load_regional_cost_comparison(business_id):
    """Load regional cost comparison data"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        """
        SELECT 
            p.project_title,
            p.project_state,
            p.regional_cost_multiplier,
            (p.estimated_budget_min + p.estimated_budget_max) / 2 as actual_cost,
            ((p.estimated_budget_min + p.estimated_budget_max) / 2) / p.regional_cost_multiplier as national_baseline
        FROM projects p
        WHERE p.business_id = ?
        ORDER BY p.posted_date DESC
        LIMIT 10
        """,
        conn,
        params=[business_id]
    )
    conn.close()
    return df

def load_platform_overview():
    """Load platform-wide metrics for admin dashboard"""
    conn = get_db_connection()
    
    total_businesses = pd.read_sql_query("SELECT COUNT(*) as count FROM businesses", conn)['count'][0]
    total_estimators = pd.read_sql_query("SELECT COUNT(*) as count FROM estimators", conn)['count'][0]
    total_projects = pd.read_sql_query("SELECT COUNT(*) as count FROM projects", conn)['count'][0]
    active_projects = pd.read_sql_query("SELECT COUNT(*) as count FROM projects WHERE status NOT IN ('completed', 'cancelled')", conn)['count'][0]
    total_estimates = pd.read_sql_query("SELECT COUNT(*) as count FROM estimates", conn)['count'][0]
    
    conn.close()
    
    return {
        'total_businesses': total_businesses,
        'total_estimators': total_estimators,
        'total_projects': total_projects,
        'active_projects': active_projects,
        'total_estimates': total_estimates
    }

# ============================================================================
# LAYOUT COMPONENTS
# ============================================================================

def create_navigation_bar(active_tab):
    """Create navigation bar with tabs"""
    tabs = [
        {'id': 'customer', 'label': '👤 Customer View', 'icon': 'business'},
        {'id': 'consultant', 'label': '🏢 Consultant View', 'icon': 'work'},
        {'id': 'freelancer', 'label': '💼 Freelancer View', 'icon': 'person'},
        {'id': 'admin', 'label': '⚙️ Platform Admin', 'icon': 'admin'},
        {'id': 'schema', 'label': '📊 Data Schema', 'icon': 'schema'}
    ]
    
    tab_buttons = []
    for tab in tabs:
        is_active = tab['id'] == active_tab
        tab_buttons.append(
            html.Button(
                tab['label'],
                id=f"tab-{tab['id']}",
                n_clicks=0,
                style={
                    'padding': '0.75rem 1.5rem',
                    'fontSize': '0.875rem',
                    'fontWeight': '600',
                    'backgroundColor': COLORS['primary'] if is_active else 'white',
                    'color': 'white' if is_active else COLORS['text'],
                    'border': f"2px solid {COLORS['primary']}",
                    'borderRadius': '0.5rem',
                    'cursor': 'pointer',
                    'marginRight': '0.5rem',
                    'transition': 'all 0.2s'
                }
            )
        )
    
    return html.Div([
        html.Div([
            html.Div([
                html.H1('Construction Check', style={
                    'fontSize': '1.5rem',
                    'fontWeight': '700',
                    'color': 'white',
                    'margin': '0'
                }),
                html.P('Platform Demo - All User Perspectives', style={
                    'fontSize': '0.75rem',
                    'color': 'rgba(255,255,255,0.9)',
                    'margin': '0.25rem 0 0 0'
                })
            ]),
            html.Div(
                datetime.now().strftime('%B %d, %Y'),
                style={'fontSize': '0.75rem', 'color': 'rgba(255,255,255,0.8)'}
            )
        ], style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'center',
            'padding': '1rem 2rem',
            'background': f'linear-gradient(135deg, {COLORS["gradient_start"]} 0%, {COLORS["gradient_end"]} 100%)'
        }),
        
        html.Div(
            tab_buttons,
            style={
                'padding': '1rem 2rem',
                'backgroundColor': COLORS['background'],
                'borderBottom': '1px solid #e2e8f0'
            }
        )
    ])

def create_metric_card(title, value, subtitle=None, color='primary'):
    """Shared metric card component"""
    gradient = f'linear-gradient(135deg, {COLORS[color]} 0%, {COLORS.get(color + "_light", COLORS[color])} 100%)'
    
    return html.Div([
        html.Div([
            html.H3(title, style={
                'fontSize': '0.875rem',
                'fontWeight': '500',
                'color': 'white',
                'opacity': '0.9',
                'margin': '0 0 0.5rem 0'
            }),
            html.Div(str(value), style={
                'fontSize': '2rem',
                'fontWeight': '700',
                'color': 'white',
                'margin': '0',
                'lineHeight': '1'
            }),
            html.P(subtitle if subtitle else '', style={
                'fontSize': '0.75rem',
                'color': 'white',
                'opacity': '0.8',
                'margin': '0.5rem 0 0 0'
            }) if subtitle else None
        ], style={
            'padding': '1.5rem',
            'background': gradient,
            'borderRadius': '0.75rem',
            'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
        })
    ], style={'marginBottom': '1rem'})

# ============================================================================
# PAGE LAYOUTS
# ============================================================================

def create_customer_page():
    """Customer dashboard page"""
    return html.Div([
        html.Div([
            html.Div([
                html.H2('Customer Dashboard', 
                        style={'fontSize': '1.5rem', 'fontWeight': '600', 'color': COLORS['text'], 'margin': '0 0 0.5rem 0'}),
                html.P('Select a customer to view their dashboard', 
                       style={'fontSize': '0.875rem', 'color': COLORS['text_light']})
            ]),
            html.Div([
                html.Label('Select Customer:', style={'fontSize': '0.875rem', 'fontWeight': '500', 'marginRight': '0.5rem'}),
                dcc.Dropdown(
                    id='customer-selector',
                    options=[],
                    value=DEMO_BUSINESS_ID,
                    style={'width': '350px', 'display': 'inline-block'}
                )
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], style={'padding': '1.5rem 2rem', 'backgroundColor': COLORS['card'], 'borderBottom': '1px solid #e2e8f0', 'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}),
        
        html.Div(id='customer-content', style={'padding': '2rem', 'backgroundColor': COLORS['background']})
    ])

def create_consultant_page():
    """Consultant dashboard page"""
    return html.Div([
        html.Div([
            html.Div([
                html.H2('Consultant Dashboard', 
                        style={'fontSize': '1.5rem', 'fontWeight': '600', 'color': COLORS['text'], 'margin': '0 0 0.5rem 0'}),
                html.P('Select a consulting firm to view their metrics', 
                       style={'fontSize': '0.875rem', 'color': COLORS['text_light']})
            ]),
            html.Div([
                html.Label('Select Consultant:', style={'fontSize': '0.875rem', 'fontWeight': '500', 'marginRight': '0.5rem'}),
                dcc.Dropdown(
                    id='consultant-selector',
                    options=[],
                    value=None,
                    style={'width': '350px', 'display': 'inline-block'}
                )
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], style={'padding': '1.5rem 2rem', 'backgroundColor': COLORS['card'], 'borderBottom': '1px solid #e2e8f0', 'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}),
        
        html.Div(id='consultant-content', style={'padding': '2rem', 'backgroundColor': COLORS['background']})
    ])

def create_freelancer_page():
    """Freelancer dashboard page"""
    return html.Div([
        html.Div([
            html.Div([
                html.H2('Freelancer Dashboard', 
                        style={'fontSize': '1.5rem', 'fontWeight': '600', 'color': COLORS['text'], 'margin': '0 0 0.5rem 0'}),
                html.P('Select a freelance estimator to view their metrics', 
                       style={'fontSize': '0.875rem', 'color': COLORS['text_light']})
            ]),
            html.Div([
                html.Label('Select Freelancer:', style={'fontSize': '0.875rem', 'fontWeight': '500', 'marginRight': '0.5rem'}),
                dcc.Dropdown(
                    id='freelancer-selector',
                    options=[],
                    value=None,
                    style={'width': '350px', 'display': 'inline-block'}
                )
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], style={'padding': '1.5rem 2rem', 'backgroundColor': COLORS['card'], 'borderBottom': '1px solid #e2e8f0', 'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}),
        
        html.Div(id='freelancer-content', style={'padding': '2rem', 'backgroundColor': COLORS['background']})
    ])

def create_schema_page():
    """Data schema infographic page"""
    return html.Div([
        html.Div([
            html.H2('Data Schema Overview', style={'fontSize': '1.5rem', 'fontWeight': '600', 'color': COLORS['text']}),
            html.P('Database structure powering this demo', style={'fontSize': '0.875rem', 'color': COLORS['text_light']})
        ], style={'padding': '1.5rem 2rem', 'backgroundColor': COLORS['card'], 'borderBottom': '1px solid #e2e8f0'}),
        
        html.Div([
            html.Div([
                html.H3('📊 Database Overview', style={'fontSize': '1.5rem', 'marginBottom': '2rem', 'textAlign': 'center'}),
                
                # Core Tables
                html.Div([
                    html.Div([
                        html.Div('BUSINESSES', style={'fontSize': '1rem', 'fontWeight': '700', 'marginBottom': '0.5rem', 'color': COLORS['primary']}),
                        html.Ul([
                            html.Li('business_id (PK)', style={'fontSize': '0.75rem'}),
                            html.Li('company_name', style={'fontSize': '0.75rem'}),
                            html.Li('location (city, state)', style={'fontSize': '0.75rem'}),
                            html.Li('150 records', style={'fontSize': '0.75rem', 'fontWeight': '600', 'color': COLORS['success']})
                        ], style={'listStyle': 'none', 'padding': '0'})
                    ], style={'padding': '1rem', 'backgroundColor': '#eff6ff', 'borderRadius': '0.5rem', 'border': f'2px solid {COLORS["primary"]}'}),
                    
                    html.Div([
                        html.Div('ESTIMATORS', style={'fontSize': '1rem', 'fontWeight': '700', 'marginBottom': '0.5rem', 'color': COLORS['success']}),
                        html.Ul([
                            html.Li('estimator_id (PK)', style={'fontSize': '0.75rem'}),
                            html.Li('display_name', style={'fontSize': '0.75rem'}),
                            html.Li('estimator_type', style={'fontSize': '0.75rem'}),
                            html.Li('350 records', style={'fontSize': '0.75rem', 'fontWeight': '600', 'color': COLORS['success']})
                        ], style={'listStyle': 'none', 'padding': '0'})
                    ], style={'padding': '1rem', 'backgroundColor': '#f0fdf4', 'borderRadius': '0.5rem', 'border': f'2px solid {COLORS["success"]}'}),
                    
                    html.Div([
                        html.Div('PROJECTS', style={'fontSize': '1rem', 'fontWeight': '700', 'marginBottom': '0.5rem', 'color': COLORS['accent']}),
                        html.Ul([
                            html.Li('project_id (PK)', style={'fontSize': '0.75rem'}),
                            html.Li('business_id (FK)', style={'fontSize': '0.75rem'}),
                            html.Li('regional_cost_multiplier', style={'fontSize': '0.75rem', 'fontWeight': '600'}),
                            html.Li('800 records', style={'fontSize': '0.75rem', 'fontWeight': '600', 'color': COLORS['success']})
                        ], style={'listStyle': 'none', 'padding': '0'})
                    ], style={'padding': '1rem', 'backgroundColor': '#faf5ff', 'borderRadius': '0.5rem', 'border': f'2px solid {COLORS["accent"]}'})
                ], style={'display': 'flex', 'gap': '1rem', 'marginBottom': '2rem', 'justifyContent': 'center'}),
                
                # ESTIMATES (star of the show)
                html.Div([
                    html.Div('⭐ ESTIMATES', style={'fontSize': '1.25rem', 'fontWeight': '700', 'marginBottom': '0.5rem', 'color': COLORS['warning'], 'textAlign': 'center'}),
                    html.Div('Enhanced with AACE Classes & Progressive Refinement', style={'fontSize': '0.875rem', 'color': COLORS['text_light'], 'marginBottom': '1rem', 'textAlign': 'center'}),
                    html.Div([
                        html.Div([
                            html.Strong('Key Fields:', style={'display': 'block', 'marginBottom': '0.5rem'}),
                            html.Ul([
                                html.Li('estimate_id (PK)', style={'fontSize': '0.75rem'}),
                                html.Li('project_id (FK)', style={'fontSize': '0.75rem'}),
                                html.Li('estimator_id (FK)', style={'fontSize': '0.75rem'}),
                                html.Li('estimate_sequence', style={'fontSize': '0.75rem', 'fontWeight': '600'}),
                                html.Li('aace_class (class_5 → class_1)', style={'fontSize': '0.75rem', 'fontWeight': '600'}),
                                html.Li('engineering_completion_percent', style={'fontSize': '0.75rem', 'fontWeight': '600'}),
                                html.Li('confidence_interval_low/high', style={'fontSize': '0.75rem', 'fontWeight': '600'})
                            ], style={'listStyle': 'none', 'padding': '0', 'columnCount': '2', 'columnGap': '2rem'})
                        ], style={'flex': '1'}),
                        html.Div([
                            html.Strong('Statistics:', style={'display': 'block', 'marginBottom': '0.5rem'}),
                            html.Div('2,108 total estimates', style={'fontSize': '1.25rem', 'fontWeight': '700', 'color': COLORS['success'], 'marginBottom': '0.25rem'}),
                            html.Div('315 projects (40%) with progressive refinement', style={'fontSize': '0.875rem', 'marginBottom': '0.25rem'}),
                            html.Div('2-5 estimates per progressive project', style={'fontSize': '0.875rem'})
                        ], style={'flex': '1', 'textAlign': 'right'})
                    ], style={'display': 'flex', 'gap': '2rem'})
                ], style={'padding': '2rem', 'backgroundColor': '#fffbeb', 'borderRadius': '0.75rem', 'border': f'3px solid {COLORS["warning"]}', 'marginBottom': '2rem'}),
                
                # Supporting tables
                html.Div([
                    html.H4('Supporting Tables', style={'fontSize': '1rem', 'marginBottom': '1rem', 'color': COLORS['text_light']}),
                    html.Div([
                        html.Div('EXPERTISE (692)', style={'padding': '0.75rem', 'backgroundColor': COLORS['background'], 'borderRadius': '0.5rem', 'fontSize': '0.875rem'}),
                        html.Div('REVIEWS (164)', style={'padding': '0.75rem', 'backgroundColor': COLORS['background'], 'borderRadius': '0.5rem', 'fontSize': '0.875rem'})
                    ], style={'display': 'flex', 'gap': '1rem', 'justifyContent': 'center'})
                ], style={'textAlign': 'center'}),
                
                # Key Innovation
                html.Div([
                    html.H4('🎯 Key Innovation: Progressive Estimate Refinement', style={'fontSize': '1.25rem', 'marginBottom': '1rem', 'color': COLORS['primary']}),
                    html.P('Same estimator provides multiple estimates as engineering documentation progresses:', style={'fontSize': '0.875rem', 'marginBottom': '0.5rem'}),
                    html.Div('Class 5 (Conceptual) → Class 4 (Feasibility) → Class 3 (Budget) → Class 2 (Bid) → Class 1 (Final)', 
                             style={'fontSize': '0.875rem', 'fontWeight': '600', 'color': COLORS['primary'], 'textAlign': 'center', 'padding': '1rem', 'backgroundColor': '#eff6ff', 'borderRadius': '0.5rem'}),
                    html.P('Confidence intervals narrow from ±50-100% to ±10-15% as project matures', 
                           style={'fontSize': '0.875rem', 'marginTop': '0.5rem', 'fontStyle': 'italic', 'color': COLORS['text_light']})
                ], style={'marginTop': '2rem', 'padding': '1.5rem', 'backgroundColor': '#f8fafc', 'borderRadius': '0.75rem', 'border': '1px solid #e2e8f0'})
                
            ], style={
                'padding': '2rem',
                'backgroundColor': COLORS['card'],
                'borderRadius': '0.75rem',
                'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                'maxWidth': '1200px',
                'margin': '0 auto'
            })
        ], style={'padding': '2rem', 'backgroundColor': COLORS['background'], 'minHeight': '60vh'})
    ])

def load_geographic_estimators():
    """Load estimator distribution by state for heat map"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        """
        SELECT 
            state,
            COUNT(*) as count,
            AVG(client_satisfaction_score) as avg_rating,
            AVG(estimate_accuracy_rate) as avg_accuracy
        FROM estimators
        WHERE verification_status = 'verified'
        GROUP BY state
        """,
        conn
    )
    conn.close()
    return df

def load_project_status_data():
    """Load project counts by status"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        """
        SELECT status, COUNT(*) as count
        FROM projects
        GROUP BY status
        ORDER BY count DESC
        """,
        conn
    )
    conn.close()
    return df

def load_project_types():
    """Load top project types"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        """
        SELECT project_subtype, COUNT(*) as count
        FROM projects
        WHERE project_subtype IS NOT NULL
        GROUP BY project_subtype
        ORDER BY count DESC
        LIMIT 8
        """,
        conn
    )
    conn.close()
    return df

def create_admin_page():
    """Platform admin dashboard page"""
    overview = load_platform_overview()
    
    return html.Div([
        html.Div([
            html.H2('Platform Admin Dashboard', style={'fontSize': '1.5rem', 'fontWeight': '600', 'color': COLORS['text']}),
            html.P('Platform-wide metrics and analytics', style={'fontSize': '0.875rem', 'color': COLORS['text_light']})
        ], style={'padding': '1.5rem 2rem', 'backgroundColor': COLORS['card'], 'borderBottom': '1px solid #e2e8f0'}),
        
        html.Div([
            # Metrics
            html.Div([
                html.Div([create_metric_card('Total Businesses', overview['total_businesses'], 'Customers', 'primary')], 
                         style={'width': '20%', 'padding': '0 0.5rem'}),
                html.Div([create_metric_card('Total Estimators', overview['total_estimators'], 'Network', 'success')], 
                         style={'width': '20%', 'padding': '0 0.5rem'}),
                html.Div([create_metric_card('Total Projects', overview['total_projects'], 'All time', 'accent')], 
                         style={'width': '20%', 'padding': '0 0.5rem'}),
                html.Div([create_metric_card('Active Projects', overview['active_projects'], 'In progress', 'warning')], 
                         style={'width': '20%', 'padding': '0 0.5rem'}),
                html.Div([create_metric_card('Total Estimates', overview['total_estimates'], 'Delivered', 'primary')], 
                         style={'width': '20%', 'padding': '0 0.5rem'})
            ], style={'display': 'flex', 'marginBottom': '2rem'}),
            
            # Charts Row 1
            html.Div([
                html.Div([
                    html.H3('Estimator Network by State', style={'fontSize': '1.25rem', 'fontWeight': '600', 'marginBottom': '1rem'}),
                    dcc.Graph(id='admin-geo-map', config={'displayModeBar': False}, style={'height': '350px'})
                ], style={
                    'width': '50%',
                    'padding': '1.5rem',
                    'backgroundColor': COLORS['card'],
                    'borderRadius': '0.75rem',
                    'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                    'marginRight': '1rem'
                }),
                
                html.Div([
                    html.H3('Project Status Distribution', style={'fontSize': '1.25rem', 'fontWeight': '600', 'marginBottom': '1rem'}),
                    dcc.Graph(id='admin-status-chart', config={'displayModeBar': False}, style={'height': '350px'})
                ], style={
                    'width': '50%',
                    'padding': '1.5rem',
                    'backgroundColor': COLORS['card'],
                    'borderRadius': '0.75rem',
                    'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                })
            ], style={'display': 'flex', 'marginBottom': '2rem'}),
            
            # Charts Row 2
            html.Div([
                html.Div([
                    html.H3('Top Project Types', style={'fontSize': '1.25rem', 'fontWeight': '600', 'marginBottom': '1rem'}),
                    dcc.Graph(id='admin-types-chart', config={'displayModeBar': False}, style={'height': '300px'})
                ], style={
                    'width': '100%',
                    'padding': '1.5rem',
                    'backgroundColor': COLORS['card'],
                    'borderRadius': '0.75rem',
                    'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                })
            ], style={'marginBottom': '2rem'})
        ], style={'padding': '2rem', 'backgroundColor': COLORS['background'], 'minHeight': '60vh'})
    ])

# ============================================================================
# MAIN LAYOUT
# ============================================================================

app.layout = html.Div([
    dcc.Store(id='active-tab', data='customer'),
    html.Div(id='navigation-bar'),
    html.Div(id='page-content')
], style={
    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    'margin': '0',
    'padding': '0'
})

# ============================================================================
# CALLBACKS
# ============================================================================

@app.callback(
    Output('active-tab', 'data'),
    [Input('tab-customer', 'n_clicks'),
     Input('tab-consultant', 'n_clicks'),
     Input('tab-freelancer', 'n_clicks'),
     Input('tab-admin', 'n_clicks'),
     Input('tab-schema', 'n_clicks')],
    prevent_initial_call=True
)
def update_active_tab(customer_clicks, consultant_clicks, freelancer_clicks, admin_clicks, schema_clicks):
    """Update active tab based on button clicks"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return 'customer'
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    return button_id.replace('tab-', '')

@app.callback(
    [Output('navigation-bar', 'children'),
     Output('page-content', 'children')],
    Input('active-tab', 'data')
)
def render_page(active_tab):
    """Render navigation and page content based on active tab"""
    nav = create_navigation_bar(active_tab)
    
    if active_tab == 'customer':
        content = create_customer_page()
    elif active_tab == 'consultant':
        content = create_consultant_page()
    elif active_tab == 'freelancer':
        content = create_freelancer_page()
    elif active_tab == 'schema':
        content = create_schema_page()
    else:  # admin
        content = create_admin_page()
    
    return nav, content

# Customer page callbacks
@app.callback(
    [Output('customer-selector', 'options'),
     Output('customer-selector', 'value')],
    Input('active-tab', 'data')
)
def populate_customer_selector(active_tab):
    """Populate customer selector dropdown"""
    if active_tab != 'customer':
        return [], DEMO_BUSINESS_ID
    
    conn = get_db_connection()
    # Get DEMO customer info
    demo_customer = pd.read_sql_query(
        """
        SELECT b.business_id, b.company_name, b.city, b.state, COUNT(p.project_id) as project_count
        FROM businesses b
        LEFT JOIN projects p ON b.business_id = p.business_id
        WHERE b.business_id = ?
        GROUP BY b.business_id
        """,
        conn,
        params=[DEMO_BUSINESS_ID]
    )
    
    # Get 4 other random customers
    other_customers = pd.read_sql_query(
        """
        SELECT b.business_id, b.company_name, b.city, b.state, COUNT(p.project_id) as project_count
        FROM businesses b
        LEFT JOIN projects p ON b.business_id = p.business_id
        WHERE b.business_id != ?
        GROUP BY b.business_id
        HAVING project_count >= 3
        ORDER BY RANDOM()
        LIMIT 4
        """,
        conn,
        params=[DEMO_BUSINESS_ID]
    )
    conn.close()
    
    # Combine: demo first, then others
    df = pd.concat([demo_customer, other_customers], ignore_index=True)
    
    options = [
        {'label': f"{row['company_name']} ({row['city']}, {row['state']}) - {row['project_count']} projects",
         'value': row['business_id']}
        for idx, row in df.iterrows()
    ]
    
    return options, DEMO_BUSINESS_ID

@app.callback(
    Output('customer-content', 'children'),
    Input('customer-selector', 'value')
)
def update_customer_content(business_id):
    """Update customer dashboard content based on selected customer"""
    if not business_id:
        return html.Div()
    
    customer = load_customer_info(business_id)
    overview = load_customer_overview(business_id)
    
    return [
        # Metrics
        html.Div([
            html.Div([create_metric_card('Total Projects', overview['total_projects'], 'All time', 'primary')], 
                     style={'width': '25%', 'padding': '0 0.5rem'}),
            html.Div([create_metric_card('Active Projects', overview['active_projects'], 'In progress', 'success')], 
                     style={'width': '25%', 'padding': '0 0.5rem'}),
            html.Div([create_metric_card('Total Investment', f"${overview['total_spent']:,.0f}", 'Estimated', 'accent')], 
                     style={'width': '25%', 'padding': '0 0.5rem'}),
            html.Div([create_metric_card('Estimate Precision', f"±${overview['avg_accuracy']:,.0f}", 'Avg range', 'warning')], 
                     style={'width': '25%', 'padding': '0 0.5rem'})
        ], style={'display': 'flex', 'marginBottom': '2rem'}),
        
        # Charts Row: Funnel (left) and Regional (right) side by side
        html.Div([
            # Estimate Funnel Section (LEFT)
            html.Div([
                html.H3('Estimate Refinement Funnel', style={'fontSize': '1.25rem', 'fontWeight': '600', 'margin': '0 0 0.5rem 0'}),
                html.P('Progressive estimate convergence (AACE Classes 5→1)', style={'fontSize': '0.875rem', 'color': COLORS['text_light'], 'marginBottom': '1rem'}),
                
                dcc.Dropdown(
                    id='customer-project-selector',
                    options=[],
                    value=None,
                    placeholder='Select project...',
                    style={'marginBottom': '1rem'}
                ),
                
                dcc.Graph(id='customer-funnel-chart', config={'displayModeBar': False}, style={'height': '350px'}),
                html.Div(id='customer-funnel-insights', style={'marginTop': '1rem'})
            ], style={
                'width': '50%',
                'padding': '1.5rem',
                'backgroundColor': COLORS['card'],
                'borderRadius': '0.75rem',
                'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                'marginRight': '1rem'
            }),
            
            # Regional Cost Comparison (RIGHT)
            html.Div([
                html.H3('Regional Cost Analysis', style={'fontSize': '1.25rem', 'fontWeight': '600', 'marginBottom': '0.5rem'}),
                html.P('Your projects vs national averages (regional multipliers)', style={'fontSize': '0.875rem', 'color': COLORS['text_light'], 'marginBottom': '1rem'}),
                dcc.Graph(id='customer-regional-chart', config={'displayModeBar': False}, style={'height': '350px'})
            ], style={
                'width': '50%',
                'padding': '1.5rem',
                'backgroundColor': COLORS['card'],
                'borderRadius': '0.75rem',
                'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
            })
        ], style={'display': 'flex', 'marginBottom': '2rem'}),
        
        # Projects Table
        html.Div([
            html.H3('Your Projects', style={'fontSize': '1.25rem', 'fontWeight': '600', 'marginBottom': '1rem'}),
            html.Div(id='customer-projects-table')
        ], style={
            'padding': '1.5rem',
            'backgroundColor': COLORS['card'],
            'borderRadius': '0.75rem',
            'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
        })
    ]

@app.callback(
    [Output('customer-project-selector', 'options'),
     Output('customer-project-selector', 'value')],
    Input('customer-selector', 'value')
)
def populate_customer_projects(business_id):
    """Populate customer project selector"""
    if not business_id:
        return [], None
    
    df = load_customer_projects(business_id)
    progressive = df[df['estimate_count'] > 1].copy()
    
    if len(progressive) == 0:
        return [], None
    
    options = [
        {'label': f"{row['project_title']} ({row['estimate_count']} estimates)", 
         'value': row['project_id']}
        for idx, row in progressive.iterrows()
    ]
    
    return options, progressive.iloc[0]['project_id']

@app.callback(
    [Output('customer-funnel-chart', 'figure'),
     Output('customer-funnel-insights', 'children')],
    Input('customer-project-selector', 'value')
)
def update_customer_funnel(project_id):
    """Update estimate funnel chart"""
    if not project_id:
        return go.Figure(), html.Div()
    
    df = load_estimate_funnel(project_id)
    
    if len(df) == 0:
        return go.Figure(), html.Div("No estimates available")
    
    fig = go.Figure()
    
    # Confidence band
    fig.add_trace(go.Scatter(
        x=df['estimate_sequence'],
        y=df['confidence_interval_high'],
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['estimate_sequence'],
        y=df['confidence_interval_low'],
        mode='lines',
        line=dict(width=0),
        fillcolor='rgba(37, 99, 235, 0.2)',
        fill='tonexty',
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Estimate line
    fig.add_trace(go.Scatter(
        x=df['estimate_sequence'],
        y=df['estimated_total_cost'],
        mode='lines+markers',
        name='Estimate',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=10, color=COLORS['primary']),
        text=df.apply(lambda x: f"<b>{x['aace_class'].replace('class_', 'Class ').upper()}</b><br>" +
                                 f"${x['estimated_total_cost']:,.0f}<br>" +
                                 f"Engineering: {x['engineering_completion_percent']:.0f}%", axis=1),
        hovertemplate='%{text}<extra></extra>'
    ))
    
    fig.update_layout(
        xaxis_title="Estimate Refinement",
        yaxis_title="Project Cost ($)",
        margin=dict(l=0, r=0, t=20, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='inherit', size=12),
        xaxis=dict(showgrid=True, gridcolor='#f1f5f9', dtick=1),
        yaxis=dict(showgrid=True, gridcolor='#f1f5f9', tickprefix='$', tickformat=',.0f'),
        height=400
    )
    
    # Insights
    first_interval = df.iloc[0]['confidence_interval_high'] - df.iloc[0]['confidence_interval_low']
    last_interval = df.iloc[-1]['confidence_interval_high'] - df.iloc[-1]['confidence_interval_low']
    reduction = ((first_interval - last_interval) / first_interval * 100)
    
    insights = html.Div([
        html.Div([
            html.Div([
                html.Strong('Confidence Improvement', style={'fontSize': '0.875rem'}),
                html.Div(f"{reduction:.0f}% narrower", style={'fontSize': '1.5rem', 'fontWeight': '700', 'color': COLORS['success']})
            ], style={'flex': '1', 'padding': '1rem', 'backgroundColor': '#f0fdf4', 'borderRadius': '0.5rem', 'marginRight': '1rem'}),
            
            html.Div([
                html.Strong('Engineering Progress', style={'fontSize': '0.875rem'}),
                html.Div(f"{df.iloc[0]['engineering_completion_percent']:.0f}% → {df.iloc[-1]['engineering_completion_percent']:.0f}%", 
                         style={'fontSize': '1.5rem', 'fontWeight': '700', 'color': COLORS['primary']})
            ], style={'flex': '1', 'padding': '1rem', 'backgroundColor': '#eff6ff', 'borderRadius': '0.5rem', 'marginRight': '1rem'}),
            
            html.Div([
                html.Strong('AACE Class', style={'fontSize': '0.875rem'}),
                html.Div(f"{df.iloc[0]['aace_class'].replace('class_', '')} → {df.iloc[-1]['aace_class'].replace('class_', '')}", 
                         style={'fontSize': '1.5rem', 'fontWeight': '700', 'color': COLORS['accent']})
            ], style={'flex': '1', 'padding': '1rem', 'backgroundColor': '#faf5ff', 'borderRadius': '0.5rem'})
        ], style={'display': 'flex'})
    ])
    
    return fig, insights

@app.callback(
    Output('customer-regional-chart', 'figure'),
    Input('customer-selector', 'value')
)
def update_regional_chart(business_id):
    """Update regional cost comparison chart"""
    if not business_id:
        return go.Figure()
    
    df = load_regional_cost_comparison(business_id)
    
    if len(df) == 0:
        return go.Figure()
    
    # Truncate long project titles
    df['short_title'] = df['project_title'].apply(lambda x: x[:30] + '...' if len(x) > 30 else x)
    
    fig = go.Figure()
    
    # National baseline
    fig.add_trace(go.Bar(
        name='National Average',
        x=df['short_title'],
        y=df['national_baseline'],
        marker=dict(color=COLORS['neutral']),
        text=df['national_baseline'].apply(lambda x: f'${x:,.0f}'),
        textposition='outside'
    ))
    
    # Actual regional cost
    fig.add_trace(go.Bar(
        name='Regional Cost',
        x=df['short_title'],
        y=df['actual_cost'],
        marker=dict(color=COLORS['warning']),
        text=df.apply(lambda x: f"${x['actual_cost']:,.0f}<br>({x['regional_cost_multiplier']:.2f}x)", axis=1),
        textposition='outside'
    ))
    
    fig.update_layout(
        barmode='group',
        xaxis_title="Projects",
        yaxis_title="Estimated Cost ($)",
        margin=dict(l=0, r=0, t=20, b=100),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='inherit', size=11),
        xaxis=dict(showgrid=False, tickangle=-45),
        yaxis=dict(showgrid=True, gridcolor='#f1f5f9', tickprefix='$', tickformat=',.0f'),
        height=350,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    return fig

@app.callback(
    Output('customer-projects-table', 'children'),
    Input('customer-selector', 'value')
)
def update_customer_table(business_id):
    """Update customer projects table"""
    if not business_id:
        return html.Div()
    
    df = load_customer_projects(business_id)
    
    if len(df) == 0:
        return html.Div('No projects found', style={'color': COLORS['text_light'], 'padding': '1rem'})
    
    df['posted_date'] = pd.to_datetime(df['posted_date']).dt.strftime('%Y-%m-%d')
    
    return html.Table([
        html.Thead(
            html.Tr([
                html.Th('Project', style={'textAlign': 'left', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'textTransform': 'uppercase', 'color': COLORS['text_light']}),
                html.Th('Type', style={'textAlign': 'left', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'textTransform': 'uppercase', 'color': COLORS['text_light']}),
                html.Th('Location', style={'textAlign': 'left', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'textTransform': 'uppercase', 'color': COLORS['text_light']}),
                html.Th('Status', style={'textAlign': 'left', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'textTransform': 'uppercase', 'color': COLORS['text_light']}),
                html.Th('Budget', style={'textAlign': 'right', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'textTransform': 'uppercase', 'color': COLORS['text_light']}),
                html.Th('Estimates', style={'textAlign': 'center', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'textTransform': 'uppercase', 'color': COLORS['text_light']}),
                html.Th('Posted', style={'textAlign': 'left', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'textTransform': 'uppercase', 'color': COLORS['text_light']})
            ], style={'borderBottom': f"2px solid {COLORS['border']}"})
        ),
        html.Tbody([
            html.Tr([
                html.Td(row['project_title'], style={'padding': '0.75rem', 'fontSize': '0.875rem', 'color': COLORS['text']}),
                html.Td(row['project_subtype'], style={'padding': '0.75rem', 'fontSize': '0.875rem', 'color': COLORS['text_light']}),
                html.Td(row['location'], style={'padding': '0.75rem', 'fontSize': '0.875rem', 'color': COLORS['text_light']}),
                html.Td(
                    html.Span(row['status'], style={
                        'padding': '0.25rem 0.5rem',
                        'fontSize': '0.75rem',
                        'fontWeight': '600',
                        'borderRadius': '0.375rem',
                        'backgroundColor': '#eff6ff' if row['status'] == 'in_progress' else '#fef3c7' if row['status'] == 'posted' else '#f0fdf4',
                        'color': COLORS['primary'] if row['status'] == 'in_progress' else COLORS['warning'] if row['status'] == 'posted' else COLORS['success']
                    }),
                    style={'padding': '0.75rem', 'fontSize': '0.875rem'}
                ),
                html.Td(f"${row['budget']:,.0f}", style={'padding': '0.75rem', 'fontSize': '0.875rem', 'textAlign': 'right', 'fontWeight': '500', 'color': COLORS['text']}),
                html.Td(str(row['estimate_count']), style={'padding': '0.75rem', 'fontSize': '0.875rem', 'textAlign': 'center', 'color': COLORS['text']}),
                html.Td(row['posted_date'], style={'padding': '0.75rem', 'fontSize': '0.875rem', 'color': COLORS['text_light']})
            ], style={'borderBottom': f"1px solid {COLORS['border']}", 'transition': 'background-color 0.2s'}) for idx, row in df.iterrows()
        ])
    ], style={'width': '100%', 'borderCollapse': 'collapse'})

# Consultant callbacks
@app.callback(
    [Output('consultant-selector', 'options'),
     Output('consultant-selector', 'value')],
    Input('active-tab', 'data')
)
def populate_consultant_selector(active_tab):
    """Populate consultant selector dropdown"""
    if active_tab != 'consultant':
        return [], None
    
    df = load_random_consultants(5)
    options = [
        {'label': f"{row['display_name']} ({row['city']}, {row['state']}) - {row['years_experience']} yrs exp",
         'value': row['estimator_id']}
        for idx, row in df.iterrows()
    ]
    
    return options, df.iloc[0]['estimator_id'] if len(df) > 0 else None

@app.callback(
    Output('consultant-content', 'children'),
    Input('consultant-selector', 'value')
)
def update_consultant_content(estimator_id):
    """Update consultant dashboard content"""
    if not estimator_id:
        return html.Div()
    
    consultant = load_estimator_info(estimator_id)
    overview = load_consultant_overview(estimator_id)
    
    if overview is None:
        return html.Div("No data available")
    
    return [
        # Metrics
        html.Div([
            html.Div([create_metric_card('Total Estimates', overview['total_estimates'], 'Delivered', 'primary')], 
                     style={'width': '25%', 'padding': '0 0.5rem'}),
            html.Div([create_metric_card('Revenue', f"${overview['total_revenue']:,.0f}", 'Est. 5% fee', 'success')], 
                     style={'width': '25%', 'padding': '0 0.5rem'}),
            html.Div([create_metric_card('Unique Clients', overview['unique_clients'], 'Portfolio', 'accent')], 
                     style={'width': '25%', 'padding': '0 0.5rem'}),
            html.Div([create_metric_card('Win Rate', f"{overview['win_rate']:.1f}%", 'Conversion', 'warning')], 
                     style={'width': '25%', 'padding': '0 0.5rem'})
        ], style={'display': 'flex', 'marginBottom': '2rem'}),
        
        # Performance metrics
        html.Div([
            html.Div([
                html.H3('Performance Analytics', style={'fontSize': '1.25rem', 'fontWeight': '600', 'marginBottom': '1rem'}),
                dcc.Graph(id='consultant-aace-chart', config={'displayModeBar': False}, style={'height': '300px'})
            ], style={
                'width': '50%',
                'padding': '1.5rem',
                'backgroundColor': COLORS['card'],
                'borderRadius': '0.75rem',
                'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                'marginRight': '1rem'
            }),
            
            html.Div([
                html.H3('Key Metrics', style={'fontSize': '1.25rem', 'fontWeight': '600', 'marginBottom': '1.5rem'}),
                html.Div([
                    html.Div([
                        html.Strong('Estimate Accuracy', style={'fontSize': '0.875rem', 'color': COLORS['text_light']}),
                        html.Div(f"{overview['accuracy_rate']:.1f}%", style={'fontSize': '2rem', 'fontWeight': '700', 'color': COLORS['success']})
                    ], style={'padding': '1rem', 'backgroundColor': '#f0fdf4', 'borderRadius': '0.5rem', 'marginBottom': '1rem'}),
                    
                    html.Div([
                        html.Strong('Client Satisfaction', style={'fontSize': '0.875rem', 'color': COLORS['text_light']}),
                        html.Div(f"{overview['satisfaction']:.1f} / 5.0", style={'fontSize': '2rem', 'fontWeight': '700', 'color': COLORS['primary']})
                    ], style={'padding': '1rem', 'backgroundColor': '#eff6ff', 'borderRadius': '0.5rem'})
                ])
            ], style={
                'width': '50%',
                'padding': '1.5rem',
                'backgroundColor': COLORS['card'],
                'borderRadius': '0.75rem',
                'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
            })
        ], style={'display': 'flex'})
    ]

@app.callback(
    Output('consultant-aace-chart', 'figure'),
    Input('consultant-selector', 'value')
)
def update_consultant_aace_chart(estimator_id):
    """Update consultant AACE class distribution"""
    if not estimator_id:
        return go.Figure()
    
    df = load_estimator_estimates_by_class(estimator_id)
    
    if len(df) == 0:
        return go.Figure()
    
    class_names = {
        'class_5': 'Class 5\nConceptual',
        'class_4': 'Class 4\nFeasibility',
        'class_3': 'Class 3\nBudget',
        'class_2': 'Class 2\nBid Prep',
        'class_1': 'Class 1\nFinal Bid'
    }
    
    df['name'] = df['aace_class'].map(class_names)
    df['color'] = df['aace_class'].map(COLORS)
    
    fig = go.Figure(data=[go.Bar(
        x=df['name'],
        y=df['count'],
        marker=dict(color=df['color']),
        text=df['count'],
        textposition='outside'
    )])
    
    fig.update_layout(
        xaxis_title="AACE Class",
        yaxis_title="Estimates Delivered",
        margin=dict(l=0, r=0, t=20, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='inherit', size=11),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
        height=300
    )
    
    return fig

# Freelancer callbacks
@app.callback(
    [Output('freelancer-selector', 'options'),
     Output('freelancer-selector', 'value')],
    Input('active-tab', 'data')
)
def populate_freelancer_selector(active_tab):
    """Populate freelancer selector dropdown"""
    if active_tab != 'freelancer':
        return [], None
    
    df = load_random_freelancers(5)
    options = [
        {'label': f"{row['display_name']} ({row['city']}, {row['state']}) - ${row['hourly_rate']:.0f}/hr",
         'value': row['estimator_id']}
        for idx, row in df.iterrows()
    ]
    
    return options, df.iloc[0]['estimator_id'] if len(df) > 0 else None

@app.callback(
    Output('freelancer-content', 'children'),
    Input('freelancer-selector', 'value')
)
def update_freelancer_content(estimator_id):
    """Update freelancer dashboard content"""
    if not estimator_id:
        return html.Div()
    
    freelancer = load_estimator_info(estimator_id)
    overview = load_freelancer_overview(estimator_id)
    
    if overview is None:
        return html.Div("No data available")
    
    return [
        # Metrics
        html.Div([
            html.Div([create_metric_card('Active Projects', overview['active_projects'], 'In progress', 'primary')], 
                     style={'width': '25%', 'padding': '0 0.5rem'}),
            html.Div([create_metric_card('Total Earnings', f"${overview['total_earnings']:,.0f}", 'Est. 3% fee', 'success')], 
                     style={'width': '25%', 'padding': '0 0.5rem'}),
            html.Div([create_metric_card('Estimates Delivered', overview['total_estimates'], 'All time', 'accent')], 
                     style={'width': '25%', 'padding': '0 0.5rem'}),
            html.Div([create_metric_card('Hourly Rate', f"${overview['hourly_rate']:.0f}", 'Per hour', 'warning')], 
                     style={'width': '25%', 'padding': '0 0.5rem'})
        ], style={'display': 'flex', 'marginBottom': '2rem'}),
        
        # Performance metrics
        html.Div([
            html.Div([
                html.H3('Work Distribution', style={'fontSize': '1.25rem', 'fontWeight': '600', 'marginBottom': '1rem'}),
                dcc.Graph(id='freelancer-aace-chart', config={'displayModeBar': False}, style={'height': '300px'})
            ], style={
                'width': '50%',
                'padding': '1.5rem',
                'backgroundColor': COLORS['card'],
                'borderRadius': '0.75rem',
                'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                'marginRight': '1rem'
            }),
            
            html.Div([
                html.H3('Reputation', style={'fontSize': '1.25rem', 'fontWeight': '600', 'marginBottom': '1.5rem'}),
                html.Div([
                    html.Div([
                        html.Strong('Estimate Accuracy', style={'fontSize': '0.875rem', 'color': COLORS['text_light']}),
                        html.Div(f"{overview['accuracy_rate']:.1f}%", style={'fontSize': '2rem', 'fontWeight': '700', 'color': COLORS['success']})
                    ], style={'padding': '1rem', 'backgroundColor': '#f0fdf4', 'borderRadius': '0.5rem', 'marginBottom': '1rem'}),
                    
                    html.Div([
                        html.Strong('Client Rating', style={'fontSize': '0.875rem', 'color': COLORS['text_light']}),
                        html.Div(f"{overview['satisfaction']:.1f} ⭐", style={'fontSize': '2rem', 'fontWeight': '700', 'color': COLORS['primary']})
                    ], style={'padding': '1rem', 'backgroundColor': '#eff6ff', 'borderRadius': '0.5rem'})
                ])
            ], style={
                'width': '50%',
                'padding': '1.5rem',
                'backgroundColor': COLORS['card'],
                'borderRadius': '0.75rem',
                'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
            })
        ], style={'display': 'flex'})
    ]

@app.callback(
    Output('freelancer-aace-chart', 'figure'),
    Input('freelancer-selector', 'value')
)
def update_freelancer_aace_chart(estimator_id):
    """Update freelancer AACE class distribution"""
    if not estimator_id:
        return go.Figure()
    
    df = load_estimator_estimates_by_class(estimator_id)
    
    if len(df) == 0:
        return go.Figure()
    
    class_names = {
        'class_5': 'Class 5',
        'class_4': 'Class 4',
        'class_3': 'Class 3',
        'class_2': 'Class 2',
        'class_1': 'Class 1'
    }
    
    df['name'] = df['aace_class'].map(class_names)
    df['color'] = df['aace_class'].map(COLORS)
    
    fig = go.Figure(data=[go.Pie(
        labels=df['name'],
        values=df['count'],
        marker=dict(colors=df['color']),
        textposition='inside',
        textinfo='percent+label'
    )])
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='inherit', size=11),
        height=300,
        showlegend=False
    )
    
    return fig

# Admin page callbacks
@app.callback(
    Output('admin-geo-map', 'figure'),
    Input('active-tab', 'data')
)
def update_admin_geo_map(active_tab):
    """Update geographic estimator map"""
    if active_tab != 'admin':
        return go.Figure()
    
    df = load_geographic_estimators()
    
    if len(df) == 0:
        return go.Figure()
    
    fig = go.Figure(data=go.Choropleth(
        locations=df['state'],
        z=df['count'],
        locationmode='USA-states',
        colorscale='Blues',
        text=df['state'],
        marker_line_color='white',
        colorbar_title="Estimators"
    ))
    
    fig.update_layout(
        geo=dict(
            scope='usa',
            projection=go.layout.geo.Projection(type='albers usa'),
            showlakes=True,
            lakecolor='rgb(255, 255, 255)'
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        height=350
    )
    
    return fig

@app.callback(
    Output('admin-status-chart', 'figure'),
    Input('active-tab', 'data')
)
def update_admin_status_chart(active_tab):
    """Update project status chart"""
    if active_tab != 'admin':
        return go.Figure()
    
    df = load_project_status_data()
    
    if len(df) == 0:
        return go.Figure()
    
    status_colors = {
        'posted': COLORS['warning'],
        'in_progress': COLORS['primary'],
        'completed': COLORS['success'],
        'cancelled': COLORS['danger']
    }
    
    df['color'] = df['status'].map(lambda x: status_colors.get(x, COLORS['neutral']))
    
    fig = go.Figure(data=[go.Bar(
        x=df['status'],
        y=df['count'],
        marker=dict(color=df['color']),
        text=df['count'],
        textposition='outside'
    )])
    
    fig.update_layout(
        xaxis_title="Status",
        yaxis_title="Projects",
        margin=dict(l=0, r=0, t=20, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='inherit', size=11),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
        height=350
    )
    
    return fig

@app.callback(
    Output('admin-types-chart', 'figure'),
    Input('active-tab', 'data')
)
def update_admin_types_chart(active_tab):
    """Update project types chart"""
    if active_tab != 'admin':
        return go.Figure()
    
    df = load_project_types()
    
    if len(df) == 0:
        return go.Figure()
    
    fig = go.Figure(data=[go.Bar(
        y=df['project_subtype'],
        x=df['count'],
        orientation='h',
        marker=dict(color=COLORS['primary']),
        text=df['count'],
        textposition='outside'
    )])
    
    fig.update_layout(
        xaxis_title="Number of Projects",
        yaxis_title="",
        margin=dict(l=0, r=0, t=20, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='inherit', size=11),
        xaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
        yaxis=dict(showgrid=False),
        height=300
    )
    
    return fig

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Construction Check - Unified Platform Demo")
    print("="*60)
    print("\n📊 AVAILABLE VIEWS:")
    print("  ✓ Customer Dashboard (5 random customers)")
    print("  ✓ Consultant Dashboard (5 random consultants)")
    print("  ✓ Freelancer Dashboard (5 random freelancers)")
    print("  ✓ Platform Admin Dashboard")
    print("  ✓ Data Schema Infographic")
    print("\n🎯 FEATURES:")
    print("  • Multi-page navigation with tabs")
    print("  • Dropdown selectors for each user type")
    print("  • Estimate Refinement Funnel (AACE Classes)")
    print("  • User-specific metrics & analytics")
    print("  • Performance & reputation tracking")
    print("\nStarting unified dashboard...")
    print("Open your browser to: http://127.0.0.1:8050")
    print("="*60 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=8050)
