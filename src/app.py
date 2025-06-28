from flask import Flask, render_template, request
import pandas as pd
import os
import logging
from src.data_processing import load_data, clean_data
from src.indicators import calculate_indicators
from src.modeling import calculate_integral_index, recommend_improvements
from src.visualization import plot_indicators, create_map

from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

Base = declarative_base()


class FarmData(Base):
    __tablename__ = 'farm_data'
    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer)
    sustainability_index = Column(Float)
    recommendations = Column(String)


engine = create_engine('sqlite:///database/agrosustain.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

app = Flask(__name__)
UPLOAD_FOLDER = 'data/uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload, process data, calculate sustainability indicators,
    perform integral assessment, generate visualizations, and save results to database.
    Returns results.html with visualizations and recommendations or error message.
    """
    # Check if a file is provided
    if 'file' not in request.files:
        logger.error("No file uploaded in request")
        return render_template('results.html', error="Файл не загружен"), 400

    file = request.files['file']

    # Check if a file was selected
    if file.filename == '':
        logger.error("No file selected")
        return render_template('results.html', error="Файл не выбран"), 400

    # Validate file extension
    if not file.filename.endswith('.csv'):
        logger.error(f"Invalid file type: {file.filename}")
        return render_template('results.html', error="Поддерживаются только CSV файлы"), 400

    try:
        # Save uploaded file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        logger.info(f"File saved: {file_path}")

        # Load and process data
        df = load_data(file_path)
        logger.info("Data loaded successfully")

        # Validate required columns
        required_columns = [
            'farm_id', 'species_count', 'area_ha', 'organic_matter', 'ph_level',
            'soil_structure', 'water_consumption', 'yield_tons', 'co2_emissions',
            'revenue', 'costs', 'labor_hours', 'income_per_capita', 'regional_average_income'
        ]
        if not all(col in df.columns for col in required_columns):
            logger.error("Missing required columns in CSV")
            return render_template('results.html', error="В CSV файле отсутствуют обязательные столбцы"), 400

        # Clean data
        df_clean = clean_data(df)
        logger.info("Data cleaned successfully")

        # Calculate sustainability indicators
        indicators_df = calculate_indicators(df_clean)
        logger.info("Indicators calculated")

        # Calculate integral sustainability index
        integral_index = calculate_integral_index(indicators_df)
        logger.info("Integral index calculated")

        # Generate recommendations (translated to Russian)
        recommendations = recommend_improvements(indicators_df)
        translated_recommendations = [
            "Увеличить разнообразие севооборотов и использовать местные сорта" if "crop rotation" in rec
            else "Внедрить капельное орошение для оптимизации водопользования" if "drip irrigation" in rec
            else "Оптимизировать затраты и внедрить точное земледелие" if "precision agriculture" in rec
            else "Сократить использование удобрений и внедрить возобновляемые источники энергии" if "renewable energy" in rec
            else rec
            for rec in recommendations
        ]
        logger.info("Recommendations generated")

        # Generate visualizations
        plot = plot_indicators(indicators_df)
        map_html = create_map('data/spatial_data/farms.shp', integral_index)
        map_output = map_html._repr_html_() if map_html else "Карта недоступна из-за отсутствия или некорректных пространственных данных"
        logger.info("Visualizations generated")

        # Save results to database
        session = Session()
        try:
            for index, row in integral_index.iterrows():
                farm_entry = FarmData(
                    farm_id=int(row['farm_id']),
                    sustainability_index=float(row['sustainability_index']),
                    recommendations="; ".join(translated_recommendations)
                )
                session.add(farm_entry)
            session.commit()
            logger.info("Results saved to database")
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
        finally:
            session.close()

        # Render results page
        return render_template(
            'results.html',
            plot=plot.to_html(full_html=False),
            map=map_output,
            recommendations=translated_recommendations,
            error=None
        )

    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return render_template('results.html', error=f"Ошибка обработки файла: {str(e)}"), 500


if __name__ == '__main__':
    app.run(debug=True)
