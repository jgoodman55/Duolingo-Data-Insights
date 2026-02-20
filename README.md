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

Choose either option below to utilize your GCP key.

### Option 1: Create a secrets folder in codespaces
1. Create a secrets folder and add the file to the secrets folder (secrets/*.json is in .gitignore)
1. Create a **.env** file based on [template.env](template.env)
    - Set `GCP_KEY_PATH` to where you saved the key .json in the secrets folder
    - Set `LOCAL_FLOWS_PATH` to the repositories kestra/flows folder

### Option 2: Fork the repository and upload a GitHub Codespaces secret
1. Follow these [instructions](https://docs.github.com/en/codespaces/managing-your-codespaces/managing-your-account-specific-secrets-for-github-codespaces) to create a GitHub Codespaces secret
1. Create a **.env** file based on [template.env](template.env)
    - Set `LOCAL_FLOWS_PATH` to the repositories kestra/flows folder

## Github Codespaces

To avoid dependencies and installations, run this project by connecting to GitHub codespaces.

### Requirements

1. You need a GitHub account
1. Install VS Code
1. Open VS Code, go to Extensions, and install GitHub Codespaces
1. Clone this git repository

## Initialize the Project

1. Open VS Code
1. In the search bar in the top middle, search "> Codespaces: Create New Codespace" and click the result.
    - If you've already set up a codespace, search "> Codespaces: Connect to Codespace"
1. For a new codespace, choose the repository, and choose the 2 core option

## Kestra

Kestra will be the tool that runs the end to end pipeline process.

1. Update the following variables in [gcp_kv.yml](kestra/flows/gcp_kv.yml)
    - gcp_project_id
    - gcp_location
    - gcp_bucket_name
    - gcp_dataset
1. Run **docker compose up** to start up kestra.
1. Launch http://127.0.0.1:8080/ui/ and login with credentials defined in [docker-compose.yml](docker-compose.yml) under kestra -> server -> basicAuth
1. Run the gcp_kv flow to create the key value pairs needed for GCP
1. Run the gcp_setup flow to create the buckets
1. Left off here, create a master file that can run several flows for ELT

### Kestra Flow Order
1. Create key, value pairs with [duolingo.gcp_kv.yml](kestra/flows/duolingo.gcp_kv.yml)
1. Create GCS buckets and dataset with [duolingo.gcp_setup.yml](kestra/flows/duolingo.gcp_setup.yml)
1. Download and ingest the gzipped data with [duolingo.ingestion.yml](kestra/flows/duolingo.ingestion.yml)


## DBT

Need to set up ~/.dbt directory to place profiles.yml