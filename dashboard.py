
import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.express as px

ROOT = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Restaurant Analytics",
    page_icon="🍽️",
    layout="wide"
)

st.title("Restaurant Sales Forecasting and Customer Preference Analytics")
st.caption("Restaurant demand forecasting, customer preference analysis and menu pricing")

st.warning(
    "The forecasting dataset predicts visitor counts, not sales revenue. "
    "Cuisine counts and listed menu prices do not represent actual purchases."
)

# Project file paths
METRICS_PATH = ROOT / "outputs" / "forecast_metrics.csv"
IMAGE_PATH = ROOT / "outputs" / "forecast_comparison.png"
ZOMATO_PATH = ROOT / "data" / "raw" / "zomato" / "zomato.csv"
MENU_PATH = ROOT / "outputs" / "chennai_restaurant_menu.csv"

# --------------------------------------------------
# 1. FORECASTING ANALYSIS
# --------------------------------------------------
st.header("1. Restaurant Demand Forecasting")

if METRICS_PATH.exists():
    metrics = pd.read_csv(METRICS_PATH)
    st.subheader("Forecast Model Comparison")
    st.dataframe(metrics, use_container_width=True)

    required = {"model", "MAE", "RMSE"}
    if required.issubset(metrics.columns):
        st.subheader("Compare Forecast Errors")
        metric_choice = st.selectbox(
            "Choose evaluation metric",
            ["MAE", "RMSE"] +
            (["sMAPE_percent"] if "sMAPE_percent" in metrics.columns else [])
        )

        chart = px.bar(
            metrics,
            x="model",
            y=metric_choice,
            color="model",
            title=f"Model Comparison — {metric_choice}",
            labels={
                "model": "Forecasting Model",
                metric_choice: metric_choice
            }
        )
        st.plotly_chart(chart, use_container_width=True)
        st.caption("Lower error values indicate better forecasting performance.")
else:
    st.info("Forecast metrics not found. Run: python run_pipeline.py")

if IMAGE_PATH.exists():
    st.subheader("Actual vs Predicted Visitor Counts")
    st.image(
        str(IMAGE_PATH),
        use_container_width=True
    )

# --------------------------------------------------
# 2. RESTAURANT DATASET OVERVIEW
# --------------------------------------------------
st.divider()
st.header("2. Restaurant Dataset Overview")

