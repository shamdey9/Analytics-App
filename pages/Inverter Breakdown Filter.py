import streamlit as st
import pandas as pd
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

st.title("Filter Power Data Based on Inverter Breakdown Ranges")
st.write("Clean excel file to remove timestamps with inverter breakdown.")

# Upload BD file
bd_file = st.file_uploader("Upload Inverter Breakdown (BD) file", type=["csv", "xlsx"])
if bd_file:
    bd_df = pd.read_csv(bd_file) if bd_file.name.endswith(".csv") else pd.read_excel(bd_file)
    st.subheader("Preview of BD file")
    st.dataframe(bd_df.head())

    # Select start and end timestamp columns
    start_col = st.selectbox("Select START timestamp column", bd_df.columns)
    end_col = st.selectbox("Select END timestamp column", bd_df.columns)

    # Upload Power file
    power_file = st.file_uploader("Upload Power file", type=["csv", "xlsx"])
    if power_file:
        power_df = pd.read_csv(power_file) if power_file.name.endswith(".csv") else pd.read_excel(power_file)
        st.subheader("Preview of Power file")
        st.dataframe(power_df.head())

        # Select timestamp column in Power file
        power_ts_col = st.selectbox("Select timestamp column in Power file", power_df.columns)

        # Caching the filtering function
        @st.cache_data
        def filter_power(power_df, bd_df, power_ts_col, start_col, end_col):
            # Convert to datetime
            power_df[power_ts_col] = pd.to_datetime(power_df[power_ts_col], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
            bd_df[start_col] = pd.to_datetime(bd_df[start_col], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')

            bd_df[end_col] = pd.to_datetime(bd_df[end_col], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')

            # Initialize mask
            mask = pd.Series(False, index=power_df.index)

            # For each BD range, mark matching power timestamps
            for start, end in zip(bd_df[start_col], bd_df[end_col]):
                if pd.notnull(start) and pd.notnull(end):
                    mask |= (power_df[power_ts_col] >= start) & (power_df[power_ts_col] <= end)
                    

            removed_count = mask.sum()
            filtered_df = power_df[~mask]
            return filtered_df, removed_count

        # Apply filtering
        filtered_power_df, removed_rows = filter_power(power_df, bd_df, power_ts_col, start_col, end_col)

        # Display stats
        st.write(f"Number of rows in BD data: {len(bd_df)}")
        st.write(f"Number of rows removed from Power data: {removed_rows}")

        # Download button
        st.download_button(
            label="Download filtered Power data",
            data=filtered_power_df.to_csv(index=False).encode("utf-8"),
            file_name="filtered_power.csv",
            mime="text/csv"
        )