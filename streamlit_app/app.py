import os
import pandas as pd
import streamlit as st
import altair as alt
from google.cloud import bigquery

st.set_page_config(page_title="Duolingo Dashboard", layout="wide")

project_id = os.environ["GCP_PROJECT_ID"]
dataset_mart = os.environ["BQ_DATASET_MART"]

client = bigquery.Client(project=project_id)

def run_query(sql: str) -> pd.DataFrame:
    return client.query(sql).to_dataframe()

st.title("Duolingo Learning Insights")

col1, col2 = st.columns(2)

# Tile 1: categorical distribution (users by learning language)
with col1:
    st.subheader("Users by learning language")
    sql = f"""
    SELECT
      learning_language,
      COUNT(DISTINCT user_id) AS users
    FROM `{project_id}.{dataset_mart}.fct_user_learning_language`
    GROUP BY 1
    ORDER BY users DESC
    """

    df = run_query(sql)

    # Ensure numeric
    df["users"] = pd.to_numeric(df["users"], errors="coerce")

    # Compute total + percent
    total_users = df["users"].sum()
    df["total_users"] = total_users
    df["percent_of_total"] = df["users"] / total_users

    chart = (
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
            title="Percent of Total Users",
            axis=alt.Axis(format="%")
        ),
        tooltip=[
            alt.Tooltip("learning_language:N", title="Language"),
            alt.Tooltip("users:Q", title="Users", format=","),
            alt.Tooltip("total_users:Q", title="Total Users", format=","),
            alt.Tooltip("percent_of_total:Q", title="Percent of Total", format=".2%")
            ]
        )
    )

    # Text labels layer
    text = (
        alt.Chart(df)
        .mark_text(
            align="center",
            baseline="bottom",
            dy=-5
        )
        .encode(
            x=alt.X(
                "learning_language:N",
                sort=alt.SortField(field="users", order="descending")
            ),
            y="percent_of_total:Q",
            text=alt.Text("percent_of_total:Q", format=".1%")
        )
    )

    # Layer them together
    final_chart = chart + text

    st.altair_chart(final_chart, use_container_width=True)

# Tile 2: categorical distribution (users by learning language)
with col2:
    st.subheader("Users by learning language")
    sql = f"""
    SELECT
      learning_language,
      COUNT(DISTINCT user_id) AS users
    FROM `{project_id}.{dataset_mart}.fct_user_learning_language`
    GROUP BY 1
    ORDER BY users DESC
    """
    df = run_query(sql)
    st.bar_chart(df.set_index("learning_language"))