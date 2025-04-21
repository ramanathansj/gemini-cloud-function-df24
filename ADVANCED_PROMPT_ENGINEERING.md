# Advanced Prompt Engineering Documentation

## Overview
The gemini-cloud-function-dreamforce-2024-demo project demonstrates an advanced prompt engineering solution for extracting structured invoice details from PDF documents using Google Cloud Functions and Vertex AI's generative models.

## Features
- **Advanced Prompt Engineering**: Utilizes carefully crafted system and data extraction instructions to ensure accurate extraction of invoice data.
- **Cloud Deployment**: Deployable as an HTTP-triggered Google Cloud Function, leveraging GCP's capabilities.
- **Structured Response**: Returns results in a strictly formatted JSON structure.

## Architecture
- **Request Handling**: An HTTP endpoint implemented using Flask receives POST requests. The request payload includes a base64 encoded PDF string and an API key.
- **API Key Authentication**: Validates the API key before processing the request.
- **PDF Processing**: The PDF file is base64-decoded and passed to the Vertex AI model.
- **Prompt Composition**: The extraction prompt comprises:
  - **Instructional Prefix**: A prompt that begins with "Execute below tasks step by step to complete the prompt" to guide the model's behavior.
  - **System Instruction**: Directs the model to act as a top-notch data extraction agent, ensuring responses conform to a strict JSON format.
  - **Data Extraction Instruction**: Provides detailed instructions to extract invoice line items, supplier and client details, invoice metadata, and totals.
- **Model Configuration**: Fine-tuned parameters including maximum output tokens, temperature, and top probability settings are applied.
- **Post-Processing**: The output is cleaned to remove any markdown formatting, delivering a valid JSON response.

## Prompt Engineering Details
- **System Instruction**: Instructs the generative model to extract invoice data accurately without fabricating any details. It enforces the format and the behavior expected of the model.
- **Data Extraction Instruction**: Specifies the attributes to extract, such as:
  - Invoice lines: Description, Quantity, UoM, UnitPrice, SKU, TotalPrice
  - Supplier details: Name, Address, SupTaxId
  - Client details: Name, Address, TaxId
  - Invoice metadata: InvoiceNo, InvoiceDate, SubTotal, TaxTotal, GrossTotal, SalesOrder
- **Safety Settings**: Configured with thresholds to block harmful content across multiple categories (hate speech, dangerous content, sexually explicit, and harassment).

## Deployment
### Prerequisites
- A Google Cloud Platform (GCP) account with Vertex AI enabled.
- A GCP service account JSON file with the necessary permissions placed in the `/gcpfunctions/keys` directory.
- Update the `.env` file with the following:
  - `projectid`: Your GCP project ID
  - `zone`: Location/zone of your GCP project
  - `modelid`: The Gemini model ID (default is `gemini-1.5-flash-001`)
  - `keypath`: Path to the GCP service account JSON file or your Vertex API key

### Deployment Command
From the `gcpfunctions` directory, run the following command to deploy the cloud function:
```
gcloud functions deploy pdf-extract-v3 \
    --runtime=python312 \
    --region=<Your-App-Zone> \
    --source=. \
    --entry-point=prompt_pdf_to_text \
    --trigger-http \
    --allow-unauthenticated --gen2
```
Note: The cloud function is unauthenticated but utilizes an internal API key for additional security.

### Testing the Function
- Use a sample PDF document from the `/data` directory.
- Base64-encode the PDF content.
- Send a POST request to the deployed cloud function endpoint containing the keys `pdf_string` and `api_key`.
- The function will return the extracted invoice details in a JSON format. For cases where the extraction fails, a JSON with empty fields is returned.

## Future Enhancements
- Improve error handling and logging to capture and debug issues more effectively.
- Extend prompt extraction capabilities to support additional document formats and more complex invoice structures.
- Refine prompt templates further for enhanced extraction accuracy.

## References
- [Vertex AI Generative Models Documentation](https://cloud.google.com/vertex-ai/docs/generative-models)
- [Salesforce Dreamforce 24 Demo Repository](https://github.com/ramanathansj/advanced-prompt-engineering-df2024)
