import streamlit as st
import pandas as pd
from utils import hide_streamlit_style

hide_streamlit_style()

st.title("Merge WeatherSmart Activation and Stow Event Files")

def round_time_column(df, col_name):
    try:
        df[col_name] = pd.to_datetime(df[col_name], format="%H:%M:%S", errors="raise")
        df[col_name] = df[col_name].dt.floor("H")
        return df
    except Exception:
        return df

# Upload files
ws_file = st.file_uploader("Upload Ws file (CSV or Excel)", type=["csv", "xlsx", "xls"], key="ws")
stow_file = st.file_uploader("Upload Stow Event file (CSV or Excel)", type=["csv", "xlsx", "xls"], key="stow")

if ws_file and stow_file:
    ws_df = pd.read_csv(ws_file) if ws_file.name.endswith(".csv") else pd.read_excel(ws_file)
    stow_df = pd.read_csv(stow_file) if stow_file.name.endswith(".csv") else pd.read_excel(stow_file)

    st.subheader("Preview Ws File")
    st.dataframe(ws_df.head())
    st.subheader("Preview Stow Event File")
    st.dataframe(stow_df.head())

    ws_merge_col = st.selectbox("Select column to merge on (Ws file)", ws_df.columns)
    stow_merge_col = st.selectbox("Select column to merge on (Stow Event file)", stow_df.columns)

    ws_df[ws_merge_col] = pd.to_datetime(ws_df[ws_merge_col], format="%Y-%m-%d %H:%M:%S")
    stow_df[stow_merge_col] = pd.to_datetime(stow_df[stow_merge_col], format="%Y-%m-%d %H:%M:%S")
    ws_df = round_time_column(ws_df, ws_merge_col)
    stow_df = round_time_column(stow_df, stow_merge_col)

    # Merge immediately (no button needed)
    merged_df = pd.merge(ws_df, stow_df, left_on=ws_merge_col, right_on=stow_merge_col, how="inner")

    st.subheader("Merged File Preview")
    st.dataframe(merged_df.head())

    # Persist filename in session_state
    if "file_name" not in st.session_state:
        st.session_state.file_name = "merged_output.csv"

    file_name = st.text_input("Enter file name:", st.session_state.file_name)
    st.session_state.file_name = file_name  # update on every rerun

    # Always show download button
    merged_csv = merged_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Merged File as CSV",
        data=merged_csv,
        file_name=st.session_state.file_name,
        mime="text/csv",
    )