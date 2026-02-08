import streamlit as st
import pandas as pd
import numpy as np
import os
import pytz
from datetime import datetime
import time

# Utility Functions
def list_excel_csv_files(folder):
    return [f for f in os.listdir(folder) if f.endswith(('.xlsx', '.xls', '.csv'))]

def load_file(filepath):
    if filepath.endswith('.csv'):
        return pd.read_csv(filepath)
    else:
        return pd.read_excel(filepath)

def convert_timestamp_column(df, column, from_tz, to_tz):
    df[column] = df[column].astype(str).str[:24]  # Trim first 24 characters
    df[column] = pd.to_datetime(df[column], errors='coerce')
    df[column] = df[column].dt.tz_localize(from_tz, ambiguous='NaT', nonexistent='NaT')
    df[column] = df[column].dt.tz_convert(to_tz).dt.strftime('%Y-%m-%d %H:%M:%S')
    return df

def add_average_column(df, exclude_column):
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    numeric_cols = [col for col in numeric_cols if col != exclude_column]
    df['row_average'] = df[numeric_cols].mean(axis=1)
    return df

# Streamlit UI
st.title("Angle Information")
st.write("1) This page helps you append all the data downloaded for angle verification of nodes in a single excel file.  \n2) It will assist you to convert from one time zone to another to maintain consistency across analysis.  \n3) This will also help you to identify the kind of tracking period automatically extracted from angle data ")

# Step 1: Folder input
folder = st.text_input("📁 Enter folder path containing Excel/CSV files:")

