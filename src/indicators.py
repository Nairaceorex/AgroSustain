import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def calculate_indicators(df):
    """Calculate sustainability indicators."""
    logger.info("Calculating sustainability indicators")

    # Initialize indicators DataFrame
    indicators = {
        'farm_id': df['farm_id'].astype(int)
    }

    # Calculate indicators with checks for division by zero
    # Biodiversity index
    indicators['biodiversity_index'] = np.where(
        df['area_ha'] != 0,
        df['species_count'] / df['area_ha'],
        0
    )

    # Soil quality
    indicators['soil_quality'] = (
            df['organic_matter'] * 0.5 +
            df['ph_level'] * 0.3 +
            df['soil_structure'] * 0.2
    )

    # Water usage
    indicators['water_usage'] = np.where(
        df['yield_tons'] != 0,
        df['water_consumption'] / df['yield_tons'],
        0
    )

    # GHG emissions
    indicators['ghg_emissions'] = np.where(
        df['yield_tons'] != 0,
        df['co2_emissions'] / df['yield_tons'],
        0
    )

    # Profitability
    indicators['profitability'] = np.where(
        df['costs'] != 0,
        (df['revenue'] - df['costs']) / df['costs'] * 100,
        0
    )

    # Labor productivity
    indicators['labor_productivity'] = np.where(
        df['labor_hours'] != 0,
        df['yield_tons'] / df['labor_hours'],
        0
    )

    # Social welfare
    indicators['social_welfare'] = np.where(
        df['regional_average_income'] != 0,
        df['income_per_capita'] / df['regional_average_income'],
        0
    )

    indicators_df = pd.DataFrame(indicators)

    # Replace inf/-inf with 0
    indicators_df = indicators_df.replace([np.inf, -np.inf], 0)

    # Log any remaining issues
    if indicators_df.isna().any().any():
        logger.warning(f"NaN values in indicators:\n{indicators_df.isna().sum()}")
    if np.isinf(indicators_df.select_dtypes(include=[np.number])).any().any():
        logger.warning("Infinite values found in indicators, replaced with 0")

    logger.info(f"Indicators columns: {indicators_df.columns.tolist()}")
    return indicators_df