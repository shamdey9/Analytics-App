import streamlit as st
import pandas as pd
import pytz
import os
from io import BytesIO
from utils import hide_streamlit_style

hide_streamlit_style()

st.title("🕒 CSV Timestamp Cleaner & Merger")
st.write("Helps to convert Time from one zone to another")

# Step 1: User inputs folder path
folder_path = st.text_input("📂 Enter folder path containing CSV files")

@st.cache_data
def list_csv_files(folder):
    return [f for f in os.listdir(folder) if f.endswith('.csv')]

@st.cache_data
def load_csv(file_path):
    return pd.read_csv(file_path)

@st.cache_data
def trim_timestamp(df, column):
    df[column] = df[column].astype(str).str.slice(0, 24)
    return df

@st.cache_data
def convert_timezone(df, column, from_zone, to_zone):
    from_tz = pytz.timezone(from_zone)
    to_tz = pytz.timezone(to_zone)
    df = trim_timestamp(df, column)
    df[column] = pd.to_datetime(df[column], format="%a %b %d %Y %H:%M:%S")
    df[column] = df[column].dt.tz_localize(from_tz, ambiguous='NaT', nonexistent='NaT').dt.tz_convert(to_tz).dt.strftime('%Y-%m-%d %H:%M:%S')
    return df

if folder_path and os.path.isdir(folder_path):
    csv_files = list_csv_files(folder_path)
    if csv_files:
        first_file = os.path.join(folder_path, csv_files[0])
        df = load_csv(first_file)
        st.subheader(f"📄 Preview of: {csv_files[0]}")
        st.dataframe(df.head())

        timestamp_col = st.selectbox("Select timestamp column", df.columns)

        if st.button("✂️ Trim Timestamp (0:24 chars)"):
            df = trim_timestamp(df, timestamp_col)
            st.subheader("🧼 Trimmed Timestamp Preview")
            st.dataframe(df.head())

        timezones = pytz.all_timezones
        from_zone = st.selectbox("From Time Zone", timezones)
        to_zone = st.selectbox("To Time Zone", timezones)

        if st.button("🌐 Convert Time Zone"):
            df = convert_timezone(df, timestamp_col, from_zone, to_zone)
            st.subheader("🕰️ Converted Timestamp Preview")
            st.dataframe(df.head())

        if st.button("🔄 Apply to All & Merge"):
            merged_df = pd.DataFrame()
            progress = st.progress(0)
            for i, file in enumerate(csv_files):
                path = os.path.join(folder_path, file)
                temp_df = load_csv(path)
                temp_df = trim_timestamp(temp_df, timestamp_col)
                temp_df = convert_timezone(temp_df, timestamp_col, from_zone, to_zone)
                merged_df = pd.concat([merged_df, temp_df], ignore_index=True)
                progress.progress((i + 1) / len(csv_files))
            st.success("✅ All files transformed and merged!")
            st.subheader("📊 Merged Data Preview")
            st.dataframe(merged_df.head())

            # Save to CSV in memory
            csv_buffer = BytesIO()
            merged_df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)

            st.download_button(
                label="⬇️ Download Merged CSV",
                data=csv_buffer,
                file_name="merged_transformed.csv",
                mime="text/csv"
            )
    else:
        st.warning("No CSV files found in the folder.")
else:
    st.info("Please enter a valid folder path.")