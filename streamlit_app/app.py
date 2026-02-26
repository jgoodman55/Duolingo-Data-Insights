import os
import pandas as pd
import streamlit as st
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
    st.bar_chart(df.set_index("learning_language"))

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