if folder and os.path.isdir(folder):
    files = list_excel_csv_files(folder)
    if files:
        first_file = os.path.join(folder, files[0])
        st.subheader(f"📄 Preview of first file: {files[0]}")
        df_preview = load_file(first_file)
        st.dataframe(df_preview.head())

        # Step 2: Select timestamp column
        timestamp_col = st.selectbox("🕓 Select timestamp column:", df_preview.columns)

        # Step 3: Time zone selection
        timezones = pytz.all_timezones
        from_tz = st.selectbox("🌍 From Time Zone:", timezones)
        to_tz = st.selectbox("🌎 To Time Zone:", timezones)

        # Step 4: Preview conversion
        if st.button("🔄 Convert and Preview"):
            df_converted = convert_timestamp_column(df_preview.copy(), timestamp_col, from_tz, to_tz)
            df_converted = add_average_column(df_converted, timestamp_col)
            st.subheader("✅ Converted Preview with Row Averages")
            st.dataframe(df_converted.head())

        # Step 5: Apply to all and merge
        if st.button("📦 Apply to All and Merge"):
            merged_df = pd.DataFrame()
            for file in files:
                path = os.path.join(folder, file)
                df = load_file(path)
                if timestamp_col in df.columns:
                    df = convert_timestamp_column(df, timestamp_col, from_tz, to_tz)
                    df = add_average_column(df, timestamp_col)
                merged_df = pd.concat([merged_df, df], ignore_index=True)

            merged_df.drop_duplicates(inplace=True)
            st.session_state.merged_df = merged_df  # ✅ Save to session state

            st.subheader("📊 Merged Data with Row Averages")
            st.dataframe(merged_df.head())

        # Step 6: Save merged file (triggered after merge)
        if "merged_df" in st.session_state and not st.session_state.merged_df.empty:
            st.subheader("💾 Save Merged File")

            file_format = st.radio("Select file format:", ["CSV", "Excel (.xlsx)"], horizontal=True)
            filename = st.text_input("📝 Enter filename (without extension):")

            if st.button("📥 Save File"):
                if filename:
                    if file_format == "CSV":
                        filename += ".csv"
                    else:
                        filename += ".xlsx"

                    full_path = os.path.join(os.getcwd(), filename)

                    with st.spinner("Generating file..."):
                        time.sleep(1)
                        if file_format == "CSV":
                            st.session_state.merged_df.to_csv(full_path, index=False)
                        else:
                            st.session_state.merged_df.to_excel(full_path, index=False)

                        progress_bar = st.progress(0)
                        for i in range(1, 101, 10):
                            progress_bar.progress(i / 100)
                            time.sleep(0.1)

                    st.success(f"✅ File saved to: {full_path}")
                else:
                    st.warning("Please enter a filename before saving.")
            # Step 7: Group by extracted time string and show median of row_average
            if "merged_df" in st.session_state and not st.session_state.merged_df.empty:
                st.subheader("⏱️ Median Row Average by Extracted Time")

                time_df = st.session_state.merged_df.copy()

                # Extract time portion from timestamp string (assumes format includes time)
                time_df['time_only'] = time_df[timestamp_col].astype(str).str.extract(r'(\d{2}:\d{2}:\d{2})')

                # Drop rows where time extraction failed
                time_df = time_df.dropna(subset=['time_only'])

                # Group by extracted time and calculate median of row_average
                mode_by_time = time_df.groupby('time_only')['row_average'].median().reset_index() 
                mode_by_time.rename(columns={'row_average': 'mode_row_average'}, inplace=True)



                st.dataframe(mode_by_time)
                # Step 8: Display top 2 min and max absolute values with timestamps

                # Add a column for absolute values
                mode_by_time['abs_mode_row_average'] = mode_by_time['mode_row_average']

                # Get top 2 minimum absolute values
                top_2_min = mode_by_time.nsmallest(1, 'abs_mode_row_average')[['time_only', 'mode_row_average']]

                # Get top 2 maximum absolute values
                top_2_max = mode_by_time.nlargest(1, 'abs_mode_row_average')[['time_only', 'mode_row_average']]

                # Display results in Streamlit
                #st.subheader("📉 Top 2 Minimum Absolute Mode Row Averages")
                #for i, row in top_2_min.iterrows():
                #    st.write(f"Time: {row['time_only']}, Value: {row['mode_row_average']}")

                #st.subheader("📈 Top 2 Maximum Absolute Mode Row Averages")
                #for i, row in top_2_max.iterrows():
                #    st.write(f"Time: {row['time_only']}, Value: {row['mode_row_average']}")
                # Step 9: Find smallest positive value preceding the minimum negative
                min_neg_idx = top_2_min.index[0]  # Index of the minimum negative value
                preceding = mode_by_time.iloc[:min_neg_idx]  # Slice before that index
                positives = preceding[preceding['mode_row_average'] >= 0]

                if not positives.empty:
                    min_pos_idx = positives['mode_row_average'].idxmin()
                    min_pos_row_1 = mode_by_time.loc[min_pos_idx]

                    #st.subheader("🟢 Smallest Positive Value Preceding Min Negative")
                    #st.write(f"Time: {min_pos_row_1['time_only']}, Value: {min_pos_row_1['mode_row_average']}")
                else:
                    st.warning("No positive values found preceding the minimum negative value.")
                # Step 10: Find smallest positive value succeeding the maximum positive
                max_pos_idx = top_2_max.index[0]  # Index of the maximum positive value
                succeeding = mode_by_time.iloc[max_pos_idx + 1:]  # Slice after that index
                positives = succeeding[succeeding['mode_row_average'] >= 0]

                if not positives.empty:
                    min_pos_idx = positives['mode_row_average'].idxmin()
                    min_pos_row_2 = mode_by_time.loc[min_pos_idx]

                    st.subheader("🟢 Smallest Positive Value Succeeding Max Positive")
                    st.write(f"Time: {min_pos_row_2['time_only']}, Value: {min_pos_row_2['mode_row_average']}")
                else:
                    st.warning("No positive values found after the maximum positive value.")
                # Step 11: Add Conditional Column Based on Time Range
                # Ensure both reference times are available
                has_min_pos_1 = 'min_pos_row_1' in locals() and not top_2_min.empty
                has_min_pos_2 = 'min_pos_row_2' in locals() and not top_2_max.empty

                if has_min_pos_1 and has_min_pos_2: 
                    end_time = min_pos_row_2['time_only']
                    start_time = top_2_max.iloc[0]['time_only']
                    start_time_mor = min_pos_row_1['time_only']
                    end_time_mor = top_2_min.iloc[0]['time_only']
                    # Convert time strings to datetime.time for comparison
                    mode_by_time['time_obj'] = pd.to_datetime(mode_by_time['time_only'], format='%H:%M:%S').dt.time
                    start_time_obj = pd.to_datetime(start_time, format='%H:%M:%S').time()
                    end_time_obj = pd.to_datetime(end_time, format='%H:%M:%S').time()
                    start_time_mor_obj = pd.to_datetime(start_time_mor, format='%H:%M:%S').time()
                    end_time_mor_obj = pd.to_datetime(end_time_mor, format='%H:%M:%S').time()

                    # Apply condition
                    mode_by_time['Tracking'] = mode_by_time['time_obj'].apply(
                        lambda t: 'EB' if start_time_obj <= t <= end_time_obj
                        else 'MB' if start_time_mor_obj <= t <= end_time_mor_obj
                        else 'TT' if end_time_mor_obj < t < start_time_obj
                        else 'None' )
                    

                    # Preview result
                    st.subheader("🧪 Preview of Time-Based Status Classification")
                    st.dataframe(mode_by_time[['time_only', 'mode_row_average', 'Tracking']])
                else:
                    st.warning("Could not compute conditional status due to missing reference times.")
                # Step 12: Save merged file (triggered after merge)
                st.session_state.mode_by_time = mode_by_time

                if "mode_by_time" in st.session_state and not st.session_state.mode_by_time.empty:
                    st.subheader("💾 Save  Tracking info File")

                    file_format_info = st.radio("Select file format:", ["CSV", "Excel (.xlsx)"], horizontal=True,key="angle_info")
                    filename_info = st.text_input("📝 Enter filename (without extension):",key="angle_info_file")
                    
                    mode_by_time_save = mode_by_time[['time_only','Tracking']]
                    st.session_state.mode_by_time_save = mode_by_time_save
                    
                    if st.button("📥 Save Tracking Info File"):
                        if filename_info:
                            if file_format_info == "CSV":
                                filename_info += ".csv"
                            else:
                                filename_info += ".xlsx"

                            full_path = os.path.join(os.getcwd(), filename_info)

                            with st.spinner("Generating file..."):
                                time.sleep(1)
                                if file_format_info == "CSV":
                                    st.session_state.mode_by_time_save.to_csv(full_path, index=False)
                                else:
                                    st.session_state.mode_by_time_save.to_excel(full_path, index=False)

                                progress_bar = st.progress(0)
                                for i in range(1, 101, 10):
                                    progress_bar.progress(i / 100)
                                    time.sleep(0.1)

                            st.success(f"✅ File saved to: {full_path}")
                        else:
                            st.warning("Please enter a filename before saving.")



