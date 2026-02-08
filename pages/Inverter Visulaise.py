import streamlit as st
import pandas as pd
import plotly.express as px
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

hide_streamlit_style = """
    <style>
    /* Hide the GitHub and Fork icons in the Streamlit Cloud header */
    .stAppHeader .stToolbar > div:nth-child(2) {
        display: none !important;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


st.title("Excel Invereter Generation-Sheet Merger & Interactive Plot")
st.write("Visualise multiple inverter data")
@st.cache_data
def load_excel(uploaded_file):
    return pd.read_excel(uploaded_file, sheet_name=None)

@st.cache_data
def merge_sheets(all_sheets, merge_col):
    renamed_sheets = {}
    for sheet_name, df in all_sheets.items():
        prefix = sheet_name[:3]
        new_cols = []
        for col in df.columns:
            if col != merge_col:
                new_cols.append(f"{prefix}_{col}")
            else:
                new_cols.append(col)
        df = df.rename(columns=dict(zip(df.columns, new_cols)))
        renamed_sheets[sheet_name] = df

    merged_df = None
    for df in renamed_sheets.values():
        if merged_df is None:
            merged_df = df
        else:
            merged_df = pd.merge(merged_df, df, on=merge_col, how="outer")

    # Handle timestamp column
    timestamp_cols = [col for col in merged_df.columns if "time" in col.lower() or "stamp" in col.lower() or "date" in col.lower()]
    if len(timestamp_cols) > 1:
        keep = timestamp_cols[0]
        drop_cols = timestamp_cols[1:]
        merged_df = merged_df.drop(columns=drop_cols)
        merged_df = merged_df.rename(columns={keep: "Timestamp"})
    elif len(timestamp_cols) == 1:
        merged_df = merged_df.rename(columns={timestamp_cols[0]: "Timestamp"})
    else:
        raise ValueError("No timestamp column found!")

    merged_df["Timestamp"] = pd.to_datetime(merged_df["Timestamp"], errors="coerce")
    merged_df["Date"] = merged_df["Timestamp"].dt.date
    merged_df["Time"] = merged_df["Timestamp"].dt.time
    merged_df["Hour"] = merged_df["Timestamp"].dt.hour
    merged_df["Minute"] = merged_df["Timestamp"].dt.minute

    return merged_df

uploaded_file = st.file_uploader("Upload Excel file with multiple sheets", type=["xls", "xlsx"])

if uploaded_file:
    all_sheets = load_excel(uploaded_file)
    st.write(f"Sheets found: {list(all_sheets.keys())}")

    sample_df = list(all_sheets.values())[0]
    merge_col = st.selectbox("Select column to merge on", options=sample_df.columns)

    merged_df = merge_sheets(all_sheets, merge_col)

    st.subheader("Merged Data Preview")
    st.dataframe(merged_df.head())

    # ✅ Block prefix filter (exclude Timestamp/Irradiance)
    block_prefixes = sorted(set([col[:3] for col in merged_df.columns
                                 if not col.lower().startswith("timestamp")
                                 and not col.lower().startswith("irradiance") and not col.lower().startswith("date") and not col.lower().startswith("time") and not col.lower().startswith("hour") and not col.lower().startswith("minute")]))
    block_choice = st.selectbox("Select block prefix (first 3 letters)", options=block_prefixes)

    # ✅ First text box → dotted line columns
    dotted_input = st.text_area("Paste column names for Delayed Inverters")
    dotted_cols = []
    if dotted_input:
        col_list = [c.strip() for c in dotted_input.splitlines() if c.strip()]
        for c in col_list:
            matches = [col for col in merged_df.columns
                       if c.lower() in col.lower() and col.startswith(block_choice)]
            dotted_cols.extend(matches)
        dotted_cols = list(dict.fromkeys(dotted_cols))

    # ✅ Second text box → solid line columns
    solid_input = st.text_area("Paste column names for Reference Inverters")
    solid_cols = []
    if solid_input:
        col_list = [c.strip() for c in solid_input.splitlines() if c.strip()]
        for c in col_list:
            matches = [col for col in merged_df.columns
                       if c.lower() in col.lower() and col.startswith(block_choice)]
            solid_cols.extend(matches)
        solid_cols = list(dict.fromkeys(solid_cols))

    st.write("Delay line columns:", dotted_cols)
    st.write("Reference line columns:", solid_cols)

    width = st.slider("Figure width", min_value=600, max_value=1600, value=900, step=100)
    height = st.slider("Figure height", min_value=400, max_value=1000, value=600, step=100)

    if dotted_cols or solid_cols:
        plot_df = merged_df.melt(
            id_vars=["Timestamp"],
            value_vars=solid_cols + dotted_cols,
            var_name="Series",
            value_name="Value"
        )

        # ✅ Use valid Plotly dash names
        plot_df["LineStyle"] = plot_df["Series"].apply(
            lambda s: "dot" if s in dotted_cols else "solid"
        )

        fig = px.line(
            plot_df,
            x="Timestamp",
            y="Value",
            color="Series",
            line_dash="LineStyle",  # Plotly interprets "dot" and "solid"
            hover_data={"Timestamp": True, "Value": True, "Series": True, "LineStyle": True}
        )
        for trace in fig.data:
                # Legend labels look like "ColumnName, solid" or "ColumnName, dot"
                parts = trace.name.split(",")
                if len(parts) == 2:
                    col_name, style = parts[0], parts[1].strip()
                    if style == "solid":
                        trace.name = f"{col_name} (Reference)"
                    elif style == "dot":
                        trace.name = f"{col_name} (Delayed)"
                    else:
                        trace.name = col_name  # fallback
                else:
                    trace.name = trace.name


        fig.update_layout(
            width=width,
            height=height,
            legend=dict(orientation="v", x=1.02, y=1,title=dict(text="Series")),
            dragmode="zoom"
        )

        st.plotly_chart(fig, use_container_width=True)