if ZOMATO_PATH.exists():
    df = pd.read_csv(ZOMATO_PATH, low_memory=False)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Records", f"{len(df):,}")

    if "name" in df.columns:
        col2.metric("Unique Restaurant Names", f"{df['name'].nunique():,}")
    else:
        col2.metric("Dataset Columns", len(df.columns))

    col3.metric("Missing Values", f"{int(df.isna().sum().sum()):,}")

    with st.expander("View dataset preview and missing values"):
        st.dataframe(df.head(20), use_container_width=True)

        missing = df.isna().sum().reset_index()
        missing.columns = ["Column", "Missing Values"]
        missing = missing[missing["Missing Values"] > 0]
        if not missing.empty:
            st.dataframe(missing, use_container_width=True)
        else:
            st.success("No missing values found.")

    # Interactive filters
    st.subheader("Explore Restaurants")
    filtered = df.copy()

    if "location" in filtered.columns:
        locations = sorted(
            filtered["location"].dropna().astype(str).unique().tolist()
        )
        selected_locations = st.multiselect(
            "Filter by location",
            locations
        )
        if selected_locations:
            filtered = filtered[
                filtered["location"].astype(str).isin(selected_locations)
            ]

    if "online_order" in filtered.columns:
        order_options = sorted(
            filtered["online_order"].dropna().astype(str).unique().tolist()
        )
        selected_order = st.selectbox(
            "Online ordering",
            ["All"] + order_options
        )
        if selected_order != "All":
            filtered = filtered[
                filtered["online_order"].astype(str) == selected_order
            ]

    st.write(f"Records matching filters: **{len(filtered):,}**")
    visible_columns = [
        c for c in ["name", "location", "cuisines", "rate",
                    "rest_type", "online_order",
                    "approx_cost(for two people)"]
        if c in filtered.columns
    ]
    if visible_columns:
        st.dataframe(
            filtered[visible_columns].head(100),
            use_container_width=True
        )

    # Cuisine analysis
    if "cuisines" in filtered.columns:
        st.subheader("Popular Cuisines")
        cuisine_data = (
            filtered["cuisines"]
            .dropna()
            .astype(str)
            .str.split(",")
            .explode()
            .str.strip()
        )
        cuisine_data = cuisine_data[cuisine_data != ""]
        top_cuisines = cuisine_data.value_counts().head(10)

        if not top_cuisines.empty:
            cuisine_chart = px.bar(
                x=top_cuisines.index,
                y=top_cuisines.values,
                labels={"x": "Cuisine", "y": "Restaurant Listings"},
                title="Top 10 Cuisine Listings"
            )
            st.plotly_chart(cuisine_chart, use_container_width=True)

    # Rating analysis
    if "rate" in filtered.columns:
        st.subheader("Restaurant Rating Analysis")
        ratings = pd.to_numeric(
            filtered["rate"].astype(str).str.extract(
                r"(\d+(?:\.\d+)?)"
            )[0],
            errors="coerce"
        ).dropna()

        if not ratings.empty:
            r1, r2 = st.columns(2)
            r1.metric("Average Listed Rating", f"{ratings.mean():.2f}")
            r2.metric("Restaurants with Rating", f"{len(ratings):,}")

            rating_chart = px.histogram(
                x=ratings,
                nbins=20,
                labels={"x": "Rating", "y": "Number of Records"},
                title="Distribution of Listed Ratings"
            )
            st.plotly_chart(rating_chart, use_container_width=True)

    # Listed cost analysis
    cost_col = "approx_cost(for two people)"
    if cost_col in filtered.columns:
        st.subheader("Listed Restaurant Cost Analysis")
        costs = pd.to_numeric(
            filtered[cost_col].astype(str).str.replace(",", "", regex=False),
            errors="coerce"
        ).dropna()

        if not costs.empty:
            a, b = st.columns(2)
            a.metric("Median Listed Cost for Two", f"₹{costs.median():,.0f}")
            b.metric("Records with Cost Data", f"{len(costs):,}")

            cost_chart = px.histogram(
                x=costs,
                nbins=30,
                labels={"x": "Listed Cost for Two (₹)", "y": "Records"},
                title="Distribution of Listed Restaurant Costs"
            )
            st.plotly_chart(cost_chart, use_container_width=True)

else:
    st.warning("Zomato dataset not found at data/raw/zomato/zomato.csv")

# --------------------------------------------------
# 3. SCRAPED MENU ANALYSIS
# --------------------------------------------------
st.divider()
st.header("3. Web-Scraped Menu Price Analysis")

if MENU_PATH.exists():
    menu = pd.read_csv(MENU_PATH)

    if "price_inr" in menu.columns:
        menu["price_inr"] = pd.to_numeric(
            menu["price_inr"], errors="coerce"
        )

    if "dish" in menu.columns and "price_inr" in menu.columns:
        menu = menu.dropna(subset=["dish", "price_inr"])

        m1, m2, m3 = st.columns(3)
        m1.metric("Menu Items", f"{len(menu):,}")
        m2.metric("Average Listed Price", f"₹{menu['price_inr'].mean():.2f}")
        m3.metric("Median Listed Price", f"₹{menu['price_inr'].median():.2f}")

        st.subheader("Scraped Menu Records")
        st.dataframe(menu, use_container_width=True)

        menu_chart = px.bar(
            menu.sort_values("price_inr", ascending=False),
            x="dish",
            y="price_inr",
            title="Listed Menu Price by Dish",
            labels={"dish": "Menu Item", "price_inr": "Listed Price (₹)"}
        )
        menu_chart.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(menu_chart, use_container_width=True)

        st.caption(
            "Source: Live Chennai Saravana Bhavan menu page. "
            "Prices should be verified against the original page. "
            "These are listed prices, not actual sales."
        )
else:
    st.info(
        "Scraped menu file not found. Expected location: "
        "outputs/chennai_restaurant_menu.csv"
    )

st.divider()
st.caption(
    "Project note: Cuisine listings represent dataset records, "
    "not verified customer purchases. Forecasting results refer to "
    "visitor counts rather than revenue."
)
