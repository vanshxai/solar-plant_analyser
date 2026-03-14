"""
Sample Data Generator for Solar Plant Analyzer
Generates realistic synthetic solar plant data for demonstration and testing.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional


def generate_solar_data(
    days: int = 7,
    interval_minutes: int = 60,
    plant_capacity_kw: float = 500,
    seed: Optional[int] = 42,
    inject_faults: bool = True
) -> pd.DataFrame:
    """
    Generate realistic synthetic solar plant data.
    
    Args:
        days: Number of days of data to generate
        interval_minutes: Data interval in minutes
        plant_capacity_kw: Rated plant capacity in kW
        seed: Random seed for reproducibility
        inject_faults: Whether to inject realistic faults
        
    Returns:
        DataFrame with synthetic solar data
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Generate timestamps
    start_date = datetime(2026, 3, 1, 6, 0, 0)
    end_date = start_date + timedelta(days=days)
    timestamps = pd.date_range(start=start_date, end=end_date, freq=f'{interval_minutes}min')
    
    n_points = len(timestamps)
    
    # Hour of day for each timestamp
    hours = np.array([t.hour + t.minute/60 for t in timestamps])
    day_of_year = np.array([t.timetuple().tm_yday for t in timestamps])
    
    # Solar irradiance model (bell curve centered at solar noon)
    # Adjusts for seasonal variation
    seasonal_factor = 1 - 0.3 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
    irradiance = 1000 * np.exp(-((hours - 12) ** 2) / 8) * seasonal_factor
    irradiance = np.maximum(irradiance, 0)
    irradiance += np.random.normal(0, 50, n_points)  # Add noise
    irradiance = np.clip(irradiance, 0, 1200)
    
    # Voltage model (relatively stable, varies with temperature and irradiance)
    base_voltage = 580
    voltage_variation = np.random.normal(0, 8, n_points)
    voltage_variation += (irradiance - 500) / 100  # Slight irradiance effect
    voltage = base_voltage + voltage_variation
    voltage = np.clip(voltage, 540, 620)
    
    # Current model (follows irradiance)
    base_current = plant_capacity_kw * 1000 / base_voltage / 10  # Assume 10 strings
    current = (irradiance / 1000) * base_current + np.random.normal(0, 0.3, n_points)
    current = np.maximum(current, 0)
    
    # Power calculation with efficiency losses
    efficiency = 0.95 + np.random.normal(0, 0.02, n_points)
    efficiency = np.clip(efficiency, 0.85, 0.98)
    power = voltage * current * efficiency
    power = np.maximum(power, 0)
    
    # Temperature model (ambient + heating from sun)
    base_temp = 25 + 5 * np.sin(2 * np.pi * (day_of_year - 200) / 365)
    temp_variation = 8 * np.sin((hours - 6) * np.pi / 12)
    temperature = base_temp + np.maximum(temp_variation, 0) + np.random.normal(0, 2, n_points)
    temperature = np.clip(temperature, 10, 55)
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'voltage': voltage,
        'current': current,
        'power': power,
        'temperature': temperature,
        'irradiance': irradiance
    })
    
    # Add string-level data (simulate 4 strings)
    n_strings = 4
    for i in range(n_strings):
        string_current = current / n_strings * (1 + np.random.normal(0, 0.05, n_points))
        string_current = np.maximum(string_current, 0)
        df[f'string_{i+1}_current'] = string_current
    
    # Inject realistic faults
    if inject_faults:
        df = inject_realistic_faults(df, n_strings)
    
    return df


