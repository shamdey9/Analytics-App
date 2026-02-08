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

st.title("Tracking Summary Tool")

# File uploader (accepts CSV or Excel)
uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    # Detect file type and read accordingly
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Ensure time column is parsed correctly
    df['time_only'] = pd.to_datetime(df['time_only'], format='%H:%M:%S').dt.time
    # Replace Python None values
    df = df.replace({None: "NG"})

    def summarize_blocks(df):
        summaries = []
        current_label = -1
        start_time = None
        prev_time = None

        if df.empty:
            return pd.DataFrame(columns=["Category", "Start", "End"])

        for _, row in df.iterrows():
            label = row['Tracking']
            time = row['time_only']

            if current_label == -1:
                # First row initializes the first block
                current_label = label
                start_time = time
            elif label != current_label:
                # Close previous block
                summaries.append({
                    "Category": current_label,
                    "Start": start_time,
                    "End": prev_time
                })
                # Start new block
                current_label = label
                start_time = time

            prev_time = time

        if current_label != -1:
            summaries.append({
                "Category": current_label,
                "Start": start_time,
                "End": prev_time
            })

        return pd.DataFrame(summaries)

    # Summarize
    summary_df = summarize_blocks(df)

    st.subheader("Summary of Consecutive Blocks")
    st.dataframe(summary_df)

    # Download button for CSV
    csv = summary_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Summary as CSV",
        data=csv,
        file_name="summary_output.csv",
        mime="text/csv",
    )

    # Step 2: Upload another file to add Tracking_Info
    st.subheader("Add Tracking_Info to Another File")
    target_file = st.file_uploader("Upload the file to add Tracking_Info", type=["csv", "xlsx", "xls"], key="target")
    
    if target_file is not None:
        if target_file.name.endswith(".csv"):
            try:
               target_df = pd.read_excel(target_file)
            except:
               target_df = pd.read_csv(target_file)
        else:
            try:
                df = pd.read_csv(target_file, encoding="utf-8")
            except UnicodeDecodeError:
                # fallback if utf-8 fails
                df = pd.read_csv(target_file, encoding="latin1")
            

        # Ask user to choose which column is time
        time_col = st.selectbox("Select the column to use as time", target_df.columns)

        # Convert to datetime.time for comparison
        target_df[time_col] = pd.to_datetime(target_df[time_col], format='%H:%M:%S').dt.time

        # Add Tracking_Info column
        def assign_tracking_info(time_val):
            for _, row in summary_df.iterrows():
                if row['Start'] <= time_val <= row['End']:
                    return row['Category']
            return "No Match"

        target_df["Tracking_Info"] = target_df[time_col].apply(assign_tracking_info)

        st.write("Updated File Preview:")
        st.dataframe(target_df.head())

        # Allow download
        updated_csv = target_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download updated file with Tracking_Info",
            data=updated_csv,
            file_name="updated_tracking_info.csv",
            mime="text/csv",
        )