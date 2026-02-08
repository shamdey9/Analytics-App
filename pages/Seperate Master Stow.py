import streamlit as st
import pandas as pd
import os
import time
  # Ensure stow.py has this function

st.set_page_config(page_title="CSV Fission Tool", layout="centered")

def add_stow_column(df: pd.DataFrame, cols: list, new_col_name: str = 'stow') -> pd.DataFrame:
    """
    Adds a conditional column to the DataFrame based on the values in two specified columns.

    Parameters:
    - df: pandas DataFrame
    - cols: list of two column names [col1, col2]
    - new_col_name: name of the new conditional column (default: 'category')

    Returns:
    - Modified DataFrame with the new column added
    """
    if len(cols) != 2:
        raise ValueError("Exactly two column names must be provided.")

    col1, col2 = cols

    def categorize(row):
        if row[col1] == 50 and row[col2] == -50:
            return 'Normal'
        elif row[col1] == 10 and row[col2] == -10:
            return 'WS'
        elif row[col1]  == 50 and row[col2] in [-35,-30,-20,-10,0,10,20,25,30,35]:
            return 'Wind'
        else:
            return 'others'

    df[new_col_name] = df.apply(categorize, axis=1)
    return df

def fission_process():
    st.title("🔬 CSV Seperate Tool")
    st.write("Seperate Different Master Stow information into Two file.")

    uploaded_file = st.file_uploader("Upload a CSV file to begin fission", type=["csv"])
    if not uploaded_file:
        st.stop()

    df = pd.read_csv(uploaded_file)
    st.subheader("Preview of Uploaded File")
    st.dataframe(df.head())

    st.subheader("Step 1: Select Columns to Include")
    selected_columns = st.multiselect("Choose columns to keep in the fissioned file", df.columns.tolist())
    if not selected_columns:
        st.warning("Please select at least one column.")
        st.stop()

    df_selected = df[selected_columns]
    st.subheader("Preview of Selected Columns")
    st.dataframe(df_selected.head())

    st.subheader("Step 2: Add 'stow' Column?")
    include_stow = st.radio("Do you want to include a 'stow' column?", ["Yes", "No"])

    if include_stow == "Yes":
        df_selected = df_selected.dropna()

        # Ask user to identify the timestamp column
        timestamp_column = st.selectbox("Select the timestamp column", df_selected.columns)

        # Identify columns excluding the selected timestamp column
        stow_candidates = [col for col in df_selected.columns if col != timestamp_column]
        if len(stow_candidates) < 2:
            st.error("At least two non-timestamp columns are required to add 'stow'.")
            st.stop()

        col1 = st.selectbox("Select first column for stow", stow_candidates, index=0)
        col2 = st.selectbox("Select second column for stow", [c for c in stow_candidates if c != col1], index=0)

        df_selected = add_stow_column(df_selected, [col1, col2])
        st.subheader("Preview with 'stow' Column")
        st.dataframe(df_selected.head())

    st.subheader("Step 3: Download Fissioned File")
    filename = st.text_input("Enter filename for download (e.g., output.csv)", value="fissioned_output.csv")
    download_location = st.text_input("Enter download folder path", value=os.getcwd())

    if st.button("Download CSV"):
        full_path = os.path.join(download_location, filename)
        with st.spinner("Generating file..."):
            time.sleep(1)
            df_selected.to_csv(full_path, index=False)
            progress_bar = st.progress(0)
            for i in range(1, 101, 10):
                progress_bar.progress(i / 100)
                time.sleep(0.1)
        st.success(f"File saved to: {full_path}")

    st.subheader("Step 4: Continue Fission?")
    if st.button("Finish"):
        st.write("✅ The app has finished. You may now close this tab.")
        st.stop()



if __name__ == "__main__":
    fission_process()