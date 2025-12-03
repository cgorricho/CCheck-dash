#!/usr/bin/env python3
"""
Construction Check - Customer Dashboard
Customer-specific view with estimate refinement funnel and regional cost benchmarking

Builder: Carlos Gorricho
Date: 2025-12-01
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sqlite3
from datetime import datetime
import numpy as np

# Database connection
DB_PATH = '../data/construction_check.db'

# DEMO: Default customer for demonstration
# In production, this would come from authentication/session
DEMO_BUSINESS_ID = '0f65e92e-878d-4d7f-90c2-4d47773c7c7a'  # Blanchard, Taylor and Porter

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Construction Check - Customer Dashboard"

# Color scheme
COLORS = {
    'primary': '#2563eb',
    'primary_light': '#60a5fa',
    'success': '#10b981',
    'success_light': '#34d399',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'neutral': '#64748b',
    'background': '#f8fafc',
    'card': '#ffffff',
    'text': '#1e293b',
    'text_light': '#64748b',
    'accent': '#8b5cf6',
    'gradient_start': '#2563eb',
    'gradient_end': '#7c3aed',
    
    # AACE class colors
    'class_5': '#ef4444',  # Red - high uncertainty
    'class_4': '#f59e0b',  # Orange
    'class_3': '#eab308',  # Yellow
    'class_2': '#84cc16',  # Lime
    'class_1': '#10b981'   # Green - high certainty
}

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def get_db_connection():
    """Create database connection"""
    return sqlite3.connect(DB_PATH)

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
            e.submitted_date,
            est.display_name as estimator_name
        FROM estimates e
        JOIN estimators est ON e.estimator_id = est.estimator_id
        WHERE e.project_id = ?
        ORDER BY e.estimate_sequence
        """,
        conn,
        params=[project_id]
    )
    conn.close()
    return df

def load_customer_projects(business_id):
    """Load all projects for customer with estimate counts"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        """
        SELECT 
            p.project_id,
            p.project_title,
            p.project_type,
            p.project_subtype,
            p.project_city || ', ' || p.project_state as location,
            p.project_state,
            p.regional_cost_multiplier,
            p.status,
            (p.estimated_budget_min + p.estimated_budget_max) / 2 as budget,
            p.posted_date,
            COUNT(e.estimate_id) as estimate_count,
            MAX(e.aace_class) as best_class
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

def load_regional_comparison(business_id):
    """Load regional cost comparison data"""
    conn = get_db_connection()
    
    # Customer's project costs by state
    customer_df = pd.read_sql_query(
        """
        SELECT 
            p.project_state,
            p.project_subtype,
            p.regional_cost_multiplier,
            AVG((p.estimated_budget_min + p.estimated_budget_max) / 2) as avg_cost,
            COUNT(*) as project_count
        FROM projects p
        WHERE p.business_id = ?
        GROUP BY p.project_state, p.project_subtype, p.regional_cost_multiplier
        """,
        conn,
        params=[business_id]
    )
    
    # Industry benchmark
    industry_df = pd.read_sql_query(
        """
        SELECT 
            project_state,
            project_subtype,
            regional_cost_multiplier,
            AVG((estimated_budget_min + estimated_budget_max) / 2) as avg_cost,
            COUNT(*) as project_count
        FROM projects
        GROUP BY project_state, project_subtype, regional_cost_multiplier
        HAVING project_count >= 3
        """
        ,
        conn
    )
    
    conn.close()
    
    return customer_df, industry_df

