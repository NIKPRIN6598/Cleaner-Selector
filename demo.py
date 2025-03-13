import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- TITLE & LOGO ---
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown("<h1 style='text-align: center;'>AMC eSelector</h1>", unsafe_allow_html=True)
with col3:
    st.image("henkel_logo.png", width=200)

# Load data
file_path = "cleaners.xlsx"
df = pd.read_excel(file_path)

# Convert columns to correct types
df["Conc."] = pd.to_numeric(df["Conc."], errors="coerce")
df["Temp min"] = pd.to_numeric(df["Temp min"], errors="coerce")
df["Temp max"] = pd.to_numeric(df["Temp max"], errors="coerce")

# Custom CSS for red "Clear Filters" button
st.markdown("""
    <style>
        div.stButton > button {
            background-color: red !important;
            color: white !important;
            border-radius: 5px;
            border: none;
            padding: 8px 16px;
            font-size: 16px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for filters
if "filters" not in st.session_state:
    st.session_state.filters = {
        "region": [],
        "pH": [],
        "application": [],
        "form": [],
        "condition": [],
        "etching_rate": [],
        "contains_surfactants": [],
        "concentration": (int(df["Conc."].min()), int(df["Conc."].max())),
        "temp_min": (int(df["Temp min"].min()), int(df["Temp min"].max())),
        "temp_max": (int(df["Temp max"].min()), int(df["Temp max"].max())),
    }

# Sidebar filters - CLEAR BUTTON AT THE TOP
st.sidebar.header("Filter Options")
if st.sidebar.button("Clear Filters"):
    st.session_state.filters = {
        "region": [],
        "pH": [],
        "application": [],
        "form": [],
        "condition": [],
        "etching_rate": [],
        "contains_surfactants": [],
        "concentration": (int(df["Conc."].min()), int(df["Conc."].max())),
        "temp_min": (int(df["Temp min"].min()), int(df["Temp min"].max())),
        "temp_max": (int(df["Temp max"].min()), int(df["Temp max"].max())),
    }
    st.rerun()

# Multiselect widgets
multiselect_fields = [
    ("region", "Select Region", "Country"),
    ("pH", "Select pH", "Kind"),
    ("application", "Select Application", "Application"),
    ("form", "Select Form", "Effect"),
    ("condition", "Select Condition", "Condition"),
    ("etching_rate", "Select Etching Rate", "Etching Rate"),
    ("contains_surfactants", "Contains Surfactants", "contains Surfactants"),
]

for field, label, column in multiselect_fields:
    # Define selected_options inside the loop
    selected_options = st.sidebar.multiselect(
        label,
        options=df[column].unique(),
        default=st.session_state.filters[field],
        key=f"multiselect_{field}",
    )
    
    # Check if selected_options differ from the session state
    if selected_options != st.session_state.filters[field]:
        # Update session state
        st.session_state.filters[field] = selected_options
        # Force a rerun to close the dropdown
        st.rerun()
# Slider widgets
st.session_state.filters["concentration"] = st.sidebar.slider(
    "Select Concentration",
    min_value=int(df["Conc."].min()),
    max_value=int(df["Conc."].max()),
    value=st.session_state.filters["concentration"],
)
st.session_state.filters["temp_min"] = st.sidebar.slider(
    "Select Temp Min",
    min_value=int(df["Temp min"].min()),
    max_value=int(df["Temp min"].max()),
    value=st.session_state.filters["temp_min"],
)
st.session_state.filters["temp_max"] = st.sidebar.slider(
    "Select Temp Max",
    min_value=int(df["Temp max"].min()),
    max_value=int(df["Temp max"].max()),
    value=st.session_state.filters["temp_max"],
)

# Filtering logic
filtered_df = df.copy()
criteria_applied = False

for field, _, column in multiselect_fields:
    if st.session_state.filters[field]:
        filtered_df = filtered_df[filtered_df[column].isin(st.session_state.filters[field])]
        criteria_applied = True

if criteria_applied:
    filtered_df = filtered_df[
        (filtered_df["Conc."] >= st.session_state.filters["concentration"][0]) &
        (filtered_df["Conc."] <= st.session_state.filters["concentration"][1])
    ]
    filtered_df = filtered_df[
        (filtered_df["Temp min"] >= st.session_state.filters["temp_min"][0]) &
        (filtered_df["Temp min"] <= st.session_state.filters["temp_min"][1])
    ]
    filtered_df = filtered_df[
        (filtered_df["Temp max"] >= st.session_state.filters["temp_max"][0]) &
        (filtered_df["Temp max"] <= st.session_state.filters["temp_max"][1])
    ]

if not criteria_applied:
    filtered_df = df.copy()

# Reset index to start from 1
filtered_df.index = range(1, len(filtered_df) + 1)
# Display all cleaners
st.dataframe(filtered_df, use_container_width=True, height=700)

# Export buttons
st.markdown("**Download Results**")

# CSV Download
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(label="Download as CSV", data=csv, file_name="filtered_results.csv", mime="text/csv")

## Image Download
if not filtered_df.empty:  # Only generate image if there are results
    fig, ax = plt.subplots(figsize=(14, 8))  # Increase figure size
    ax.axis("tight")
    ax.axis("off")

    table = ax.table(
        cellText=filtered_df.values,
        colLabels=filtered_df.columns,
        cellLoc="center",
        loc="center",
        colWidths=[0.2] + [0.1] * (len(filtered_df.columns) - 1) # Adjust column widths
    )

    table.auto_set_font_size(False)  # Disable auto font size adjustment
    table.set_fontsize(12)  # Increase font size

    # Adjust row height
    for (row, col), cell in table.get_celld().items():
        if row > 0:
            cell.set_height(0.05)  # Adjust row height

    # Adjust column header height
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_height(0.08)  # Adjust header row height

    # Increase resolution (dpi)
    plt.savefig("filtered_results.png", dpi=300, bbox_inches='tight')

    with open("filtered_results.png", "rb") as img_file:
        st.download_button(label="Download as Image", data=img_file, file_name="filtered_results.png", mime="image/png")