import folium
import pandas as pd
import geopandas as gpd
import logging
from branca.colormap import LinearColormap

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def plot_indicators(indicators_df):
    """Visualize sustainability indicators as a bar chart."""
    import plotly.express as px
    plot_data = indicators_df.melt(id_vars=['farm_id'], var_name='Indicator', value_name='Value')
    fig = px.bar(plot_data, x='Indicator', y='Value', color='farm_id', barmode='group',
                 title="Индикаторы устойчивости по хозяйствам")
    fig.update_xaxes(title="Индикаторы")
    fig.update_yaxes(title="Нормализованные значения")
    return fig

def create_map(indicators_df, spatial_data_path='data/spatial_data/farms.shp'):
    """
    Create a choropleth map with sustainability index.
    """
    try:
        gdf = gpd.read_file(spatial_data_path)
        logger.info(f"Shapefile loaded: {spatial_data_path}")

        if 'farm_id' not in gdf.columns:
            logger.error("Shapefile missing 'farm_id' column")
            return None
        gdf['farm_id'] = gdf['farm_id'].astype(int)

        if 'farm_id' not in indicators_df.columns:
            logger.error("Indicators missing 'farm_id' column")
            return None
        indicators_df['farm_id'] = indicators_df['farm_id'].astype(int)

        if 'integral_index' not in indicators_df.columns:
            logger.error(f"Indicators missing 'integral_index' column. Available columns: {indicators_df.columns.tolist()}")
            return None

        gdf = gdf.merge(indicators_df[['farm_id', 'integral_index']], on='farm_id', how='left')
        if gdf['integral_index'].isna().all():
            logger.error("No matching farm_id found in indicators data")
            logger.debug(f"Merged DataFrame sample:\n{gdf[['farm_id', 'integral_index']].head().to_string()}")
            return None

        # Center map on shapefile centroid
        centroid = gdf.geometry.centroid
        center = [centroid.y.mean(), centroid.x.mean()]
        m = folium.Map(location=center, zoom_start=10)

        # Create colormap
        colormap = LinearColormap(colors=['red', 'yellow', 'green'],
                                 vmin=gdf['integral_index'].min(),
                                 vmax=gdf['integral_index'].max())

        # Add choropleth layer
        folium.Choropleth(
            geo_data=gdf,
            name='choropleth',
            data=gdf,
            columns=['farm_id', 'integral_index'],
            key_on='feature.properties.farm_id',
            fill_color='YlGn',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='Индекс устойчивости'
        ).add_to(m)

        # Add tooltip
        folium.GeoJson(
            gdf,
            style_function=lambda feature: {
                'fillColor': colormap(feature['properties']['integral_index'])
                             if not pd.isna(feature['properties']['integral_index']) else 'gray',
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.7,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['farm_id', 'integral_index'],
                aliases=['Farm ID', 'Sustainability Index'],
                localize=True
            )
        ).add_to(m)

        folium.LayerControl().add_to(m)
        logger.info("Map created successfully")
        return m
    except Exception as e:
        logger.error(f"Error creating map: {str(e)}")
        return None