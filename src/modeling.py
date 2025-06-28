import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def calculate_integral_index(indicators_df):
    """Calculate integral sustainability index using PCA."""
    logger.info("Calculating integral sustainability index")
    try:
        # Select numerical columns for PCA (exclude farm_id)
        numeric_cols = [col for col in indicators_df.columns if col != 'farm_id']
        if not numeric_cols:
            logger.error("No numerical columns for PCA")
            raise ValueError("No numerical columns for PCA")

        X = indicators_df[numeric_cols]

        # Check for NaN values
        if X.isna().any().any():
            logger.error(f"NaN values found in indicators data:\n{X.isna().sum()}")
            raise ValueError("Input contains NaN values, which PCA cannot handle")

        # Check for infinite values
        if np.isinf(X).any().any():
            logger.error(f"Infinite values found in indicators data:\n{np.isinf(X).sum()}")
            raise ValueError("Input contains infinite values, which PCA cannot handle")

        # Apply PCA
        pca = PCA(n_components=1)
        integral_index = pca.fit_transform(X)

        # Return DataFrame with farm_id and integral_index
        result_df = pd.DataFrame({
            'farm_id': indicators_df['farm_id'],
            'integral_index': integral_index.flatten()
        })
        return result_df

    except Exception as e:
        logger.error(f"Error in calculate_integral_index: {e}")
        raise


def recommend_improvements(indicators_df):
    """Generate recommendations based on indicators."""
    logger.info("Generating recommendations")
    recommendations = []
    if 'biodiversity_index' in indicators_df.columns and indicators_df['biodiversity_index'].mean() < 0.5:
        recommendations.append("Increase crop rotation diversity and use local species.")
    if 'water_usage' in indicators_df.columns and indicators_df['water_usage'].mean() > 1.0:
        recommendations.append("Implement drip irrigation to optimize water usage.")
    if 'profitability' in indicators_df.columns and indicators_df['profitability'].mean() < 10:
        recommendations.append("Optimize costs and adopt precision agriculture.")
    if 'ghg_emissions' in indicators_df.columns and indicators_df['ghg_emissions'].mean() > 100:
        recommendations.append("Reduce fertilizer use and adopt renewable energy.")
    return recommendations