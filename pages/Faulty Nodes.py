import streamlit as st
import pandas as pd
import numpy as np
from utils import hide_streamlit_style

hide_streamlit_style()

st.title("📊Faulty Node Identfier")
st.write("Identfy faulty Nodes and the difference observed for the timeline of data")


# Upload matrices
matrix1_file = st.file_uploader("Upload Matrix 1 (CSV or Excel)", type=["csv", "xlsx", "xls"])
matrix2_file = st.file_uploader("Upload Matrix 2 (CSV or Excel)", type=["csv", "xlsx", "xls"])
ellio_file = st.file_uploader("Upload Angle info File (CSV or Excel)", type=["csv", "xlsx", "xls"])

@st.cache_data
def read_file(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    elif file.name.endswith(('.xlsx', '.xls')):
        return pd.read_excel(file)
    return None

if matrix1_file and matrix2_file:
    with st.spinner("Reading and processing matrix files..."):
        df1 = read_file(matrix1_file)
        df2 = read_file(matrix2_file)

        if df1 is None or df2 is None:
            st.error("Unsupported file format.")
        elif df1.shape != df2.shape:
            st.error("Matrices must have the same shape.")
        else:
            st.success("Matrix files uploaded and read successfully!")

            # Detect timestamp column
            timestamp_col = next((col for col in df1.columns if 'time' in col.lower()), None)

            # Select comparison columns
            comp_cols = [col for col in df1.columns if col != timestamp_col]
            df1_comp = df1[comp_cols]
            df2_comp = df2[comp_cols]

            # Compute difference matrix using NumPy
            diff_matrix = df1_comp.values - df2_comp.values
            mask = np.where((diff_matrix < -5) | (diff_matrix > 5), 1, 0)

            # Build result list
            result = []
            rows, cols = np.where(mask == 1)
            for r, c in zip(rows, cols):
                result.append({
                    'Timestamp': df1[timestamp_col].iloc[r] if timestamp_col else None,
                    'Column': comp_cols[c],
                    'Difference': diff_matrix[r, c]
                })

            result_df = pd.DataFrame(result)

            # Merge with Ellio file if uploaded
            if ellio_file:
                with st.spinner("Reading and merging Info file..."):
                    ellio_df = read_file(ellio_file)
                    ellio_time_col = next((col for col in ellio_df.columns if 'time_only' in col.lower()), None)
                    info_col = next((col for col in ellio_df.columns if col != ellio_time_col), None)

                    if ellio_time_col and info_col:
                        # Extract time-only from both sources for matching
                        result_df['MatchTime'] = pd.to_datetime(result_df['Timestamp']).dt.time
                        ellio_df['MatchTime'] = pd.to_datetime(ellio_df[ellio_time_col]).dt.time

                        # Merge on time-only column
                        merged_df = pd.merge(result_df, ellio_df[['MatchTime', info_col]],
                                            on='MatchTime', how='left')

                        # Drop helper column used for matching
                        merged_df.drop(columns=['MatchTime'], inplace=True)
                        merged_df[['Node', 'Master']] = merged_df['Column'].str.extract(r'^(.*?)\s*\((.*?)\)$')
                        merged_df['Time'] = pd.to_datetime(merged_df['Timestamp']).dt.time
                        merged_df['Date'] = pd.to_datetime(merged_df['Timestamp']).dt.date


                        merged_df = merged_df[merged_df[info_col].notna()].reset_index(drop=True)


                        # Full timestamp is preserved in 'Timestamp'
                        result_df = merged_df
                        
                        st.success("Ellio data merged successfully!")
                    else:
                        st.warning("Ellio file must contain a timestamp column and one info column.")

            # Display results
            st.subheader("📋 Significant Differences (Outside [-5, 5])")
            st.dataframe(result_df)

            # Download button
            st.download_button(
                label="Download Result as CSV",
                data=result_df.to_csv(index=False),
                file_name="differences_with_info.csv",
                mime="text/csv"
            )
            st.subheader("🔍 Explore Unique Values with One Filter")

            # Step 1: Select one column to filter and analyze
            columns = result_df.columns.tolist()
            selected_column = st.selectbox("Select a column to filter and view unique values", columns)

            # Step 2: Filter by selected column
            unique_values = result_df[selected_column].unique().tolist()
            selected_values = st.multiselect(f"Filter {selected_column}", unique_values)

            # Apply filter
            filtered_df = result_df[result_df[selected_column].isin(selected_values)] if selected_values else result_df

            # Step 3: Show unique value counts for the selected column
            if not filtered_df.empty:
                value_counts = (
                    filtered_df[selected_column]
                    .value_counts(dropna=True)
                    .reset_index()
                    .rename(columns={
                        'index': f"Unique values in '{selected_column}'",
                        selected_column: "Count"
                    })
                )

                st.markdown(f"**Unique value counts for `{selected_column}` after filtering:**")
                st.dataframe(value_counts, use_container_width=True)
                st.write(f"Unique row count: {filtered_df.drop_duplicates().shape[0]}")
            else:
                st.warning("No data matches the selected filter.")