""" 
* @description       : Google Cloud PDF Extraction Prompt Microservice
* @author            : Ramanathan
"""

import flask
import functions_framework
from markupsafe import escape
import base64
from google.cloud import aiplatform
import vertexai
from vertexai.generative_models import (
    GenerativeModel,
    Part,
    SafetySetting,
    FinishReason,
)
import vertexai.preview.generative_models as generative_models
import os
import json
import re
from dotenv import load_dotenv
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("keypath")

# varaible
pdf_string = ""

#### data extraction prompt #####
datainstruction = """
2. Read the items table section of decoded document from step #1  and each row represent an invoice line.
3. \"Extract\" the following attributes from matching items tabular section if found:
- Description as string
- Quantity as Number
- UoM from Unit of Measure as String
- UnitPrice from Net price as currency in USD value
- SKU from SKU as String value
- TotalPrice from Total Price as currency in USD value
4. Output Extracted invoice lines as array with key \"invoice_lines\"
5. Extract supplier details under seller section
6. Extract client details under client section
7. Extract invoice number as InvoiceNo
8. Extract Data of invoice issued as InvoiceDate
9. Extract Gross Amount as SubTotal
10. Extract Total Tax as TaxTotal
11. Extract Gross Price as GrossTotal
12. Extract Sale Order No as SalesOrderNo

##### Excepted response JSON Format #####
{"invoice_lines":[{"Description":"Coffee Machine","Quantity":5,"UoM":"each","UnitPrice":1000,"SKU":"0-100","TotalPrice":5000},{"Description":"Linux Laptop","Quantity":10,"UoM":"each","UnitPrice":2000,"SKU":"C-104","TotalPrice":20000}],"Supplier":{"Name":"XYZ Corps LLC","Address":"FJAK Rd\n San Jose, CA 94517","SupTaxId":"000-79-8853"},"Client":{"Name":"ASD LLC","Address":"123 Main St\nFremont, CA 94536","TaxId":"777-78-8888"},"InvoiceNo":"10001","InvoiceDate":"09/11/2024","SubTotal":434750,"TaxTotal":43475,"GrossTotal":478225,"SalesOrder":"I-122323","Status":"Commpleted"}

##### Excepted Error esponse JSON Format #####
{"invoice_lines":[],"Supplier":{"Name":"","Address":"","SupTaxId":""},"Client":{"Name":"","Address":"","TaxId":""},"InvoiceNo":"","InvoiceDate":"","SubTotal":"","TaxTotal":"","GrossTotal":"","SalesOrder":"","Status":"Failed"}

<note>
 - You first job is to identify the attached file is not empty, and it is related to invoice document, otherwise simply send empty JSON response only.
- If the there is no tabular section, simply return empty JSON response only
</note>"""

### system instruction prompt ###
sysinstruction = """<Instruction>
- You are a top notch data extract agent for extracting invoice document details from provided PDF file.
- You are job is to accurately extract information in structured format like JSON usually.
- You must provide answer in JSON response_format only and not other response format.
- You must execute tasks in the provided orders to extract information from PDF file.
- You must not make up answers, otherwise simply say i do not know.
</Instruction>"""

### HTTP method called from Salesforce ####
@functions_framework.http
def prompt_pdf_to_text(request):
    """HTTP Cloud Function.s
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    # request_args = request.args
    # print("pdf == "+ request.json["pdf_string"])
    api_key = ""
    if request.json and "pdf_string" in request.json:
        raw_pdf = request.json["pdf_string"]
        global pdf_string
        pdf_string += raw_pdf
        # Sprint(pdf_string)
    if request.json and "api_key" in request.json:
        api_key = request.json["api_key"]
        # print("api_kye == "+api_key)
    if api_key == os.getenv("apikey"):
        print("auth OK!")
        prompt_rsp = generate()
        headers = {"Content-Type": "application/json"}
        return (
            clean_json_string(
                prompt_rsp["candidates"][0]["content"]["parts"][0]["text"]
            ),
            200,
            headers,
        )
        # return ({"error": "OK!!"}, 200, headers)
    else:
        headers = {"Content-Type": "application/json"}
        return ({"error": "error occurred!!"}, 500, headers)

### Prompt Execution Method ###
def generate():
    vertexai.init(project=os.getenv("projectid"), location=os.getenv("zone"))
    model = GenerativeModel(os.getenv("modelid"), system_instruction=[sysinstruction])
    # print("document1 === "+str(document1))
    responses = model.generate_content(
        [
            """Execute below tasks step by step to complete the prompt
            1. Read contents attached pdf file""",
            Part.from_data(
                mime_type="application/pdf",
                data=base64.b64decode(f""" {pdf_string} """),
            ),
            datainstruction,
        ],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=False,
    )
    print(type(responses))
    print(responses)
    return responses.to_dict()

### Model Configuration ###
generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

### Model Saftey Configuration ###
safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    ),
]

#### clean JSON response from model ####
def clean_json_string(json_string):
    pattern = r"^```json\s*(.*?)\s*```$"
    json_str = re.sub(pattern, r"\1", json_string, flags=re.DOTALL)
    return json_str.strip()
