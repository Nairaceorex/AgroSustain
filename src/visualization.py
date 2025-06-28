import plotly.express as px
import folium
import geopandas as gpd


def plot_indicators(indicators_df):
    """Visualize sustainability indicators as a bar chart."""
    # Melt the dataframe for easier plotting
    plot_data = indicators_df.melt(id_vars=['farm_id'], var_name='Indicator', value_name='Value')
    fig = px.bar(plot_data, x='Indicator', y='Value', color='farm_id', barmode='group',
                 title="Sustainability Indicators by Farm")
    fig.update_xaxes(title="Indicators")
    fig.update_yaxes(title="Normalized Values")
    return fig


def create_map(spatial_data_path, indicators_df):
    """Create a map with sustainability index."""
    try:
        gdf = gpd.read_file(spatial_data_path)
        gdf = gdf.merge(indicators_df, on='farm_id')

        # Center map on the region (adjust coordinates as needed)
        m = folium.Map(location=[55.75, 37.62], zoom_start=10)
        folium.Choropleth(
            geo_data=gdf,
            name='choropleth',
            data=gdf,
            columns=['farm_id', 'sustainability_index'],
            key_on='feature.properties.farm_id',
            fill_color='YlGn',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='Sustainability Index'
        ).add_to(m)
        return m
    except Exception as e:
        print(f"Error creating map: {e}")
        return None