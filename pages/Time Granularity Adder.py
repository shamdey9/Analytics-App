import streamlit as st
import pandas as pd
from utils import hide_streamlit_style

hide_streamlit_style()

st.title("Date & Time Column Enhancer")
st.write("Helps to expand time and dat column into month, year,day, hour and minute.")

uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
            try:
               df = pd.read_excel(uploaded_file)
            except:
               df = pd.read_csv(uploaded_file)
    else:
            try:
                df = pd.read_csv(uploaded_file, encoding="utf-8")
            except UnicodeDecodeError:
                # fallback if utf-8 fails
                df = pd.read_csv(uploaded_file, encoding="latin1")

    # Step 2: Preview
    st.subheader("Preview of Uploaded File")
    st.dataframe(df.head())

    # Step 3: Ask user to select date and time columns
    date_col = st.selectbox("Select the Date column", df.columns)
    time_col = st.selectbox("Select the Time column", df.columns)
    df[date_col] = pd.to_datetime(df[date_col])
    df[time_col] = pd.to_datetime(df[time_col])
    # Option 1: Keep as datetime but only show date
    df[date_col] = df[date_col].dt.date
    df[time_col] = pd.to_datetime(df[time_col])

    # Step 2: Round to nearest minute
    df[time_col] = df[time_col].dt.round("min")
    
    df[time_col] = df[time_col].dt.strftime("%H:%M:%S")

    # Option 2: Format as string yyyy-mm-dd
    #df[date_col] = df[date_col].dt.strftime("%Y-%m-%d")

    # Step 4: Combine date and time into a single datetime column
    try:
        df["datetime"] = pd.to_datetime(df[date_col].astype(str) + " " + df[time_col].astype(str))

        # Step 5: Add new columns
        df["year"] = df["datetime"].dt.year
        df["month"] = df["datetime"].dt.month
        df["day"] = df["datetime"].dt.day
        df["hour"] = df["datetime"].dt.hour
        df["minute"] = df["datetime"].dt.minute

        st.subheader("Preview with Added Columns")
        st.dataframe(df.head())

        # Step 6: User input for file name
        file_name = st.text_input("Enter file name for download:", "enhanced_output.csv")

        # Step 7: Download button
        enhanced_csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Enhanced File as CSV",
            data=enhanced_csv,
            file_name=file_name if file_name else "enhanced_output.csv",
            mime="text/csv",
        )
    except Exception as e:
        st.error(f"Error parsing date/time columns: {e}")