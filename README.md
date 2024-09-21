# gemini-cloud-function-df24
 gemini pdf extraction cloud function

1. Sign up for free GCP account 
https://cloud.google.com/free

2. Create a Service Account and downlaod JWT cert and place it /keys folder
https://cloud.google.com/iam/docs/service-accounts-create

3. Enable Vertex AI API and create a Vertex API key if you are not planning to use service account authentication
https://cloud.google.com/vertex-ai/docs/start/cloud-environment

Make sure service account have Vertex AI permission enabled

4. Modify .env properties file with following according to your GCP project settings
projectid=GCP project id
zone=location/zone of gcp project
modelid = gemini-1.5-flash-001, change it to other model id as needed
keypath=gcp-service-account-jwt.json  or enter vertex API key

5. Install gcloud CLI and sign in with your GCP account, https://cloud.google.com/sdk/docs/install

6. Execute following command from gcpcloudfunction folder to deploy the project to gcp cloud

gcloud functions deploy pdf-extract-v3 \                    
    --runtime=python312 \
    --region=us-west1 \
    --source=. \
    --entry-point=prompt_pdf_to_text \
    --trigger-http \
    --allow-unauthenticated --gen2

Note: The cloud function is unauthenticated but we are using our own api key to validate the incoming request. This can be potentially changed to authenticated with Service Account as needed.

Note down the URL of cloud function for testing and updating salesforce custom settings. 

7. Use pdf document in /data and base64 encoded to test above pdf extraction prompt service.


