# ☀️ Solar Plant Analyzer

A comprehensive Python tool for solar plant performance analysis and fault detection. Upload plant data (CSV/Excel) and automatically detect performance anomalies, then view an interactive dashboard and generate reports.

## Features

- **Data Loading**: Support for CSV and Excel files from inverters/monitoring systems
- **Performance Analysis**: Calculate efficiency metrics, performance ratios, and degradation trends
- **Fault Detection**: Automatic detection of:
  - Current mismatch (shading, damaged panels)
  - Sudden power drops (inverter trips, grid issues)
  - Voltage anomalies
  - Temperature-related efficiency loss
  - Long-term degradation
  - Low performance ratio
- **Interactive Dashboard**: Streamlit-based visualization with Plotly graphs
- **Report Generation**: Export fault reports in Text, CSV, JSON, or PDF format

## Installation

### Using existing virtual environment

```bash
cd solar_analyzer
source ../.venv/bin/activate  # or use your preferred virtual environment
pip install -r requirements.txt
```

### Or create a new virtual environment

```bash
cd solar_analyzer
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Running the Dashboard

```bash
streamlit run main.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Using Sample Data

1. Launch the dashboard
2. Check "Use sample data for demo" in the sidebar
3. View the analysis with pre-injected faults

### Using Your Own Data

1. Export data from your inverter/monitoring system as CSV or Excel
2. Ensure required columns: `timestamp`, `voltage`, `current`, `power`
3. Optional columns: `temperature`, `irradiance`, `string_id`, `inverter_id`
4. Upload the file in the dashboard

### Expected Data Format

```csv
timestamp,voltage,current,power,temperature
2026-03-14 09:00:00,580,8.2,4756,35
2026-03-14 10:00:00,590,8.5,5015,36
2026-03-14 11:00:00,590,8.3,4897,37
```

## Generating Sample Data

```bash
python sample_data_generator.py
```

This creates sample datasets in the `sample_data/` folder:
- `solar_sample.csv` - 7 days of data with injected faults
- `solar_clean.csv` - 3 days of clean data
- `solar_multistring.csv` - String-level data

## Project Structure

```
solar_analyzer/
├── main.py                 # Streamlit dashboard application
├── data_loader.py          # Data loading and validation
├── analysis_engine.py      # Performance calculations
├── fault_detector.py       # Fault detection algorithms
├── visualization.py        # Plotly visualizations
├── report_generator.py     # Report generation (PDF, CSV, etc.)
├── sample_data_generator.py # Synthetic data generator
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── sample_data/
    ├── solar_sample.csv
    ├── solar_clean.csv
    └── solar_multistring.csv
```

## Module Overview

### Data Loader (`data_loader.py`)
- Loads CSV/Excel files
- Validates required columns
- Handles missing values and duplicates
- Parses timestamps

### Analysis Engine (`analysis_engine.py`)
- Power verification (P = V × I)
- Performance ratio calculation
- Efficiency metrics
- String-level analysis
- Degradation trend analysis
- Temperature efficiency analysis

### Fault Detector (`fault_detector.py`)
- Current mismatch detection
- Sudden power drop detection
- Voltage anomaly detection
- Degradation detection
- Temperature anomaly detection
- Performance ratio monitoring

### Visualization (`visualization.py`)
- Power time series
- Voltage & current plots
- Performance ratio trends
- Fault markers on graphs
- Temperature efficiency scatter
- Summary dashboard

### Report Generator (`report_generator.py`)
- Text reports
- CSV exports
- JSON reports
- PDF reports (requires reportlab)

## Configuration

Adjust detection thresholds in the sidebar:
- **Current Mismatch Threshold**: Flag current below X% of average (default: 70%)
- **Power Drop Threshold**: Flag power drops exceeding X% (default: 40%)
- **Low Performance Ratio**: Flag PR below X% (default: 75%)

## Fault Severity Levels

- 🔴 **Critical**: Immediate action required
- 🟠 **High**: Address within 24 hours
- 🟡 **Medium**: Plan maintenance within the week
- 🔵 **Low**: Monitor and address during next scheduled maintenance

## Building an Executable (Optional)

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller --onefile --add-data "main.py:." --name "SolarAnalyzer" main.py
```

Note: Streamlit apps are best run as web applications. For distribution, consider:
- Sharing the source code
- Creating a Docker container
- Deploying to Streamlit Cloud

## Troubleshooting

### No data showing after upload
- Check that your file has the required columns: `timestamp`, `voltage`, `current`, `power`
- Ensure timestamps are in a parseable format
- Check for error messages in the sidebar

### PDF export not working
- Install reportlab: `pip install reportlab`
- If reportlab is not available, text reports will be generated instead

### Graphs not displaying
- Ensure plotly is installed: `pip install plotly`
- Try refreshing the browser page

## License

MIT License - Feel free to use and modify for your solar analysis needs.

## Contributing

Contributions welcome! Areas for improvement:
- Additional fault detection algorithms
- Machine learning-based anomaly detection
- Support for more data formats
- Integration with real-time data sources
- Multi-language support
