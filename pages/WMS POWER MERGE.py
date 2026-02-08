import streamlit as st
import pandas as pd
from utils import hide_streamlit_style

hide_streamlit_style()

@st.cache_data
def load_file(uploaded_file):
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".csv"):
            return pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith((".xls", ".xlsx")):
            return pd.read_excel(uploaded_file)
    return None

st.title("WMS & Power File Merger")
st.write("Merge WMS and Power File")
# Step 1: Upload WMS file
st.header("Step 1: Upload WMS File")
wms_file = st.file_uploader("Upload WMS file (CSV or Excel)", type=["csv", "xls", "xlsx"], key="wms")

if wms_file:
    wms_df = load_file(wms_file)
    st.write(f"Rows in WMS file: {len(wms_df)}")

    st.subheader("Preview of WMS File")
    st.dataframe(wms_df.head())

    selected_columns = st.multiselect(
        "Select columns to keep from WMS file",
        options=wms_df.columns.tolist(),
        default=wms_df.columns.tolist()
    )

    wms_timestamp_col = st.selectbox(
        "Select timestamp column in WMS file",
        options=wms_df.columns.tolist()
    )

    wms_df = wms_df[selected_columns]

    # Step 2: Upload Power file
    st.header("Step 2: Upload Power File")
    power_file = st.file_uploader("Upload Power file (CSV or Excel)", type=["csv", "xls", "xlsx"], key="power")

    if power_file:
        power_df = load_file(power_file)
        st.write(f"Rows in Power file: {len(power_df)}")

        st.subheader("Preview of Power File")
        st.dataframe(power_df.head())

        power_timestamp_col = st.selectbox(
            "Select timestamp column in Power file",
            options=power_df.columns.tolist()
        )

        # Convert timestamps to datetime for safe merging
        wms_df[wms_timestamp_col] = pd.to_datetime(wms_df[wms_timestamp_col], errors="coerce")
        power_df[power_timestamp_col] = pd.to_datetime(power_df[power_timestamp_col], errors="coerce")

        # Step 3: Decide which file has fewer rows
        if len(wms_df) <= len(power_df):
            left_df, right_df = wms_df, power_df
            left_ts_col, right_ts_col = wms_timestamp_col, power_timestamp_col
            lesser_file = "WMS"
        else:
            left_df, right_df = power_df, wms_df
            left_ts_col, right_ts_col = power_timestamp_col, wms_timestamp_col
            lesser_file = "Power"

        # Highlight which file is chosen as base
        st.success(f"Using **{lesser_file} file** as the base for merging (fewer rows).")

        # Merge keeping rows from the lesser file
        merged_df = pd.merge(
            left_df,
            right_df,
            left_on=left_ts_col,
            right_on=right_ts_col,
            how="left"
        )

        # Drop only date/time/timestamp columns from the larger file
        base_cols = set(left_df.columns)  # keep these intact
        cols_to_drop = [
            col for col in merged_df.columns
            if col not in base_cols and ("time" in col.lower() or "date" in col.lower() or "stamp" in col.lower())
        ]
        merged_df = merged_df.drop(columns=cols_to_drop)

        # Rename unified timestamp column
        merged_df = merged_df.rename(columns={left_ts_col: "Timestamp"})

        st.write(f"Rows in Final merged file: {len(merged_df)}")
        st.subheader("Merged Data Preview")
        st.dataframe(merged_df.head())

        # Option to download merged file
        csv = merged_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Merged CSV",
            data=csv,
            file_name="merged_wms_power.csv",
            mime="text/csv"
        )