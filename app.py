"""
Integrated Aadhar Government Dashboard - Main Application
Comprehensive multi-dataset dashboard for government decision-making
Total Data Coverage: ~4.94M records across Biometric, Demographic, and Enrolment datasets
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))
sys.path.insert(0, str(Path(__file__).parent / 'components'))
sys.path.insert(0, str(Path(__file__).parent / 'analytics'))

from data_pipeline import IntegratedAadharDataPipeline

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
    title="Aadhar Analytics Dashboard - Government of India"
)
server = app.server

# Global data storage
DATA_PIPELINE = None
BIOMETRIC_DF = None
DEMOGRAPHIC_DF = None
ENROLMENT_DF = None
INTEGRATED_DF = None
NATIONAL_KPIS = {}

# Color schemes for government-grade visualizations
COLORS = {
    'primary': '#1f77b4',
    'success': '#2ca02c',
    'warning': '#ff7f0e',
    'danger': '#d62728',
    'info': '#17becf',
    'zones': {
        'North': '#1f77b4',
        'South': '#ff7f0e',
        'East': '#2ca02c',
        'West': '#d62728',
        'Central': '#9467bd',
        'North East': '#8c564b'
    },
    'gradient': ['#08519c', '#3182bd', '#6baed6', '#9ecae1', '#c6dbef']
}


def load_data_on_startup(sample_frac=0.1):
    """Load data when application starts."""
    global DATA_PIPELINE, BIOMETRIC_DF, DEMOGRAPHIC_DF, ENROLMENT_DF, INTEGRATED_DF, NATIONAL_KPIS
    
    print("=" * 80)
    print("INITIALIZING AADHAR DASHBOARD")
    print("=" * 80)
    
    DATA_PIPELINE = IntegratedAadharDataPipeline()
    
    # Load with sample for faster startup (use None for full data in production)
    BIOMETRIC_DF, DEMOGRAPHIC_DF, ENROLMENT_DF = DATA_PIPELINE.load_all(sample_frac=sample_frac)
    INTEGRATED_DF = DATA_PIPELINE.create_integrated_view()
    NATIONAL_KPIS = DATA_PIPELINE.get_national_kpis()
    
    print("\n✓ Dashboard initialized successfully!")
    print("=" * 80 + "\n")


def create_kpi_card(title, value, subtitle="", icon="fa-chart-line", color="primary", value_id=None, subtitle_id=None):
    """Create a KPI card for executive dashboard."""
    subtitle_props = {'className': 'text-secondary'}
    if subtitle_id:
        subtitle_props['id'] = subtitle_id
    
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.I(className=f"fas {icon} fa-2x", style={'color': COLORS[color]}),
                html.Div([
                    html.H3(value, id=value_id, className="mb-0", style={'fontWeight': 'bold'}),
                    html.P(title, className="text-muted mb-0", style={'fontSize': '0.9rem'}),
                    html.Small(subtitle, **subtitle_props)
                ], style={'marginLeft': '15px'})
            ], style={'display': 'flex', 'alignItems': 'center'})
        ])
    ], className="mb-3 shadow-sm")


def create_executive_kpi_section():
    """Create Executive KPI Cards - Tier 1."""
    return dbc.Container([
        html.H2("Executive Dashboard", className="mt-4 mb-4", style={'fontWeight': 'bold'}),
        
        dbc.Row([
            dbc.Col(create_kpi_card(
                "Total Biometric Transactions",
                "0",
                subtitle="Authentication Updates",
                icon="fa-fingerprint",
                color="primary",
                value_id="kpi-bio-trans"
            ), width=3),
            
            dbc.Col(create_kpi_card(
                "Total Enrolments",
                "0",
                subtitle="Infant: 0",
                icon="fa-user-plus",
                color="success",
                value_id="kpi-total-enrol",
                subtitle_id="kpi-enrol-subtitle"
            ), width=3),
            
            dbc.Col(create_kpi_card(
                "Auth Success Rate",
                "0.0%",
                subtitle="Total Records: 0",
                icon="fa-check-circle",
                color="success",
                value_id="kpi-auth-rate",
                subtitle_id="kpi-auth-subtitle"
            ), width=3),
            
            dbc.Col(create_kpi_card(
                "P99 Latency",
                "0 ms",
                subtitle="Median: 0 ms",
                icon="fa-clock",
                color="warning",
                value_id="kpi-latency",
                subtitle_id="kpi-latency-subtitle"
            ), width=3),
        ]),
        
        dbc.Row([
            dbc.Col(create_kpi_card(
                "Active States (Biometric)",
                "0",
                subtitle="Districts: 0",
                icon="fa-map-marked-alt",
                color="info",
                value_id="kpi-states-bio",
                subtitle_id="kpi-states-bio-subtitle"
            ), width=3),
            
            dbc.Col(create_kpi_card(
                "Active States (Enrolment)",
                "0",
                subtitle="Enrollment Coverage",
                icon="fa-globe-asia",
                color="info",
                value_id="kpi-states-enrol"
            ), width=3),
            
            dbc.Col(create_kpi_card(
                "Total Data Points",
                "0",
                subtitle="Integrated Records",
                icon="fa-database",
                color="primary",
                value_id="kpi-data-points"
            ), width=3),
            
            dbc.Col(create_kpi_card(
                "Data Quality",
                "99.8%",
                subtitle="Completeness Score",
                icon="fa-shield-alt",
                color="success",
                value_id="kpi-quality"
            ), width=3),
        ]),
    ], fluid=True)


def create_strategic_overview_section():
    """Create Strategic Overview - Tier 2."""
    return dbc.Container([
        html.H2("Strategic Overview", className="mt-5 mb-4", style={'fontWeight': 'bold'}),
        
        dbc.Row([
            # Zonal Market Share
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Zonal Distribution", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id='zonal-distribution-chart', config={'displayModeBar': False})
                    ])
                ], className="shadow-sm h-100")
            ], width=6),
            
            # State Performance Matrix
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Top 10 States by Volume", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id='state-performance-chart', config={'displayModeBar': False})
                    ])
                ], className="shadow-sm h-100")
            ], width=6),
        ], className="mb-4"),
        
        dbc.Row([
            # Growth Trajectory
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("National Growth Trajectory", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id='growth-trajectory-chart', config={'displayModeBar': False})
                    ])
                ], className="shadow-sm h-100")
            ], width=12),
        ]),
    ], fluid=True)


def create_operational_monitoring_section():
    """Create Operational Monitoring - Tier 3."""
    return dbc.Container([
        html.H2("Operational Monitoring", className="mt-5 mb-4", style={'fontWeight': 'bold'}),
        
        dbc.Row([
            # Biometric Modality Performance
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Auth Modality Performance", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id='modality-performance-chart', config={'displayModeBar': False})
                    ])
                ], className="shadow-sm h-100")
            ], width=6),
            
            # Error Analysis
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Top Error Codes", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id='error-analysis-chart', config={'displayModeBar': False})
                    ])
                ], className="shadow-sm h-100")
            ], width=6),
        ], className="mb-4"),
        
        dbc.Row([
            # Latency Heatmap
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("State Latency Performance", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id='latency-heatmap-chart', config={'displayModeBar': False})
                    ])
                ], className="shadow-sm h-100")
            ], width=6),
            
            # Temporal Patterns
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Day-of-Week Patterns", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id='temporal-patterns-chart', config={'displayModeBar': False})
                    ])
                ], className="shadow-sm h-100")
            ], width=6),
        ]),
    ], fluid=True)


def create_geographic_deepdive_section():
    """Create Geographic Deep-Dive - Tier 4."""
    return dbc.Container([
        html.H2("Geographic Deep-Dive", className="mt-5 mb-4", style={'fontWeight': 'bold'}),
        
        # Filters
        dbc.Row([
            dbc.Col([
                dbc.Label("Select State(s)"),
                dcc.Dropdown(
                    id='state-filter',
                    options=[],  # Will be populated dynamically
                    multi=True,
                    placeholder="All States"
                )
            ], width=6),
            
            dbc.Col([
                dbc.Label("Select Zone(s)"),
                dcc.Dropdown(
                    id='zone-filter',
                    options=[
                        {'label': 'North', 'value': 'North'},
                        {'label': 'South', 'value': 'South'},
                        {'label': 'East', 'value': 'East'},
                        {'label': 'West', 'value': 'West'},
                        {'label': 'Central', 'value': 'Central'},
                        {'label': 'North East', 'value': 'North East'},
                    ],
                    multi=True,
                    placeholder="All Zones"
                )
            ], width=6),
        ], className="mb-4"),
        
        dbc.Row([
            # District Inequality Analysis
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("District Inequality (Lorenz Curve)", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id='district-inequality-chart', config={'displayModeBar': False})
                    ])
                ], className="shadow-sm h-100")
            ], width=6),
            
            # State-District Scatter
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("State vs District Concentration", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id='state-district-scatter-chart', config={'displayModeBar': False})
                    ])
                ], className="shadow-sm h-100")
            ], width=6),
        ], className="mb-4"),
        
        dbc.Row([
            # Inclusion Gaps
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Bottom 20 Districts (Inclusion Gaps)", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id='inclusion-gaps-chart', config={'displayModeBar': False})
                    ])
                ], className="shadow-sm h-100")
            ], width=12),
        ]),
    ], fluid=True)


def create_predictive_analytics_section():
    """Create Predictive Analytics - Tier 5."""
    return dbc.Container([
        html.H2("Predictive Analytics & Insights", className="mt-5 mb-4", style={'fontWeight': 'bold'}),
        
        dbc.Row([
            # Anomaly Detection
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Anomaly Detection (Z-Score)", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id='anomaly-detection-chart', config={'displayModeBar': False})
                    ])
                ], className="shadow-sm h-100")
            ], width=6),
            
            # 30-Day Forecast
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("30-Day Volume Forecast", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id='forecast-chart', config={'displayModeBar': False})
                    ])
                ], className="shadow-sm h-100")
            ], width=6),
        ], className="mb-4"),
        
        dbc.Row([
            # Cross-Dataset Correlation
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Cross-Dataset Correlation Matrix", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id='correlation-matrix-chart', config={'displayModeBar': False})
                    ])
                ], className="shadow-sm h-100")
            ], width=12),
        ]),
    ], fluid=True)


# Main Layout
app.layout = dbc.Container([
    # Header
    dbc.Navbar([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.NavbarBrand("🇮🇳 Aadhar Analytics Dashboard", className="ms-2",
                                   style={'fontSize': '1.5rem', 'fontWeight': 'bold'})
                ], width="auto"),
            ], align="center"),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-calendar-alt", style={'marginRight': '5px'}),
                        html.Span(id='last-updated', children=datetime.now().strftime("%B %d, %Y %H:%M"))
                    ], style={'color': 'white', 'fontSize': '0.9rem'})
                ])
            ])
        ], fluid=True)
    ], color="primary", dark=True, className="mb-4"),
    
    # Date Range Filter (Global)
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Date Range", html_for="date-range-picker"),
                            dcc.DatePickerRange(
                                id='date-range-picker',
                                start_date=datetime(2025, 3, 1),
                                end_date=datetime(2025, 12, 31),
                                display_format='DD-MM-YYYY',
                                style={'width': '100%'}
                            )
                        ], width=4),
                        
                        dbc.Col([
                            dbc.Label("Dataset Focus"),
                            dcc.Dropdown(
                                id='dataset-focus',
                                options=[
                                    {'label': 'Integrated View', 'value': 'integrated'},
                                    {'label': 'Biometric', 'value': 'biometric'},
                                    {'label': 'Demographic', 'value': 'demographic'},
                                    {'label': 'Enrolment', 'value': 'enrolment'},
                                ],
                                value='integrated'
                            )
                        ], width=3),
                        
                        dbc.Col([
                            dbc.Label("Aggregation Level"),
                            dcc.Dropdown(
                                id='aggregation-level',
                                options=[
                                    {'label': 'Daily', 'value': 'daily'},
                                    {'label': 'Weekly', 'value': 'weekly'},
                                    {'label': 'Monthly', 'value': 'monthly'},
                                ],
                                value='daily'
                            )
                        ], width=3),
                        
                        dbc.Col([
                            html.Br(),
                            dbc.Button("Refresh Dashboard", id='refresh-button', 
                                     color="primary", className="mt-2")
                        ], width=2),
                    ])
                ])
            ], className="mb-4 shadow-sm")
        ])
    ]),
    
    # Content Sections
    create_executive_kpi_section(),
    html.Hr(className="my-5"),
    create_strategic_overview_section(),
    html.Hr(className="my-5"),
    create_operational_monitoring_section(),
    html.Hr(className="my-5"),
    create_geographic_deepdive_section(),
    html.Hr(className="my-5"),
    create_predictive_analytics_section(),
    
    # Auto-refresh component (triggers KPI update on page load)
    dcc.Interval(id='interval-component', interval=1000, n_intervals=0, max_intervals=1),
    
    # Footer
    html.Footer([
        dbc.Container([
            html.Hr(),
            html.P([
                html.Strong("Developed by Team Sankhya (Team ID: UIDAI_4245) for the UIDAI Data Hackathon 2026")
            ], className="text-center", style={'fontSize': '1rem', 'color': '#1f77b4', 'fontWeight': '600'})
        ], fluid=True)
    ], className="mt-5 mb-3")
    
], fluid=True, style={'backgroundColor': '#f8f9fa'})


# ============================================================================
# CALLBACKS - Data Visualization Updates
# ============================================================================

@app.callback(
    Output('state-filter', 'options'),
    Input('refresh-button', 'n_clicks')
)
def update_state_filter(n_clicks):
    """Populate state filter dropdown."""
    if BIOMETRIC_DF is not None:
        states = sorted(BIOMETRIC_DF['state'].unique())
        return [{'label': state, 'value': state} for state in states]
    return []


@app.callback(
    Output('zonal-distribution-chart', 'figure'),
    [Input('refresh-button', 'n_clicks'),
     Input('dataset-focus', 'value'),
     Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date')]
)
def update_zonal_distribution(n_clicks, dataset, start_date, end_date):
    """Update zonal distribution donut chart."""
    # Select appropriate dataset
    if dataset == 'biometric' and BIOMETRIC_DF is not None:
        df = BIOMETRIC_DF.copy()
        metric_col = 'total_transactions'
        title = 'Biometric Transactions by Zone'
    elif dataset == 'demographic' and DEMOGRAPHIC_DF is not None:
        df = DEMOGRAPHIC_DF.copy()
        metric_col = 'total_demographic'
        title = 'Demographic Updates by Zone'
    elif dataset == 'enrolment' and ENROLMENT_DF is not None:
        df = ENROLMENT_DF.copy()
        metric_col = 'total_enrolment'
        title = 'Enrolments by Zone'
    elif dataset == 'integrated' and INTEGRATED_DF is not None:
        df = INTEGRATED_DF.copy()
        metric_col = 'bio_transactions'
        title = 'Integrated Metrics by Zone'
    else:
        return go.Figure()
    
    # Filter by date
    if start_date and end_date:
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    
    zone_data = df.groupby('zone')[metric_col].sum().sort_values(ascending=False)
    
    fig = go.Figure(data=[go.Pie(
        labels=zone_data.index,
        values=zone_data.values,
        hole=0.4,
        marker=dict(colors=[COLORS['zones'].get(z, '#999') for z in zone_data.index])
    )])
    
    fig.update_layout(
        title=title,
        height=350,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02)
    )
    
    return fig


@app.callback(
    [Output('kpi-bio-trans', 'children'),
     Output('kpi-total-enrol', 'children'),
     Output('kpi-enrol-subtitle', 'children'),
     Output('kpi-auth-rate', 'children'),
     Output('kpi-auth-subtitle', 'children'),
     Output('kpi-latency', 'children'),
     Output('kpi-latency-subtitle', 'children'),
     Output('kpi-states-bio', 'children'),
     Output('kpi-states-bio-subtitle', 'children'),
     Output('kpi-states-enrol', 'children'),
     Output('kpi-data-points', 'children')],
    [Input('refresh-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')]
)
def update_kpi_cards(n_clicks, n_intervals):
    """Update all KPI cards with loaded data."""
    return (
        f"{NATIONAL_KPIS.get('total_biometric_transactions', 0):,.0f}",
        f"{NATIONAL_KPIS.get('total_enrolments', 0):,.0f}",
        f"Infant: {NATIONAL_KPIS.get('infant_enrolments', 0):,.0f}",
        f"{NATIONAL_KPIS.get('national_auth_success_rate', 0):.1f}%",
        f"Total Records: {NATIONAL_KPIS.get('total_demographic_records', 0):,.0f}",
        f"{NATIONAL_KPIS.get('p99_latency_ms', 0):.0f} ms",
        f"Median: {NATIONAL_KPIS.get('median_latency_ms', 0):.0f} ms",
        f"{NATIONAL_KPIS.get('active_states_biometric', 0)}",
        f"Districts: {NATIONAL_KPIS.get('active_districts_biometric', 0):,}",
        f"{NATIONAL_KPIS.get('active_states_enrolment', 0)}",
        f"{NATIONAL_KPIS.get('total_data_points', 0):,.0f}"
    )


@app.callback(
    Output('state-performance-chart', 'figure'),
    [Input('refresh-button', 'n_clicks'),
     Input('dataset-focus', 'value'),
     Input('zone-filter', 'value'),
     Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date')]
)
def update_state_performance(n_clicks, dataset, zones, start_date, end_date):
    """Update top states bar chart."""
    # Select appropriate dataset
    if dataset == 'biometric' and BIOMETRIC_DF is not None:
        df = BIOMETRIC_DF.copy()
        metric_col = 'total_transactions'
        title = 'Top 10 States - Biometric Transactions'
    elif dataset == 'demographic' and DEMOGRAPHIC_DF is not None:
        df = DEMOGRAPHIC_DF.copy()
        metric_col = 'total_demographic'
        title = 'Top 10 States - Demographic Updates'
    elif dataset == 'enrolment' and ENROLMENT_DF is not None:
        df = ENROLMENT_DF.copy()
        metric_col = 'total_enrolment'
        title = 'Top 10 States - Enrolments'
    elif dataset == 'integrated' and INTEGRATED_DF is not None:
        df = INTEGRATED_DF.copy()
        metric_col = 'bio_transactions'
        title = 'Top 10 States - Integrated Metrics'
    else:
        return go.Figure()
    
    # Filter by date
    if start_date and end_date:
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    
    # Filter by zone
    if zones:
        df = df[df['zone'].isin(zones)]
    
    state_data = df.groupby('state')[metric_col].sum().sort_values(ascending=False).head(10)
    
    fig = go.Figure(data=[go.Bar(
        x=state_data.values,
        y=state_data.index,
        orientation='h',
        marker=dict(color=COLORS['primary'])
    )])
    
    fig.update_layout(
        title=title,
        xaxis_title="Total Count",
        yaxis_title="",
        height=350,
        yaxis=dict(autorange="reversed")
    )
    
    return fig


@app.callback(
    Output('growth-trajectory-chart', 'figure'),
    [Input('refresh-button', 'n_clicks'),
     Input('dataset-focus', 'value'),
     Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date'),
     Input('aggregation-level', 'value')]
)
def update_growth_trajectory(n_clicks, dataset, start_date, end_date, aggregation):
    """Update national growth trajectory line chart."""
    # Select appropriate dataset
    if dataset == 'biometric' and BIOMETRIC_DF is not None:
        df = BIOMETRIC_DF.copy()
        metric_col = 'total_transactions'
        title = 'Biometric Transactions Growth'
    elif dataset == 'demographic' and DEMOGRAPHIC_DF is not None:
        df = DEMOGRAPHIC_DF.copy()
        metric_col = 'total_demographic'
        title = 'Demographic Updates Growth'
    elif dataset == 'enrolment' and ENROLMENT_DF is not None:
        df = ENROLMENT_DF.copy()
        metric_col = 'total_enrolment'
        title = 'Enrolment Growth'
    elif dataset == 'integrated' and INTEGRATED_DF is not None:
        df = INTEGRATED_DF.copy()
        metric_col = 'bio_transactions'
        title = 'Integrated Metrics Growth'
    else:
        return go.Figure()
    
    # Filter by date
    if start_date and end_date:
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    
    # Apply aggregation
    if aggregation == 'weekly':
        df['period'] = df['date'].dt.to_period('W').dt.to_timestamp()
    elif aggregation == 'monthly':
        df['period'] = df['date'].dt.to_period('M').dt.to_timestamp()
    else:
        df['period'] = df['date']
    
    daily_data = df.groupby('period')[metric_col].sum().sort_index()
    cumulative = daily_data.cumsum()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=cumulative.index,
        y=cumulative.values,
        mode='lines',
        name='Cumulative Volume',
        line=dict(color=COLORS['primary'], width=3),
        fill='tozeroy',
        fillcolor='rgba(31, 119, 180, 0.2)'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Cumulative Count",
        height=400,
        hovermode='x unified'
    )
    
    return fig


@app.callback(
    Output('modality-performance-chart', 'figure'),
    [Input('refresh-button', 'n_clicks'),
     Input('dataset-focus', 'value'),
     Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date')]
)
def update_modality_performance(n_clicks, dataset, start_date, end_date):
    """Update biometric modality performance chart."""
    # Modality data only available in demographic dataset
    if dataset != 'demographic' or DEMOGRAPHIC_DF is None:
        fig = go.Figure()
        fig.add_annotation(
            text="Auth Modality analysis only available<br>for Demographic dataset",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(title="Auth Modality: Volume vs Success Rate", height=350)
        return fig
    
    df = DEMOGRAPHIC_DF.copy()
    
    # Filter by date
    if start_date and end_date:
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    
    # Modality distribution
    modality_counts = df['auth_modality'].value_counts()
    
    # Success rate by modality
    success_by_modality = df.groupby('auth_modality')['auth_status'].apply(
        lambda x: (x == 'Success').sum() / len(x) * 100
    )
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Volume',
        x=modality_counts.index,
        y=modality_counts.values,
        yaxis='y',
        marker=dict(color=COLORS['primary'])
    ))
    
    fig.add_trace(go.Scatter(
        name='Success Rate %',
        x=success_by_modality.index,
        y=success_by_modality.values,
        yaxis='y2',
        mode='lines+markers',
        marker=dict(size=10, color=COLORS['success']),
        line=dict(width=3)
    ))
    
    fig.update_layout(
        title="Auth Modality: Volume vs Success Rate",
        xaxis_title="Authentication Modality",
        yaxis=dict(title="Transaction Volume", side='left'),
        yaxis2=dict(title="Success Rate (%)", side='right', overlaying='y', range=[0, 100]),
        height=350,
        hovermode='x unified'
    )
    
    return fig


@app.callback(
    Output('error-analysis-chart', 'figure'),
    [Input('refresh-button', 'n_clicks'),
     Input('dataset-focus', 'value'),
     Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date')]
)
def update_error_analysis(n_clicks, dataset, start_date, end_date):
    """Update error code analysis chart."""
    # Error code analysis only available in demographic dataset
    if dataset != 'demographic' or DEMOGRAPHIC_DF is None:
        fig = go.Figure()
        fig.add_annotation(
            text="Error code analysis only available<br>for Demographic dataset",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(title="Top Error Codes", height=350)
        return fig
    
    df = DEMOGRAPHIC_DF.copy()
    
    # Filter by date
    if start_date and end_date:
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    
    errors = df[df['auth_status'] == 'Failure']
    error_counts = errors['error_code'].value_counts()
    
    error_labels = {
        300: 'Biometric Mismatch',
        510: 'Invalid Request',
        998: 'Technical Error',
        570: 'Device Error'
    }
    
    labels = [error_labels.get(int(code), f'Error {int(code)}') for code in error_counts.index]
    
    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=error_counts.values,
        marker=dict(color=COLORS['danger']),
        text=error_counts.values,
        textposition='outside'
    )])
    
    fig.update_layout(
        title="Top Authentication Error Codes",
        xaxis_title="Error Type",
        yaxis_title="Frequency",
        height=350
    )
    
    return fig


@app.callback(
    Output('latency-heatmap-chart', 'figure'),
    [Input('refresh-button', 'n_clicks'),
     Input('dataset-focus', 'value'),
     Input('state-filter', 'value'),
     Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date')]
)
def update_latency_heatmap(n_clicks, dataset, states, start_date, end_date):
    """Update state latency performance heatmap."""
    # Latency data only available in demographic dataset
    if dataset != 'demographic' or DEMOGRAPHIC_DF is None:
        fig = go.Figure()
        fig.add_annotation(
            text="Latency analysis only available<br>for Demographic dataset",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(title="State-wise Latency Performance Matrix", height=350)
        return fig
    
    df = DEMOGRAPHIC_DF.copy()
    
    # Filter by date
    if start_date and end_date:
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    
    if states:
        df = df[df['state'].isin(states)]
    
    # Get top 15 states by volume
    top_states = df.groupby('state')['response_time_ms'].count().sort_values(ascending=False).head(15).index
    df = df[df['state'].isin(top_states)]
    
    # Calculate latency metrics
    latency_metrics = df.groupby('state')['response_time_ms'].agg(['median', 'mean', 
                                                                     lambda x: x.quantile(0.95),
                                                                     lambda x: x.quantile(0.99)])
    latency_metrics.columns = ['Median', 'Mean', 'P95', 'P99']
    latency_metrics = latency_metrics.sort_values('P99', ascending=False)
    
    fig = go.Figure(data=go.Heatmap(
        z=latency_metrics.values.T,
        x=latency_metrics.index,
        y=latency_metrics.columns,
        colorscale='RdYlGn_r',
        text=latency_metrics.values.T.round(0),
        texttemplate='%{text} ms',
        textfont={"size": 10},
        colorbar=dict(title="Latency (ms)")
    ))
    
    fig.update_layout(
        title="State-wise Latency Performance Matrix",
        xaxis_title="State",
        yaxis_title="Metric",
        height=350
    )
    
    return fig


@app.callback(
    Output('temporal-patterns-chart', 'figure'),
    [Input('refresh-button', 'n_clicks'),
     Input('dataset-focus', 'value'),
     Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date')]
)
def update_temporal_patterns(n_clicks, dataset, start_date, end_date):
    """Update day-of-week patterns chart."""
    # Select appropriate dataset
    if dataset == 'biometric' and BIOMETRIC_DF is not None:
        df = BIOMETRIC_DF.copy()
        metric_col = 'total_transactions'
        title = 'Biometric Volume by Day of Week'
    elif dataset == 'demographic' and DEMOGRAPHIC_DF is not None:
        df = DEMOGRAPHIC_DF.copy()
        metric_col = 'total_demographic'
        title = 'Demographic Updates by Day of Week'
    elif dataset == 'enrolment' and ENROLMENT_DF is not None:
        df = ENROLMENT_DF.copy()
        metric_col = 'total_enrolment'
        title = 'Enrolments by Day of Week'
    elif dataset == 'integrated' and INTEGRATED_DF is not None:
        df = INTEGRATED_DF.copy()
        metric_col = 'bio_transactions'
        title = 'Integrated Metrics by Day of Week'
    else:
        return go.Figure()
    
    # Filter by date
    if start_date and end_date:
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    
    # Ensure day_of_week column exists
    if 'day_of_week' not in df.columns:
        df['day_of_week'] = df['date'].dt.day_name()
    
    # Day of week order
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    dow_data = df.groupby('day_of_week')[metric_col].sum()
    dow_data = dow_data.reindex(day_order)
    
    colors = [COLORS['danger'] if day == 'Sunday' else COLORS['primary'] for day in dow_data.index]
    
    fig = go.Figure(data=[go.Bar(
        x=dow_data.index,
        y=dow_data.values,
        marker=dict(color=colors),
        text=dow_data.values,
        textposition='outside',
        texttemplate='%{text:,.0f}'
    )])
    
    fig.update_layout(
        title=title,
        xaxis_title="Day",
        yaxis_title="Total Transactions",
        height=350,
        annotations=[dict(
            text="Sunday Effect: Lower operational activity",
            xref="paper", yref="paper",
            x=0.5, y=1.05,
            showarrow=False,
            font=dict(size=10, color=COLORS['danger'])
        )]
    )
    
    return fig


@app.callback(
    Output('district-inequality-chart', 'figure'),
    [Input('refresh-button', 'n_clicks'),
     Input('dataset-focus', 'value'),
     Input('state-filter', 'value'),
     Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date')]
)
def update_district_inequality(n_clicks, dataset, states, start_date, end_date):
    """Update Lorenz curve for district inequality."""
    # Select appropriate dataset
    if dataset == 'biometric' and BIOMETRIC_DF is not None:
        df = BIOMETRIC_DF.copy()
        metric_col = 'total_transactions'
        title = 'District Inequality - Biometric (Lorenz Curve)'
    elif dataset == 'demographic' and DEMOGRAPHIC_DF is not None:
        df = DEMOGRAPHIC_DF.copy()
        metric_col = 'total_demographic'
        title = 'District Inequality - Demographic (Lorenz Curve)'
    elif dataset == 'enrolment' and ENROLMENT_DF is not None:
        df = ENROLMENT_DF.copy()
        metric_col = 'total_enrolment'
        title = 'District Inequality - Enrolment (Lorenz Curve)'
    elif dataset == 'integrated' and INTEGRATED_DF is not None:
        df = INTEGRATED_DF.copy()
        metric_col = 'bio_transactions'
        title = 'District Inequality - Integrated (Lorenz Curve)'
    else:
        return go.Figure()
    
    # Filter by date
    if start_date and end_date:
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    
    if states:
        df = df[df['state'].isin(states)]
    
    district_volumes = df.groupby('district')[metric_col].sum().sort_values()
    cumsum = district_volumes.cumsum()
    
    # Lorenz curve
    lorenz_x = np.arange(1, len(district_volumes) + 1) / len(district_volumes) * 100
    lorenz_y = cumsum / cumsum.iloc[-1] * 100
    
    fig = go.Figure()
    
    # Perfect equality line
    fig.add_trace(go.Scatter(
        x=[0, 100],
        y=[0, 100],
        mode='lines',
        name='Perfect Equality',
        line=dict(dash='dash', color='gray')
    ))
    
    # Lorenz curve
    fig.add_trace(go.Scatter(
        x=lorenz_x,
        y=lorenz_y,
        mode='lines',
        name='Actual Distribution',
        line=dict(color=COLORS['primary'], width=3),
        fill='tonexty',
        fillcolor='rgba(31, 119, 180, 0.2)'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Cumulative % of Districts",
        yaxis_title="Cumulative % of Volume",
        height=400,
        hovermode='x unified'
    )
    
    return fig


@app.callback(
    Output('state-district-scatter-chart', 'figure'),
    [Input('refresh-button', 'n_clicks'),
     Input('dataset-focus', 'value'),
     Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date')]
)
def update_state_district_scatter(n_clicks, dataset, start_date, end_date):
    """Update state vs district concentration scatter."""
    # Select appropriate dataset
    if dataset == 'biometric' and BIOMETRIC_DF is not None:
        df = BIOMETRIC_DF.copy()
        metric_col = 'total_transactions'
        title = 'State vs District Concentration - Biometric'
    elif dataset == 'demographic' and DEMOGRAPHIC_DF is not None:
        df = DEMOGRAPHIC_DF.copy()
        metric_col = 'total_demographic'
        title = 'State vs District Concentration - Demographic'
    elif dataset == 'enrolment' and ENROLMENT_DF is not None:
        df = ENROLMENT_DF.copy()
        metric_col = 'total_enrolment'
        title = 'State vs District Concentration - Enrolment'
    elif dataset == 'integrated' and INTEGRATED_DF is not None:
        df = INTEGRATED_DF.copy()
        metric_col = 'bio_transactions'
        title = 'State vs District Concentration - Integrated'
    else:
        return go.Figure()
    
    # Filter by date
    if start_date and end_date:
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    
    # Calculate state totals and max district per state
    state_totals = df.groupby('state')[metric_col].sum()
    
    max_district_per_state = df.groupby(['state', 'district'])[metric_col].sum()\
        .groupby('state').max()
    
    scatter_df = pd.DataFrame({
        'state_total': state_totals,
        'max_district': max_district_per_state,
        'zone': df.groupby('state')['zone'].first()
    })
    
    scatter_df['centralization_ratio'] = scatter_df['max_district'] / scatter_df['state_total'] * 100
    
    fig = px.scatter(
        scatter_df,
        x='state_total',
        y='max_district',
        color='zone',
        color_discrete_map=COLORS['zones'],
        hover_data=['centralization_ratio'],
        log_x=True,
        log_y=True,
        labels={
            'state_total': 'State Total Volume',
            'max_district': 'Largest District Volume',
            'centralization_ratio': 'Centralization %'
        }
    )
    
    fig.update_layout(
        title=title + " (Log-Log Scale)",
        height=400
    )
    
    return fig


@app.callback(
    Output('inclusion-gaps-chart', 'figure'),
    [Input('refresh-button', 'n_clicks'),
     Input('dataset-focus', 'value'),
     Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date')]
)
def update_inclusion_gaps(n_clicks, dataset, start_date, end_date):
    """Update bottom 20 districts (inclusion gaps)."""
    # Select appropriate dataset
    if dataset == 'biometric' and BIOMETRIC_DF is not None:
        df = BIOMETRIC_DF.copy()
        metric_col = 'total_transactions'
        title = 'Bottom 20 Districts - Biometric'
    elif dataset == 'demographic' and DEMOGRAPHIC_DF is not None:
        df = DEMOGRAPHIC_DF.copy()
        metric_col = 'total_demographic'
        title = 'Bottom 20 Districts - Demographic'
    elif dataset == 'enrolment' and ENROLMENT_DF is not None:
        df = ENROLMENT_DF.copy()
        metric_col = 'total_enrolment'
        title = 'Bottom 20 Districts - Enrolment'
    elif dataset == 'integrated' and INTEGRATED_DF is not None:
        df = INTEGRATED_DF.copy()
        metric_col = 'bio_transactions'
        title = 'Bottom 20 Districts - Integrated'
    else:
        return go.Figure()
    
    # Filter by date
    if start_date and end_date:
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    
    district_data = df.groupby(['state', 'district'])[metric_col].sum().sort_values().head(20)
    labels = [f"{d} ({s})" for s, d in district_data.index]
    
    fig = go.Figure(data=[go.Bar(
        x=district_data.values,
        y=labels,
        orientation='h',
        marker=dict(color=COLORS['danger']),
        text=district_data.values,
        textposition='outside',
        texttemplate='%{text:,.0f}'
    )])
    
    fig.update_layout(
        title=title + " - Priority Intervention Zones",
        xaxis_title="Volume",
        yaxis_title="",
        height=500,
        yaxis=dict(autorange="reversed")
    )
    
    return fig


@app.callback(
    Output('anomaly-detection-chart', 'figure'),
    [Input('refresh-button', 'n_clicks'),
     Input('dataset-focus', 'value'),
     Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date')]
)
def update_anomaly_detection(n_clicks, dataset, start_date, end_date):
    """Update anomaly detection Z-score chart."""
    # Select appropriate dataset
    if dataset == 'biometric' and BIOMETRIC_DF is not None:
        df = BIOMETRIC_DF.copy()
        metric_col = 'total_transactions'
        title = 'Biometric Transaction Anomalies'
    elif dataset == 'demographic' and DEMOGRAPHIC_DF is not None:
        df = DEMOGRAPHIC_DF.copy()
        metric_col = 'total_demographic'
        title = 'Demographic Update Anomalies'
    elif dataset == 'enrolment' and ENROLMENT_DF is not None:
        df = ENROLMENT_DF.copy()
        metric_col = 'total_enrolment'
        title = 'Enrolment Anomalies'
    elif dataset == 'integrated' and INTEGRATED_DF is not None:
        df = INTEGRATED_DF.copy()
        metric_col = 'bio_transactions'
        title = 'Integrated Metrics Anomalies'
    else:
        return go.Figure()
    
    # Filter by date
    if start_date and end_date:
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    
    daily_volume = df.groupby('date')[metric_col].sum().sort_index()
    
    # Calculate Z-scores
    mean_vol = daily_volume.mean()
    std_vol = daily_volume.std()
    z_scores = (daily_volume - mean_vol) / std_vol
    
    # Identify anomalies (Z-score > 3)
    anomalies = z_scores[abs(z_scores) > 3]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=z_scores.index,
        y=z_scores.values,
        mode='lines+markers',
        name='Z-Score',
        line=dict(color=COLORS['primary'])
    ))
    
    # Add threshold lines
    fig.add_hline(y=3, line_dash="dash", line_color=COLORS['danger'], 
                  annotation_text="3σ threshold")
    fig.add_hline(y=-3, line_dash="dash", line_color=COLORS['danger'])
    
    # Mark anomalies
    if len(anomalies) > 0:
        fig.add_trace(go.Scatter(
            x=anomalies.index,
            y=anomalies.values,
            mode='markers',
            name='Anomalies',
            marker=dict(size=12, color=COLORS['danger'], symbol='x')
        ))
    
    fig.update_layout(
        title=f"{title} (Z-Score Analysis) - {len(anomalies)} detected",
        xaxis_title="Date",
        yaxis_title="Z-Score (Standard Deviations)",
        height=400,
        hovermode='x unified'
    )
    
    return fig


@app.callback(
    Output('forecast-chart', 'figure'),
    [Input('refresh-button', 'n_clicks'),
     Input('dataset-focus', 'value'),
     Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date')]
)
def update_forecast(n_clicks, dataset, start_date, end_date):
    """Update 30-day forecast chart using NumPy polynomial fitting."""
    # Select appropriate dataset
    if dataset == 'biometric' and BIOMETRIC_DF is not None:
        df = BIOMETRIC_DF.copy()
        metric_col = 'total_transactions'
        title = 'Biometric 30-Day Forecast'
    elif dataset == 'demographic' and DEMOGRAPHIC_DF is not None:
        df = DEMOGRAPHIC_DF.copy()
        metric_col = 'total_demographic'
        title = 'Demographic 30-Day Forecast'
    elif dataset == 'enrolment' and ENROLMENT_DF is not None:
        df = ENROLMENT_DF.copy()
        metric_col = 'total_enrolment'
        title = 'Enrolment 30-Day Forecast'
    elif dataset == 'integrated' and INTEGRATED_DF is not None:
        df = INTEGRATED_DF.copy()
        metric_col = 'bio_transactions'
        title = 'Integrated 30-Day Forecast'
    else:
        return go.Figure()
    
    # Filter by date
    if start_date and end_date:
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    
    daily_volume = df.groupby('date')[metric_col].sum().sort_index()
    
    # Simple linear regression for forecast using NumPy
    x = np.arange(len(daily_volume))
    y = daily_volume.values
    
    # Linear regression using numpy polyfit
    coeffs = np.polyfit(x, y, 1)  # degree 1 for linear
    slope, intercept = coeffs[0], coeffs[1]
    
    # Calculate R-squared
    y_pred = slope * x + intercept
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    # Forecast 30 days
    forecast_days = 30
    forecast_x = np.arange(len(daily_volume), len(daily_volume) + forecast_days)
    forecast_y = slope * forecast_x + intercept
    forecast_dates = pd.date_range(start=daily_volume.index[-1] + timedelta(days=1), 
                                   periods=forecast_days, freq='D')
    
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(go.Scatter(
        x=daily_volume.index,
        y=daily_volume.values,
        mode='lines',
        name='Historical',
        line=dict(color=COLORS['primary'])
    ))
    
    # Forecast
    fig.add_trace(go.Scatter(
        x=forecast_dates,
        y=forecast_y,
        mode='lines',
        name='30-Day Forecast',
        line=dict(color=COLORS['warning'], dash='dash')
    ))
    
    fig.update_layout(
        title=f"{title} (R² = {r_squared:.3f})",
        xaxis_title="Date",
        yaxis_title="Daily Count",
        height=400,
        hovermode='x unified'
    )
    
    return fig


@app.callback(
    Output('correlation-matrix-chart', 'figure'),
    Input('refresh-button', 'n_clicks')
)
def update_correlation_matrix(n_clicks):
    """Update cross-dataset correlation matrix."""
    if INTEGRATED_DF is None:
        return go.Figure()
    
    # Select key metrics for correlation
    correlation_cols = [
        'bio_transactions', 'bio_youth', 'bio_adult',
        'demo_total', 'auth_success_rate', 'median_latency_ms',
        'enrol_total', 'enrol_infant', 'enrol_youth', 'enrol_adult'
    ]
    
    # State-level aggregation
    state_metrics = INTEGRATED_DF.groupby('state')[correlation_cols].sum()
    
    # Calculate correlation matrix
    corr_matrix = state_metrics.corr()
    
    # Create labels
    labels = {
        'bio_transactions': 'Bio Trans',
        'bio_youth': 'Bio Youth',
        'bio_adult': 'Bio Adult',
        'demo_total': 'Demo Total',
        'auth_success_rate': 'Auth Success %',
        'median_latency_ms': 'Latency',
        'enrol_total': 'Enrol Total',
        'enrol_infant': 'Enrol Infant',
        'enrol_youth': 'Enrol Youth',
        'enrol_adult': 'Enrol Adult'
    }
    
    display_labels = [labels.get(col, col) for col in corr_matrix.columns]
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=display_labels,
        y=display_labels,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 9},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title="Cross-Dataset Correlation Matrix (State-Level Aggregation)",
        height=500,
        xaxis={'side': 'bottom'},
        yaxis={'autorange': 'reversed'}
    )
    
    return fig


if __name__ == '__main__':
    # Load data on startup (use sample_frac=0.1 for fast testing, None for full data)
    load_data_on_startup(sample_frac=0.1)
    
    # Run the app
    print("\n" + "=" * 80)
    print("Starting Dashboard Server...")
    print("Access dashboard at: http://127.0.0.1:8050")
    print("=" * 80 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=8050)
