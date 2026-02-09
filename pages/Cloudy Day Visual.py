import streamlit as st
import pandas as pd
import plotly.express as px
from utils import hide_streamlit_style

hide_streamlit_style()
hide_streamlit_style = """
    <style>
    /* Hide GitHub and Fork icons in Streamlit Cloud header */
    [data-testid="stToolbar"] {
        display: none !important;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("Interactive Line Plot Tool (with multiple slicers & line styles)")
st.write("Visualise data for various dates to find sunny dates for analysis.")
# Step 1: Cached file reader
@st.cache_data
def load_file(uploaded_file):
    """Read CSV or Excel file with caching."""
    if uploaded_file.name.lower().endswith(".csv"):
        try:
          return pd.read_csv(uploaded_file)
        except:
            return pd.read_excel(uploaded_file)
    else:
        return pd.read_excel(uploaded_file)

# Step 2: Upload file
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    df = load_file(uploaded_file)
    # ✅ Remove duplicate columns
    df = df.loc[:, ~df.columns.duplicated()]

    # ✅ Format Date and Time columns if present
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%d-%m-%Y")
    if "Time" in df.columns:
        df["Time"] = pd.to_datetime(df["Time"], errors="coerce").dt.strftime("%H:%M:%S")

    st.subheader("Preview of Uploaded File")
    st.dataframe(df.head())

    # Step 3: Ask user for slicer columns
    slicer_cols = []
    add_more = True
    counter = 1
    while add_more:
        slicer_col = st.selectbox(f"Select slicer column {counter}", df.columns, key=f"slicer_{counter}")
        if slicer_col:
            slicer_vals = st.multiselect(f"Select values for {slicer_col}", df[slicer_col].unique(), key=f"slicer_vals_{counter}")
            if slicer_vals:
                df = df[df[slicer_col].isin(slicer_vals)]
                slicer_cols.append((slicer_col, slicer_vals))

        add_more = st.radio(f"Do you want to add another slicer?", ["No", "Yes"], key=f"radio_{counter}") == "Yes"
        counter += 1

    # Step 4: Ask user for x-axis column
    x_col = st.selectbox("Select X-axis column", df.columns)

    # Step 5: Ask user for y-axis columns (multiple allowed)
    y_cols = st.multiselect("Select Y-axis columns", df.columns)

    # Step 6: Ask user for line type column
    line_type_col = st.selectbox("Select line type column (for line styles)", df.columns)

    if x_col and y_cols and line_type_col:
        # Melt dataframe for Plotly
        df_melted = df.melt(
            id_vars=[x_col, line_type_col],
            value_vars=y_cols,
            var_name="Y_variable",
            value_name="Value"
        )

        # Step 7: Plot with Plotly
        fig = px.line(
            df_melted,
            x=x_col,
            y="Value",
            color="Y_variable",          # different colors for each Y variable
            line_dash=line_type_col,     # different line styles based on line type column
            title="Interactive Line Plot"
        )

        st.plotly_chart(fig, use_container_width=True)