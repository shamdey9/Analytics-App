import streamlit as st
import pandas as pd
import pytz
import os
from datetime import datetime, timedelta
import pytz

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

st.title("📊 WeatherSmart Processor")
st.write("Help preprocess the Weathersmart Activation CSV file to unify it with Stow event file,")
def round_to_half_hour(dt):
    minute = dt.minute
    if minute < 15:
        return dt.replace(minute=0, second=0, microsecond=0)
    elif minute < 45:
        return dt.replace(minute=30, second=0, microsecond=0)
    else:
        return (dt + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)


# Step 1: Upload CSV
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
if uploaded_file:
    df_raw = pd.read_csv(uploaded_file, header=None)
    st.subheader("🔍 Raw Preview (No Header)")
    st.dataframe(df_raw)

    # Step 2: Remove Top Rows
    num_rows_to_remove = st.number_input("Number of top rows to remove", min_value=0, max_value=len(df_raw)-1, value=0)
    df_trimmed = df_raw.iloc[num_rows_to_remove:].reset_index(drop=True)
    st.subheader("📉 Preview After Removing Top Rows")
    st.dataframe(df_trimmed)

    # Step 3: Merge Top Rows to Form Header
    num_rows_to_merge = st.number_input("Number of top rows to merge as header", min_value=1, max_value=len(df_trimmed), value=1)
    header_rows = df_trimmed.iloc[:num_rows_to_merge].fillna("").astype(str)
    merged_header = header_rows.apply(lambda x: " ".join(x), axis=0)
    df_final = df_trimmed.iloc[num_rows_to_merge:].reset_index(drop=True)
    df_final.columns = merged_header
    st.subheader("🧠 Preview After Merging Header")
    st.dataframe(df_final)

    # Step 4: Choose Timestamp Column and Timezones
    timestamp_column = st.selectbox("Select column to use as timestamp", df_final.columns)
    from_tz = st.selectbox("Select original timezone", pytz.all_timezones)
    to_tz = st.selectbox("Select target timezone", pytz.all_timezones)

    # Convert timestamp column
    try:
        df_final[timestamp_column] = pd.to_datetime(df_final[timestamp_column], errors='coerce')
        if df_final[timestamp_column].dt.tz is None:
            df_final[timestamp_column] = df_final[timestamp_column].dt.tz_localize(from_tz)
        df_final[timestamp_column] = df_final[timestamp_column].dt.tz_convert(to_tz)
        df_final[timestamp_column] = df_final[timestamp_column].apply(round_to_half_hour).dt.strftime('%Y-%m-%d %H:%M:%S')

        st.subheader(f"🕒 Timestamp Preview ({to_tz})")
        st.dataframe(df_final[[timestamp_column]])
    except Exception as e:
        st.error(f"⚠️ Timestamp conversion failed: {e}")

    # Step 5: Choose Columns to Keep
    selected_columns = st.multiselect("Select columns to keep", df_final.columns.tolist(), default=df_final.columns.tolist())
    df_preview = df_final[selected_columns]
    st.subheader("🔍 Preview Selected Columns")
    st.dataframe(df_preview)

    # Step 6: Clean None Rows
    if st.button("Clean None Rows"):
        df_preview_cleaned = df_preview.dropna()
        df_no_duplicates = df_preview_cleaned.drop_duplicates()

        st.subheader("🧹 Cleaned Preview (No None/NaN Rows)")
        st.dataframe(df_no_duplicates)
        df_cleaned = df_no_duplicates
    else:
        df_no_duplicates = df_preview.drop_duplicates()
        df_cleaned = df_no_duplicates

    # Step 7: Download Processed CSV
    download_location = st.text_input("Enter folder path to save CSV", value=os.getcwd())
    filename = st.text_input("Enter filename", value="processed.csv")

    if st.button("Save CSV"):
        full_path = os.path.join(download_location, filename)
        df_preview_cleaned = df_preview.dropna()
        df_preview_cleaned.to_csv(full_path, index=False)
        st.success(f"📁 File saved to: {full_path}")
        #st.download_button("Click to download", data=df_cleaned.to_csv(index=False), file_name=filename, mime="text/csv")