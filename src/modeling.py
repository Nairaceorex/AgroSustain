from sklearn.decomposition import PCA
import pandas as pd


def calculate_integral_index(indicators_df):
    """Calculate integral sustainability index using PCA."""
    # Select numerical columns for PCA
    numeric_cols = indicators_df.select_dtypes(include=['float64', 'int64']).columns
    if len(numeric_cols) == 0:
        raise ValueError("No numerical columns for PCA")

    pca = PCA(n_components=1)
    integral_index = pca.fit_transform(indicators_df[numeric_cols])
    return pd.DataFrame({
        'farm_id': indicators_df['farm_id'],
        'sustainability_index': integral_index.flatten()
    })


def recommend_improvements(indicators_df):
    """Generate recommendations based on indicators."""
    recommendations = []
    if indicators_df['biodiversity_index'].mean() < 0.5:
        recommendations.append("Increase crop rotation diversity and use local species.")
    if indicators_df['water_usage'].mean() > 1.0:
        recommendations.append("Implement drip irrigation to optimize water usage.")
    if indicators_df['profitability'].mean() < 10:
        recommendations.append("Optimize costs and adopt precision agriculture.")
    if indicators_df['ghg_emissions'].mean() > 100:
        recommendations.append("Reduce fertilizer use and adopt renewable energy.")
    return recommendations