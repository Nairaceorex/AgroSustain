import pandas as pd

def calculate_indicators(df):
    """Calculate sustainability indicators."""
    indicators = {
        'farm_id': df['farm_id'],
        'biodiversity_index': df['species_count'] / df['area_ha'],  # Biodiversity index
        'soil_quality': df['organic_matter'] * 0.5 + df['ph_level'] * 0.3 + df['soil_structure'] * 0.2,  # Soil quality
        'water_usage': df['water_consumption'] / df['yield_tons'],  # Water consumption per yield
        'ghg_emissions': df['co2_emissions'] / df['yield_tons'],  # GHG emissions per yield
        'profitability': (df['revenue'] - df['costs']) / df['costs'] * 100,  # Profitability (%)
        'labor_productivity': df['yield_tons'] / df['labor_hours'],  # Labor productivity
        'social_welfare': df['income_per_capita'] / df['regional_average_income']  # Social welfare
    }
    return pd.DataFrame(indicators)