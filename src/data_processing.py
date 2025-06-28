import pandas as pd
import numpy as np

def load_data(file_path):
    """Load data from a CSV file."""
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        raise Exception(f"Error loading data: {e}")

def clean_data(df):
    """Clean data: handle missing values and normalize."""
    # Fill missing values with column means
    df = df.fillna(df.mean(numeric_only=True))
    # Normalize numerical columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = (df[numeric_cols] - df[numeric_cols].mean()) / df[numeric_cols].std()
    return df

def save_data(df, output_path):
    """Save processed data to CSV."""
    df.to_csv(output_path, index=False)