"""
Australian Employment Data Dashboard
Visualizes employment data by industry and state using ABS Labour Force Table 10
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="Australian Employment Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    :root {
        --primary-color: #0052CC;
        --secondary-color: #36B9CC;
        --success-color: #28A745;
        --danger-color: #DC3545;
        --light-bg: #F8FAFC;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
    }
    
    .metric-card {
        background-color: var(--light-bg);
        border-radius: 10px;
        padding: 1.5rem;
        border-left: 5px solid var(--primary-color);
    }
    
    .header-section {
        background: linear-gradient(135deg, #0052CC 0%, #36B9CC 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .stSelectbox label, .stMultiSelect label {
        font-weight: 600;
        color: #333;
    }
    
    .comparison-container {
        background-color: #F0F8FF;
        border-left: 4px solid #0052CC;
        padding: 1rem;
        border-radius: 5px;
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== DATA LOADING ====================
@st.cache_data
def load_employment_data():
    """
    Load ABS Labour Force Table 10 data
    This function caches the data to improve performance
    """
    try:
        data_path = "au-employment-dashboard/data/table10.csv"
        
        # Try loading from local file
        try:
            df = pd.read_csv(data_path)
            logger.info(f"Loaded data from {data_path}")
        except FileNotFoundError:
            st.warning(f"""
            ⚠️ Data file not found at `{data_path}`
            
            **Instructions to add data:**
            1. Download Table 10 from: https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia
            2. Save the CSV file to the `data/` folder as `table10.csv`
            3. Refresh this app
            """)
            return None
        
        # Data preprocessing
        df = preprocess_employment_data(df)
        return df
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        logger.error(f"Data loading error: {str(e)}")
        return None

def preprocess_employment_data(df):
    """
    Preprocess ABS Labour Force data
    Handles various ABS data formats and cleans the data
    """
    df = df.copy()
    
    # Common column name variations from ABS
    date_cols = ['DATE', 'Date', 'date', 'TIME_PERIOD', 'Month', 'month']
    state_cols = ['STATE', 'State', 'state', 'STATE_ABBREV', 'ST']
    value_cols = ['VALUE', 'Value', 'value', 'OBS_VALUE', 'Obs_Value']
    series_cols = ['SERIES_ID', 'Series_ID', 'SERIES', 'Series']
    
    # Find actual column names
    date_col = next((col for col in date_cols if col in df.columns), None)
    state_col = next((col for col in state_cols if col in df.columns), None)
    value_col = next((col for col in value_cols if col in df.columns), None)
    series_col = next((col for col in series_cols if col in df.columns), None)
    
    if not all([date_col, state_col, value_col]):
        st.error("⚠️ Data format not recognized. Please check the CSV structure.")
        return None
    
    # Rename columns to standard names
    rename_dict = {
        date_col: 'Date',
        state_col: 'State',
        value_col: 'Value'
    }
    if series_col:
        rename_dict[series_col] = 'Series'
    
    df = df.rename(columns=rename_dict).dropna(subset=['Date', 'State', 'Value'])
    
    # Convert date to datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    
    # Convert Value to numeric
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    df = df.dropna(subset=['Value'])
    
    # Extract employment type/industry from Series if available
    if 'Series' in df.columns:
        df['Industry'] = df['Series'].str.extract(r'(Employed|Unemployed|Participation|Unemployment)')[0]
        df['Industry'] = df['Industry'].fillna('Employed')
    else:
        df['Industry'] = 'Employed'
    
    # Sort by date
    df = df.sort_values('Date')
    
    return df

# ==================== UTILITY FUNCTIONS ====================
def get_date_range(df):
    """Get min and max dates from dataframe"""
    if df is None or df.empty:
        return None, None
    return df['Date'].min(), df['Date'].max()

def filter_data(df, states, industries, start_date, end_date):
    """Filter dataframe by selected criteria"""
    filtered = df[
        (df['State'].isin(states)) &
        (df['Industry'].isin(industries)) &
        (df['Date'] >= start_date) &
        (df['Date'] <= end_date)
    ].copy()
    return filtered

def calculate_metrics(df):
    """Calculate key employment metrics"""
    if df.empty:
        return {
            'total_employed': 0,
            'change': 0,
            'change_pct': 0,
            'latest_date': pd.Timestamp.now(),
            'data_points': 0
        }
    
    latest_date = df['Date'].max()
    latest_data = df[df['Date'] == latest_date]
    
    total_employed = latest_data['Value'].sum()
    prev_date = df['Date'].unique()[-2] if len(df['Date'].unique()) > 1 else latest_date
    prev_data = df[df['Date'] == prev_date]
    prev_total = prev_data['Value'].sum()
    
    change = total_employed - prev_total
    change_pct = (change / prev_total * 100) if prev_total > 0 else 0
    
    return {
        'total_employed': total_employed,
        'change': change,
        'change_pct': change_pct,
        'latest_date': latest_date,
        'data_points': len(df)
    }

# ==================== CHART FUNCTIONS ====================
def create_line_chart(df, title="Employment Trend Over Time"):
    """Create interactive line chart for time series data"""
    if df.empty:
        return None
    
    fig = px.line(
        df,
        x='Date',
        y='Value',
        color='State',
        title=title,
        labels={'Value': 'Number of Employed Persons', 'Date': 'Date'},
        template='plotly_white',
        hover_data={'Value': ':.0f'}
    )
    
    fig.update_layout(
        height=450,
        hovermode='x unified',
        font=dict(size=11),
        xaxis_title="Date",
        yaxis_title="Employed Persons",
        title_font_size=16,
        title_font_color="#0052CC",
        template='plotly_white'
    )
    
    fig.update_traces(mode='lines+markers', line=dict(width=2.5))
    
    return fig

def create_area_chart(df, title="Employment Distribution"):
    """Create stacked area chart"""
    if df.empty:
        return None
    
    pivot_df = df.pivot_table(
        values='Value',
        index='Date',
        columns='State',
        aggfunc='sum'
    )
    
    fig = go.Figure()
    
    for state in pivot_df.columns:
        fig.add_trace(go.Scatter(
            x=pivot_df.index,
            y=pivot_df[state],
            mode='lines',
            name=state,
            stackgroup='one',
            fillcolor=None,
            line=dict(width=0.5),
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Employed Persons",
        height=450,
        hovermode='x unified',
        template='plotly_white',
        font=dict(size=11),
        title_font_size=16,
        title_font_color="#0052CC"
    )
    
    return fig

def create_bar_chart(df, groupby='State', title="Employment by State"):
    """Create bar chart for comparison"""
    if df.empty:
        return None
    
    grouped_data = df.groupby(groupby)['Value'].sum().sort_values(ascending=False)
    
    fig = px.bar(
        x=grouped_data.index,
        y=grouped_data.values,
        title=title,
        labels={'x': groupby, 'y': 'Total Employed Persons'},
        template='plotly_white',
        color=grouped_data.values,
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        height=450,
        font=dict(size=11),
        title_font_size=16,
        title_font_color="#0052CC",
        showlegend=False,
        hovermode='x'
    )
    
    return fig

def create_heatmap(df, title="Employment Heatmap by State and Month"):
    """Create heatmap visualization"""
    if df.empty:
        return None
    
    df_copy = df.copy()
    df_copy['YearMonth'] = df_copy['Date'].dt.to_period('M')
    
    pivot_data = df_copy.pivot_table(
        values='Value',
        index='State',
        columns='YearMonth',
        aggfunc='sum'
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns.astype(str),
        y=pivot_data.index,
        colorscale='Blues',
        colorbar=dict(title="Employed<br>Persons")
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Year-Month",
        yaxis_title="State",
        height=450,
        font=dict(size=11),
        title_font_size=16,
        title_font_color="#0052CC"
    )
    
    return fig

def create_comparison_chart(df1, df2, label1, label2, title="Comparison"):
    """Create comparison chart for two datasets"""
    if df1.empty or df2.empty:
        return None
    
    fig = go.Figure()
    
    # Aggregate by date
    data1_agg = df1.groupby('Date')['Value'].sum()
    data2_agg = df2.groupby('Date')['Value'].sum()
    
    fig.add_trace(go.Scatter(
        x=data1_agg.index,
        y=data1_agg.values,
        mode='lines+markers',
        name=label1,
        line=dict(color='#0052CC', width=3),
        marker=dict(size=6)
    ))
    
    fig.add_trace(go.Scatter(
        x=data2_agg.index,
        y=data2_agg.values,
        mode='lines+markers',
        name=label2,
        line=dict(color='#36B9CC', width=3),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Employed Persons",
        height=450,
        hovermode='x unified',
        template='plotly_white',
        font=dict(size=11),
        title_font_size=16,
        title_font_color="#0052CC"
    )
    
    return fig

# ==================== SIDEBAR FILTERS ====================
st.sidebar.markdown("### 🎛️ Dashboard Filters")
st.sidebar.markdown("---")

# Load data
df = load_employment_data()

if df is not None and not df.empty:
    # Date range filter
    min_date, max_date = get_date_range(df)
    
    st.sidebar.markdown("#### 📅 Date Range")
    date_range = st.sidebar.slider(
        "Select date range:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        format="YYYY-MM"
    )
    start_date, end_date = date_range
    
    # State multi-select
    st.sidebar.markdown("#### 🗺️ States & Territories")
    available_states = sorted(df['State'].unique())
    selected_states = st.sidebar.multiselect(
        "Select States/Territories:",
        options=available_states,
        default=available_states[:3] if len(available_states) > 0 else available_states,
        help="Choose one or more states to display"
    )
    
    if not selected_states:
        st.sidebar.warning("⚠️ Please select at least one state")
        selected_states = available_states[:1]
    
    # Industry multi-select
    st.sidebar.markdown("#### 🏭 Employment Type")
    available_industries = sorted(df['Industry'].unique())
    selected_industries = st.sidebar.multiselect(
        "Select Employment Type:",
        options=available_industries,
        default=available_industries,
        help="Choose employment categories to display"
    )
    
    if not selected_industries:
        st.sidebar.warning("⚠️ Please select at least one employment type")
        selected_industries = available_industries
    
    # Filter data
    filtered_df = filter_data(df, selected_states, selected_industries, start_date, end_date)
    
    # ==================== MAIN DASHBOARD ====================
    
    # Header
    st.markdown("""
        <div class='header-section'>
            <h1>📊 Australian Employment Dashboard</h1>
            <p>Real-time visualization of employment data by state and industry (ABS Labour Force Table 10)</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Key Metrics
    if not filtered_df.empty:
        metrics = calculate_metrics(filtered_df)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Employed",
                f"{metrics['total_employed']:,.0f}",
                f"{metrics['change']:+,.0f}",
                delta_color="normal"
            )
        
        with col2:
            st.metric(
                "Change %",
                f"{metrics['change_pct']:.2f}%",
                help="Percentage change from previous period"
            )
        
        with col3:
            st.metric(
                "Latest Date",
                metrics['latest_date'].strftime("%B %Y"),
                help="Most recent data point"
            )
        
        with col4:
            st.metric(
                "Data Points",
                metrics['data_points'],
                help="Number of records displayed"
            )
        
        st.markdown("---")
        
        # Time Series Analysis
        st.markdown("### 📈 Employment Trends Over Time")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            trend_chart = create_line_chart(filtered_df, "Employment Trend - All Selected Data")
            if trend_chart:
                st.plotly_chart(trend_chart, use_container_width=True)
        
        with col2:
            st.markdown("**Chart Information:**")
            st.info("""
            • Shows employment trends over time
            • Color-coded by state
            • Hover for exact values
            • Click legend to hide/show states
            """)
        
        # Distribution Analysis
        st.markdown("### 📊 Distribution Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            area_chart = create_area_chart(filtered_df, "Employment Distribution by State")
            if area_chart:
                st.plotly_chart(area_chart, use_container_width=True)
        
        with col2:
            bar_chart = create_bar_chart(filtered_df, 'State', "Total Employment by State")
            if bar_chart:
                st.plotly_chart(bar_chart, use_container_width=True)
        
        # State Comparison Analysis
        st.markdown("### 🔍 State Comparison Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            industry_bar = create_bar_chart(filtered_df, 'Industry', "Employment by Type")
            if industry_bar:
                st.plotly_chart(industry_bar, use_container_width=True)
        
        with col2:
            heatmap_chart = create_heatmap(filtered_df, "Employment Heatmap")
            if heatmap_chart:
                st.plotly_chart(heatmap_chart, use_container_width=True)
        
        # Advanced Comparison Feature
        st.markdown("### ⚖️ Advanced Comparison")
        
        st.markdown("""
        Compare employment trends between two different selections.
        """)
        
        comparison_col1, comparison_col2 = st.columns(2)
        
        with comparison_col1:
            st.markdown("**Selection 1**")
            comp1_states = st.multiselect(
                "States for Comparison 1:",
                options=available_states,
                default=available_states[:1],
                key="comp1_states"
            )
            comp1_industries = st.multiselect(
                "Employment Type for Comparison 1:",
                options=available_industries,
                default=available_industries[:1],
                key="comp1_ind"
            )
        
        with comparison_col2:
            st.markdown("**Selection 2**")
            comp2_states = st.multiselect(
                "States for Comparison 2:",
                options=available_states,
                default=available_states[1:2] if len(available_states) > 1 else available_states,
                key="comp2_states"
            )
            comp2_industries = st.multiselect(
                "Employment Type for Comparison 2:",
                options=available_industries,
                default=available_industries[:1],
                key="comp2_ind"
            )
        
        if comp1_states and comp2_states:
            comp1_data = filter_data(df, comp1_states, comp1_industries, start_date, end_date)
            comp2_data = filter_data(df, comp2_states, comp2_industries, start_date, end_date)
            
            if not comp1_data.empty and not comp2_data.empty:
                comp_label1 = f"{', '.join(comp1_states[:2])}{'...' if len(comp1_states) > 2 else ''}"
                comp_label2 = f"{', '.join(comp2_states[:2])}{'...' if len(comp2_states) > 2 else ''}"
                
                comparison_chart = create_comparison_chart(
                    comp1_data,
                    comp2_data,
                    comp_label1,
                    comp_label2,
                    "Employment Comparison"
                )
                
                if comparison_chart:
                    st.plotly_chart(comparison_chart, use_container_width=True)
                
                # Comparison Statistics
                col1, col2 = st.columns(2)
                
                with col1:
                    metrics1 = calculate_metrics(comp1_data)
                    st.markdown(f"""
                    **Selection 1: {comp_label1}**
                    
                    - Total Employed: {metrics1['total_employed']:,.0f}
                    - Change: {metrics1['change']:+,.0f} ({metrics1['change_pct']:.2f}%)
                    - Latest: {metrics1['latest_date'].strftime('%B %Y')}
                    """)
                
                with col2:
                    metrics2 = calculate_metrics(comp2_data)
                    st.markdown(f"""
                    **Selection 2: {comp_label2}**
                    
                    - Total Employed: {metrics2['total_employed']:,.0f}
                    - Change: {metrics2['change']:+,.0f} ({metrics2['change_pct']:.2f}%)
                    - Latest: {metrics2['latest_date'].strftime('%B %Y')}
                    """)
        
        # Data Table
        st.markdown("### 📋 Detailed Data View")
        
        if st.checkbox("Show raw data table", value=False):
            st.dataframe(
                filtered_df.sort_values('Date', ascending=False),
                use_container_width=True,
                height=400
            )
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; font-size: 12px;'>
            <p>📊 Data Source: Australian Bureau of Statistics (ABS) Labour Force Table 10</p>
            <p>Last Updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
            <p>Dashboard built with Streamlit | Data visualization with Plotly</p>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.warning("⚠️ No data available for the selected filters. Please adjust your selections.")

else:
    st.error("""
    ❌ Error: Unable to load employment data.
    
    Please follow these steps:
    
    1. **Download the data from ABS:**
       - Visit: https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia
       - Download **Table 10** (Labour force status by Sex, State and Territory)
       - Save as CSV format
    
    2. **Add to project:**
       - Create a `data/` folder in your project directory
       - Save the CSV file as `table10.csv`
    
    3. **Refresh the app:**
       - Run: `streamlit run app.py`
    
    For Streamlit Cloud deployment, commit the data file to your GitHub repository.
    """)
