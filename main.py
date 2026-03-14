"""
Solar Plant Analyzer - Simple Dashboard
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from data_loader import DataLoader
from analysis_engine import AnalysisEngine
from fault_detector import FaultDetector
from visualization import Visualizer
from report_generator import ReportGenerator


st.set_page_config(
    page_title="Solar Plant Analyzer",
    page_icon="☀️",
    layout="wide"
)

# Title
st.title("☀️ Solar Plant Analyzer")

# Info button - toggle help section
if 'show_info' not in st.session_state:
    st.session_state.show_info = False

col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("Automatic fault detection and performance analysis for solar plants")
with col2:
    if st.button("ℹ️ What is this?", use_container_width=True):
        st.session_state.show_info = not st.session_state.show_info
        st.rerun()

# Info Section (shown when button clicked)
if st.session_state.show_info:
    with st.expander("📖 What Does This App Do?", expanded=True):
        st.markdown("""
        ### 🎯 Purpose
        
        This tool analyzes your solar plant's performance data and automatically finds problems.
        
        ---
        
        ### 📥 What You Need to Provide
        
        A **CSV or Excel file** from your solar inverter or monitoring system with these columns:
        
        | Column | Description | Example |
        |--------|-------------|---------|
        | `timestamp` | Date and time | 2026-03-14 10:00:00 |
        | `voltage` | Panel voltage (Volts) | 580 |
        | `current` | String current (Amps) | 8.5 |
        | `power` | Power generated (Watts) | 5015 |
        
        **Optional:** `temperature`, `irradiance`, `string_id`
        
        ---
        
        ### 🔍 What The App Detects
        
        | Fault Type | What It Means | Why It Matters |
        |------------|---------------|----------------|
        | **Current Mismatch** | One string producing less current | Shading, damaged panel, or bad connection |
        | **Power Drop** | Sudden decrease in power output | Inverter trip, grid issue, or breaker trip |
        | **Voltage Anomaly** | Voltage too high or too low | Equipment malfunction or measurement error |
        | **Low Performance** | System not producing expected power | Soiling, degradation, or inefficiency |
        | **Temperature Issue** | High temp with low power | Hot spots or poor ventilation |
        
        ---
        
        ### 📊 What You Get
        
        1. **Performance Metrics** - Total energy, average power, efficiency ratings
        2. **Fault List** - All detected issues with severity (Critical/High/Medium/Low)
        3. **Interactive Graphs** - Visual trends of power, voltage, current over time
        4. **Downloadable Report** - Text report and raw data for sharing
        
        ---
        
        ### 🚀 How to Use
        
        1. Check **"Use Sample Data"** to see a demo (recommended first time)
        2. Or **upload your own CSV/Excel** file from your inverter
        3. Review the **faults detected** and their priority
        4. Check the **graphs** to understand performance trends
        5. **Download report** to share with your maintenance team
        
        ---
        
        ### ⚙️ Settings (Sidebar)
        
        - **Plant Capacity** - Your system's rated power (default: 500 kW)
        - **Upload File** - Your solar data file
        - **Use Sample Data** - Demo mode with built-in test data
        """)
    
    st.divider()


# Sidebar
with st.sidebar:
    st.header("Settings")
    
    uploaded_file = st.file_uploader("Upload CSV/Excel", type=['csv', 'xlsx'])
    
    use_sample = st.checkbox("Use Sample Data", value=True)
    
    st.divider()
    
    plant_capacity = st.slider("Plant Capacity (kW)", 10, 1000, 500)


def load_sample_data():
    """Generate simple sample data."""
    import numpy as np
    np.random.seed(42)
    
    timestamps = pd.date_range(start='2026-03-14 06:00', end='2026-03-14 18:00', freq='H')
    hours = np.array([t.hour for t in timestamps])
    
    # Solar curve
    irradiance = 1000 * np.exp(-((hours - 12) ** 2) / 8)
    
    voltage = 580 + np.random.normal(0, 5, len(timestamps))
    current = (irradiance / 1000) * 10
    power = voltage * current * 0.95
    temperature = 25 + 8 * np.sin((hours - 6) * np.pi / 12)
    
    # Inject simple faults
    power[8] *= 0.5  # Power drop at 14:00
    current[4] = 3.5  # Low current at 10:00
    
    return pd.DataFrame({
        'timestamp': timestamps,
        'voltage': voltage,
        'current': current,
        'power': power,
        'temperature': temperature
    })


# Main logic
if uploaded_file or use_sample:
    # Load data
    if use_sample:
        df = load_sample_data()
    else:
        loader = DataLoader()
        df, report = loader.load_and_process(uploaded_file)
        if df is None:
            st.error(f"Error loading file: {report}")
            st.stop()
    
    # Analyze
    analyzer = AnalysisEngine(plant_capacity_kw=plant_capacity)
    results = analyzer.analyze(df)
    metrics = results.get('efficiency_metrics', {})
    
    # Detect faults
    detector = FaultDetector()
    faults = detector.detect_all_faults(df, results)
    
    # Display Results
    st.divider()
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Energy", f"{metrics.get('total_energy_kwh', 0):.1f} kWh")
    
    with col2:
        st.metric("Avg Power", f"{metrics.get('avg_power_kw', 0):.1f} kW")
    
    with col3:
        st.metric("Peak Power", f"{metrics.get('peak_power_kw', 0):.1f} kW")
    
    with col4:
        st.metric("Faults Found", len(faults))
    
    st.divider()
    
    # Faults Section
    st.subheader("⚠️ Faults Detected")
    
    if not faults:
        st.success("✅ No faults detected! System is running normally.")
    else:
        # Group by severity
        critical = [f for f in faults if f['severity'] == 'critical']
        high = [f for f in faults if f['severity'] == 'high']
        medium = [f for f in faults if f['severity'] == 'medium']
        low = [f for f in faults if f['severity'] == 'low']
        
        if critical:
            st.error(f"🔴 **{len(critical)} Critical Issues** - Immediate action needed!")
        if high:
            st.warning(f"🟠 **{len(high)} High Priority** - Address within 24 hours")
        if medium:
            st.info(f"🟡 **{len(medium)} Medium Priority** - Schedule maintenance")
        if low:
            st.info(f"🔵 **{len(low)} Low Priority** - Monitor")
        
        st.divider()
        
        # Show each fault simply
        for fault in faults:
            icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}.get(fault['severity'], "🔵")
            
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{icon} {fault['fault_type'].replace('_', ' ').title()}**")
                    st.write(fault['description'])
                
                with col2:
                    if fault.get('timestamp') and fault['timestamp'] != 'N/A':
                        st.caption(f"Time: {fault['timestamp']}")
                
                with st.expander("View Details"):
                    st.write(f"**Cause:** {fault['possible_cause']}")
                    st.write(f"**Action:** {fault['recommended_action']}")
                
                st.divider()
    
    # Graphs
    st.subheader("📊 Graphs")
    
    viz = Visualizer()
    
    tab1, tab2, tab3 = st.tabs(["Power", "Voltage & Current", "Performance"])
    
    with tab1:
        st.plotly_chart(viz.create_power_time_series(df), use_container_width=True)
    
    with tab2:
        st.plotly_chart(viz.create_voltage_current_plot(df), use_container_width=True)
    
    with tab3:
        st.plotly_chart(viz.create_performance_ratio_plot(df), use_container_width=True)
    
    # Export
    st.divider()
    st.subheader("📥 Download Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        generator = ReportGenerator()
        text_report = generator.generate_text_report(metrics, faults, {'capacity_kw': plant_capacity})
        st.download_button(
            "Download Text Report",
            text_report,
            f"report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        )
    
    with col2:
        csv_data = df.to_csv(index=False)
        st.download_button(
            "Download Data (CSV)",
            csv_data,
            f"data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        )

else:
    st.info("👈 Check the sidebar to upload data or use sample data to see the analysis.")
