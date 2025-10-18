import streamlit as st
import pandas as pd
import altair as alt
from PIL import Image

# --- CONFIGURATION ---
st.set_page_config(
    page_title="BMW Sales Dashboard",
    page_icon="🚗",
    layout="wide"
)
st.markdown("### Created by:S.Sathiya priya")
st.markdown("#### My Streamlit Dashboard about BMW Car Sales Dataset ")
# --- DATA LOADING & CLEANING (Executed once) ---
@st.cache_data
def load_data():
    """Loads and cleans the BMW sales data."""
    try:
        df = pd.read_csv(r"C:\Users\LOKESHRAJ\Desktop\Streamlit_app\bmw.csv")
    except FileNotFoundError:
        st.error("Error: 'bmw.csv' not found. Please ensure the file is in the same directory.")
        return pd.DataFrame()

    # Standardize column names (as done in the analysis)
    df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('/', '')

    # Basic type conversion check (through already clean, good practice)
    numeric_cols = ['year', 'engine_size_l', 'mileage_km', 'price_usd', 'sales_volume']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df.dropna(subset=numeric_cols)

df = load_data()

# Check if data loaded successfully
if df.empty:
    st.stop()


# --- MULTI-PAGE STRUCTURE ---

def home_page():
    """Defines the content for the Home/Overview page."""
    st.title("🚗 BMW Sales Dashboard Overview")
    st.markdown("### A snapshot of key performance indicators (KPIs) and overall sales data.")

    # 1. KPI ANALYSIS
    avg_price = df['price_usd'].mean()
    total_sales = df['sales_volume'].sum()
    avg_mileage = df['mileage_km'].mean()

    # Display KPIs using st.columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="Average Selling Price", value=f"${avg_price:,.2f}")
    with col2:
        st.metric(label="Total Sales Volume", value=f"{total_sales:,.0f} units")
    with col3:
        st.metric(label="Average Mileage", value=f"{avg_mileage:,.0f} KM")

    st.markdown("---")

    # 2. INTERACTIVE WIDGET & CHART: Sales Volume Trend
    st.subheader("Sales Volume Trend Over Time")
    
    # Widget: Sales Classification Filter
    sales_class = df['sales_classification'].unique()
    selected_class = st.multiselect(
        "Filter by Sales Classification",
        options=sales_class,
        default=['High', 'Low']
    )
    
    # Filter data
    df_filtered = df[df['sales_classification'].isin(selected_class)]

    # Aggregate sales volume by year
    sales_by_year = df_filtered.groupby('year')['sales_volume'].sum().reset_index()

    # Create Altair chart
    chart = alt.Chart(sales_by_year).mark_line(point=True).encode(
        x=alt.X('year:O', title='Year'), # 'O' for Ordinal/Categorical
        y=alt.Y('sales_volume', title='Total Sales Volume'),
        tooltip=['year', alt.Tooltip('sales_volume', format=',.0f')]
    ).properties(
        title="Total Sales Volume by Year"
    ).interactive() # Allows zooming/panning

    st.altair_chart(chart, use_container_width=True)

    st.markdown("---")

    # 3. Raw Data Snippet
    st.subheader("Raw Data Sample")
    st.dataframe(df.sample(10), use_container_width=True)


def detailed_analysis_page():
    """Defines the content for the Detailed Analysis page."""
    st.title("🔬 Detailed Market Analysis")
    st.markdown("#### Explore price and sales distribution across various dimensions.")

    # Streamlit WIDGET: Sidebar Filter (Year Range)
    st.sidebar.header("Chart Filters")
    min_year, max_year = int(df['year'].min()), int(df['year'].max())
    year_range = st.sidebar.slider(
        "Select Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )
    
    df_charts = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
    
    st.info(f"Showing data for years {year_range[0]} to {year_range[1]}.")
    
    col_a, col_b = st.columns(2)
# Chart A: Sales by Region (Bar Chart)
    with col_a:
        st.subheader("Sales Volume by Region")
        sales_by_region = df_charts.groupby('region')['sales_volume'].sum().reset_index()
        sales_by_region = sales_by_region.sort_values('sales_volume', ascending=False)
        
        chart_region = alt.Chart(sales_by_region).mark_bar().encode(
            x=alt.X('region:N', sort='-y', title='Region'),
            y=alt.Y('sales_volume', title='Total Sales Volume'),
            color='region',
            tooltip=['region', alt.Tooltip('sales_volume', format=',.0f')]
        ).properties(
            height=400
        )
        st.altair_chart(chart_region, use_container_width=True)

    # Chart B: Average Price by Fuel Type (Bar Chart)
    with col_b:
        st.subheader("Average Price by Fuel Type")
        price_by_fuel = df_charts.groupby('fuel_type')['price_usd'].mean().reset_index()
        price_by_fuel = price_by_fuel.sort_values('price_usd', ascending=False)
        
        chart_fuel = alt.Chart(price_by_fuel).mark_bar().encode(
            x=alt.X('price_usd', title='Average Price (USD)'),
            y=alt.Y('fuel_type:N', sort='-x', title='Fuel Type'),
            color='fuel_type',
            tooltip=['fuel_type', alt.Tooltip('price_usd', format='$,.0f')]
        ).properties(
            height=400
        )
        st.altair_chart(chart_fuel, use_container_width=True)

    st.markdown("---")

    # Chart C: Price vs. Mileage (Scatter Plot)
    st.subheader("Price vs. Mileage (Interactive Scatter Plot)")
    
    # Streamlit WIDGET: Selectbox for Color Encoding
    color_by = st.selectbox(
        "Color points by:",
        options=['model', 'transmission', 'sales_classification', 'color'],
        index=2
    )

    scatter = alt.Chart(df_charts).mark_circle(size=60).encode(
        x=alt.X('mileage_km', title='Mileage (KM)'),
        y=alt.Y('price_usd', title='Price (USD)'),
        color=color_by,
        tooltip=['model', 'mileage_km', alt.Tooltip('price_usd', format='$,.0f'), color_by]
    ).interactive()

    st.altair_chart(scatter, use_container_width=True)


# --- MAIN APP LOGIC (Page Selector) ---
def main():
    """The main function to handle page routing via the sidebar."""
    st.sidebar.title("Navigation")
    
    # Widget: Radio button for page selection
    page = st.sidebar.radio("Go to", ["1. Overview & KPIs", "2. Detailed Analysis"])

    if page == "1. Overview & KPIs":
        home_page()
    elif page == "2. Detailed Analysis":
        detailed_analysis_page()

# --- APPLICATION ENTRY POINT  ---
if __name__ == "__main__":
    main()