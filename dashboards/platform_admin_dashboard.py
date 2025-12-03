#!/usr/bin/env python3
"""
Construction Check - Business User Dashboard V2
ENHANCED: Geographic Heat Maps, Accuracy Tracking, AI Matching, Multi-Level Drill-Down

Builder: Carlos Gorricho
Date: 2025-11-30
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import numpy as np

# Database connection
DB_PATH = '../data/construction_check.db'

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Construction Check - Business Dashboard"

# Color scheme - enhanced
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
    'accent': '#8b5cf6',  # Purple for highlights
    'gradient_start': '#2563eb',
    'gradient_end': '#7c3aed'
}

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def get_db_connection():
    """Create database connection"""
    return sqlite3.connect(DB_PATH)

def load_overview_data():
    """Load key metrics with enhancements"""
    conn = get_db_connection()
    
    active_projects = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM projects WHERE status NOT IN ('completed', 'cancelled')",
        conn
    )['count'][0]
    
    pending_estimates = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM projects WHERE status = 'posted'",
        conn
    )['count'][0]
    
    total_projects = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM projects",
        conn
    )['count'][0]
    
    avg_response = pd.read_sql_query(
        "SELECT AVG(average_response_hours) as avg FROM estimators WHERE verification_status = 'verified'",
        conn
    )['avg'][0]
    
    # NEW: Calculate potential savings
    completed_accurate = pd.read_sql_query(
        """
        SELECT COUNT(*) as count
        FROM estimates e
        JOIN projects p ON e.project_id = p.project_id
        WHERE e.status = 'accepted' 
            AND p.status = 'completed'
            AND e.variance_percent IS NOT NULL
            AND ABS(e.variance_percent) < 10
        """,
        conn
    )['count'][0]
    
    conn.close()
    
    return {
        'active_projects': active_projects,
        'pending_estimates': pending_estimates,
        'total_projects': total_projects,
        'avg_response_hours': round(avg_response, 1) if avg_response else 0,
        'accurate_estimates': completed_accurate
    }

def load_geographic_estimators():
    """Load estimator distribution by state for heat map"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        """
        SELECT 
            state,
            COUNT(*) as count,
            AVG(client_satisfaction_score) as avg_rating,
            AVG(estimate_accuracy_rate) as avg_accuracy,
            COUNT(CASE WHEN availability_status = 'available' THEN 1 END) as available_count
        FROM estimators
        WHERE verification_status = 'verified'
        GROUP BY state
        """,
        conn
    )
    conn.close()
    return df

def load_estimate_accuracy_data():
    """Load estimate vs actual cost data for scatter plot"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        """
        SELECT 
            e.estimated_total_cost,
            p.actual_cost,
            p.project_type,
            p.project_subtype,
            (p.actual_cost - e.estimated_total_cost) as variance_amount,
            ((p.actual_cost - e.estimated_total_cost) / e.estimated_total_cost * 100) as variance_percent,
            est.display_name as estimator_name
        FROM estimates e
        JOIN projects p ON e.project_id = p.project_id
        JOIN estimators est ON e.estimator_id = est.estimator_id
        WHERE e.status = 'accepted'
            AND p.status = 'completed'
            AND p.actual_cost IS NOT NULL
            AND e.estimated_total_cost > 0
        """,
        conn
    )
    conn.close()
    return df

def load_top_estimators():
    """Load top performing estimators for AI matching simulation"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        """
        SELECT 
            estimator_id,
            display_name,
            estimator_type,
            city,
            state,
            years_experience,
            hourly_rate,
            estimate_accuracy_rate,
            client_satisfaction_score,
            average_response_hours,
            total_estimates_delivered,
            win_rate
        FROM estimators
        WHERE verification_status = 'verified'
            AND account_status = 'active'
            AND total_estimates_delivered > 0
        ORDER BY 
            (estimate_accuracy_rate * 0.4 + 
             client_satisfaction_score * 20 * 0.3 + 
             (100 - average_response_hours/24*100) * 0.3) DESC
        LIMIT 10
        """,
        conn
    )
    conn.close()
    return df

def load_projects_by_status():
    """Load project counts by status"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        """
        SELECT 
            status,
            COUNT(*) as count,
            AVG((estimated_budget_min + estimated_budget_max) / 2) as avg_budget
        FROM projects
        GROUP BY status
        ORDER BY count DESC
        """,
        conn
    )
    conn.close()
    return df

def load_projects_by_type():
    """Load project distribution by type"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        """
        SELECT 
            project_subtype,
            COUNT(*) as count,
            AVG((estimated_budget_min + estimated_budget_max) / 2) as avg_budget
        FROM projects
        WHERE project_subtype IS NOT NULL
        GROUP BY project_subtype
        ORDER BY count DESC
        LIMIT 10
        """,
        conn
    )
    conn.close()
    return df

def load_recent_projects(status_filter=None, type_filter=None):
    """Load recent projects with optional filters"""
    conn = get_db_connection()
    
    query = """
        SELECT 
            project_id,
            project_title,
            project_type,
            project_subtype,
            project_city || ', ' || project_state as location,
            status,
            (estimated_budget_min + estimated_budget_max) / 2 as budget,
            number_of_bids,
            posted_date
        FROM projects
        WHERE 1=1
    """
    
    params = []
    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)
    if type_filter:
        query += " AND project_subtype = ?"
        params.append(type_filter)
    
    query += " ORDER BY posted_date DESC LIMIT 20"
    
    df = pd.read_sql_query(query, conn, params=params if params else None)
    conn.close()
    
    df['budget'] = df['budget'].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A")
    df['posted_date'] = pd.to_datetime(df['posted_date']).dt.strftime('%Y-%m-%d')
    
    return df

def load_projects_timeline():
    """Load project posting timeline"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        """
        SELECT 
            DATE(posted_date) as date,
            COUNT(*) as count,
            SUM((estimated_budget_min + estimated_budget_max) / 2) as total_value
        FROM projects
        WHERE posted_date >= date('now', '-6 months')
        GROUP BY DATE(posted_date)
        ORDER BY date
        """,
        conn
    )
    conn.close()
    df['date'] = pd.to_datetime(df['date'])
    return df

# ============================================================================
# LAYOUT COMPONENTS
# ============================================================================

def create_metric_card(title, value, subtitle=None, trend=None, color='primary'):
    """Enhanced metric card with gradients and trends"""
    gradient = f'linear-gradient(135deg, {COLORS[color]} 0%, {COLORS.get(color + "_light", COLORS[color])} 100%)'
    
    trend_indicator = None
    if trend:
        trend_color = COLORS['success'] if trend > 0 else COLORS['danger']
        trend_symbol = "↑" if trend > 0 else "↓"
        trend_indicator = html.Div([
            html.Span(f"{trend_symbol} {abs(trend)}%", style={
                'fontSize': '0.75rem',
                'color': trend_color,
                'fontWeight': '600'
            })
        ], style={'marginTop': '0.5rem'})
    
    return html.Div([
        html.Div([
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
                    'fontSize': '2.5rem',
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
                }) if subtitle else None,
                trend_indicator
            ])
        ], style={
            'padding': '1.5rem',
            'background': gradient,
            'borderRadius': '0.75rem',
            'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
            'transition': 'transform 0.2s',
            'cursor': 'pointer'
        }, className='metric-card')
    ], style={'marginBottom': '1rem'})

def create_section_header(title, subtitle=None, badge=None):
    """Enhanced section header with optional badge"""
    return html.Div([
        html.Div([
            html.H2(title, style={
                'fontSize': '1.25rem',
                'fontWeight': '600',
                'color': COLORS['text'],
                'margin': '0'
            }),
            html.Span(badge, style={
                'marginLeft': '0.75rem',
                'padding': '0.25rem 0.75rem',
                'fontSize': '0.75rem',
                'fontWeight': '600',
                'backgroundColor': COLORS['primary'],
                'color': 'white',
                'borderRadius': '9999px'
            }) if badge else None
        ], style={'display': 'flex', 'alignItems': 'center'}),
        html.P(subtitle if subtitle else '', style={
            'fontSize': '0.875rem',
            'color': COLORS['text_light'],
            'margin': '0.25rem 0 0 0'
        }) if subtitle else None
    ], style={'marginBottom': '1rem'})

# ============================================================================
# MAIN LAYOUT
# ============================================================================

overview = load_overview_data()

app.layout = html.Div([
    # Enhanced Header with gradient
    html.Div([
        html.Div([
            html.Div([
                html.H1('Construction Check', style={
                    'fontSize': '1.75rem',
                    'fontWeight': '700',
                    'color': 'white',
                    'margin': '0'
                }),
                html.P('Business Dashboard', style={
                    'fontSize': '0.875rem',
                    'color': 'rgba(255,255,255,0.9)',
                    'margin': '0.25rem 0 0 0'
                })
            ]),
            html.Div([
                html.Span(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", style={
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
                    'Active Projects',
                    overview['active_projects'],
                    'Currently in progress',
                    trend=12,
                    color='primary'
                )
            ], style={'width': '25%', 'padding': '0 0.5rem'}),
            
            html.Div([
                create_metric_card(
                    'Pending Estimates',
                    overview['pending_estimates'],
                    'Awaiting bids',
                    trend=-5,
                    color='warning'
                )
            ], style={'width': '25%', 'padding': '0 0.5rem'}),
            
            html.Div([
                create_metric_card(
                    'Accurate Estimates',
                    overview['accurate_estimates'],
                    'Within 10% variance',
                    trend=8,
                    color='success'
                )
            ], style={'width': '25%', 'padding': '0 0.5rem'}),
            
            html.Div([
                create_metric_card(
                    'Avg Response',
                    f"{overview['avg_response_hours']}h",
                    'From estimators',
                    color='accent'
                )
            ], style={'width': '25%', 'padding': '0 0.5rem'})
        ], style={
            'display': 'flex',
            'marginBottom': '2rem'
        }),
        
        # NEW: AI Matching Preview + Cost Savings
        html.Div([
            # AI Matching
            html.Div([
                create_section_header('AI-Powered Matching', 'Top recommendations for your next project', 'BETA'),
                html.Div(id='ai-matching-cards')
            ], style={
                'width': '60%',
                'padding': '1.5rem',
                'backgroundColor': COLORS['card'],
                'borderRadius': '0.75rem',
                'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                'marginRight': '1rem'
            }),
            
            # Cost Savings Calculator
            html.Div([
                create_section_header('Potential Savings', 'Using accurate estimates'),
                dcc.Graph(
                    id='savings-gauge',
                    config={'displayModeBar': False},
                    style={'height': '250px'}
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
        
        # Charts Row 1: Geographic + Accuracy
        html.Div([
            # Geographic Heat Map
            html.Div([
                create_section_header('Estimator Network', 'Click state to see available estimators'),
                dcc.Graph(
                    id='geo-map',
                    config={'displayModeBar': False},
                    style={'height': '350px'}
                )
            ], style={
                'width': '50%',
                'padding': '1.5rem',
                'backgroundColor': COLORS['card'],
                'borderRadius': '0.75rem',
                'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                'marginRight': '1rem'
            }),
            
            # Estimate Accuracy Scatter
            html.Div([
                create_section_header('Estimate Accuracy', 'Actual vs Estimated costs'),
                dcc.Graph(
                    id='accuracy-scatter',
                    config={'displayModeBar': False},
                    style={'height': '350px'}
                )
            ], style={
                'width': '50%',
                'padding': '1.5rem',
                'backgroundColor': COLORS['card'],
                'borderRadius': '0.75rem',
                'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
            })
        ], style={
            'display': 'flex',
            'marginBottom': '2rem'
        }),
        
        # Charts Row 2: Status + Types
        html.Div([
            html.Div([
                create_section_header('Project Status', 'Click to filter projects below'),
                dcc.Graph(
                    id='status-chart',
                    config={'displayModeBar': False},
                    style={'height': '300px'}
                )
            ], style={
                'width': '50%',
                'padding': '1.5rem',
                'backgroundColor': COLORS['card'],
                'borderRadius': '0.75rem',
                'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                'marginRight': '1rem'
            }),
            
            html.Div([
                create_section_header('Top Project Types', 'Click to filter'),
                dcc.Graph(
                    id='type-chart',
                    config={'displayModeBar': False},
                    style={'height': '300px'}
                )
            ], style={
                'width': '50%',
                'padding': '1.5rem',
                'backgroundColor': COLORS['card'],
                'borderRadius': '0.75rem',
                'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
            })
        ], style={
            'display': 'flex',
            'marginBottom': '2rem'
        }),
        
        # Timeline
        html.Div([
            html.Div([
                create_section_header('Project Activity', 'Last 6 months'),
                dcc.Graph(
                    id='timeline-chart',
                    config={'displayModeBar': False},
                    style={'height': '300px'}
                )
            ], style={
                'width': '100%',
                'padding': '1.5rem',
                'backgroundColor': COLORS['card'],
                'borderRadius': '0.75rem',
                'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
            })
        ], style={'marginBottom': '2rem'}),
        
        # Projects Table with Breadcrumbs
        html.Div([
            html.Div(id='breadcrumbs', style={'marginBottom': '1rem'}),
            create_section_header('Recent Projects', 'Multi-level filtering active'),
            html.Div(id='projects-table')
        ], style={
            'padding': '1.5rem',
            'backgroundColor': COLORS['card'],
            'borderRadius': '0.75rem',
            'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
        }),
        
        # Hidden stores for filter state
        dcc.Store(id='filter-status', data=None),
        dcc.Store(id='filter-type', data=None)
        
    ], style={
        'padding': '2rem',
        'backgroundColor': COLORS['background'],
        'minHeight': 'calc(100vh - 100px)'
    }),
    
    # CSS for hover effects
    
], style={
    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    'margin': '0',
    'padding': '0'
})

# ============================================================================
# CALLBACKS
# ============================================================================

@app.callback(
    Output('ai-matching-cards', 'children'),
    Input('filter-status', 'data')
)
def update_ai_matching(dummy):
    """Create AI matching recommendation cards"""
    df = load_top_estimators().head(3)
    
    cards = []
    for idx, row in df.iterrows():
        match_score = round(row['estimate_accuracy_rate'] * 0.4 + row['client_satisfaction_score'] * 20 * 0.3 + (100 - row['average_response_hours']/24*100) * 0.3, 1)
        
        card = html.Div([
            html.Div([
                html.Div([
                    html.Strong(f"#{idx+1}", style={'color': COLORS['primary'], 'fontSize': '0.875rem'}),
                    html.H4(row['display_name'], style={'margin': '0.25rem 0', 'fontSize': '1rem', 'fontWeight': '600'}),
                    html.P(f"{row['city']}, {row['state']} • {row['years_experience']} years exp", 
                           style={'fontSize': '0.75rem', 'color': COLORS['text_light'], 'margin': '0'})
                ], style={'flex': '1'}),
                html.Div([
                    html.Div(f"{match_score}%", style={
                        'fontSize': '1.5rem',
                        'fontWeight': '700',
                        'color': COLORS['success']
                    }),
                    html.Div('Match', style={'fontSize': '0.625rem', 'color': COLORS['text_light'], 'textAlign': 'center'})
                ])
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'start', 'marginBottom': '0.75rem'}),
            
            html.Div([
                html.Span(f"⭐ {row['client_satisfaction_score']:.1f}", style={'marginRight': '1rem', 'fontSize': '0.75rem'}),
                html.Span(f"🎯 {row['estimate_accuracy_rate']:.0f}% accuracy", style={'marginRight': '1rem', 'fontSize': '0.75rem'}),
                html.Span(f"⚡ {row['average_response_hours']:.0f}h response", style={'fontSize': '0.75rem'})
            ])
        ], style={
            'padding': '1rem',
            'backgroundColor': COLORS['background'],
            'borderRadius': '0.5rem',
            'marginBottom': '0.75rem',
            'border': f'2px solid {"#10b981" if idx == 0 else "#e2e8f0"}',
            'transition': 'all 0.2s',
            'cursor': 'pointer'
        })
        
        cards.append(card)
    
    return cards

@app.callback(
    Output('savings-gauge', 'figure'),
    Input('filter-status', 'data')
)
def update_savings_gauge(dummy):
    """Create cost savings gauge"""
    # Simulate potential savings (industry avg 15% variance vs Construction Check 8%)
    potential_savings = 7  # percentage points
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = potential_savings,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Cost Variance Reduction", 'font': {'size': 14}},
        delta = {'reference': 15, 'suffix': '%'},
        gauge = {
            'axis': {'range': [None, 20], 'ticksuffix': "%"},
            'bar': {'color': COLORS['success']},
            'steps': [
                {'range': [0, 5], 'color': '#dcfce7'},
                {'range': [5, 10], 'color': '#86efac'},
                {'range': [10, 20], 'color': '#fef3c7'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 15
            }
        }
    ))
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='inherit', size=12),
        height=250
    )
    
    return fig

@app.callback(
    Output('geo-map', 'figure'),
    Input('filter-status', 'data')
)
def update_geo_map(dummy):
    """Create geographic heat map of estimators"""
    df = load_geographic_estimators()
    
    fig = go.Figure(data=go.Choropleth(
        locations=df['state'],
        z=df['count'],
        locationmode='USA-states',
        colorscale=[[0, '#dbeafe'], [0.5, '#60a5fa'], [1, '#2563eb']],
        colorbar_title="Estimators",
        text=df.apply(lambda x: f"{x['state']}<br>{x['count']} estimators<br>{x['available_count']} available<br>⭐ {x['avg_rating']:.1f}", axis=1),
        hovertemplate='%{text}<extra></extra>',
        marker_line_color='white',
        marker_line_width=1
    ))
    
    fig.update_layout(
        geo=dict(
            scope='usa',
            projection=go.layout.geo.Projection(type='albers usa'),
            showlakes=False,
            lakecolor='rgb(255, 255, 255)',
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        height=350
    )
    
    return fig

@app.callback(
    Output('accuracy-scatter', 'figure'),
    Input('filter-status', 'data')
)
def update_accuracy_scatter(dummy):
    """Create estimate accuracy scatter plot"""
    df = load_estimate_accuracy_data()
    
    if len(df) == 0:
        return go.Figure()
    
    # Color by variance (green = accurate, red = off)
    df['color'] = df['variance_percent'].apply(
        lambda x: COLORS['success'] if abs(x) < 10 else COLORS['warning'] if abs(x) < 20 else COLORS['danger']
    )
    
    fig = go.Figure()
    
    # Perfect estimate line
    max_val = max(df['estimated_total_cost'].max(), df['actual_cost'].max())
    fig.add_trace(go.Scatter(
        x=[0, max_val],
        y=[0, max_val],
        mode='lines',
        name='Perfect Estimate',
        line=dict(color='gray', dash='dash', width=1),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Actual data points
    fig.add_trace(go.Scatter(
        x=df['estimated_total_cost'],
        y=df['actual_cost'],
        mode='markers',
        marker=dict(
            size=8,
            color=df['variance_percent'],
            colorscale=[[0, COLORS['success']], [0.5, COLORS['warning']], [1, COLORS['danger']]],
            showscale=True,
            colorbar=dict(title="Variance %", thickness=10, len=0.5)
        ),
        text=df.apply(lambda x: f"Estimator: {x['estimator_name']}<br>Estimated: ${x['estimated_total_cost']:,.0f}<br>Actual: ${x['actual_cost']:,.0f}<br>Variance: {x['variance_percent']:.1f}%", axis=1),
        hovertemplate='%{text}<extra></extra>',
        showlegend=False
    ))
    
    fig.update_layout(
        xaxis_title="Estimated Cost ($)",
        yaxis_title="Actual Cost ($)",
        margin=dict(l=0, r=0, t=0, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='inherit', size=11),
        xaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
        yaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
        height=350,
        hoverlabel=dict(bgcolor='white', font_size=11)
    )
    
    return fig

@app.callback(
    Output('status-chart', 'figure'),
    Input('filter-type', 'data')
)
def update_status_chart(type_filter):
    """Create project status chart"""
    df = load_projects_by_status()
    
    status_colors = {
        'completed': COLORS['success'],
        'in_progress': COLORS['primary'],
        'posted': COLORS['warning'],
        'in_bidding': COLORS['warning'],
        'matched': COLORS['primary'],
        'cancelled': COLORS['danger']
    }
    
    colors = [status_colors.get(status, COLORS['neutral']) for status in df['status']]
    
    fig = go.Figure(data=[
        go.Bar(
            x=df['count'],
            y=df['status'],
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(width=0)
            ),
            text=df['count'],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Count: %{x}<br>Avg Budget: $%{customdata:,.0f}<extra></extra>',
            customdata=df['avg_budget']
        )
    ])
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='inherit', size=12),
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=11)),
        height=300,
        hoverlabel=dict(bgcolor='white', font_size=12)
    )
    
    return fig

@app.callback(
    Output('type-chart', 'figure'),
    Input('filter-status', 'data')
)
def update_type_chart(status_filter):
    """Create project type chart"""
    df = load_projects_by_type()
    
    fig = go.Figure(data=[
        go.Bar(
            x=df['project_subtype'],
            y=df['count'],
            marker=dict(
                color=COLORS['primary'],
                line=dict(width=0)
            ),
            text=df['count'],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Projects: %{y}<br>Avg Budget: $%{customdata:,.0f}<extra></extra>',
            customdata=df['avg_budget']
        )
    ])
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='inherit', size=12),
        xaxis=dict(showgrid=False, tickangle=-45, tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor='#f1f5f9', zeroline=False),
        height=300,
        hoverlabel=dict(bgcolor='white', font_size=12)
    )
    
    return fig

@app.callback(
    Output('timeline-chart', 'figure'),
    Input('filter-status', 'data')
)
def update_timeline_chart(dummy):
    """Create timeline chart"""
    df = load_projects_timeline()
    
    fig = go.Figure(data=[
        go.Scatter(
            x=df['date'],
            y=df['count'],
            mode='lines+markers',
            line=dict(color=COLORS['primary'], width=3),
            marker=dict(size=6, color=COLORS['primary']),
            fill='tozeroy',
            fillcolor=f"rgba(37, 99, 235, 0.1)",
            hovertemplate='<b>%{x|%B %d, %Y}</b><br>Projects: %{y}<br>Total Value: $%{customdata:,.0f}<extra></extra>',
            customdata=df['total_value']
        )
    ])
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='inherit', size=12),
        xaxis=dict(showgrid=False, tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor='#f1f5f9', zeroline=False),
        height=300,
        hoverlabel=dict(bgcolor='white', font_size=12)
    )
    
    return fig

@app.callback(
    [Output('projects-table', 'children'),
     Output('breadcrumbs', 'children'),
     Output('filter-status', 'data'),
     Output('filter-type', 'data')],
    [Input('status-chart', 'clickData'),
     Input('type-chart', 'clickData')],
    [State('filter-status', 'data'),
     State('filter-type', 'data')]
)
def update_projects_table(status_click, type_click, current_status, current_type):
    """Update projects table with multi-level drill-down and breadcrumbs"""
    ctx = callback_context
    
    # Determine which filter changed
    if ctx.triggered:
        trigger = ctx.triggered[0]['prop_id']
        if 'status-chart' in trigger and status_click:
            current_status = status_click['points'][0]['y']
        elif 'type-chart' in trigger and type_click:
            current_type = type_click['points'][0]['x']
    
    # Load filtered data
    df = load_recent_projects(current_status, current_type)
    
    # Create breadcrumbs
    breadcrumb_items = [html.Span('All Projects', style={'color': COLORS['text_light'], 'fontSize': '0.875rem'})]
    if current_status:
        breadcrumb_items.append(html.Span(' > ', style={'margin': '0 0.5rem', 'color': COLORS['text_light']}))
        breadcrumb_items.append(html.Span(current_status, style={'color': COLORS['primary'], 'fontSize': '0.875rem', 'fontWeight': '500'}))
    if current_type:
        breadcrumb_items.append(html.Span(' > ', style={'margin': '0 0.5rem', 'color': COLORS['text_light']}))
        breadcrumb_items.append(html.Span(current_type, style={'color': COLORS['primary'], 'fontSize': '0.875rem', 'fontWeight': '500'}))
    
    if current_status or current_type:
        breadcrumb_items.append(
            html.Button('Clear All Filters', id='clear-filters', n_clicks=0, style={
                'marginLeft': '1rem',
                'padding': '0.25rem 0.75rem',
                'fontSize': '0.75rem',
                'backgroundColor': COLORS['danger'],
                'color': 'white',
                'border': 'none',
                'borderRadius': '0.25rem',
                'cursor': 'pointer'
            })
        )
    
    breadcrumbs = html.Div(breadcrumb_items, style={'display': 'flex', 'alignItems': 'center'})
    
    # Create table (same as before)
    table = html.Table([
        html.Thead(
            html.Tr([
                html.Th('Project', style={'textAlign': 'left', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'color': COLORS['text_light'], 'textTransform': 'uppercase'}),
                html.Th('Type', style={'textAlign': 'left', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'color': COLORS['text_light'], 'textTransform': 'uppercase'}),
                html.Th('Subtype', style={'textAlign': 'left', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'color': COLORS['text_light'], 'textTransform': 'uppercase'}),
                html.Th('Location', style={'textAlign': 'left', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'color': COLORS['text_light'], 'textTransform': 'uppercase'}),
                html.Th('Status', style={'textAlign': 'left', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'color': COLORS['text_light'], 'textTransform': 'uppercase'}),
                html.Th('Budget', style={'textAlign': 'right', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'color': COLORS['text_light'], 'textTransform': 'uppercase'}),
                html.Th('Bids', style={'textAlign': 'center', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'color': COLORS['text_light'], 'textTransform': 'uppercase'}),
                html.Th('Posted', style={'textAlign': 'left', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'color': COLORS['text_light'], 'textTransform': 'uppercase'})
            ], style={'borderBottom': '2px solid #e2e8f0'})
        ),
        html.Tbody([
            html.Tr([
                html.Td(row['project_title'], style={'padding': '0.75rem', 'fontSize': '0.875rem', 'color': COLORS['text']}),
                html.Td(row['project_type'], style={'padding': '0.75rem', 'fontSize': '0.875rem', 'color': COLORS['text_light']}),
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
                html.Td(row['budget'], style={'padding': '0.75rem', 'fontSize': '0.875rem', 'color': COLORS['text'], 'textAlign': 'right', 'fontWeight': '500'}),
                html.Td(str(row['number_of_bids']), style={'padding': '0.75rem', 'fontSize': '0.875rem', 'color': COLORS['text'], 'textAlign': 'center'}),
                html.Td(row['posted_date'], style={'padding': '0.75rem', 'fontSize': '0.875rem', 'color': COLORS['text_light']})
            ], style={'borderBottom': '1px solid #f1f5f9'}) for idx, row in df.iterrows()
        ])
    ], style={'width': '100%', 'borderCollapse': 'collapse'})
    
    return table, breadcrumbs, current_status, current_type

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Construction Check - Enhanced Business Dashboard V2")
    print("="*60)
    print("\n🚀 NEW FEATURES:")
    print("  • Geographic heat map of estimator network")
    print("  • Estimate accuracy tracking (scatter plot)")
    print("  • AI-powered matching preview")
    print("  • Cost savings calculator")
    print("  • Multi-level drill-down with breadcrumbs")
    print("  • Enhanced visuals with gradients & animations")
    print("\nStarting dashboard server...")
    print("Open your browser to: http://127.0.0.1:8050")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=8050)
