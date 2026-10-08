import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Cricket Player Performance Dashboard",
    page_icon="🏏",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
    .main {
        padding-top: 1rem;
    }

    .dashboard-title {
        font-size: 38px;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .dashboard-subtitle {
        font-size: 17px;
        margin-bottom: 25px;
    }

    div[data-testid="stMetric"] {
        border: 1px solid #dddddd;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# ============================================================
# BACKGROUND IMAGE
# ============================================================

def set_background(image_file):
    with open(image_file, "rb") as image:
        encoded_image = base64.b64encode(image.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image:
                linear-gradient(
                    rgba(0, 0, 0, 0.65),
                    rgba(0, 0, 0, 0.65)
                ),
                url("data:image/jpeg;base64,{encoded_image}");

            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        [data-testid="stSidebar"] {{
            background-color: rgba(0, 0, 0, 0.75);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


set_background("background.jpg")


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="dashboard-title">🏏 Cricket Player Performance Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dashboard-subtitle">'
    "Performance evaluation and format trends across ODI, T20 and Test cricket"
    "</div>",
    unsafe_allow_html=True
)


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_data():

    odi = pd.read_csv("odb.csv")
    t20 = pd.read_csv("tb.csv")
    test = pd.read_csv("twb.csv")

    # Remove unnecessary index column
    for data in [odi, t20, test]:
        if "Unnamed: 0" in data.columns:
            data.drop(columns=["Unnamed: 0"], inplace=True)

    # --------------------------------------------------------
    # Clean Matches column
    # --------------------------------------------------------

    odi["Mat"] = pd.to_numeric(odi["Mat"], errors="coerce")
    test["Mat"] = pd.to_numeric(test["Mat"], errors="coerce")

    # T20 Mat contains * for some players
    t20["Mat"] = (
        t20["Mat"]
        .astype(str)
        .str.replace("*", "", regex=False)
        .astype(int)
    )

    # --------------------------------------------------------
    # Clean Highest Score
    # --------------------------------------------------------

    odi["HS_numeric"] = (
        odi["HS"]
        .astype(str)
        .str.replace("*", "", regex=False)
        .astype(int)
    )

    t20["HS_numeric"] = (
        t20["HS"]
        .astype(str)
        .str.replace("*", "", regex=False)
        .astype(int)
    )

    test["HS_numeric"] = (
        test["HS"]
        .astype(str)
        .str.replace("*", "", regex=False)
        .astype(int)
    )

    # --------------------------------------------------------
    # Select common columns
    # --------------------------------------------------------

    odi_analysis = odi[
        [
            "Player",
            "Span",
            "Mat",
            "Inns",
            "NO",
            "Runs",
            "HS_numeric",
            "Ave",
            "BF",
            "SR"
        ]
    ].copy()

    t20_analysis = t20[
        [
            "Player",
            "Span",
            "Mat",
            "Inns",
            "NO",
            "Runs",
            "HS_numeric",
            "Ave"
        ]
    ].copy()

    test_analysis = test[
        [
            "Player",
            "Span",
            "Mat",
            "Inns",
            "NO",
            "Runs",
            "HS_numeric",
            "Ave",
            "BF",
            "SR"
        ]
    ].copy()

    # Add missing columns to T20
    t20_analysis["BF"] = pd.NA
    t20_analysis["SR"] = pd.NA

    # Add format
    odi_analysis["Format"] = "ODI"
    t20_analysis["Format"] = "T20"
    test_analysis["Format"] = "Test"

    # Combine
    df = pd.concat(
        [odi_analysis, t20_analysis, test_analysis],
        ignore_index=True
    )

    return df


# Load data
df = load_data()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🎛️ Dashboard Filters")

format_options = ["All", "ODI", "T20", "Test"]

selected_format = st.sidebar.selectbox(
    "Select Format",
    format_options
)

player_search = st.sidebar.text_input(
    "Search Player",
    placeholder="Enter player name..."
)

min_matches = st.sidebar.slider(
    "Minimum Matches",
    min_value=0,
    max_value=int(df["Mat"].max()),
    value=0
)

top_n = st.sidebar.slider(
    "Top N Players",
    min_value=5,
    max_value=20,
    value=10
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df.copy()

if selected_format != "All":
    filtered_df = filtered_df[
        filtered_df["Format"] == selected_format
    ]

if player_search:
    filtered_df = filtered_df[
        filtered_df["Player"]
        .str.contains(player_search, case=False, na=False)
    ]

filtered_df = filtered_df[
    filtered_df["Mat"] >= min_matches
]


# ============================================================
# KPI SECTION
# ============================================================

st.subheader("📌 Performance Overview")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_players = len(filtered_df)
total_runs = filtered_df["Runs"].sum()
average_runs = filtered_df["Runs"].mean()
average_average = filtered_df["Ave"].mean()

with kpi1:
    st.metric(
        "Players",
        f"{total_players:,}"
    )

with kpi2:
    st.metric(
        "Total Runs",
        f"{total_runs:,.0f}"
    )

with kpi3:
    st.metric(
        "Average Runs",
        f"{average_runs:,.2f}" if pd.notna(average_runs) else "N/A"
    )

with kpi4:
    st.metric(
        "Average Batting Average",
        f"{average_average:.2f}"
        if pd.notna(average_average)
        else "N/A"
    )


st.divider()


# ============================================================
# FORMAT COMPARISON
# ============================================================

st.subheader("📊 Format Performance Comparison")

format_summary = (
    filtered_df
    .groupby("Format")
    .agg(
        Average_Runs=("Runs", "mean"),
        Average_Batting_Average=("Ave", "mean"),
        Average_Highest_Score=("HS_numeric", "mean")
    )
    .reset_index()
)


col1, col2 = st.columns(2)


# ------------------------------------------------------------
# Average Runs
# ------------------------------------------------------------

with col1:

    fig, ax = plt.subplots(figsize=(7, 5))

    ax.bar(
        format_summary["Format"],
        format_summary["Average_Runs"]
    )

    ax.set_xlabel("Format")
    ax.set_ylabel("Average Runs")
    ax.set_title("Average Runs by Format")

    st.pyplot(fig)


# ------------------------------------------------------------
# Batting Average
# ------------------------------------------------------------

with col2:

    fig, ax = plt.subplots(figsize=(7, 5))

    ax.bar(
        format_summary["Format"],
        format_summary["Average_Batting_Average"]
    )

    ax.set_xlabel("Format")
    ax.set_ylabel("Average Batting Average")
    ax.set_title("Average Batting Average by Format")

    st.pyplot(fig)


col3, col4 = st.columns(2)


# ------------------------------------------------------------
# Highest Score
# ------------------------------------------------------------

with col3:

    fig, ax = plt.subplots(figsize=(7, 5))

    ax.bar(
        format_summary["Format"],
        format_summary["Average_Highest_Score"]
    )

    ax.set_xlabel("Format")
    ax.set_ylabel("Average Highest Score")
    ax.set_title("Average Highest Score by Format")

    st.pyplot(fig)


# ------------------------------------------------------------
# Player Distribution
# ------------------------------------------------------------

with col4:

    player_counts = filtered_df["Format"].value_counts()

    fig, ax = plt.subplots(figsize=(7, 5))

    ax.bar(
        player_counts.index,
        player_counts.values
    )

    ax.set_xlabel("Format")
    ax.set_ylabel("Number of Players")
    ax.set_title("Players by Format")

    st.pyplot(fig)


st.divider()


# ============================================================
# TOP RUN SCORERS
# ============================================================

st.subheader(f"🏆 Top {top_n} Run Scorers")

top_players = (
    filtered_df
    .nlargest(top_n, "Runs")
    .sort_values("Runs", ascending=True)
)


fig, ax = plt.subplots(figsize=(10, 6))

ax.barh(
    top_players["Player"],
    top_players["Runs"]
)

ax.set_xlabel("Runs")
ax.set_ylabel("Player")
ax.set_title(f"Top {top_n} Run Scorers")

st.pyplot(fig)


# ============================================================
# TOP PLAYERS TABLE
# ============================================================

st.subheader("📋 Player Performance Details")

display_columns = [
    "Player",
    "Format",
    "Mat",
    "Inns",
    "Runs",
    "HS_numeric",
    "Ave",
    "BF",
    "SR"
]

display_df = (
    filtered_df[display_columns]
    .sort_values("Runs", ascending=False)
    .head(top_n)
    .copy()
)

display_df.columns = [
    "Player",
    "Format",
    "Matches",
    "Innings",
    "Runs",
    "Highest Score",
    "Batting Average",
    "Balls Faced",
    "Strike Rate"
]

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


st.divider()


# ============================================================
# BALLS FACED ANALYSIS
# ============================================================

st.subheader("🏏 Runs vs Balls Faced")

bf_df = filtered_df.dropna(
    subset=["BF", "Runs"]
).copy()


if bf_df.empty:

    st.info(
        "Balls Faced data is not available for the selected format. "
        "The T20 dataset does not contain a Balls Faced column."
    )

else:

    # Use Top N players for the relationship analysis
    bf_top = bf_df.nlargest(top_n, "Runs")

    fig, ax = plt.subplots(figsize=(9, 6))

    ax.scatter(
        bf_top["BF"],
        bf_top["Runs"]
    )

    ax.set_xlabel("Balls Faced")
    ax.set_ylabel("Runs")
    ax.set_title(
        f"Top {top_n} Players: Runs vs Balls Faced"
    )

    st.pyplot(fig)

    if len(bf_top) >= 2:

        correlation = bf_top["Runs"].corr(
            bf_top["BF"]
        )

        st.metric(
            "Runs vs Balls Faced Correlation",
            f"{correlation:.3f}"
        )

        if correlation >= 0.7:
            st.success(
                "Strong positive relationship: players who faced more "
                "balls generally accumulated more runs in this selected group."
            )

        elif correlation >= 0.4:
            st.info(
                "Moderate positive relationship between balls faced and runs."
            )

        else:
            st.info(
                "Weak relationship between balls faced and runs."
            )


st.divider()


# ============================================================
# STRIKE RATE ANALYSIS
# ============================================================

st.subheader("⚡ Runs vs Strike Rate")

sr_df = filtered_df.dropna(
    subset=["SR", "Runs"]
).copy()


if sr_df.empty:

    st.info(
        "Strike Rate data is not available for the selected format. "
        "The T20 dataset used in this project does not contain Strike Rate."
    )

else:

    sr_top = sr_df.nlargest(top_n, "Runs")

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # Scatter Plot
    # --------------------------------------------------------

    with col1:

        fig, ax = plt.subplots(figsize=(8, 5))

        ax.scatter(
            sr_top["SR"],
            sr_top["Runs"]
        )

        ax.set_xlabel("Strike Rate")
        ax.set_ylabel("Runs")
        ax.set_title(
            f"Top {top_n} Players: Runs vs Strike Rate"
        )

        st.pyplot(fig)

    # --------------------------------------------------------
    # Average Strike Rate
    # --------------------------------------------------------

    with col2:

        avg_sr = (
            sr_top
            .groupby("Format")["SR"]
            .mean()
            .reset_index()
        )

        fig, ax = plt.subplots(figsize=(8, 5))

        ax.bar(
            avg_sr["Format"],
            avg_sr["SR"]
        )

        ax.set_xlabel("Format")
        ax.set_ylabel("Average Strike Rate")
        ax.set_title(
            f"Average Strike Rate of Top {top_n} Players"
        )

        st.pyplot(fig)

    # Correlation
    if len(sr_top) >= 2:

        sr_correlation = sr_top["Runs"].corr(
            sr_top["SR"]
        )

        st.metric(
            "Runs vs Strike Rate Correlation",
            f"{sr_correlation:.3f}"
        )


st.divider()


# ============================================================
# STRIKE RATE TABLE
# ============================================================

st.subheader("⚡ Highest Strike Rates Among Selected Players")

sr_table = filtered_df.dropna(
    subset=["SR"]
).copy()

if sr_table.empty:

    st.info(
        "Strike Rate information is not available for this selection."
    )

else:

    sr_table = (
        sr_table
        .sort_values("SR", ascending=False)
        .head(top_n)
    )

    sr_table = sr_table[
        [
            "Player",
            "Format",
            "Runs",
            "SR",
            "Ave",
            "Mat"
        ]
    ].copy()

    sr_table.columns = [
        "Player",
        "Format",
        "Runs",
        "Strike Rate",
        "Batting Average",
        "Matches"
    ]

    st.dataframe(
        sr_table,
        use_container_width=True,
        hide_index=True
    )


st.divider()


# ============================================================
# DOWNLOAD FILTERED DATA
# ============================================================

st.subheader("⬇️ Download Data")

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Dataset",
    data=csv_data,
    file_name="filtered_cricket_data.csv",
    mime="text/csv"
)


# ============================================================
# PROJECT NOTES
# ============================================================

st.divider()

st.subheader("ℹ️ Project Notes")

st.write(
    """
    **Dataset Coverage:** ODI, T20 and Test cricket.

    **Data Sources Used:**
    - ODI batting statistics: `odb.csv`
    - T20 batting statistics: `tb.csv`
    - Test batting statistics: `twb.csv`

    **Important Limitation:** The T20 dataset does not contain
    Balls Faced (BF) or Strike Rate (SR). Therefore, BF and SR
    analyses are available only for formats where these variables
    exist.

    **Interpretation:** Format-level averages are descriptive
    comparisons of the players represented in each dataset. They
    should not be interpreted as proof that one cricket format is
    inherently easier or harder than another.
    """
)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Cricket Player Performance Evaluation and Format Trends Analysis Using Python"
)
