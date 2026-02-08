import streamlit as st
import pandas as pd
from utils import hide_streamlit_style

hide_streamlit_style()

st.title("Power File Hourly Generation")

# Step 1: Upload power file
uploaded_file = st.file_uploader("Upload a Power CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    # Step 2: Read file
    if uploaded_file.name.lower().endswith(".csv"):
        try:
            df = pd.read_csv(uploaded_file)
        except:
            df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("Preview of Uploaded File")
    st.dataframe(df.head())

    # Step 3: Ask user column to group by
    group_col = st.selectbox("Select column to group by", df.columns)

    # Step 4: Ask user date column
    date_col = st.selectbox("Select date column", df.columns)

    # Step 5: Ask user column to aggregate
    agg_col = st.selectbox("Select column to aggregate", df.columns)

    # Step 6: Ask user kind of aggregation
    agg_func = st.radio("Select aggregation function", ["sum", "mean", "max", "min", "count"])

    # Step 7: Perform groupby + aggregation
    if group_col and date_col and agg_col and agg_func:
        # Convert date column to datetime for safety
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

        grouped_df = df.groupby([group_col, date_col])[agg_col].agg(agg_func).reset_index()

        st.subheader("Preview of Grouped & Aggregated Results")
        st.dataframe(grouped_df.head())

        # Step 8: Download option
        file_name = st.text_input("Enter file name for download:", "grouped_output.csv")
        grouped_csv = grouped_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Grouped File as CSV",
            data=grouped_csv,
            file_name=file_name if file_name else "grouped_output.csv",
            mime="text/csv",
        )