def load_aace_class_distribution(business_id):
    """Load AACE class distribution for customer's estimates"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        """
        SELECT 
            e.aace_class,
            COUNT(*) as count
        FROM estimates e
        JOIN projects p ON e.project_id = p.project_id
        WHERE p.business_id = ?
        GROUP BY e.aace_class
        ORDER BY e.aace_class
        """,
        conn,
        params=[business_id]
    )
    conn.close()
    return df

# ============================================================================
# LAYOUT COMPONENTS
# ============================================================================

def create_metric_card(title, value, subtitle=None, color='primary'):
    """Customer metric card"""
    gradient = f'linear-gradient(135deg, {COLORS[color]} 0%, {COLORS.get(color + "_light", COLORS[color])} 100%)'
    
    return html.Div([
        html.Div([
            html.H3(title, style={
                'fontSize': '0.875rem',
                'fontWeight': '500',
                'color': 'white',
                'opacity': '0.9',
                'margin': '0',
                'marginBottom': '0.5rem'
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
            'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        })
    ], style={'marginBottom': '1rem'})

# ============================================================================
# MAIN LAYOUT
# ============================================================================

customer = load_customer_info(DEMO_BUSINESS_ID)
overview = load_customer_overview(DEMO_BUSINESS_ID)

app.layout = html.Div([
    # Header
    html.Div([
        html.Div([
            html.Div([
                html.H1('Construction Check', style={
                    'fontSize': '1.75rem',
                    'fontWeight': '700',
                    'color': 'white',
                    'margin': '0'
                }),
                html.P(f"{customer['company_name']} Dashboard" if customer is not None else 'Customer Dashboard', style={
                    'fontSize': '0.875rem',
                    'color': 'rgba(255,255,255,0.9)',
                    'margin': '0.25rem 0 0 0'
                })
            ]),
            html.Div([
                html.Span(f"{customer['city']}, {customer['state']}" if customer is not None else '', style={
                    'fontSize': '0.75rem',
                    'color': 'rgba(255,255,255,0.8)',
                    'marginRight': '1rem'
                }),
                html.Span(f"Updated: {datetime.now().strftime('%b %d, %Y')}", style={
                    'fontSize': '0.75rem',
                    'color': 'rgba(255,255,255,0.8)'
                })
            ])
        ], style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'center',
            'padding': '1.5rem 2rem',
            'background': f'linear-gradient(135deg, {COLORS["gradient_start"]} 0%, {COLORS["gradient_end"]} 100%)',
        })
    ]),
    
    # Main Content
    html.Div([
        # Overview Cards
        html.Div([
            html.Div([
                create_metric_card(
                    'Total Projects',
                    overview['total_projects'],
                    'All time',
                    color='primary'
                )
            ], style={'width': '25%', 'padding': '0 0.5rem'}),
            
            html.Div([
                create_metric_card(
                    'Active Projects',
                    overview['active_projects'],
                    'In progress',
                    color='success'
                )
            ], style={'width': '25%', 'padding': '0 0.5rem'}),
            
            html.Div([
                create_metric_card(
                    'Total Investment',
                    f"${overview['total_spent']:,.0f}",
                    'Estimated budget',
                    color='accent'
                )
            ], style={'width': '25%', 'padding': '0 0.5rem'}),
            
            html.Div([
                create_metric_card(
                    'Estimate Precision',
                    f"±${overview['avg_accuracy']:,.0f}",
                    'Avg confidence range',
                    color='warning'
                )
            ], style={'width': '25%', 'padding': '0 0.5rem'})
        ], style={
            'display': 'flex',
            'marginBottom': '2rem'
        }),
        
        # PROJECT SELECTOR & ESTIMATE FUNNEL
        html.Div([
            html.Div([
                html.H2('Estimate Refinement Funnel', style={
                    'fontSize': '1.25rem',
                    'fontWeight': '600',
                    'color': COLORS['text'],
                    'margin': '0 0 0.5rem 0'
                }),
                html.P('Watch estimates converge as engineering documentation progresses', style={
                    'fontSize': '0.875rem',
                    'color': COLORS['text_light'],
                    'margin': '0 0 1rem 0'
                }),
                
                html.Label('Select Project:', style={'fontSize': '0.875rem', 'fontWeight': '500', 'color': COLORS['text']}),
                dcc.Dropdown(
                    id='project-selector',
                    options=[],
                    value=None,
                    style={'marginBottom': '1rem'}
                ),
                
                dcc.Graph(
                    id='estimate-funnel',
                    config={'displayModeBar': False},
                    style={'height': '400px'}
                ),
                
                html.Div(id='funnel-insights', style={'marginTop': '1rem'})
                
            ], style={
                'padding': '1.5rem',
                'backgroundColor': COLORS['card'],
                'borderRadius': '0.75rem',
                'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
            })
        ], style={'marginBottom': '2rem'}),
        
        # REGIONAL COST COMPARISON
        html.Div([
            html.Div([
                html.H2('Regional Cost Analysis', style={
                    'fontSize': '1.25rem',
                    'fontWeight': '600',
                    'color': COLORS['text'],
                    'margin': '0 0 0.5rem 0'
                }),
                html.P('Your project costs compared to industry benchmarks by location', style={
                    'fontSize': '0.875rem',
                    'color': COLORS['text_light'],
                    'margin': '0 0 1rem 0'
                }),
                
                dcc.Graph(
                    id='regional-comparison',
                    config={'displayModeBar': False},
                    style={'height': '350px'}
                )
            ], style={
                'width': '60%',
                'padding': '1.5rem',
                'backgroundColor': COLORS['card'],
                'borderRadius': '0.75rem',
                'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                'marginRight': '1rem'
            }),
            
            html.Div([
                html.H2('Estimate Class Distribution', style={
                    'fontSize': '1.25rem',
                    'fontWeight': '600',
                    'color': COLORS['text'],
                    'margin': '0 0 0.5rem 0'
                }),
                html.P('AACE estimate quality levels', style={
                    'fontSize': '0.875rem',
                    'color': COLORS['text_light'],
                    'margin': '0 0 1rem 0'
                }),
                
                dcc.Graph(
                    id='aace-distribution',
                    config={'displayModeBar': False},
                    style={'height': '350px'}
                )
            ], style={
                'width': '40%',
                'padding': '1.5rem',
                'backgroundColor': COLORS['card'],
                'borderRadius': '0.75rem',
                'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
            })
        ], style={
            'display': 'flex',
            'marginBottom': '2rem'
        }),
        
        # PROJECTS TABLE
        html.Div([
            html.H2('Your Projects', style={
                'fontSize': '1.25rem',
                'fontWeight': '600',
                'color': COLORS['text'],
                'margin': '0 0 1rem 0'
            }),
            html.Div(id='projects-table')
        ], style={
            'padding': '1.5rem',
            'backgroundColor': COLORS['card'],
            'borderRadius': '0.75rem',
            'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
        }),
        
        # Hidden store
        dcc.Store(id='business-id', data=DEMO_BUSINESS_ID)
        
    ], style={
        'padding': '2rem',
        'backgroundColor': COLORS['background'],
        'minHeight': 'calc(100vh - 100px)'
    })
    
], style={
    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    'margin': '0',
    'padding': '0'
})

# ============================================================================
# CALLBACKS
# ============================================================================

@app.callback(
    [Output('project-selector', 'options'),
     Output('project-selector', 'value')],
    Input('business-id', 'data')
)
def populate_project_selector(business_id):
    """Populate project dropdown with projects that have multiple estimates"""
    df = load_customer_projects(business_id)
    
    # Filter for projects with progressive estimates (multiple estimates)
    progressive = df[df['estimate_count'] > 1].copy()
    
    if len(progressive) == 0:
        return [], None
    
    options = [
        {'label': f"{row['project_title']} ({row['estimate_count']} estimates)", 
         'value': row['project_id']}
        for idx, row in progressive.iterrows()
    ]
    
    # Default to first project
    default_value = progressive.iloc[0]['project_id']
    
    return options, default_value

@app.callback(
    [Output('estimate-funnel', 'figure'),
     Output('funnel-insights', 'children')],
    Input('project-selector', 'value')
)
def update_estimate_funnel(project_id):
    """Create estimate refinement funnel chart"""
    if not project_id:
        return go.Figure(), html.Div()
    
    df = load_estimate_funnel(project_id)
    
    if len(df) == 0:
        return go.Figure(), html.Div("No estimates available")
    
    fig = go.Figure()
    
    # Confidence interval band (shaded area)
    fig.add_trace(go.Scatter(
        x=df['estimate_sequence'],
        y=df['confidence_interval_high'],
        mode='lines',
        name='Upper Bound',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['estimate_sequence'],
        y=df['confidence_interval_low'],
        mode='lines',
        name='Lower Bound',
        line=dict(width=0),
        fillcolor='rgba(37, 99, 235, 0.2)',
        fill='tonexty',
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Estimated cost line
    fig.add_trace(go.Scatter(
        x=df['estimate_sequence'],
        y=df['estimated_total_cost'],
        mode='lines+markers',
        name='Estimate',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=10, color=COLORS['primary']),
        text=df.apply(lambda x: f"<b>{x['aace_class'].replace('class_', 'Class ').upper()}</b><br>" +
                                 f"${x['estimated_total_cost']:,.0f}<br>" +
                                 f"Range: ±${(x['confidence_interval_high']-x['confidence_interval_low'])/2:,.0f}<br>" +
                                 f"Engineering: {x['engineering_completion_percent']:.0f}%<br>" +
                                 f"Contingency: {x['contingency_percent']:.1f}%", axis=1),
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
        height=400,
        hoverlabel=dict(bgcolor='white', font_size=12)
    )
    
    # Calculate insights
    first_interval = df.iloc[0]['confidence_interval_high'] - df.iloc[0]['confidence_interval_low']
    last_interval = df.iloc[-1]['confidence_interval_high'] - df.iloc[-1]['confidence_interval_low']
    reduction = ((first_interval - last_interval) / first_interval * 100)
    
    insights = html.Div([
        html.Div([
            html.Div([
                html.Strong('Confidence Improvement', style={'fontSize': '0.875rem', 'color': COLORS['text']}),
                html.Div(f"{reduction:.0f}% narrower", style={'fontSize': '1.5rem', 'fontWeight': '700', 'color': COLORS['success']})
            ], style={'flex': '1', 'padding': '1rem', 'backgroundColor': '#f0fdf4', 'borderRadius': '0.5rem', 'marginRight': '1rem'}),
            
            html.Div([
                html.Strong('Engineering Progress', style={'fontSize': '0.875rem', 'color': COLORS['text']}),
                html.Div(f"{df.iloc[0]['engineering_completion_percent']:.0f}% → {df.iloc[-1]['engineering_completion_percent']:.0f}%", 
                         style={'fontSize': '1.5rem', 'fontWeight': '700', 'color': COLORS['primary']})
            ], style={'flex': '1', 'padding': '1rem', 'backgroundColor': '#eff6ff', 'borderRadius': '0.5rem', 'marginRight': '1rem'}),
            
            html.Div([
                html.Strong('AACE Class', style={'fontSize': '0.875rem', 'color': COLORS['text']}),
                html.Div(f"{df.iloc[0]['aace_class'].replace('class_', '')} → {df.iloc[-1]['aace_class'].replace('class_', '')}", 
                         style={'fontSize': '1.5rem', 'fontWeight': '700', 'color': COLORS['accent']})
            ], style={'flex': '1', 'padding': '1rem', 'backgroundColor': '#faf5ff', 'borderRadius': '0.5rem'})
        ], style={'display': 'flex'})
    ])
    
    return fig, insights

@app.callback(
    Output('regional-comparison', 'figure'),
    Input('business-id', 'data')
)
def update_regional_comparison(business_id):
    """Create regional cost comparison chart"""
    customer_df, industry_df = load_regional_comparison(business_id)
    
    if len(customer_df) == 0:
        return go.Figure()
    
    # Aggregate customer data by state
    customer_agg = customer_df.groupby('project_state').agg({
        'avg_cost': 'mean',
        'regional_cost_multiplier': 'first',
        'project_count': 'sum'
    }).reset_index()
    
    # Aggregate industry data by state
    industry_agg = industry_df.groupby('project_state').agg({
        'avg_cost': 'mean',
        'regional_cost_multiplier': 'first',
        'project_count': 'sum'
    }).reset_index()
    
    # Merge to get states where customer has projects
    merged = customer_agg.merge(
        industry_agg, 
        on='project_state', 
        how='left',
        suffixes=('_customer', '_industry')
    )
    
    fig = go.Figure()
    
    # Industry benchmark bars
    fig.add_trace(go.Bar(
        x=merged['project_state'],
        y=merged['avg_cost_industry'],
        name='Industry Average',
        marker=dict(color=COLORS['neutral'], opacity=0.5),
        text=merged.apply(lambda x: f"${x['avg_cost_industry']:,.0f}", axis=1),
        textposition='outside'
    ))
    
    # Customer bars
    fig.add_trace(go.Bar(
        x=merged['project_state'],
        y=merged['avg_cost_customer'],
        name='Your Projects',
        marker=dict(color=COLORS['primary']),
        text=merged.apply(lambda x: f"${x['avg_cost_customer']:,.0f}<br>({x['regional_cost_multiplier_customer']:.2f}x)", axis=1),
        textposition='outside'
    ))
    
    fig.update_layout(
        xaxis_title="State",
        yaxis_title="Average Cost ($)",
        barmode='group',
        margin=dict(l=0, r=0, t=20, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='inherit', size=11),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#f1f5f9', tickprefix='$', tickformat=',.0f'),
        height=350,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hoverlabel=dict(bgcolor='white', font_size=11)
    )
    
    return fig

@app.callback(
    Output('aace-distribution', 'figure'),
    Input('business-id', 'data')
)
def update_aace_distribution(business_id):
    """Create AACE class distribution pie chart"""
    df = load_aace_class_distribution(business_id)
    
    if len(df) == 0:
        return go.Figure()
    
    # Map class to friendly names and colors
    class_names = {
        'class_5': 'Class 5<br>Conceptual',
        'class_4': 'Class 4<br>Feasibility',
        'class_3': 'Class 3<br>Budget',
        'class_2': 'Class 2<br>Bid Prep',
        'class_1': 'Class 1<br>Final Bid'
    }
    
    df['name'] = df['aace_class'].map(class_names)
    df['color'] = df['aace_class'].map(COLORS)
    
    fig = go.Figure(data=[go.Pie(
        labels=df['name'],
        values=df['count'],
        marker=dict(colors=df['color']),
        hole=0.4,
        textposition='inside',
        textinfo='percent+label'
    )])
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='inherit', size=11),
        height=350,
        showlegend=False
    )
    
    return fig

@app.callback(
    Output('projects-table', 'children'),
    Input('business-id', 'data')
)
def update_projects_table(business_id):
    """Create projects table"""
    df = load_customer_projects(business_id)
    
    if len(df) == 0:
        return html.Div("No projects found")
    
    df['posted_date'] = pd.to_datetime(df['posted_date']).dt.strftime('%Y-%m-%d')
    
    table = html.Table([
        html.Thead(
            html.Tr([
                html.Th('Project', style={'textAlign': 'left', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'color': COLORS['text_light'], 'textTransform': 'uppercase'}),
                html.Th('Type', style={'textAlign': 'left', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'color': COLORS['text_light'], 'textTransform': 'uppercase'}),
                html.Th('Location', style={'textAlign': 'left', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'color': COLORS['text_light'], 'textTransform': 'uppercase'}),
                html.Th('Status', style={'textAlign': 'left', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'color': COLORS['text_light'], 'textTransform': 'uppercase'}),
                html.Th('Budget', style={'textAlign': 'right', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'color': COLORS['text_light'], 'textTransform': 'uppercase'}),
                html.Th('Estimates', style={'textAlign': 'center', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'color': COLORS['text_light'], 'textTransform': 'uppercase'}),
                html.Th('Posted', style={'textAlign': 'left', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'color': COLORS['text_light'], 'textTransform': 'uppercase'})
            ], style={'borderBottom': '2px solid #e2e8f0'})
        ),
        html.Tbody([
            html.Tr([
                html.Td(row['project_title'], style={'padding': '0.75rem', 'fontSize': '0.875rem', 'color': COLORS['text']}),
                html.Td(row['project_subtype'], style={'padding': '0.75rem', 'fontSize': '0.875rem', 'color': COLORS['text_light']}),
                html.Td(row['location'], style={'padding': '0.75rem', 'fontSize': '0.875rem', 'color': COLORS['text_light']}),
                html.Td(
                    html.Span(row['status'], style={
                        'padding': '0.25rem 0.5rem',
                        'borderRadius': '0.25rem',
                        'fontSize': '0.75rem',
                        'fontWeight': '500',
                        'backgroundColor': '#dbeafe' if row['status'] in ['in_progress', 'matched'] else '#fef3c7' if row['status'] in ['posted', 'in_bidding'] else '#dcfce7' if row['status'] == 'completed' else '#fee2e2',
                        'color': '#1e40af' if row['status'] in ['in_progress', 'matched'] else '#92400e' if row['status'] in ['posted', 'in_bidding'] else '#166534' if row['status'] == 'completed' else '#991b1b'
                    }),
                    style={'padding': '0.75rem'}
                ),
                html.Td(f"${row['budget']:,.0f}", style={'padding': '0.75rem', 'fontSize': '0.875rem', 'color': COLORS['text'], 'textAlign': 'right', 'fontWeight': '500'}),
                html.Td(str(row['estimate_count']), style={'padding': '0.75rem', 'fontSize': '0.875rem', 'color': COLORS['text'], 'textAlign': 'center'}),
                html.Td(row['posted_date'], style={'padding': '0.75rem', 'fontSize': '0.875rem', 'color': COLORS['text_light']})
            ], style={'borderBottom': '1px solid #f1f5f9'}) for idx, row in df.iterrows()
        ])
    ], style={'width': '100%', 'borderCollapse': 'collapse'})
    
    return table

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Construction Check - Customer Dashboard")
    print("="*60)
    print("\n📊 CUSTOMER VIEW:")
    print(f"  • Company: {customer['company_name']}")
    print(f"  • Location: {customer['city']}, {customer['state']}")
    print(f"  • Projects: {overview['total_projects']}")
    print("\n🎯 KEY FEATURES:")
    print("  • Estimate Refinement Funnel (progressive estimates)")
    print("  • Regional Cost Comparison vs Industry")
    print("  • AACE Class Distribution")
    print("  • Customer-specific project list")
    print("\nStarting dashboard server...")
    print("Open your browser to: http://127.0.0.1:8050")
    print("="*60 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=8050)
