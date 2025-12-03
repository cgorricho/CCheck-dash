#!/usr/bin/env python3
"""
Construction Check - Business User Dashboard
Modern Minimalist Design with Drill-Down Capabilities

Builder: Carlos Gorricho
Date: 2025-11-30
"""

import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sqlite3
from datetime import datetime, timedelta

# Database connection
DB_PATH = '../data/construction_check.db'

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Construction Check - Business Dashboard"

# Color scheme - modern, professional
COLORS = {
    'primary': '#2563eb',      # Blue
    'success': '#10b981',      # Green
    'warning': '#f59e0b',      # Amber
    'danger': '#ef4444',       # Red
    'neutral': '#64748b',      # Slate
    'background': '#f8fafc',   # Light background
    'card': '#ffffff',         # White cards
    'text': '#1e293b',         # Dark text
    'text_light': '#64748b'    # Light text
}

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def get_db_connection():
    """Create database connection"""
    return sqlite3.connect(DB_PATH)

def load_overview_data():
    """Load key metrics for overview cards"""
    conn = get_db_connection()
    
    # Active projects
    active_projects = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM projects WHERE status NOT IN ('completed', 'cancelled')",
        conn
    )['count'][0]
    
    # Projects needing estimates
    pending_estimates = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM projects WHERE status = 'posted'",
        conn
    )['count'][0]
    
    # Total projects
    total_projects = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM projects",
        conn
    )['count'][0]
    
    # Average estimator response time
    avg_response = pd.read_sql_query(
        "SELECT AVG(average_response_hours) as avg FROM estimators WHERE verification_status = 'verified'",
        conn
    )['avg'][0]
    
    conn.close()
    
    return {
        'active_projects': active_projects,
        'pending_estimates': pending_estimates,
        'total_projects': total_projects,
        'avg_response_hours': round(avg_response, 1) if avg_response else 0
    }

def load_projects_by_status():
    """Load project counts by status"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        """
        SELECT 
            status,
            COUNT(*) as count
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
            AVG(estimated_budget_min + estimated_budget_max) / 2 as avg_budget
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

def load_recent_projects():
    """Load recent projects for table"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        """
        SELECT 
            project_title,
            project_type,
            project_city || ', ' || project_state as location,
            status,
            (estimated_budget_min + estimated_budget_max) / 2 as budget,
            number_of_bids,
            posted_date
        FROM projects
        ORDER BY posted_date DESC
        LIMIT 20
        """,
        conn
    )
    conn.close()
    
    df['budget'] = df['budget'].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A")
    df['posted_date'] = pd.to_datetime(df['posted_date']).dt.strftime('%Y-%m-%d')
    
    return df

def load_estimators_available():
    """Load available estimators count by location"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        """
        SELECT 
            state,
            COUNT(*) as count,
            AVG(client_satisfaction_score) as avg_rating
        FROM estimators
        WHERE availability_status = 'available' 
            AND verification_status = 'verified'
        GROUP BY state
        ORDER BY count DESC
        LIMIT 15
        """,
        conn
    )
    conn.close()
    return df

def load_projects_timeline():
    """Load project posting timeline"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        """
        SELECT 
            DATE(posted_date) as date,
            COUNT(*) as count
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

