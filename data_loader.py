"""
Data Loader Module for Solar Plant Analyzer
Handles loading and validation of solar plant data from CSV/Excel files.
"""

import pandas as pd
from typing import Optional, Tuple, Dict, Any
import os


class DataLoader:
    """Loads and validates solar plant data files."""
    
    REQUIRED_COLUMNS = ['timestamp', 'voltage', 'current', 'power']
    OPTIONAL_COLUMNS = ['temperature', 'irradiance', 'string_id', 'inverter_id']
    
    def __init__(self):
        self.validation_errors = []
        self.validation_warnings = []
    
    def load_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        Load data from CSV or Excel file.
        
        Args:
            file_path: Path to the data file
            
        Returns:
            DataFrame with loaded data, or None if loading fails
        """
        self.validation_errors = []
        self.validation_warnings = []
        
        if not os.path.exists(file_path):
            self.validation_errors.append(f"File not found: {file_path}")
            return None
        
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                self.validation_errors.append("Unsupported file format. Use CSV or Excel.")
                return None
            
            return df
            
        except Exception as e:
            self.validation_errors.append(f"Error loading file: {str(e)}")
            return None
    
    def load_from_bytes(self, file_bytes: bytes, file_name: str) -> Optional[pd.DataFrame]:
        """
        Load data from uploaded file bytes (for Streamlit).
        
        Args:
            file_bytes: Raw file bytes
            file_name: Name of the file (to determine format)
            
        Returns:
            DataFrame with loaded data, or None if loading fails
        """
        self.validation_errors = []
        self.validation_warnings = []
        
        try:
            if file_name.endswith('.csv'):
                df = pd.read_csv(pd.io.common.BytesIO(file_bytes))
            elif file_name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(pd.io.common.BytesIO(file_bytes))
            else:
                self.validation_errors.append("Unsupported file format. Use CSV or Excel.")
                return None
            
            return df
            
        except Exception as e:
            self.validation_errors.append(f"Error loading file: {str(e)}")
            return None
    
    def validate(self, df: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate the loaded data.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple of (is_valid, validation_report)
        """
        report = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'missing_columns': [],
            'missing_values': {},
            'duplicate_rows': 0,
            'invalid_timestamps': 0
        }
        
        # Check required columns
        for col in self.REQUIRED_COLUMNS:
            if col not in df.columns:
                report['missing_columns'].append(col)
                report['errors'].append(f"Missing required column: {col}")
        
        if report['missing_columns']:
            report['is_valid'] = False
            return True, report
        
        # Check for missing values
        for col in self.REQUIRED_COLUMNS:
            missing_count = df[col].isna().sum()
            if missing_count > 0:
                report['missing_values'][col] = missing_count
                report['warnings'].append(f"Column '{col}' has {missing_count} missing values")
        
        # Check for duplicate rows
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            report['duplicate_rows'] = duplicates
            report['warnings'].append(f"Found {duplicates} duplicate rows")
        
        # Validate and parse timestamps
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        invalid_timestamps = df['timestamp'].isna().sum()
        if invalid_timestamps > 0:
            report['invalid_timestamps'] = invalid_timestamps
            report['errors'].append(f"Found {invalid_timestamps} invalid timestamps")
            report['is_valid'] = False
        
        # Check for negative values in electrical parameters
        for col in ['voltage', 'current', 'power']:
            if col in df.columns:
                negative_count = (df[col] < 0).sum()
                if negative_count > 0:
                    report['warnings'].append(f"Column '{col}' has {negative_count} negative values")
        
        # Check data range
        if 'voltage' in df.columns:
            if df['voltage'].max() > 1500:
                report['warnings'].append("Voltage values exceed 1500V - verify data accuracy")
        
        if report['errors']:
            report['is_valid'] = False
        
        return report['is_valid'], report
    
    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and preprocess the data.
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Preprocessed DataFrame
        """
        df = df.copy()
        
        # Parse timestamps
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        # Remove rows with invalid timestamps
        df = df.dropna(subset=['timestamp'])
        
        # Remove duplicate rows
        df = df.drop_duplicates()
        
        # Fill missing numerical values with forward fill then backward fill
        numerical_cols = ['voltage', 'current', 'power', 'temperature', 'irradiance']
        for col in numerical_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].ffill().bfill()
        
        # Calculate derived parameters
        if 'voltage' in df.columns and 'current' in df.columns:
            df['calculated_power'] = df['voltage'] * df['current']
        
        # Sort by timestamp
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        return df
    
    def load_and_process(self, file_path: str) -> Tuple[Optional[pd.DataFrame], Dict[str, Any]]:
        """
        Complete load, validate, and preprocess pipeline.
        
        Args:
            file_path: Path to the data file
            
        Returns:
            Tuple of (processed DataFrame, processing report)
        """
        df = self.load_file(file_path)
        
        if df is None:
            return None, {
                'success': False,
                'errors': self.validation_errors,
                'warnings': self.validation_warnings
            }
        
        is_valid, validation_report = self.validate(df)
        
        if not is_valid:
            return None, {
                'success': False,
                'errors': validation_report['errors'],
                'warnings': validation_report['warnings']
            }
        
        processed_df = self.preprocess(df)
        
        return processed_df, {
            'success': True,
            'errors': validation_report['errors'],
            'warnings': validation_report['warnings'],
            'row_count': len(processed_df),
            'column_count': len(processed_df.columns),
            'date_range': {
                'start': str(processed_df['timestamp'].min()),
                'end': str(processed_df['timestamp'].max())
            }
        }


def load_data(file_path: str) -> Tuple[Optional[pd.DataFrame], Dict[str, Any]]:
    """
    Convenience function to load and process solar data.
    
    Args:
        file_path: Path to the data file
        
    Returns:
        Tuple of (processed DataFrame, processing report)
    """
    loader = DataLoader()
    return loader.load_and_process(file_path)
