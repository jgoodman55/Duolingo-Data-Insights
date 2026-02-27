import os
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
import altair as alt
from google.cloud import bigquery
from google.api_core.exceptions import NotFound


# -----------------------------
# App + Clients
# -----------------------------
st.set_page_config(page_title="Duolingo Dashboard", layout="wide")

project_id = os.environ["GCP_PROJECT_ID"]
dataset_mart = os.environ["BQ_DATASET_MART"]

# If you also set BQ_LOCATION (US / EU / us-central1), this will use it.
bq_location = os.getenv("BQ_LOCATION")  # optional
client = bigquery.Client(project=project_id, location=bq_location) if bq_location else bigquery.Client(project=project_id)

ET = ZoneInfo("America/New_York")


def run_query(sql: str) -> pd.DataFrame:
    return client.query(sql).to_dataframe()


def safe_run_query(sql: str) -> tuple[pd.DataFrame | None, str | None]:
    try:
        return run_query(sql), None
    except Exception as e:
        return None, str(e)


def table_exists(project_id: str, dataset_id: str, table_id: str) -> bool:
    try:
        client.get_table(f"{project_id}.{dataset_id}.{table_id}")
        return True
    except NotFound:
        return False


def get_table_last_modified(project_id: str, dataset_id: str, table_id: str):
    table = client.get_table(f"{project_id}.{dataset_id}.{table_id}")
    return table.modified  # UTC datetime


# -----------------------------
# Header + Preflight Checks
# -----------------------------
st.title("Duolingo Spaced Repetition Data Exploration for Native English Speakers")
required_tables = [
    "fct_user_learning_language",
    # Add your time-series mart here if/when you have it, e.g.:
    # "fct_practices_daily",
]

missing = [t for t in required_tables if not table_exists(project_id, dataset_mart, t)]
if missing:
    st.warning(
        "No dashboard data yet. Run your Kestra flow to create/build the mart tables.\n\n"
        f"Missing tables in `{project_id}.{dataset_mart}`:\n- " + "\n- ".join(missing)
    )
    st.stop()

lang_domain_sql = f"""
SELECT learning_language
FROM `{project_id}.{dataset_mart}.fct_user_learning_language`
GROUP BY 1
ORDER BY COUNT(DISTINCT user_id) DESC
"""

lang_df, err = safe_run_query(lang_domain_sql)
if err:
    st.error("Failed to load language domain.")
    st.code(err)
else:
    LANG_DOMAIN = lang_df["learning_language"].tolist()
    color_scale = alt.Scale(domain=LANG_DOMAIN, scheme="category10")    

# Last updated (ET) from one “source of truth” mart table
last_updated_utc = get_table_last_modified(project_id, dataset_mart, "fct_user_learning_language")
st.caption(f"Last updated (ET): {last_updated_utc.astimezone(ET):%Y-%m-%d %I:%M %p %Z}")

# -----------------------------
# Tile 1: % of total + counts in tooltip
# -----------------------------
st.subheader("Users by Learning Language")

sql = f"""
SELECT
    learning_language,
    COUNT(DISTINCT user_id) AS users
FROM `{project_id}.{dataset_mart}.fct_user_learning_language`
GROUP BY 1
ORDER BY users DESC
"""

df, err = safe_run_query(sql)
if err:
    st.error("Tile failed to load.")
    st.code(err)
else:
    df["users"] = pd.to_numeric(df["users"], errors="coerce").fillna(0)
    unique_langs = sorted(df["learning_language"].unique())

    total_users = float(df["users"].sum())
    df["total_users"] = total_users
    df["percent_of_total"] = df["users"] / total_users if total_users > 0 else 0.0

    bars = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(
                "learning_language:N",
                sort=alt.SortField(field="users", order="descending"),
                title="Learning Language",
                axis=alt.Axis(labelAngle=-30)  # optional readability
            ),
            y=alt.Y(
                "percent_of_total:Q",
                title="Percent of Total User–Learning Language Pairs",
                axis=alt.Axis(format="%")
            ),
            color=alt.Color("learning_language:N", scale=color_scale, legend=None),
            tooltip=[
                alt.Tooltip("learning_language:N", title="Language"),
                alt.Tooltip("percent_of_total:Q", title="Percent of Total", format=".2%"),
                alt.Tooltip("users:Q", title="Users", format=","),
                alt.Tooltip("total_users:Q", title="Total Pairs", format=","),
            ],
        )
    )

    labels = (
        alt.Chart(df)
        .mark_text(
            dy=-8,                # move above bar
            fontSize=12,
            color="white"         # ensure visible
        )
        .encode(
            x=alt.X(
                "learning_language:N",
                sort=alt.SortField(field="users", order="descending")
            ),
            y=alt.Y("percent_of_total:Q"),
            text=alt.Text("percent_of_total:Q", format=".1%")
        )
    )

    final_bar = (bars + labels).properties(height=350).configure_view(clip=False)
    st.altair_chart(final_bar, use_container_width=True)


