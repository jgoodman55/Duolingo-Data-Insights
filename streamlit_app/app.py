import os
import pandas as pd
import streamlit as st
import altair as alt
from google.cloud import bigquery

st.set_page_config(page_title="Duolingo Dashboard", layout="wide")

project_id = os.environ["GCP_PROJECT_ID"]
dataset_mart = os.environ["BQ_DATASET_MART"]

client = bigquery.Client(project=project_id, location=os.environ["GCP_LOCATION"])

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
    df["users"] = df["users"].astype(int)  # ensure numeric

    sort_order = df["learning_language"].tolist()  # df is already sorted by COUNT DESC from SQL

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(
                "learning_language:N",
                sort=sort_order,  # explicit list overrides Altair's default alpha sort
                title="Learning Language"
            ),
            y=alt.Y("users:Q", title="Number of Users"),
            tooltip=["learning_language:N", "users:Q"]
        )
    )

    st.altair_chart(chart, use_container_width=True)

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