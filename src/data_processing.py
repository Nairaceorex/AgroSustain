import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_data(file_path):
    """Load data from a CSV file."""
    try:
        logger.info(f"Loading data from {file_path}")
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise Exception(f"Error loading data: {e}")


def clean_data(df):
    """Clean data: handle missing values and normalize."""
    logger.info(f"Cleaning data with shape {df.shape}")
    df_clean = df.copy()

    # Ensure farm_id is integer
    if 'farm_id' in df_clean.columns:
        df_clean['farm_id'] = df_clean['farm_id'].astype(int)

    # Log column statistics before cleaning
    logger.info(f"Column means before cleaning:\n{df_clean.mean(numeric_only=True)}")
    logger.info(f"Column std before cleaning:\n{df_clean.std(numeric_only=True)}")

    # Check for NaN values and impute with mean
    if df_clean.isna().any().any():
        logger.warning(f"NaN values found before cleaning:\n{df_clean.isna().sum()}")
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].mean())
        logger.info("Imputed NaN values with column means")

    # Normalize numeric columns (exclude farm_id)
    numeric_cols = [col for col in df_clean.select_dtypes(include=[np.number]).columns if col != 'farm_id']
    for col in numeric_cols:
        if df_clean[col].std() != 0:
            df_clean[col] = (df_clean[col] - df_clean[col].mean()) / df_clean[col].std()
        else:
            logger.warning(f"Standard deviation of {col} is zero, setting to zero to avoid NaN")
            df_clean[col] = 0  # Set to 0 if std is zero to avoid NaN

    logger.info(f"NaN counts after cleaning:\n{df_clean.isna().sum()}")
    return df_clean