# -----------------------------
# Tile 2: Accuracy by Learning Language
# -----------------------------
st.subheader("Accuracy by Learning Language - Sorted by Median Accuracy Desc")
sql = f"""
SELECT
learning_language,
overall_accuracy
FROM `{project_id}.{dataset_mart}.fct_user_learning_language`
WHERE overall_accuracy IS NOT NULL
"""
df, err = safe_run_query(sql)
if err:
    st.error("Tile failed to load.")
    st.code(err)
else:
    df["overall_accuracy"] = pd.to_numeric(df["overall_accuracy"], errors="coerce")
    df = df.dropna(subset=["overall_accuracy"])

    # Sort languages by median accuracy (descending)
    order = (
        df.groupby("learning_language")["overall_accuracy"]
        .median()
        .sort_values(ascending=False)
        .index
        .tolist()
    )

    # 1) Violin layer — no column facet here
    violin = (
        alt.Chart()
        .transform_density(
            density="overall_accuracy",
            as_=["overall_accuracy", "density"],
            extent=[0, 1],
            groupby=["learning_language"],
        )
        .transform_calculate(negative_density="-datum.density")
        .mark_area(orient="horizontal", opacity=1)
        .encode(
            x=alt.X("density:Q", axis = None),
            x2="negative_density:Q", # Mirrors the area across the 0-axis
            y=alt.Y(
                "overall_accuracy:Q",
                title="Accuracy",
                scale=alt.Scale(domain=[0, 1]),
                axis=alt.Axis(format=".0%"),
            ),
            tooltip=[
                alt.Tooltip("learning_language:N", title="Learning Language"),
                alt.Tooltip("overall_accuracy:Q", title="Accuracy", format=".1%")
            ],
            color=alt.Color("learning_language:N", scale=color_scale, legend=None),
        )
    )

    # 2) Median dot — no column facet here either
    median_dot = (
        alt.Chart()
        .transform_aggregate(
            median_acc="median(overall_accuracy)",
            q1_acc="q1(overall_accuracy)",
            q3_acc="q3(overall_accuracy)",
            min_acc="min(overall_accuracy)",
            max_acc="max(overall_accuracy)",
            groupby=["learning_language"],
        )
        .transform_calculate(density="0")  # zero density = center spine
        .mark_point(color="white", filled=True, size=100, stroke="black", strokeWidth=1)
        .encode(
            x=alt.value(125),
            y=alt.Y("median_acc:Q", scale=alt.Scale(domain=[0, 1])),
            tooltip=[
                alt.Tooltip("learning_language:N", title="Learning Language"),
                alt.Tooltip("min_acc:Q", title="Min", format=".1%"),
                alt.Tooltip("q1_acc:Q", title="Q1", format=".1%"),
                alt.Tooltip("median_acc:Q", title="Median", format=".1%"),
                alt.Tooltip("q3_acc:Q", title="Q3", format=".1%"),
                alt.Tooltip("max_acc:Q", title="Max", format=".1%"),
            ],
        )
    )

    # 3) Layer first, THEN facet
    final = (
        alt.layer(violin, median_dot, data=df)
        .properties(width=250, height=400)
        .facet(
            column=alt.Column(
                "learning_language:N",
                title="Learning Language",
                sort=order,
                header=alt.Header(titleOrient="bottom", labelOrient="bottom"),
            )
        )
        .configure_facet(spacing=5)
        .configure_view(stroke=None)
        .properties(title="")
        .resolve_scale(x="shared")
    )

    st.altair_chart(final, use_container_width=True)

# -----------------------------
# Tile 3: Daily Practices per User by Learning Language (line chart)
# -----------------------------        
st.subheader("Daily Practices per User by Learning Language")

sql = f"""
SELECT
    learning_language,
    event_dt,
    round(CAST(practices_completed AS FLOAT64)/NULLIF(active_users, 0), 2) AS practices_per_user
FROM `{project_id}.{dataset_mart}.fct_daily_language_activity`
ORDER BY 1, 2
"""
df, err = safe_run_query(sql)

if err:
    st.error("Tile failed to load.")
    st.code(err)
else:
    df["event_dt"] = pd.to_datetime(df["event_dt"])

    # Optional: filter to LANG_DOMAIN so colors stay aligned
    df = df[df["learning_language"].isin(LANG_DOMAIN)]

    line = (
        alt.Chart(df)
        .mark_line(strokeWidth=2)
        .encode(
            x=alt.X(
                "event_dt:T",
                title="Date",
                axis=alt.Axis(format="%m/%d/%y")
            ),
            y=alt.Y(
                "practices_per_user:Q",
                title="Practices Per User"
            ),
            color=alt.Color(
                "learning_language:N",
                scale=color_scale,
                legend=alt.Legend(title="Learning Language")
            )
        )
    )

    points = (
        alt.Chart(df)
        .mark_circle(size=60)
        .encode(
            x="event_dt:T",
            y="practices_per_user:Q",
            color=alt.Color(
                "learning_language:N",
                scale=color_scale,
                legend=None
            ),
            tooltip=[
                alt.Tooltip("learning_language:N", title="Learning Language"),
                alt.Tooltip("event_dt:T", title="Date", format="%m/%d/%y"),
                alt.Tooltip("practices_per_user:Q", title="Practices Per User", format=",")
            ]
        )
    )

    final_chart = (line + points).properties(height=400)

    st.altair_chart(final_chart, use_container_width=True)