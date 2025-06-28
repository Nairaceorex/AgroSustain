from flask import Flask, render_template, request
import pandas as pd
import os
from src.data_processing import load_data, clean_data
from src.indicators import calculate_indicators
from src.modeling import calculate_integral_index, recommend_improvements
from src.visualization import plot_indicators, create_map

app = Flask(__name__)
UPLOAD_FOLDER = 'data/uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file uploaded", 400
    file = request.files['file']
    if file.filename == '':
        return "No file selected", 400

    # Save uploaded file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    try:
        # Process data
        df = load_data(file_path)
        df_clean = clean_data(df)
        indicators_df = calculate_indicators(df_clean)
        integral_index = calculate_integral_index(indicators_df)
        recommendations = recommend_improvements(indicators_df)

        # Generate visualizations
        plot = plot_indicators(indicators_df)
        map_html = create_map('data/spatial_data/farms.shp', integral_index)

        return render_template('results.html',
                               plot=plot.to_html(full_html=False),
                               map=map_html._repr_html_() if map_html else "Map unavailable",
                               recommendations=recommendations)
    except Exception as e:
        return f"Error processing file: {e}", 500


if __name__ == '__main__':
    app.run(debug=True)