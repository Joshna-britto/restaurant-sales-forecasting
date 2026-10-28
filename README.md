# Restaurant Sales Forecasting and Customer Preference Analytics System

## Overview
A Python-based data science project combining restaurant visitor forecasting, restaurant metadata analysis, menu web scraping, and a Streamlit dashboard.

## Technologies
- Python
- Pandas and NumPy
- Scikit-learn
- Streamlit
- Matplotlib and Plotly
- Web scraping

## Forecasting Models
1. Seasonal Naive baseline using lag 7
2. Random Forest Regression

## Evaluation
The models are compared using MAE, RMSE, and sMAPE. In the evaluated test period, the Seasonal Naive baseline performed better than Random Forest.

## Run the Project
Install the required packages from requirements.txt, place the required datasets in data/raw/, and run:

    python run_pipeline.py

To launch the dashboard:

    streamlit run dashboard.py

## Note
The forecasting target is visitor counts, not sales revenue. Restaurant metadata and scraped menu prices are analysed separately.
