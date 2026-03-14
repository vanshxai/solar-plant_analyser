"""
Visualization Module for Solar Plant Analyzer
Creates interactive plots and dashboards using Plotly.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Any, Optional
import numpy as np


class Visualizer:
    """Creates visualizations for solar plant data analysis."""
    
    def __init__(self, template: str = "plotly_white"):
        """
        Initialize visualizer.
        
        Args:
            template: Plotly template theme
        """
        self.template = template
        self.color_palette = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'warning': '#ff9800',
            'danger': '#d62728',
            'info': '#17becf'
        }
    
    def create_power_time_series(self, df: pd.DataFrame) -> go.Figure:
        """
        Create power vs time plot.
        
        Args:
            df: DataFrame with timestamp and power data
            
        Returns:
            Plotly figure
        """
        if 'timestamp' not in df.columns or 'power' not in df.columns:
            return go.Figure().add_annotation(text="No power data available")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['power'] / 1000,  # Convert to kW
            mode='lines',
            name='Power',
            line=dict(color=self.color_palette['primary'], width=2),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.2)'
        ))
        
        fig.update_layout(
            title="Power Generation Over Time",
            xaxis_title="Time",
            yaxis_title="Power (kW)",
            template=self.template,
            hovermode='x unified'
        )
        
        return fig
    
    def create_voltage_current_plot(self, df: pd.DataFrame) -> go.Figure:
        """
        Create voltage and current over time plot.
        
        Args:
            df: DataFrame with timestamp, voltage, and current data
            
        Returns:
            Plotly figure
        """
        if 'timestamp' not in df.columns:
            return go.Figure().add_annotation(text="No timestamp data available")
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Voltage trace
        if 'voltage' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['voltage'],
                    mode='lines',
                    name='Voltage',
                    line=dict(color=self.color_palette['secondary'], width=2)
                ),
                secondary_y=False
            )
        
        # Current trace
        if 'current' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['current'],
                    mode='lines',
                    name='Current',
                    line=dict(color=self.color_palette['info'], width=2)
                ),
                secondary_y=True
            )
        
        fig.update_layout(
            title="Voltage and Current Over Time",
            template=self.template,
            hovermode='x unified'
        )
        
        fig.update_xaxes(title_text="Time")
        fig.update_yaxes(title_text="Voltage (V)", secondary_y=False)
        fig.update_yaxes(title_text="Current (A)", secondary_y=True)
        
        return fig
    
    def create_performance_ratio_plot(self, df: pd.DataFrame) -> go.Figure:
        """
        Create performance ratio over time plot.
        
        Args:
            df: DataFrame with timestamp and performance_ratio data
            
        Returns:
            Plotly figure
        """
        if 'performance_ratio' not in df.columns:
            return go.Figure().add_annotation(text="No performance ratio data available")
        
        fig = go.Figure()
        
        # Add PR trace
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['performance_ratio'] * 100,  # Convert to percentage
            mode='lines',
            name='Performance Ratio',
            line=dict(color=self.color_palette['success'], width=2),
            fill='tozeroy',
            fillcolor='rgba(44, 160, 44, 0.2)'
        ))
        
        # Add threshold line
        fig.add_hline(
            y=75,
            line_dash="dash",
            line_color=self.color_palette['warning'],
            annotation_text="75% Threshold",
            annotation_position="top right"
        )
        
        fig.update_layout(
            title="Performance Ratio Over Time",
            xaxis_title="Time",
            yaxis_title="Performance Ratio (%)",
            template=self.template,
            hovermode='x unified'
        )
        
        return fig
    
    def create_fault_markers_plot(
        self, 
        df: pd.DataFrame, 
        faults: List[Dict]
    ) -> go.Figure:
        """
        Create power plot with fault markers.
        
        Args:
            df: DataFrame with timestamp and power data
            faults: List of detected faults
            
        Returns:
            Plotly figure
        """
        fig = self.create_power_time_series(df)
        
        # Add fault markers
        fault_times = []
        fault_texts = []
        
        for fault in faults:
            if fault.get('timestamp') and fault['timestamp'] != 'N/A':
                try:
                    fault_time = pd.to_datetime(fault['timestamp'])
                    fault_times.append(fault_time)
                    fault_texts.append(f"{fault['fault_type']}: {fault['description'][:50]}")
                except:
                    continue
        
        if fault_times:
            fig.add_trace(go.Scatter(
                x=fault_times,
                y=[df['power'].max() / 1000] * len(fault_times),
                mode='markers',
                name='Faults',
                marker=dict(
                    symbol='x',
                    size=15,
                    color=self.color_palette['danger'],
                    line_width=2
                ),
                text=fault_texts,
                hoverinfo='text'
            ))
        
        fig.update_layout(title="Power Generation with Fault Markers")
        
        return fig
    
    def create_temperature_efficiency_plot(self, df: pd.DataFrame) -> go.Figure:
        """
        Create temperature vs power scatter plot.
        
        Args:
            df: DataFrame with temperature and power data
            
        Returns:
            Plotly figure
        """
        if 'temperature' not in df.columns or 'power' not in df.columns:
            return go.Figure().add_annotation(text="No temperature data available")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['temperature'],
            y=df['power'] / 1000,
            mode='markers',
            name='Data Points',
            marker=dict(
                size=8,
                color=df['power'] / 1000,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Power (kW)")
            ),
            text=df['timestamp'].astype(str) if 'timestamp' in df.columns else None,
            hovertemplate='Temp: %{x:.1f}°C<br>Power: %{y:.2f} kW<br>Time: %{text}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Temperature vs Power Generation",
            xaxis_title="Temperature (°C)",
            yaxis_title="Power (kW)",
            template=self.template
        )
        
        return fig
    
    def create_string_comparison_plot(
        self, 
        df: pd.DataFrame, 
        string_col: str = 'string_id'
    ) -> go.Figure:
        """
        Create string performance comparison plot.
        
        Args:
            df: DataFrame with string data
            string_col: Name of string identifier column
            
        Returns:
            Plotly figure
        """
        if string_col not in df.columns or 'power' not in df.columns:
            return go.Figure().add_annotation(text="No string data available")
        
        # Aggregate by string
        string_power = df.groupby(string_col)['power'].mean() / 1000
        
        fig = go.Figure(data=[
            go.Bar(
                x=string_power.index.astype(str),
                y=string_power.values,
                marker_color=self.color_palette['primary'],
                text=[f"{v:.2f} kW" for v in string_power.values],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Average Power by String",
            xaxis_title="String ID",
            yaxis_title="Average Power (kW)",
            template=self.template
        )
        
        return fig
    
    def create_degradation_trend_plot(
        self, 
        df: pd.DataFrame, 
        degradation_data: Dict
    ) -> go.Figure:
        """
        Create degradation trend visualization.
        
        Args:
            df: DataFrame with timestamp and power data
            degradation_data: Degradation analysis results
            
        Returns:
            Plotly figure
        """
        if degradation_data.get('trend') == 'insufficient_data':
            return go.Figure().add_annotation(text="Insufficient data for degradation analysis")
        
        rolling_avg = degradation_data.get('rolling_average', [])
        
        if not rolling_avg:
            return go.Figure().add_annotation(text="No rolling average data available")
        
        # Create date range for rolling average
        if 'timestamp' in df.columns:
            dates = pd.date_range(
                start=df['timestamp'].min(),
                end=df['timestamp'].max(),
                freq='D'
            )
            dates = dates[:len(rolling_avg)]
        else:
            dates = list(range(len(rolling_avg)))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=[v / 1000 for v in rolling_avg],  # Convert to kWh
            mode='lines',
            name='Rolling Average',
            line=dict(color=self.color_palette['primary'], width=3)
        ))
        
        fig.update_layout(
            title="Energy Generation Trend (7-day Rolling Average)",
            xaxis_title="Date",
            yaxis_title="Energy (kWh)",
            template=self.template
        )
        
        # Add annotation for trend
        trend = degradation_data.get('trend', 'unknown')
        pct_change = degradation_data.get('percentage_change', 0)
        
        fig.add_annotation(
            text=f"Trend: {trend.replace('_', ' ').title()} ({pct_change:.1f}%)",
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            showarrow=False,
            bgcolor="white",
            bordercolor=self.color_palette['primary'],
            borderwidth=1
        )
        
        return fig
    
    def create_summary_dashboard(
        self, 
        df: pd.DataFrame,
        metrics: Dict,
        faults: List[Dict]
    ) -> go.Figure:
        """
        Create a multi-panel summary dashboard.
        
        Args:
            df: DataFrame with analyzed data
            metrics: Efficiency metrics
            faults: Detected faults
            
        Returns:
            Plotly figure with multiple subplots
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Power Generation",
                "Voltage & Current",
                "Performance Ratio",
                "Temperature Impact"
            ),
            specs=[[{"type": "scatter"}, {"type": "scatter"}],
                   [{"type": "scatter"}, {"type": "scatter"}]]
        )
        
        # Power plot (top-left)
        if 'timestamp' in df.columns and 'power' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['power'] / 1000,
                    mode='lines',
                    name='Power',
                    line=dict(color=self.color_palette['primary'])
                ),
                row=1, col=1
            )
        
        # Voltage & Current (top-right)
        if 'timestamp' in df.columns:
            if 'voltage' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['voltage'],
                        mode='lines',
                        name='Voltage',
                        line=dict(color=self.color_palette['secondary'])
                    ),
                    row=1, col=2
                )
            if 'current' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['current'],
                        mode='lines',
                        name='Current',
                        line=dict(color=self.color_palette['info'])
                    ),
                    row=1, col=2
                )
        
        # Performance Ratio (bottom-left)
        if 'performance_ratio' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['performance_ratio'] * 100,
                    mode='lines',
                    name='PR',
                    line=dict(color=self.color_palette['success'])
                ),
                row=2, col=1
            )
        
        # Temperature vs Power (bottom-right)
        if 'temperature' in df.columns and 'power' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df['temperature'],
                    y=df['power'] / 1000,
                    mode='markers',
                    name='Temp vs Power',
                    marker=dict(
                        size=6,
                        color=self.color_palette['info']
                    )
                ),
                row=2, col=2
            )
        
        fig.update_layout(
            height=800,
            title="Solar Plant Analysis Dashboard",
            template=self.template,
            showlegend=False
        )
        
        fig.update_xaxes(title_text="Time", row=1, col=1)
        fig.update_xaxes(title_text="Time", row=1, col=2)
        fig.update_xaxes(title_text="Time", row=2, col=1)
        fig.update_xaxes(title_text="Temperature (°C)", row=2, col=2)
        
        fig.update_yaxes(title_text="Power (kW)", row=1, col=1)
        fig.update_yaxes(title_text="Value", row=1, col=2)
        fig.update_yaxes(title_text="PR (%)", row=2, col=1)
        fig.update_yaxes(title_text="Power (kW)", row=2, col=2)
        
        return fig
    
    def create_fault_summary_chart(self, faults: List[Dict]) -> go.Figure:
        """
        Create fault summary pie chart.
        
        Args:
            faults: List of detected faults
            
        Returns:
            Plotly figure
        """
        if not faults:
            fig = go.Figure()
            fig.add_annotation(text="No faults detected", showarrow=False)
            return fig
        
        # Count faults by type
        fault_counts = {}
        for fault in faults:
            fault_type = fault.get('fault_type', 'unknown')
            fault_counts[fault_type] = fault_counts.get(fault_type, 0) + 1
        
        fig = go.Figure(data=[
            go.Pie(
                labels=[ft.replace('_', ' ').title() for ft in fault_counts.keys()],
                values=list(fault_counts.values()),
                hole=0.4,
                marker_colors=[
                    self.color_palette['danger'],
                    self.color_palette['warning'],
                    self.color_palette['info'],
                    self.color_palette['primary'],
                    self.color_palette['secondary']
                ]
            )
        ])
        
        fig.update_layout(
            title="Fault Distribution by Type",
            template=self.template
        )
        
        return fig


def create_visualizations(
    df: pd.DataFrame,
    metrics: Dict,
    faults: List[Dict],
    analysis_results: Optional[Dict] = None
) -> Dict[str, go.Figure]:
    """
    Create all standard visualizations.
    
    Args:
        df: Analyzed DataFrame
        metrics: Efficiency metrics
        faults: Detected faults
        analysis_results: Full analysis results
        
    Returns:
        Dictionary of figures
    """
    viz = Visualizer()
    
    figures = {
        'power_time_series': viz.create_power_time_series(df),
        'voltage_current': viz.create_voltage_current_plot(df),
        'performance_ratio': viz.create_performance_ratio_plot(df),
        'fault_markers': viz.create_fault_markers_plot(df, faults),
        'fault_summary': viz.create_fault_summary_chart(faults),
        'summary_dashboard': viz.create_summary_dashboard(df, metrics, faults)
    }
    
    if 'temperature' in df.columns:
        figures['temperature_efficiency'] = viz.create_temperature_efficiency_plot(df)
    
    if analysis_results and 'degradation_analysis' in analysis_results:
        figures['degradation_trend'] = viz.create_degradation_trend_plot(
            df, 
            analysis_results['degradation_analysis']
        )
    
    return figures
