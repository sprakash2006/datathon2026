"""
Government-Grade Visualization Components
Advanced charts for comprehensive analysis including Pareto, Lorenz, control charts, etc.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from scipy import stats


class VisualizationSuite:
    """Collection of government-grade visualization builders."""
    
    # Color schemes
    COLORS = {
        'primary': '#1f77b4',
        'success': '#2ca02c',
        'warning': '#ff7f0e',
        'danger': '#d62728',
        'info': '#17becf',
        'government': ['#08519c', '#3182bd', '#6baed6', '#9ecae1', '#c6dbef'],
        'diverging': ['#d73027', '#f46d43', '#fdae61', '#fee08b', '#d9ef8b', 
                     '#a6d96a', '#66bd63', '#1a9850'],
    }
    
    @staticmethod
    def create_pareto_chart(data, labels, title="Pareto Analysis"):
        """
        Create Pareto chart (80/20 analysis).
        
        Args:
            data: Series or array of values
            labels: Category labels
            title: Chart title
            
        Returns:
            plotly.graph_objects.Figure
        """
        # Sort data descending
        sorted_indices = np.argsort(data)[::-1]
        sorted_data = np.array(data)[sorted_indices]
        sorted_labels = np.array(labels)[sorted_indices]
        
        # Calculate cumulative percentage
        cumsum = np.cumsum(sorted_data)
        cumsum_pct = cumsum / cumsum[-1] * 100
        
        # Find 80% threshold
        threshold_idx = np.where(cumsum_pct >= 80)[0][0] if len(np.where(cumsum_pct >= 80)[0]) > 0 else len(cumsum_pct) - 1
        
        fig = go.Figure()
        
        # Bar chart for individual values
        fig.add_trace(go.Bar(
            x=sorted_labels,
            y=sorted_data,
            name='Volume',
            marker_color=VisualizationSuite.COLORS['primary'],
            yaxis='y'
        ))
        
        # Line chart for cumulative percentage
        fig.add_trace(go.Scatter(
            x=sorted_labels,
            y=cumsum_pct,
            name='Cumulative %',
            mode='lines+markers',
            marker=dict(color=VisualizationSuite.COLORS['warning'], size=6),
            line=dict(width=3),
            yaxis='y2'
        ))
        
        # Add 80% threshold line
        fig.add_hline(
            y=80, line_dash="dash", line_color=VisualizationSuite.COLORS['danger'],
            annotation_text="80% Threshold", annotation_position="right",
            yref='y2'
        )
        
        # Add vertical line at 80% point
        fig.add_vline(
            x=threshold_idx, line_dash="dot", line_color=VisualizationSuite.COLORS['danger'],
            annotation_text=f"Top {threshold_idx+1} = 80%", annotation_position="top"
        )
        
        fig.update_layout(
            title=title,
            xaxis=dict(title="Categories", tickangle=-45),
            yaxis=dict(title="Value", side='left'),
            yaxis2=dict(title="Cumulative %", side='right', overlaying='y', range=[0, 100]),
            height=500,
            hovermode='x unified',
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def create_lorenz_curve(values, title="Lorenz Curve - Inequality Analysis"):
        """
        Create Lorenz curve for inequality measurement.
        
        Args:
            values: Array of values to analyze
            title: Chart title
            
        Returns:
            plotly.graph_objects.Figure
        """
        sorted_values = np.sort(values)
        cumsum = np.cumsum(sorted_values)
        
        # Lorenz curve coordinates
        lorenz_x = np.arange(1, len(sorted_values) + 1) / len(sorted_values) * 100
        lorenz_y = cumsum / cumsum[-1] * 100
        
        # Calculate Gini coefficient
        # Gini = (A) / (A + B) where A is area between perfect equality and Lorenz curve
        gini = 1 - 2 * np.trapz(lorenz_y / 100, lorenz_x / 100)
        
        fig = go.Figure()
        
        # Perfect equality line
        fig.add_trace(go.Scatter(
            x=[0, 100],
            y=[0, 100],
            mode='lines',
            name='Perfect Equality',
            line=dict(dash='dash', color='gray', width=2)
        ))
        
        # Lorenz curve
        fig.add_trace(go.Scatter(
            x=np.concatenate([[0], lorenz_x]),
            y=np.concatenate([[0], lorenz_y]),
            mode='lines',
            name=f'Actual Distribution (Gini={gini:.3f})',
            line=dict(color=VisualizationSuite.COLORS['primary'], width=3),
            fill='tonexty',
            fillcolor='rgba(31, 119, 180, 0.3)'
        ))
        
        # Add annotations
        annotations_text = f"Gini Coefficient: {gini:.3f}<br>"
        if gini < 0.3:
            annotations_text += "Low Inequality"
        elif gini < 0.5:
            annotations_text += "Moderate Inequality"
        else:
            annotations_text += "High Inequality"
        
        fig.add_annotation(
            text=annotations_text,
            xref="paper", yref="paper",
            x=0.05, y=0.95,
            showarrow=False,
            bgcolor="white",
            bordercolor=VisualizationSuite.COLORS['primary'],
            borderwidth=2
        )
        
        fig.update_layout(
            title=title,
            xaxis_title="Cumulative % of Population",
            yaxis_title="Cumulative % of Volume",
            height=500,
            hovermode='x unified'
        )
        
        return fig
    
    @staticmethod
    def create_control_chart(data, dates, title="Statistical Process Control Chart", 
                            sigma_levels=[1, 2, 3]):
        """
        Create control chart with Z-scores and sigma bands.
        
        Args:
            data: Time series data
            dates: Corresponding dates
            title: Chart title
            sigma_levels: List of sigma levels to display
            
        Returns:
            plotly.graph_objects.Figure
        """
        # Calculate statistics
        mean_val = np.mean(data)
        std_val = np.std(data)
        z_scores = (data - mean_val) / std_val
        
        # Identify outliers
        outliers_indices = np.where(np.abs(z_scores) > 3)[0]
        
        fig = go.Figure()
        
        # Main data line
        fig.add_trace(go.Scatter(
            x=dates,
            y=data,
            mode='lines+markers',
            name='Actual Values',
            line=dict(color=VisualizationSuite.COLORS['primary'], width=2),
            marker=dict(size=4)
        ))
        
        # Mean line
        fig.add_hline(
            y=mean_val, line_dash="solid", line_color=VisualizationSuite.COLORS['success'],
            annotation_text=f"Mean: {mean_val:,.0f}",
            annotation_position="right"
        )
        
        # Sigma bands
        colors_sigma = {1: 'lightgreen', 2: 'yellow', 3: 'red'}
        for sigma in sigma_levels:
            upper = mean_val + sigma * std_val
            lower = mean_val - sigma * std_val
            
            fig.add_hline(
                y=upper, line_dash="dash", line_color=colors_sigma.get(sigma, 'gray'),
                annotation_text=f"+{sigma}σ",
                annotation_position="right"
            )
            fig.add_hline(
                y=lower, line_dash="dash", line_color=colors_sigma.get(sigma, 'gray'),
                annotation_text=f"-{sigma}σ",
                annotation_position="right"
            )
        
        # Mark outliers
        if len(outliers_indices) > 0:
            fig.add_trace(go.Scatter(
                x=[dates[i] for i in outliers_indices],
                y=[data[i] for i in outliers_indices],
                mode='markers',
                name='Outliers (>3σ)',
                marker=dict(size=12, color=VisualizationSuite.COLORS['danger'], 
                          symbol='x', line=dict(width=2))
            ))
        
        fig.update_layout(
            title=f"{title} ({len(outliers_indices)} outliers detected)",
            xaxis_title="Date",
            yaxis_title="Value",
            height=500,
            hovermode='x unified',
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def create_waterfall_chart(categories, values, title="Month-over-Month Growth"):
        """
        Create waterfall chart for growth analysis.
        
        Args:
            categories: Category labels (e.g., months)
            values: Change values (can be positive or negative)
            title: Chart title
            
        Returns:
            plotly.graph_objects.Figure
        """
        # Calculate cumulative for positioning
        cumulative = np.concatenate([[0], np.cumsum(values)])
        
        colors = [VisualizationSuite.COLORS['success'] if v >= 0 
                 else VisualizationSuite.COLORS['danger'] for v in values]
        
        fig = go.Figure(go.Waterfall(
            name="Growth",
            orientation="v",
            measure=["relative"] * len(categories),
            x=categories,
            y=values,
            connector={"line": {"color": "gray"}},
            increasing={"marker": {"color": VisualizationSuite.COLORS['success']}},
            decreasing={"marker": {"color": VisualizationSuite.COLORS['danger']}},
            totals={"marker": {"color": VisualizationSuite.COLORS['primary']}}
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Period",
            yaxis_title="Change",
            height=500,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_quadrant_scatter(x_data, y_data, labels, title="Performance Matrix",
                                x_label="X Metric", y_label="Y Metric"):
        """
        Create 4-quadrant scatter plot for performance clustering.
        
        Args:
            x_data: X-axis values
            y_data: Y-axis values
            labels: Point labels
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
            
        Returns:
            plotly.graph_objects.Figure
        """
        x_median = np.median(x_data)
        y_median = np.median(y_data)
        
        # Classify into quadrants
        quadrants = []
        for x, y in zip(x_data, y_data):
            if x >= x_median and y >= y_median:
                quadrants.append('High-High (Star)')
            elif x >= x_median and y < y_median:
                quadrants.append('High-Low (Volatile)')
            elif x < x_median and y >= y_median:
                quadrants.append('Low-High (Stable)')
            else:
                quadrants.append('Low-Low (Watchlist)')
        
        colors = {
            'High-High (Star)': VisualizationSuite.COLORS['success'],
            'High-Low (Volatile)': VisualizationSuite.COLORS['warning'],
            'Low-High (Stable)': VisualizationSuite.COLORS['info'],
            'Low-Low (Watchlist)': VisualizationSuite.COLORS['danger']
        }
        
        fig = go.Figure()
        
        for quadrant in colors.keys():
            mask = [q == quadrant for q in quadrants]
            fig.add_trace(go.Scatter(
                x=np.array(x_data)[mask],
                y=np.array(y_data)[mask],
                mode='markers+text',
                name=quadrant,
                text=np.array(labels)[mask],
                textposition="top center",
                marker=dict(size=10, color=colors[quadrant]),
                textfont=dict(size=8)
            ))
        
        # Add median lines
        fig.add_vline(x=x_median, line_dash="dash", line_color="gray")
        fig.add_hline(y=y_median, line_dash="dash", line_color="gray")
        
        # Add quadrant labels
        fig.add_annotation(text="High Volume<br>High Consistency", 
                          xref="paper", yref="paper", x=0.85, y=0.95, showarrow=False,
                          bgcolor=colors['High-High (Star)'], font=dict(color='white', size=10))
        
        fig.add_annotation(text="High Volume<br>Low Consistency",
                          xref="paper", yref="paper", x=0.85, y=0.05, showarrow=False,
                          bgcolor=colors['High-Low (Volatile)'], font=dict(color='white', size=10))
        
        fig.add_annotation(text="Low Volume<br>High Consistency",
                          xref="paper", yref="paper", x=0.15, y=0.95, showarrow=False,
                          bgcolor=colors['Low-High (Stable)'], font=dict(color='white', size=10))
        
        fig.add_annotation(text="Low Volume<br>Low Consistency",
                          xref="paper", yref="paper", x=0.15, y=0.05, showarrow=False,
                          bgcolor=colors['Low-Low (Watchlist)'], font=dict(color='white', size=10))
        
        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            height=600,
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def create_sparkline(data, width=200, height=60, color='#1f77b4'):
        """
        Create a minimalist sparkline for KPI cards.
        
        Args:
            data: Time series data
            width: Chart width in pixels
            height: Chart height in pixels
            color: Line color
            
        Returns:
            plotly.graph_objects.Figure
        """
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            y=data,
            mode='lines',
            line=dict(color=color, width=2),
            fill='tozeroy',
            fillcolor=f'rgba{tuple(list(px.colors.hex_to_rgb(color)) + [0.2])}'
        ))
        
        fig.update_layout(
            width=width,
            height=height,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_gauge_chart(value, max_value, title="Progress", 
                          thresholds=[0.33, 0.67, 1.0],
                          colors=['red', 'yellow', 'green']):
        """
        Create gauge chart for target tracking.
        
        Args:
            value: Current value
            max_value: Target value
            title: Chart title
            thresholds: Threshold percentages
            colors: Colors for each threshold range
            
        Returns:
            plotly.graph_objects.Figure
        """
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title, 'font': {'size': 20}},
            delta={'reference': max_value, 'increasing': {'color': "green"}},
            gauge={
                'axis': {'range': [None, max_value], 'tickwidth': 1},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, max_value * thresholds[0]], 'color': colors[0]},
                    {'range': [max_value * thresholds[0], max_value * thresholds[1]], 
                     'color': colors[1]},
                    {'range': [max_value * thresholds[1], max_value], 'color': colors[2]}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': max_value
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return fig


# Quick test
if __name__ == "__main__":
    # Test visualizations
    vis = VisualizationSuite()
    
    # Test Pareto chart
    data = [100, 80, 60, 40, 30, 20, 15, 10, 5, 3]
    labels = [f"State {i+1}" for i in range(len(data))]
    fig = vis.create_pareto_chart(data, labels)
    print("✓ Pareto chart created")
    
    # Test Lorenz curve
    values = np.random.lognormal(5, 1, 1000)
    fig = vis.create_lorenz_curve(values)
    print("✓ Lorenz curve created")
    
    # Test control chart
    dates = pd.date_range('2025-01-01', periods=100, freq='D')
    data = np.random.normal(1000, 200, 100)
    data[50] = 2000  # Add outlier
    fig = vis.create_control_chart(data, dates)
    print("✓ Control chart created")
    
    print("\n✓ All visualization tests passed!")
