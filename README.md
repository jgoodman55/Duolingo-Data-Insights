# Duolingo-Data-Insights

## Project Problem Statement

Duolingo conducts rigorous studies to evalulate and improve the effectiveness of their app. Duolingo's paper [A Trainable Spaced Repetition Model for Language Learning](https://research.duolingo.com/papers/settles.acl16.pdf) describes spaced repition approaches and presents a new model, but the paper does not include a description of the users that are included in the study. The Duolingo Data Insights project focuses on native English speakers and visualizes the breakdown of users learning each language, the distribution of accuracy by language, and the average number of daily practices per user by language.

## Running this Project

To run the Duolingo Data Insights Project, follow the sections below.

## Google Cloud Initialization

1. Navigate to [Google Cloud](https://console.cloud.google.com/)
1. Create a new Google Cloud Project and take note of the project id
1. Go to IAM & Admin then click in Service Accounts 
1. Create a new Service Account with roles: BigQuery Admin, Compute Admin, and Storage Admin
1. Click the elipses under Actions and click the Manage Keys option
1. Click the Add key button, then click Create new key, then select JSON
1. The JSON will go to your downloads. Save the file in a safe place. Do NOT show it to anyone

## Set up Environment Variables

1. Git clone this repository into folder "Duolingo-Data-Insights"
1. Create a secrets folder within the Duolingo-Data-Insights folder and add the file to the secrets folder (secrets/*.json is in .gitignore)
1. Create a **.env** file based on [template.env](template.env)

## Kestra and Streamlit

Kestra will be the tool that runs the end to end pipeline process, and Streamlit will be the tool that visualizes this project's analytics.

1. Update the following variables in [gcp_kv.yml](kestra/flows/duolingo.gcp_kv.yml)
    - gcp_project_id
    - gcp_location
    - gcp_bucket_name
    - gcp_dataset
1. Open VS Code (or your preferred editor) and open a new Git Bash terminal
1. Cd into Duolingo-Data-Insights (the folder you created when you git cloned this repository)
1. Run **docker compose up** to start up kestra and the streamlit app that will show a populated dashboard once the kestra flows have been run
1. Open Kestra by going to http://127.0.0.1:8080/ui/ and login with the credentials defined in [docker-compose.yml](docker-compose.yml) under kestra -> server -> basicAuth
1. Run the **[Master Pipeline](kestra/flows/duolingo.pipeline_master.yml)** flow to execute all the kestra flows in the following order
    1. Create key, value pairs with [duolingo.gcp_kv.yml](kestra/flows/duolingo.gcp_kv.yml)
    1. Create GCS buckets and dataset with [duolingo.gcp_setup.yml](kestra/flows/duolingo.gcp_setup.yml)
    1. Download and ingest the gzipped data into the GCS bucket with [duolingo.ingestion.yml](kestra/flows/duolingo.ingestion.yml)
    1. Create the external table, DDL for the main table, and populate the main table with [duolingo.table_creation.yml](kestra/flows/duolingo.table_creation.yml)
    1. Use DBT to transform the data into the relevant staging and marts tables to power the visuals in the streamlit app in [duolingo.dbt_transform.yml](kestra/flows/duolingo.dbt_transform.yml)

## Streamlit Dashboard App

1. Once the [Master Pipeline](kestra/flows/duolingo.pipeline_master.yml) has run successfully at least once, launch http://localhost:8501/ to open the Streamlit Dashboard App.
1. The Dashboard contains three visuals
    1. Users by Learning Language: Visualizes the distribution of languages being learned
    1. Accuracy by Learning Language: Visualizes the overall accuracy by learning language
    1. Daily Practices per User by Learning Language: Visualizes the average number of daily practices per user by laerning language