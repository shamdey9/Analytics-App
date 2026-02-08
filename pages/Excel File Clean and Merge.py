import streamlit as st
import pandas as pd
from pathlib import Path

st.title("📁 Excel Preprocessor & Merger")
st.write("Getting Data from client with unnecessary headers? Multiple excel files? Clean and Combine these excel files into one excel file.")
# ✅ Cache Excel reading
@st.cache_data
def read_excel_file(path):
    return pd.read_excel(path, header=None)

# ✅ Step 1: Accept folder path
folder_path = st.text_input("1️⃣ Enter folder path containing Excel files")

if folder_path:
    folder = Path(folder_path)
    excel_files = list(folder.glob("*.xlsx"))

    if not excel_files:
        st.warning("No Excel files found in this folder.")
    else:
        st.success(f"Found {len(excel_files)} Excel files.")

        try:
            # ✅ Step 2: Preview first file (cached)
            raw_df = read_excel_file(excel_files[0])
            st.subheader(f"2️⃣ Raw Preview (no headers): {excel_files[0].name}")
            st.dataframe(raw_df.head(100))  # Limit preview

            # ✅ Step 3: Skip rows
            skiprows = st.number_input(
                "3️⃣ Number of top rows to skip before header merging",
                min_value=0,
                max_value=len(raw_df) - 1,
                value=0
            )

            skipped_df = raw_df.iloc[skiprows:].reset_index(drop=True)
            st.subheader(f"4️⃣ Preview after skipping {skiprows} rows")
            st.dataframe(skipped_df.head(100))  # Limit preview

            # ✅ Step 4: Merge header rows
            merge_header_rows = st.number_input(
                "5️⃣ Number of top rows to merge as header",
                min_value=1,
                max_value=len(skipped_df),
                value=2
            )

            header_rows = skipped_df.iloc[:merge_header_rows].fillna("").astype(str)
            merged_header = header_rows.apply(lambda col: "_".join(col), axis=0).tolist()

            clean_df = skipped_df.iloc[merge_header_rows:].reset_index(drop=True)
            clean_df.columns = merged_header[:len(clean_df.columns)]
            clean_df.columns = [col.lstrip("_") for col in clean_df.columns]
            st.subheader("6️⃣ Cleaned Preview with Merged Header")
            st.dataframe(clean_df.head(100))  # Limit preview

            # ✅ Step 5: Column selection
            selected_columns = st.multiselect("7️⃣ Select columns to keep", clean_df.columns.tolist())
            filtered_df = clean_df[selected_columns] if selected_columns else clean_df
            st.subheader("8️⃣ Preview with Selected Columns")
            st.dataframe(filtered_df.head(100))  # Limit preview

            # ✅ Step 6: Output file name
            output_name = st.text_input("🔖 Enter name for merged Excel file (e.g., merged.xlsx)")

            # ✅ Step 7: Merge and Save
            if st.button("🚀 Merge and Save"):
                if not output_name:
                    st.error("❌ Please enter a valid file name before merging.")
                else:
                    progress = st.progress(0, text="Starting merge process…")
                    merged_df = pd.DataFrame()

                    for i, file in enumerate(excel_files):
                        try:
                            df_raw = read_excel_file(file)
                            df_skipped = df_raw.iloc[skiprows:].reset_index(drop=True)

                            if i == 0:
                                header_rows = df_skipped.iloc[:merge_header_rows].fillna("").astype(str)
                                merged_header = header_rows.apply(lambda col: "_".join(col), axis=0).tolist()

                            df_clean = df_skipped.iloc[merge_header_rows:].reset_index(drop=True)
                            df_clean.columns = merged_header[:len(df_clean.columns)]

                            if selected_columns:
                                df_clean = df_clean[selected_columns]

                            merged_df = pd.concat([merged_df, df_clean], ignore_index=True)
                        except Exception as e:
                            st.error(f"Error processing {file.name}: {e}")

                        progress.progress((i + 1) / len(excel_files), text=f"Merging file {i + 1} of {len(excel_files)}…")

                    merged_df.drop_duplicates(inplace=True)
                    st.toast(f"🔄 Removed duplicates. Final row count: {len(merged_df)}")

                    try:
                        output_path = folder / output_name
                        merged_df.to_excel(output_path, index=False)
                        st.success(f"✅ File saved successfully as: {output_path}")
                    except Exception as e:
                        st.error(f"❌ Failed to save file: {e}")

        except Exception as e:
            st.error(f"Error previewing file: {e}")