def load_cost_variance_data():
    """Load cost variance for completed projects"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        """
        SELECT 
            p.project_type,
            p.final_estimated_cost,
            p.actual_cost,
            p.cost_variance_percent
        FROM projects p
        WHERE p.status = 'completed' 
            AND p.final_estimated_cost IS NOT NULL 
            AND p.actual_cost IS NOT NULL
        """,
        conn
    )
    conn.close()
    return df

# ============================================================================
# LAYOUT COMPONENTS
# ============================================================================

def create_metric_card(title, value, subtitle=None, icon=None, color='primary'):
    """Create a metric card component"""
    return html.Div([
        html.Div([
            html.Div([
                html.H3(title, style={
                    'fontSize': '0.875rem',
                    'fontWeight': '500',
                    'color': COLORS['text_light'],
                    'margin': '0',
                    'marginBottom': '0.5rem'
                }),
                html.Div(str(value), style={
                    'fontSize': '2rem',
                    'fontWeight': '700',
                    'color': COLORS['text'],
                    'margin': '0'
                }),
                html.P(subtitle if subtitle else '', style={
                    'fontSize': '0.75rem',
                    'color': COLORS['text_light'],
                    'margin': '0.5rem 0 0 0'
                }) if subtitle else None
            ])
        ], style={
            'padding': '1.5rem',
            'backgroundColor': COLORS['card'],
            'borderRadius': '0.5rem',
            'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
            'border': f'1px solid #e2e8f0'
        })
    ], style={'marginBottom': '1rem'})

def create_section_header(title, subtitle=None):
    """Create section header"""
    return html.Div([
        html.H2(title, style={
            'fontSize': '1.25rem',
            'fontWeight': '600',
            'color': COLORS['text'],
            'margin': '0',
            'marginBottom': '0.25rem'
        }),
        html.P(subtitle if subtitle else '', style={
            'fontSize': '0.875rem',
            'color': COLORS['text_light'],
            'margin': '0'
        }) if subtitle else None
    ], style={'marginBottom': '1rem'})

# ============================================================================
# MAIN LAYOUT
# ============================================================================

overview = load_overview_data()

app.layout = html.Div([
    # Header
    html.Div([
        html.Div([
            html.Div([
                html.H1('Construction Check', style={
                    'fontSize': '1.5rem',
                    'fontWeight': '700',
                    'color': COLORS['text'],
                    'margin': '0'
                }),
                html.P('Business Dashboard', style={
                    'fontSize': '0.875rem',
                    'color': COLORS['text_light'],
                    'margin': '0.25rem 0 0 0'
                })
            ]),
            html.Div([
                html.Span(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", style={
                    'fontSize': '0.75rem',
                    'color': COLORS['text_light']
                })
            ])
        ], style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'center',
            'padding': '1.5rem 2rem',
            'backgroundColor': COLORS['card'],
            'borderBottom': '1px solid #e2e8f0'
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
                    color='primary'
                )
            ], style={'width': '25%', 'padding': '0 0.5rem'}),
            
            html.Div([
                create_metric_card(
                    'Pending Estimates',
                    overview['pending_estimates'],
                    'Awaiting bids',
                    color='warning'
                )
            ], style={'width': '25%', 'padding': '0 0.5rem'}),
            
            html.Div([
                create_metric_card(
                    'Total Projects',
                    overview['total_projects'],
                    'All time',
                    color='neutral'
                )
            ], style={'width': '25%', 'padding': '0 0.5rem'}),
            
            html.Div([
                create_metric_card(
                    'Avg Response Time',
                    f"{overview['avg_response_hours']}h",
                    'From estimators',
                    color='success'
                )
            ], style={'width': '25%', 'padding': '0 0.5rem'})
        ], style={
            'display': 'flex',
            'marginBottom': '2rem'
        }),
        
        # Charts Row 1
        html.Div([
            # Project Status Distribution
            html.Div([
                create_section_header('Project Status', 'Click to drill down'),
                dcc.Graph(
                    id='status-chart',
                    config={'displayModeBar': False},
                    style={'height': '300px'}
                )
            ], style={
                'width': '50%',
                'padding': '1.5rem',
                'backgroundColor': COLORS['card'],
                'borderRadius': '0.5rem',
                'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
                'marginRight': '1rem'
            }),
            
            # Project Types
            html.Div([
                create_section_header('Top Project Types', 'By volume'),
                dcc.Graph(
                    id='type-chart',
                    config={'displayModeBar': False},
                    style={'height': '300px'}
                )
            ], style={
                'width': '50%',
                'padding': '1.5rem',
                'backgroundColor': COLORS['card'],
                'borderRadius': '0.5rem',
                'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
            })
        ], style={
            'display': 'flex',
            'marginBottom': '2rem'
        }),
        
        # Charts Row 2
        html.Div([
            # Timeline
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
                'borderRadius': '0.5rem',
                'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
            })
        ], style={'marginBottom': '2rem'}),
        
        # Projects Table
        html.Div([
            create_section_header('Recent Projects', 'Click status chart to filter'),
            html.Div(id='projects-table')
        ], style={
            'padding': '1.5rem',
            'backgroundColor': COLORS['card'],
            'borderRadius': '0.5rem',
            'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
        }),
        
        # Hidden div for storing filter state
        dcc.Store(id='filter-status', data=None)
        
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
# CALLBACKS - DRILL-DOWN FUNCTIONALITY
# ============================================================================

@app.callback(
    Output('status-chart', 'figure'),
    Input('filter-status', 'data')
)
def update_status_chart(filter_status):
    """Create project status distribution chart"""
    df = load_projects_by_status()
    
    # Status color mapping
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
            marker=dict(color=colors),
            text=df['count'],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Count: %{x}<extra></extra>'
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
def update_type_chart(filter_status):
    """Create project type distribution chart"""
    df = load_projects_by_type()
    
    fig = go.Figure(data=[
        go.Bar(
            x=df['project_subtype'],
            y=df['count'],
            marker=dict(color=COLORS['primary']),
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
        xaxis=dict(
            showgrid=False, 
            tickangle=-45,
            tickfont=dict(size=10)
        ),
        yaxis=dict(showgrid=True, gridcolor='#f1f5f9', zeroline=False),
        height=300,
        hoverlabel=dict(bgcolor='white', font_size=12)
    )
    
    return fig

@app.callback(
    Output('timeline-chart', 'figure'),
    Input('filter-status', 'data')
)
def update_timeline_chart(filter_status):
    """Create project timeline chart"""
    df = load_projects_timeline()
    
    fig = go.Figure(data=[
        go.Scatter(
            x=df['date'],
            y=df['count'],
            mode='lines+markers',
            line=dict(color=COLORS['primary'], width=2),
            marker=dict(size=6, color=COLORS['primary']),
            fill='tozeroy',
            fillcolor=f"rgba(37, 99, 235, 0.1)",
            hovertemplate='<b>%{x|%B %d, %Y}</b><br>Projects Posted: %{y}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='inherit', size=12),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=10)
        ),
        yaxis=dict(showgrid=True, gridcolor='#f1f5f9', zeroline=False),
        height=300,
        hoverlabel=dict(bgcolor='white', font_size=12)
    )
    
    return fig

@app.callback(
    [Output('projects-table', 'children'),
     Output('filter-status', 'data')],
    [Input('status-chart', 'clickData')],
    [State('filter-status', 'data')]
)
def update_projects_table(clickData, current_filter):
    """Update projects table with drill-down from status chart"""
    # Determine filter
    filter_status = None
    if clickData:
        filter_status = clickData['points'][0]['y']
    
    # Load and filter data
    df = load_recent_projects()
    
    if filter_status:
        df = df[df['status'] == filter_status]
    
    # Create table
    table = html.Table([
        # Header
        html.Thead(
            html.Tr([
                html.Th('Project', style={'textAlign': 'left', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'color': COLORS['text_light'], 'textTransform': 'uppercase'}),
                html.Th('Type', style={'textAlign': 'left', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'color': COLORS['text_light'], 'textTransform': 'uppercase'}),
                html.Th('Location', style={'textAlign': 'left', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'color': COLORS['text_light'], 'textTransform': 'uppercase'}),
                html.Th('Status', style={'textAlign': 'left', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'color': COLORS['text_light'], 'textTransform': 'uppercase'}),
                html.Th('Budget', style={'textAlign': 'right', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'color': COLORS['text_light'], 'textTransform': 'uppercase'}),
                html.Th('Bids', style={'textAlign': 'center', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'color': COLORS['text_light'], 'textTransform': 'uppercase'}),
                html.Th('Posted', style={'textAlign': 'left', 'padding': '0.75rem', 'fontSize': '0.75rem', 'fontWeight': '600', 'color': COLORS['text_light'], 'textTransform': 'uppercase'})
            ], style={'borderBottom': '2px solid #e2e8f0'})
        ),
        # Body
        html.Tbody([
            html.Tr([
                html.Td(row['project_title'], style={'padding': '0.75rem', 'fontSize': '0.875rem', 'color': COLORS['text']}),
                html.Td(row['project_type'], style={'padding': '0.75rem', 'fontSize': '0.875rem', 'color': COLORS['text_light']}),
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
            ], style={
                'borderBottom': '1px solid #f1f5f9',
                'transition': 'background-color 0.2s'
            }) for idx, row in df.iterrows()
        ])
    ], style={
        'width': '100%',
        'borderCollapse': 'collapse'
    })
    
    # Add filter indicator
    if filter_status:
        filter_badge = html.Div([
            html.Span(f"Filtered by status: {filter_status}", style={
                'fontSize': '0.875rem',
                'color': COLORS['primary'],
                'fontWeight': '500'
            }),
            html.Button('Clear Filter', id='clear-filter', n_clicks=0, style={
                'marginLeft': '1rem',
                'padding': '0.25rem 0.75rem',
                'fontSize': '0.75rem',
                'backgroundColor': COLORS['background'],
                'border': '1px solid #e2e8f0',
                'borderRadius': '0.25rem',
                'cursor': 'pointer'
            })
        ], style={'marginBottom': '1rem'})
        
        return [filter_badge, table], filter_status
    
    return table, None

# ============================================================================
# RUN APP
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Construction Check - Business Dashboard")
    print("="*60)
    print("\nStarting dashboard server...")
    print("Open your browser to: http://127.0.0.1:8050")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=8050)
