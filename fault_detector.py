"""
Fault Detection Engine Module for Solar Plant Analyzer
Detects anomalies and faults in solar plant data using rule-based algorithms.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class FaultSeverity(Enum):
    """Fault severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FaultType(Enum):
    """Types of detected faults."""
    CURRENT_MISMATCH = "current_mismatch"
    POWER_DROP = "power_drop"
    VOLTAGE_ANOMALY = "voltage_anomaly"
    DEGRADATION = "degradation"
    TEMPERATURE_ANOMALY = "temperature_anomaly"
    PERFORMANCE_RATIO_LOW = "performance_ratio_low"
    DATA_QUALITY = "data_quality"
    POWER_MISMATCH = "power_mismatch"


@dataclass
class Fault:
    """Represents a detected fault."""
    fault_type: str
    severity: str
    timestamp: Optional[str]
    description: str
    possible_cause: str
    recommended_action: str
    value: Optional[float] = None
    threshold: Optional[float] = None
    string_id: Optional[str] = None


class FaultDetector:
    """Detects faults and anomalies in solar plant data."""
    
    def __init__(
        self,
        current_mismatch_threshold: float = 0.7,
        power_drop_threshold: float = 0.4,
        power_drop_window_minutes: int = 10,
        degradation_threshold: float = 0.1,
        degradation_window_days: int = 30,
        pr_low_threshold: float = 0.75
    ):
        """
        Initialize fault detector with configurable thresholds.
        
        Args:
            current_mismatch_threshold: Current below this fraction of average triggers fault
            power_drop_threshold: Power drop fraction that triggers alert
            power_drop_window_minutes: Time window for power drop detection
            degradation_threshold: Degradation fraction that triggers alert
            degradation_window_days: Days to analyze for degradation
            pr_low_threshold: Performance ratio below this triggers alert
        """
        self.current_mismatch_threshold = current_mismatch_threshold
        self.power_drop_threshold = power_drop_threshold
        self.power_drop_window_minutes = power_drop_window_minutes
        self.degradation_threshold = degradation_threshold
        self.degradation_window_days = degradation_window_days
        self.pr_low_threshold = pr_low_threshold
        self.detected_faults: List[Fault] = []
    
    def detect_current_mismatch(
        self, 
        df: pd.DataFrame,
        string_col: str = 'string_id'
    ) -> List[Fault]:
        """
        Detect current mismatch between strings or abnormal low current.
        
        Args:
            df: DataFrame with current data
            string_col: Name of string identifier column
            
        Returns:
            List of detected faults
        """
        faults = []
        
        if 'current' not in df.columns:
            return faults
        
        df = df.copy()
        
        # Only analyze data during peak generation hours (when power > 0)
        # This avoids false positives at night/early morning
        generation_data = df[df['power'] > 0].copy() if 'power' in df.columns else df
        
        if len(generation_data) == 0:
            return faults
        
        avg_current = generation_data['current'].mean()
        
        # Check for overall current mismatch
        for idx, row in generation_data.iterrows():
            if row['current'] < self.current_mismatch_threshold * avg_current and avg_current > 0:
                # Only flag if power should be expected (daytime hours 8-17)
                if 'timestamp' in df.columns:
                    hour = row['timestamp'].hour if pd.notna(row['timestamp']) else 12
                    if 8 <= hour <= 17:  # Peak generation hours
                        faults.append(Fault(
                            fault_type=FaultType.CURRENT_MISMATCH.value,
                            severity=FaultSeverity.MEDIUM.value,
                            timestamp=str(row.get('timestamp', 'N/A')),
                            description=f"Current ({row['current']:.2f}A) is below {self.current_mismatch_threshold*100:.0f}% of average ({avg_current:.2f}A)",
                            possible_cause="Shading, damaged panel, connector fault, or string imbalance",
                            recommended_action="Inspect panels for shading, check connections, measure individual string currents",
                            value=row['current'],
                            threshold=self.current_mismatch_threshold * avg_current
                        ))
        
        # Check per-string if string_id exists
        if string_col in df.columns:
            string_avg_current = df.groupby(string_col)['current'].mean()
            overall_avg = string_avg_current.mean()
            
            for string_id, str_avg in string_avg_current.items():
                if str_avg < self.current_mismatch_threshold * overall_avg:
                    faults.append(Fault(
                        fault_type=FaultType.CURRENT_MISMATCH.value,
                        severity=FaultSeverity.HIGH.value,
                        timestamp=None,
                        description=f"String {string_id} average current ({str_avg:.2f}A) is below {self.current_mismatch_threshold*100:.0f}% of overall average ({overall_avg:.2f}A)",
                        possible_cause="String-level fault: shading, panel damage, or connection issue",
                        recommended_action=f"Inspect string {string_id} for faults, check all connections and panels",
                        value=str_avg,
                        threshold=self.current_mismatch_threshold * overall_avg,
                        string_id=str(string_id)
                    ))
        
        return faults
    
    def detect_sudden_power_drop(self, df: pd.DataFrame) -> List[Fault]:
        """
        Detect sudden drops in power output.
        
        Args:
            df: DataFrame with timestamp and power data
            
        Returns:
            List of detected faults
        """
        faults = []
        
        if 'power' not in df.columns or 'timestamp' not in df.columns:
            return faults
        
        df = df.copy()
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Calculate power change rate
        df['power_change'] = df['power'].pct_change()
        
        # Detect sudden drops
        for idx in range(1, len(df)):
            if pd.notna(df.loc[idx, 'power_change']):
                change = df.loc[idx, 'power_change']
                
                if change < -self.power_drop_threshold:
                    prev_power = df.loc[idx-1, 'power']
                    curr_power = df.loc[idx, 'power']
                    
                    faults.append(Fault(
                        fault_type=FaultType.POWER_DROP.value,
                        severity=FaultSeverity.HIGH.value,
                        timestamp=str(df.loc[idx, 'timestamp']),
                        description=f"Sudden power drop from {prev_power:.0f}W to {curr_power:.0f}W ({change*100:.1f}% decrease)",
                        possible_cause="Inverter trip, grid issue, breaker trip, or sudden shading",
                        recommended_action="Check inverter status, verify grid connection, inspect for new shading",
                        value=curr_power,
                        threshold=prev_power * (1 - self.power_drop_threshold)
                    ))
        
        return faults
    
    def detect_voltage_anomalies(self, df: pd.DataFrame) -> List[Fault]:
        """
        Detect voltage anomalies and out-of-range values.
        
        Args:
            df: DataFrame with voltage data
            
        Returns:
            List of detected faults
        """
        faults = []
        
        if 'voltage' not in df.columns:
            return faults
        
        df = df.copy()
        avg_voltage = df['voltage'].mean()
        std_voltage = df['voltage'].std()
        
        # Detect voltage spikes or drops
        for idx, row in df.iterrows():
            voltage = row['voltage']
            
            # Check for significant deviation from average
            if std_voltage > 0:
                z_score = abs(voltage - avg_voltage) / std_voltage
                
                if z_score > 3:  # More than 3 standard deviations
                    severity = FaultSeverity.HIGH if z_score > 4 else FaultSeverity.MEDIUM
                    
                    if voltage < avg_voltage:
                        description = f"Voltage ({voltage:.1f}V) significantly below average ({avg_voltage:.1f}V)"
                        cause = "Panel degradation, connection resistance, or partial string failure"
                    else:
                        description = f"Voltage ({voltage:.1f}V) significantly above average ({avg_voltage:.1f}V)"
                        cause = "Possible measurement error or inverter regulation issue"
                    
                    faults.append(Fault(
                        fault_type=FaultType.VOLTAGE_ANOMALY.value,
                        severity=severity.value,
                        timestamp=str(row.get('timestamp', 'N/A')),
                        description=description,
                        possible_cause=cause,
                        recommended_action="Verify voltage measurements, check panel connections and inverter settings",
                        value=voltage,
                        threshold=avg_voltage
                    ))
        
        return faults
    
    def detect_degradation(
        self, 
        df: pd.DataFrame,
        degradation_data: Optional[Dict] = None
    ) -> List[Fault]:
        """
        Detect long-term performance degradation.
        
        Args:
            df: DataFrame with historical data
            degradation_data: Pre-calculated degradation analysis from AnalysisEngine
            
        Returns:
            List of detected faults
        """
        faults = []
        
        if degradation_data is None:
            return faults
        
        if degradation_data.get('trend') in ['significant_degradation', 'moderate_degradation']:
            pct_change = degradation_data.get('percentage_change', 0)
            
            if pct_change < -10:
                severity = FaultSeverity.HIGH
            else:
                severity = FaultSeverity.MEDIUM
            
            faults.append(Fault(
                fault_type=FaultType.DEGRADATION.value,
                severity=severity.value,
                timestamp=None,
                description=f"Performance degradation detected: {pct_change:.1f}% decline over analysis period",
                possible_cause="Panel aging, soiling, permanent shading, or equipment degradation",
                recommended_action="Schedule maintenance, clean panels, inspect for new obstructions, consider panel testing",
                value=pct_change,
                threshold=-self.degradation_threshold * 100
            ))
        
        return faults
    
    def detect_temperature_anomalies(
        self, 
        df: pd.DataFrame,
        temp_analysis: Optional[Dict] = None
    ) -> List[Fault]:
        """
        Detect temperature-related efficiency issues.
        
        Args:
            df: DataFrame with temperature and power data
            temp_analysis: Pre-calculated temperature analysis from AnalysisEngine
            
        Returns:
            List of detected faults
        """
        faults = []
        
        if 'temperature' not in df.columns or 'power' not in df.columns:
            return faults
        
        if temp_analysis and temp_analysis.get('temperature_anomalies', 0) > 0:
            anomaly_count = temp_analysis['temperature_anomalies']
            
            faults.append(Fault(
                fault_type=FaultType.TEMPERATURE_ANOMALY.value,
                severity=FaultSeverity.MEDIUM.value,
                timestamp=None,
                description=f"Detected {anomaly_count} instances of high temperature with low power output",
                possible_cause="Hot spots, poor ventilation, or panel damage",
                recommended_action="Inspect panels for hot spots using thermal imaging, check ventilation and mounting",
                value=anomaly_count
            ))
        
        return faults
    
    def detect_low_performance_ratio(
        self, 
        df: pd.DataFrame
    ) -> List[Fault]:
        """
        Detect periods of low performance ratio.
        
        Args:
            df: DataFrame with performance_ratio column
            
        Returns:
            List of detected faults
        """
        faults = []
        
        if 'performance_ratio' not in df.columns:
            return faults
        
        df = df.copy()
        
        # Find periods with low PR during generation hours
        low_pr_data = df[df['performance_ratio'] < self.pr_low_threshold]
        
        if len(low_pr_data) > 0:
            avg_low_pr = low_pr_data['performance_ratio'].mean()
            
            # Determine severity based on how low the PR is
            if avg_low_pr < 0.5:
                severity = FaultSeverity.CRITICAL
            elif avg_low_pr < 0.6:
                severity = FaultSeverity.HIGH
            else:
                severity = FaultSeverity.MEDIUM
            
            faults.append(Fault(
                fault_type=FaultType.PERFORMANCE_RATIO_LOW.value,
                severity=severity.value,
                timestamp=None,
                description=f"Performance ratio below {self.pr_low_threshold*100:.0f}% for {len(low_pr_data)} data points (avg: {avg_low_pr*100:.1f}%)",
                possible_cause="System inefficiency, inverter issues, soiling, or degradation",
                recommended_action="Review system efficiency, check inverter performance, clean panels",
                value=avg_low_pr,
                threshold=self.pr_low_threshold
            ))
        
        return faults
    
    def detect_power_mismatch(self, df: pd.DataFrame) -> List[Fault]:
        """
        Detect mismatch between measured and calculated power (P = V * I).
        
        Args:
            df: DataFrame with power, voltage, current, and calculated_power
            
        Returns:
            List of detected faults
        """
        faults = []
        
        if 'calculated_power' not in df.columns or 'power' not in df.columns:
            return faults
        
        df = df.copy()
        
        # Calculate deviation percentage
        df['deviation_pct'] = abs(
            df['power'] - df['calculated_power']
        ) / df['calculated_power'].replace(0, np.nan) * 100
        
        # Flag significant deviations
        high_deviation = df[df['deviation_pct'] > 20]  # More than 20% deviation
        
        if len(high_deviation) > 0:
            faults.append(Fault(
                fault_type=FaultType.POWER_MISMATCH.value,
                severity=FaultSeverity.LOW.value,
                timestamp=None,
                description=f"Power measurement deviation detected in {len(high_deviation)} data points (>20% from V*I calculation)",
                possible_cause="Sensor calibration issue, measurement error, or power factor effects",
                recommended_action="Verify sensor calibration, check measurement equipment",
                value=high_deviation['deviation_pct'].mean()
            ))
        
        return faults
    
    def detect_all_faults(
        self, 
        df: pd.DataFrame,
        analysis_results: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Run all fault detection algorithms.
        
        Args:
            df: Analyzed DataFrame
            analysis_results: Results from AnalysisEngine
            
        Returns:
            List of detected faults as dictionaries
        """
        self.detected_faults = []
        
        # Run all detectors
        self.detected_faults.extend(self.detect_current_mismatch(df))
        self.detected_faults.extend(self.detect_sudden_power_drop(df))
        self.detected_faults.extend(self.detect_voltage_anomalies(df))
        self.detected_faults.extend(self.detect_power_mismatch(df))
        self.detected_faults.extend(self.detect_low_performance_ratio(df))
        
        # Use analysis results if available
        if analysis_results:
            degradation_data = analysis_results.get('degradation_analysis', {})
            temp_analysis = analysis_results.get('temperature_analysis', {})
            
            self.detected_faults.extend(self.detect_degradation(df, degradation_data))
            self.detected_faults.extend(self.detect_temperature_anomalies(df, temp_analysis))
        
        # Sort by severity
        severity_order = {
            FaultSeverity.CRITICAL.value: 0,
            FaultSeverity.HIGH.value: 1,
            FaultSeverity.MEDIUM.value: 2,
            FaultSeverity.LOW.value: 3
        }
        
        self.detected_faults.sort(key=lambda f: severity_order.get(f.severity, 4))
        
        # Convert to dictionaries
        return [asdict(fault) for fault in self.detected_faults]
    
    def get_fault_summary(self) -> Dict[str, Any]:
        """
        Get summary of detected faults.
        
        Returns:
            Summary dictionary
        """
        summary = {
            'total_faults': len(self.detected_faults),
            'by_severity': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            },
            'by_type': {}
        }
        
        for fault in self.detected_faults:
            summary['by_severity'][fault.severity] = summary['by_severity'].get(fault.severity, 0) + 1
            
            fault_type = fault.fault_type
            summary['by_type'][fault_type] = summary['by_type'].get(fault_type, 0) + 1
        
        return summary


def detect_faults(
    df: pd.DataFrame, 
    analysis_results: Optional[Dict] = None
) -> List[Dict]:
    """
    Convenience function to detect all faults.
    
    Args:
        df: Analyzed DataFrame
        analysis_results: Results from AnalysisEngine
        
    Returns:
        List of detected faults
    """
    detector = FaultDetector()
    return detector.detect_all_faults(df, analysis_results)
