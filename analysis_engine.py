"""
Analysis Engine Module for Solar Plant Analyzer
Handles solar performance calculations and metrics.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple


class AnalysisEngine:
    """Performs solar plant performance analysis and calculations."""
    
    def __init__(self, plant_capacity_kw: float = 500.0):
        """
        Initialize the analysis engine.
        
        Args:
            plant_capacity_kw: Rated plant capacity in kW (for performance ratio calculation)
        """
        self.plant_capacity_kw = plant_capacity_kw
        self.analysis_results = {}
    
    def calculate_power_verification(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Verify power measurements using P = V * I equation.
        
        Args:
            df: DataFrame with voltage, current, and power columns
            
        Returns:
            DataFrame with calculated power and deviation
        """
        df = df.copy()
        
        if 'voltage' in df.columns and 'current' in df.columns:
            df['calculated_power'] = df['voltage'] * df['current']
            
            # Calculate deviation between measured and calculated power
            if 'power' in df.columns:
                df['power_deviation'] = df['power'] - df['calculated_power']
                df['power_deviation_pct'] = (
                    df['power_deviation'] / df['calculated_power'].replace(0, np.nan) * 100
                )
        
        return df
    
    def calculate_performance_ratio(
        self, 
        df: pd.DataFrame, 
        expected_power_col: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Calculate Performance Ratio (PR) = Actual Power / Expected Power.
        
        Args:
            df: DataFrame with power data
            expected_power_col: Column name for expected power, or None to estimate
            
        Returns:
            DataFrame with performance ratio
        """
        df = df.copy()
        
        if expected_power_col and expected_power_col in df.columns:
            df['expected_power'] = df[expected_power_col]
        else:
            # Estimate expected power based on plant capacity and solar irradiance pattern
            # Using a simplified sine curve model for expected generation
            if 'timestamp' in df.columns:
                df['hour'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute / 60
                # Normalize hour to 0-24 range and calculate expected power
                df['expected_power'] = self.plant_capacity_kw * 1000 * np.sin(
                    np.clip(df['hour'] / 24 * np.pi, 0, np.pi)
                )
        
        if 'power' in df.columns and 'expected_power' in df.columns:
            df['performance_ratio'] = df['power'] / df['expected_power'].replace(0, np.nan)
        
        return df
    
    def calculate_efficiency_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate overall efficiency metrics for the plant.
        
        Args:
            df: DataFrame with analyzed data
            
        Returns:
            Dictionary of efficiency metrics
        """
        metrics = {}
        
        if 'power' in df.columns:
            # Total energy generated (kWh)
            # Assuming hourly data, otherwise adjust based on timestamp frequency
            metrics['total_energy_kwh'] = df['power'].sum() / 1000
            
            # Average power
            metrics['avg_power_kw'] = df['power'].mean() / 1000
            
            # Peak power
            metrics['peak_power_kw'] = df['power'].max() / 1000
            
            # Capacity factor
            if len(df) > 0:
                max_possible_energy = self.plant_capacity_kw * len(df)
                metrics['capacity_factor'] = metrics['total_energy_kwh'] / max_possible_energy if max_possible_energy > 0 else 0
        
        if 'performance_ratio' in df.columns:
            metrics['avg_performance_ratio'] = df['performance_ratio'].mean()
            metrics['min_performance_ratio'] = df['performance_ratio'].min()
        
        if 'voltage' in df.columns:
            metrics['avg_voltage'] = df['voltage'].mean()
            metrics['min_voltage'] = df['voltage'].min()
            metrics['max_voltage'] = df['voltage'].max()
        
        if 'current' in df.columns:
            metrics['avg_current'] = df['current'].mean()
            metrics['min_current'] = df['current'].min()
            metrics['max_current'] = df['current'].max()
        
        if 'temperature' in df.columns:
            metrics['avg_temperature'] = df['temperature'].mean()
            metrics['max_temperature'] = df['temperature'].max()
        
        return metrics
    
    def calculate_string_analysis(
        self, 
        df: pd.DataFrame, 
        string_col: str = 'string_id'
    ) -> Dict[str, Dict[str, float]]:
        """
        Analyze performance by string (if string_id column exists).
        
        Args:
            df: DataFrame with string data
            string_col: Name of the string identifier column
            
        Returns:
            Dictionary of performance metrics per string
        """
        if string_col not in df.columns:
            return {}
        
        string_metrics = {}
        
        for string_id in df[string_col].unique():
            string_data = df[df[string_col] == string_id]
            
            string_metrics[str(string_id)] = {
                'avg_power': string_data['power'].mean() if 'power' in string_data.columns else 0,
                'avg_current': string_data['current'].mean() if 'current' in string_data.columns else 0,
                'avg_voltage': string_data['voltage'].mean() if 'voltage' in string_data.columns else 0,
                'total_energy': string_data['power'].sum() / 1000 if 'power' in string_data.columns else 0,
                'data_points': len(string_data)
            }
        
        return string_metrics
    
    def calculate_degradation_trend(
        self, 
        df: pd.DataFrame, 
        window_days: int = 7
    ) -> Dict[str, Any]:
        """
        Calculate long-term degradation trend using rolling averages.
        
        Args:
            df: DataFrame with timestamp and power data
            window_days: Window size for rolling average in days
            
        Returns:
            Dictionary with degradation analysis
        """
        if 'timestamp' not in df.columns or 'power' not in df.columns:
            return {'trend': 'insufficient_data'}
        
        df = df.copy()
        df = df.set_index('timestamp')
        
        # Calculate daily energy
        daily_energy = df['power'].resample('D').sum()
        
        if len(daily_energy) < window_days * 2:
            return {'trend': 'insufficient_data'}
        
        # Calculate rolling average
        rolling_avg = daily_energy.rolling(window=window_days, min_periods=1).mean()
        
        # Calculate trend (percentage change over the period)
        if len(rolling_avg) >= window_days:
            first_period_avg = rolling_avg.iloc[:window_days].mean()
            last_period_avg = rolling_avg.iloc[-window_days:].mean()
            
            if first_period_avg > 0:
                pct_change = (last_period_avg - first_period_avg) / first_period_avg * 100
            else:
                pct_change = 0
            
            # Determine trend direction
            if pct_change < -10:
                trend = 'significant_degradation'
            elif pct_change < -5:
                trend = 'moderate_degradation'
            elif pct_change < 0:
                trend = 'slight_decline'
            elif pct_change < 5:
                trend = 'stable'
            else:
                trend = 'improving'
            
            return {
                'trend': trend,
                'percentage_change': pct_change,
                'first_period_avg_kwh': first_period_avg / 1000,
                'last_period_avg_kwh': last_period_avg / 1000,
                'rolling_average': rolling_avg.tolist()
            }
        
        return {'trend': 'insufficient_data'}
    
    def calculate_temperature_efficiency(
        self, 
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Analyze temperature-based efficiency impact.
        
        Args:
            df: DataFrame with temperature and power data
            
        Returns:
            Dictionary with temperature efficiency analysis
        """
        if 'temperature' not in df.columns or 'power' not in df.columns:
            return {'available': False}
        
        df = df.copy()
        
        # Calculate correlation between temperature and power
        correlation = df['temperature'].corr(df['power'])
        
        # Detect temperature anomalies (high temp with low power)
        if len(df) > 10:
            temp_threshold = df['temperature'].quantile(0.75)
            power_threshold = df['power'].quantile(0.25)
            
            temp_anomalies = df[
                (df['temperature'] > temp_threshold) & 
                (df['power'] < power_threshold)
            ]
            
            anomaly_count = len(temp_anomalies)
        else:
            anomaly_count = 0
        
        return {
            'available': True,
            'temp_power_correlation': correlation,
            'temperature_anomalies': anomaly_count,
            'avg_temperature': df['temperature'].mean(),
            'max_temperature': df['temperature'].max()
        }
    
    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Run complete analysis pipeline.
        
        Args:
            df: Preprocessed DataFrame
            
        Returns:
            Complete analysis results
        """
        # Power verification
        df = self.calculate_power_verification(df)
        
        # Performance ratio
        df = self.calculate_performance_ratio(df)
        
        # Efficiency metrics
        efficiency_metrics = self.calculate_efficiency_metrics(df)
        
        # String analysis (if applicable)
        string_metrics = self.calculate_string_analysis(df)
        
        # Degradation trend
        degradation = self.calculate_degradation_trend(df)
        
        # Temperature efficiency
        temp_efficiency = self.calculate_temperature_efficiency(df)
        
        self.analysis_results = {
            'data': df,
            'efficiency_metrics': efficiency_metrics,
            'string_metrics': string_metrics,
            'degradation_analysis': degradation,
            'temperature_analysis': temp_efficiency
        }
        
        return self.analysis_results


def analyze_data(df: pd.DataFrame, plant_capacity_kw: float = 500.0) -> Dict[str, Any]:
    """
    Convenience function to analyze solar data.
    
    Args:
        df: Preprocessed DataFrame
        plant_capacity_kw: Plant capacity in kW
        
    Returns:
        Analysis results dictionary
    """
    engine = AnalysisEngine(plant_capacity_kw)
    return engine.analyze(df)
