"""
Test script for Solar Plant Analyzer modules.
"""

import sys
sys.path.insert(0, '/Users/mac/Desktop/AI/solar_analyzer')

from data_loader import DataLoader, load_data
from analysis_engine import AnalysisEngine, analyze_data
from fault_detector import FaultDetector, detect_faults
from visualization import Visualizer
from report_generator import ReportGenerator, generate_report
import pandas as pd

def test_all_modules():
    """Test all modules with sample data."""
    print("=" * 60)
    print("Solar Plant Analyzer - Module Tests")
    print("=" * 60)
    
    # Test 1: Data Loader
    print("\n[1/5] Testing Data Loader...")
    loader = DataLoader()
    df, report = loader.load_and_process('sample_data/solar_sample.csv')
    
    if df is not None and report.get('success'):
        print(f"  ✓ Loaded {len(df)} rows")
        print(f"  ✓ Columns: {list(df.columns)}")
        print(f"  ✓ Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    else:
        print(f"  ✗ Failed to load data: {report}")
        return False
    
    # Test 2: Analysis Engine
    print("\n[2/5] Testing Analysis Engine...")
    analyzer = AnalysisEngine(plant_capacity_kw=500)
    analysis_results = analyzer.analyze(df)
    
    metrics = analysis_results.get('efficiency_metrics', {})
    print(f"  ✓ Total Energy: {metrics.get('total_energy_kwh', 0):.2f} kWh")
    print(f"  ✓ Avg Power: {metrics.get('avg_power_kw', 0):.2f} kW")
    print(f"  ✓ Peak Power: {metrics.get('peak_power_kw', 0):.2f} kW")
    print(f"  ✓ Avg Performance Ratio: {metrics.get('avg_performance_ratio', 0)*100:.1f}%")
    
    # Test 3: Fault Detector
    print("\n[3/5] Testing Fault Detector...")
    detector = FaultDetector()
    faults = detector.detect_all_faults(df, analysis_results)
    
    print(f"  ✓ Detected {len(faults)} faults")
    
    severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    for fault in faults:
        severity_counts[fault.get('severity', 'low')] += 1
    
    print(f"    - Critical: {severity_counts['critical']}")
    print(f"    - High: {severity_counts['high']}")
    print(f"    - Medium: {severity_counts['medium']}")
    print(f"    - Low: {severity_counts['low']}")
    
    # Test 4: Visualization
    print("\n[4/5] Testing Visualization...")
    visualizer = Visualizer()
    
    fig_power = visualizer.create_power_time_series(df)
    fig_pr = visualizer.create_performance_ratio_plot(df)
    fig_faults = visualizer.create_fault_summary_chart(faults)
    
    print(f"  ✓ Created power time series figure")
    print(f"  ✓ Created performance ratio figure")
    print(f"  ✓ Created fault summary chart")
    
    # Test 5: Report Generator
    print("\n[5/5] Testing Report Generator...")
    generator = ReportGenerator()
    
    # Text report
    text_report = generator.generate_text_report(metrics, faults)
    print(f"  ✓ Generated text report ({len(text_report)} chars)")
    
    # CSV report
    csv_report = generator.generate_csv_report(faults, metrics)
    print(f"  ✓ Generated CSV report ({len(csv_report)} chars)")
    
    # JSON report
    json_report = generator.generate_json_report(metrics, faults)
    print(f"  ✓ Generated JSON report with {len(json_report)} keys")
    
    # Sample text report preview
    print("\n" + "=" * 60)
    print("Sample Report Preview (first 500 chars):")
    print("=" * 60)
    print(text_report[:500] + "...")
    
    print("\n" + "=" * 60)
    print("All tests passed successfully! ✓")
    print("=" * 60)
    print("\nTo run the dashboard:")
    print("  cd /Users/mac/Desktop/AI/solar_analyzer")
    print("  streamlit run main.py")
    
    return True


if __name__ == "__main__":
    try:
        success = test_all_modules()
        if success:
            print("\n✓ Solar Plant Analyzer is ready to use!")
        else:
            print("\n✗ Some tests failed.")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
