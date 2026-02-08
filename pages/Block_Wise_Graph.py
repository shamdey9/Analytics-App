import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from utils import hide_streamlit_style

hide_streamlit_style()

# ---------------------------
# 🧪 1. Upload Dataset
# ---------------------------
np.random.seed(42)
st.title("Different Block Power generation Visualization")
st.write("Visualise Power generation from different cblock having different configuration.")
uploaded_file = st.file_uploader("📂 Upload your Excel or CSV file", type=["xlsx", "csv"])
if uploaded_file is not None:
    @st.cache_data
    def load_data(file):
        if file.name.endswith(".csv"):
            return pd.read_csv(file)
        else:
            return pd.read_excel(file, sheet_name="Power")  # default sheet

    df = load_data(uploaded_file)

    # ---------------------------
    # 🎛️ 2. UI Filters
    # ---------------------------
    st.title("Blockwise Config Wise")

    df['Date'] = pd.to_datetime(df['Date']).dt.date
    df['Time'] = pd.to_datetime(df['Time'].astype(str)).dt.time

    hour_options = sorted(df['Hour'].unique())
    selected_hours = st.multiselect("Select Hour(s)", hour_options, default=hour_options)

    categories = st.multiselect("Select Config", df['Period'].unique(), default=df['Period'].unique())
    dates_in_period = sorted(df[df['Period'].isin(categories)]['Date'].unique())
    selected_date = st.multiselect("Select Date", dates_in_period, default=dates_in_period)

    choco_types = st.multiselect("Select Tracking Time", df['Tracking'].unique(), default=df['Tracking'].unique())

    numeric_columns = df.select_dtypes(include='number').columns.tolist()
    y_axis_column = st.selectbox("Select Y-axis Variable", numeric_columns, index=0)

    # ---------------------------
    # 🧼 3. Filter the data
    # ---------------------------
    filtered = df[
        (df['Date'].isin(selected_date)) &
        (df['Hour'].isin(selected_hours)) &
        (df['Period'].isin(categories)) &
        (df['Tracking'].isin(choco_types))
    ]

    # ---------------------------
    # 📈 4. Plot with Plotly
    # ---------------------------
    chart_title = st.text_input("Enter Chart Title", value="Values over Time by Category and Date Group")

    if not filtered.empty:
        fig = px.line(
            filtered,
            x='Time',
            y=y_axis_column,
            color='Date',
            line_dash='Period',
            line_group='Period',
            markers=True,
            title=chart_title
        )
        chart_height = st.sidebar.slider("Chart Height", 300, 1000, 600)
        chart_width = st.sidebar.slider("Chart Width", 300, 1000, 600)

        fig.update_layout(
            xaxis_title='Time',
            height=chart_height,
            width=chart_width,
            yaxis_title=str(y_axis_column),
            template='plotly_white',
            legend_title='Date Group / Category'
        )
        st.plotly_chart(fig)
    else:
        st.warning("No data matches your filter selection.")
else:
    st.info("👆 Please upload an Excel or CSV file to get started.")