def inject_realistic_faults(df: pd.DataFrame, n_strings: int = 4) -> pd.DataFrame:
    """
    Inject realistic faults into the data for demonstration.
    
    Args:
        df: DataFrame with clean data
        n_strings: Number of strings
        
    Returns:
        DataFrame with injected faults
    """
    df = df.copy()
    n_points = len(df)
    
    # Fault 1: Current mismatch on Day 2 (shading on one string)
    day2_mask = (df['timestamp'].dt.day == 2) & (df['timestamp'].dt.hour >= 10) & (df['timestamp'].dt.hour <= 14)
    if day2_mask.sum() > 0:
        df.loc[day2_mask, 'string_2_current'] *= 0.5
        df.loc[day2_mask, 'current'] *= 0.9
    
    # Fault 2: Sudden power drop on Day 3 (inverter trip)
    day3_idx = df[df['timestamp'].dt.day == 3].index
    if len(day3_idx) > 5:
        trip_idx = day3_idx[5]  # Around midday
        df.loc[trip_idx:trip_idx+2, 'power'] *= 0.3
        df.loc[trip_idx:trip_idx+2, 'current'] *= 0.3
    
    # Fault 3: Gradual degradation simulation (slight decline over days)
    degradation_factor = np.linspace(1.0, 0.95, n_points)
    df['power'] *= degradation_factor
    df['current'] *= degradation_factor
    
    # Fault 4: Temperature anomaly on Day 5 (hot spot)
    day5_mask = (df['timestamp'].dt.day == 5) & (df['timestamp'].dt.hour >= 11) & (df['timestamp'].dt.hour <= 15)
    if day5_mask.sum() > 0:
        df.loc[day5_mask, 'temperature'] += 8
        df.loc[day5_mask, 'power'] *= 0.92  # Reduced efficiency due to heat
    
    # Fault 5: Voltage spike on Day 6 (grid fluctuation)
    day6_idx = df[df['timestamp'].dt.day == 6].index
    if len(day6_idx) > 3:
        spike_idx = day6_idx[3]
        df.loc[spike_idx, 'voltage'] += 40
    
    # Fault 6: Low performance ratio on Day 7 (soiling)
    day7_mask = df['timestamp'].dt.day == 7
    if day7_mask.sum() > 0:
        df.loc[day7_mask, 'power'] *= 0.8
        df.loc[day7_mask, 'current'] *= 0.8
    
    return df


def generate_multi_string_data(
    days: int = 7,
    interval_minutes: int = 30,
    seed: Optional[int] = 42
) -> pd.DataFrame:
    """
    Generate data with explicit string-level information.
    
    Args:
        days: Number of days of data
        interval_minutes: Data interval in minutes
        seed: Random seed
        
    Returns:
        DataFrame with string-level data
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Generate base data
    df = generate_solar_data(days, interval_minutes, seed=seed, inject_faults=False)
    
    # Expand to long format with string_id
    n_strings = 4
    expanded_data = []
    
    for _, row in df.iterrows():
        for string_id in range(1, n_strings + 1):
            string_row = {
                'timestamp': row['timestamp'],
                'voltage': row['voltage'] + np.random.normal(0, 5),
                'current': row[f'string_{string_id}_current'],
                'power': row['voltage'] * row[f'string_{string_id}_current'],
                'temperature': row['temperature'],
                'string_id': f'String_{string_id}'
            }
            expanded_data.append(string_row)
    
    expanded_df = pd.DataFrame(expanded_data)
    
    # Inject string-specific faults
    # String 2 has consistent underperformance
    string2_mask = expanded_df['string_id'] == 'String_2'
    expanded_df.loc[string2_mask, 'current'] *= 0.75
    expanded_df.loc[string2_mask, 'power'] *= 0.75
    
    return expanded_df


def save_sample_data(
    filepath: str = 'sample_data/solar_sample.csv',
    days: int = 7,
    inject_faults: bool = True
):
    """
    Generate and save sample data to a CSV file.
    
    Args:
        filepath: Output file path
        days: Number of days of data
        inject_faults: Whether to include faults
    """
    df = generate_solar_data(days=days, inject_faults=inject_faults)
    
    # Format timestamp for better readability
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    df.to_csv(filepath, index=False)
    print(f"Sample data saved to: {filepath}")
    print(f"Total rows: {len(df)}")
    print(f"Date range: {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")
    
    return df


if __name__ == "__main__":
    # Generate and save sample data
    save_sample_data(
        filepath='sample_data/solar_sample.csv',
        days=7,
        inject_faults=True
    )
    
    # Also generate a clean dataset for comparison
    save_sample_data(
        filepath='sample_data/solar_clean.csv',
        days=3,
        inject_faults=False
    )
    
    # Generate multi-string dataset
    multi_string_df = generate_multi_string_data(days=5, interval_minutes=60)
    multi_string_df['timestamp'] = multi_string_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    multi_string_df.to_csv('sample_data/solar_multistring.csv', index=False)
    print(f"\nMulti-string data saved to: sample_data/solar_multistring.csv")
    print(f"Total rows: {len(multi_string_df)}")
