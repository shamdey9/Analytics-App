import streamlit as st
import pandas as pd
from io import BytesIO
from utils import hide_streamlit_style

hide_streamlit_style()

st.title("📅 Merge Date and Time Columns into Timestamp Columns")
st.write("Add Timestamp column based on date and time column")
# Step 1: Upload Excel file
uploaded_file = st.file_uploader("Drop your Excel file here", type=["xlsx"])

@st.cache_data
def load_excel(file):
    return pd.read_excel(file)

@st.cache_data
def create_timestamp_columns(df, date_col, time_cols):
    df = df.copy()
    for time_col in time_cols:
        stamp_col = f"{time_col}_stamp"
        # Convert to datetime using temporary datetime objects
        date_series = pd.to_datetime(df[date_col], errors='coerce').dt.date
        time_series = pd.to_datetime(df[time_col], errors='coerce').dt.time
        # Combine date and time into timestamp
        combined = pd.to_datetime(date_series.astype(str) + " " + time_series.astype(str), errors='coerce')
        df[stamp_col] = combined
    return df

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Timestamps')
    output.seek(0)
    return output

if uploaded_file:
    df = load_excel(uploaded_file)
    st.subheader("📄 Preview of Uploaded File")
    st.dataframe(df)

    # Step 2: Select date column
    date_column = st.selectbox("📅 Select the date column", df.columns)

    # Step 3: Select one or more time columns
    time_columns = st.multiselect("⏰ Select one or more time columns", df.columns)

    if date_column and time_columns:
        df_with_stamps = create_timestamp_columns(df, date_column, time_columns)
        st.subheader("🕒 DataFrame with Timestamp Columns")
        st.dataframe(df_with_stamps)

        # Step 4: Download button
        excel_data = convert_df_to_excel(df_with_stamps)
        st.download_button(
            label="📥 Download Excel with Timestamps",
            data=excel_data,
            file_name="timestamped_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )