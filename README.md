# Duolingo-Data-Insights

Problem Statement Here

## Google Cloud Initialization

1. Create a new Google Cloud Project and take note of the project id
1. **Might delete the below**, not sure if service account is necessary
1. Go to IAM & Admin then click in Service Accounts 
1. Create a new Service Account with roles: BigQuery Admin, Compute Admin, and Storage Admin
1. Click the elipses under Actions and click the Manage Keys option
1. Click the Add key button, then click Create new key, then select JSON
1. The JSON will go to your downloads. Save the file in a safe place. Do NOT show to anyone

## Github Codespaces

To avoid dependencies and installations, run this project by connecting to GitHub codespaces.

### Requirements

1. You need a github account
1. Install VS Code
1. Open VS Code, go to Extensions, and install GitHub Codespaces

## Initialize the Project

1. Open VS Code
1. In the search bar in the top middle, search "> Codespaces: Create New Codespace" and click the result.
    - If you've already set up a codespace, search "> Codespaces: Connect to Codespace"
1. Once connected, you'll need to set up your 

## Kestra

Kestra will be the tool that runs the end to end pipeline process.

1. Update the following variables in [gcp_kv.yaml](kestra/flows/gcp_kv.yaml)
- gcp_project_id
- gcp_location
- gcp_bucket_name
- gcp_dataset

1. Run **docker compose up** to start up kestra.
    - Note that the GCP Service Account credentials will be added via the GCP_KEY_PATH varible in the docker-compose.yml and GCP_KEY_PATH comes from .env