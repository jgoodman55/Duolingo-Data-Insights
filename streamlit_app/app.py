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
st.title("Duolingo Learning Insights")

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

# Last updated (ET) from one “source of truth” mart table
last_updated_utc = get_table_last_modified(project_id, dataset_mart, "fct_user_learning_language")
st.caption(f"Last updated (ET): {last_updated_utc.astimezone(ET):%Y-%m-%d %I:%M %p %Z}")


col1, col2 = st.columns(2)


# -----------------------------
# Tile 1: % of total + counts in tooltip
# -----------------------------
with col1:
    st.subheader("Users by Learning Language (% of total)")

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
                    title="Learning Language"
                ),
                y=alt.Y(
                    "percent_of_total:Q",
                    title="Percent of Total User–Learning Language Pairs",
                    axis=alt.Axis(format="%")
                ),
                tooltip=[
                    alt.Tooltip("learning_language:N", title="Language"),
                    alt.Tooltip("percent_of_total:Q", title="Percent of Total", format=".2%"),
                    alt.Tooltip("users:Q", title="Users", format=","),
                    alt.Tooltip("total_users:Q", title="Total User-Learning Language Pairs", format=","),
                ],
            )
        )

        labels = (
            alt.Chart(df)
            .mark_text(align="center", baseline="bottom", dy=-5)
            .encode(
                x=alt.X(
                    "learning_language:N",
                    sort=alt.SortField(field="users", order="descending")
                ),
                y=alt.Y("percent_of_total:Q"),
                text=alt.Text("percent_of_total:Q", format=".1%")
            )
        )

        st.altair_chart(bars + labels, use_container_width=True)


# -----------------------------
# Tile 2: placeholder (safe) — swap in your time-series mart when ready
# -----------------------------
with col2:
    st.subheader("Coming next: Time series tile")
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

        violin = (
            alt.Chart(df)
            .transform_density(
                "overall_accuracy",
                as_=["overall_accuracy", "density"],
                groupby=["learning_language"],
                extent=[0, 1],   # accuracy is 0..1
                steps=60
            )
            .mark_area(orient="horizontal")
            .encode(
                y=alt.Y(
                    "learning_language:N",
                    sort=alt.SortField(field="learning_language", order="ascending"),
                    title="Learning Language"
                ),
                x=alt.X(
                    "density:Q",
                    stack="center",
                    title=None,
                    axis=None
                ),
                x2="density:Q",
                color=alt.Color("learning_language:N", legend=None),
                tooltip=[
                    alt.Tooltip("learning_language:N", title="Language"),
                    alt.Tooltip("overall_accuracy:Q", title="Accuracy", format=".2f"),
                    alt.Tooltip("density:Q", title="Density", format=".4f"),
                ],
            )
        )

        # Better: add a boxplot overlay for summary stats
        box = (
            alt.Chart(df)
            .mark_boxplot(size=25)
            .encode(
                y=alt.Y("learning_language:N", title=""),
                x=alt.X("overall_accuracy:Q", title="Overall Accuracy", scale=alt.Scale(domain=[0, 1])),
                tooltip=[
                    alt.Tooltip("learning_language:N", title="Language"),
                    alt.Tooltip("overall_accuracy:Q", title="Accuracy", format=".2f"),
                ],
            )
        )

        st.altair_chart((violin + box).properties(height=350), use_container_width=True)

    st.info(
        "Add your temporal trend tile here (e.g., daily practices over time). "
        "Once you have a `fct_practices_daily` mart, we can plug it in safely the same way as Tile 1."
    )