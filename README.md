# Duolingo-Data-Insights

Problem Statement Here

## Google Cloud Initialization

1. Create a new Google Cloud Project and take note of the project id
1. Go to IAM & Admin then click in Service Accounts 
1. Create a new Service Account with roles: BigQuery Admin, Compute Admin, and Storage Admin
1. Click the elipses under Actions and click the Manage Keys option
1. Click the Add key button, then click Create new key, then select JSON
1. The JSON will go to your downloads. Save the file in a safe place. Do NOT show to anyone

## Set up Environment Variables

1. Git clone this repository
1. Create a secrets folder within the Duolingo-Data-Insights folder and add the file to the secrets folder (secrets/*.json is in .gitignore)
1. Create a **.env** file based on [template.env](template.env)

## Kestra

Kestra will be the tool that runs the end to end pipeline process.

1. Update the following variables in [gcp_kv.yml](kestra/flows/gcp_kv.yml)
    - gcp_project_id
    - gcp_location
    - gcp_bucket_name
    - gcp_dataset
1. Run **docker compose up** to start up kestra and the streamlit app that will show a populated dashboard once the kestra flows have been run
1. Launch http://127.0.0.1:8080/ui/ and login with credentials defined in [docker-compose.yml](docker-compose.yml) under kestra -> server -> basicAuth
1. Run the pipeline_master flow to execute all kestra flows in the following order
    1. Create key, value pairs with [duolingo.gcp_kv.yml](kestra/flows/duolingo.gcp_kv.yml)
    1. Create GCS buckets and dataset with [duolingo.gcp_setup.yml](kestra/flows/duolingo.gcp_setup.yml)
    1. Download and ingest the gzipped data into the GCS bucket with [duolingo.ingestion.yml](kestra/flows/duolingo.ingestion.yml)
    1. Create the external table, DDL for the main table, and populate the main table with [duolingo.table_creation.yml](kestra/flows/duolingo.table_creation.yml)
    1. Use DBT to transform the data into the relevant staging and marts tables to power the visuals in the streamlit app in [duolingo.dbt_transform.yml](kestra/flows/duolingo.dbt_transform.yml)


## Streamlit Dashboard App

1. Launch http://localhost:8501/ to open the Streamlit Dashboard App which will have populated visuals once the Kestra flows have been run.