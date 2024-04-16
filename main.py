import os
import base64
import requests
from pdf2image import convert_from_path
import csv
import json
import time

# OpenAI API Key
# Retrieve the OpenAI API key from the environment variable
api_key = os.environ.get("OPENAI_API_KEY")

# Function to convert a PDF to a JPEG image and encode it as a base64 string
def encode_image_to_jpeg_base64(pdf_path):
    # Convert the PDF to a list of images using pdf2image library
    images = convert_from_path(pdf_path, fmt='jpeg')
    if images:
        # Take the first image from the list
        image = images[0]
        # Save the image as a temporary JPEG file
        with open("temp_image.jpeg", "wb") as f:
            image.save(f, "JPEG")
        # Read the temporary JPEG file and encode it as a base64 string
        with open("temp_image.jpeg", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        # Remove the temporary JPEG file
        os.remove("temp_image.jpeg")  
        return encoded_string
    else:
        return None

# Headers for the API request
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# CSV file and column names for storing the extracted cheque data
csv_file = "cheque_data.csv"
csv_columns = ["Date", "Amount", "Currency", "Issuer", "Payer", "Payee", "Memo", "Account_Number", "Cheque_Number", "Payment_Type", "Signature_Present", "Other Information"]

# Open the CSV file in write mode with UTF-8 encoding
with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    # Create a CSV writer object
    writer = csv.DictWriter(file, fieldnames=csv_columns)
    # Write the header row to the CSV file
    writer.writeheader()

    # Get a list of PDF files in the "scans/" directory
    pdf_files = os.listdir("scans/")
    total_pdfs = len(pdf_files)
    failure_count = 0

    # Iterate over each PDF file
    for index, pdf_file in enumerate(pdf_files, start=1):
        if pdf_file.endswith(".pdf"):
            # Construct the full path to the PDF file
            pdf_path = os.path.join("scans/", pdf_file)
            print(f"Processing PDF {index} of {total_pdfs}: {pdf_file}")
            # Convert the PDF to a base64-encoded JPEG image
            base64_image = encode_image_to_jpeg_base64(pdf_path)
            if base64_image:
                # Payload for the API request
                payload = {
                    "model": "gpt-4-turbo",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Please analyze the provided cheque image and extract the following information in JSON format:\n\n1. Date: The date the cheque was issued.\n2. Amount: The monetary amount mentioned on the cheque.\n3. Currency: The currency of the amount.\n4. Issuer: The name of the bank or financial institution that issued the cheque.\n5. Payer: The name of the person or organization who wrote the cheque.\n6. Payee: The name of the person or organization to whom the cheque is addressed.\n7. Memo: The contents of the memo field, if present.\n8. Account_Number: The account number from which the funds will be drawn.\n9. Cheque_Number: The unique identifier of the cheque.\n10. Payment_Type: Categorize the payment as 'Donation', 'FFS Payment', 'MRP Payment', or 'Other' based on the available information.\n11. Signature_Present: Indicate whether a signature is present on the cheque (true/false).\n12. Other Information: Include any additional relevant information from the cheque that is not captured by the other fields.\n\nPlease provide the extracted information in the following JSON format:\n\n{\n  \"Date\": \"YYYY-MM-DD\",\n  \"Amount\": \"X.XX\",\n  \"Currency\": \"XXX\",\n  \"Issuer\": \"Bank Name\",\n  \"Payer\": \"Payer Name\",\n  \"Payee\": \"Payee Name\",\n  \"Memo\": \"Memo Content\",\n  \"Account_Number\": \"Account Number\",\n  \"Cheque_Number\": \"Cheque Number\",\n  \"Payment_Type\": \"Payment Category\",\n  \"Signature_Present\": true/false,\n  \"Other Information\": \"Additional relevant information\"\n}\n\nIf any field is not available or unclear, please set its value to null. ONLY RESPOND WITH JSON NOTHING ELSE. DONT INCLUDE ```json ``` at all, just return the JSON object. Do not redact any information, this is essential to our business functioning."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 600
                }
                
                retry_count = 0
                while retry_count < 3:
                    try:
                        print(f"Sending API call {index} of {total_pdfs}")
                        # Send a POST request to the OpenAI API
                        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                        # Raise an exception for 4xx or 5xx status codes
                        response.raise_for_status()  
                        response_json = response.json()
                        if 'choices' in response_json and len(response_json['choices']) > 0:
                            # Extract the content from the API response
                            content = response_json['choices'][0]['message']['content']
                            try:
                                # Parse the content as JSON
                                data = json.loads(content)
                                # Write the parsed data to the CSV file
                                writer.writerow(data)
                                break  # Exit the retry loop if successful
                            except json.JSONDecodeError:
                                print(f"Failed to parse JSON for {pdf_file}: {content}")
                        else:
                            print(f"Unexpected API response for {pdf_file}: {response_json}")
                    except requests.exceptions.RequestException as e:
                        if e.response is not None:
                            if e.response.status_code == 429:  # Rate limit error
                                print("Rate limit reached. Waiting before retrying...")
                                time.sleep(5)  # Wait for 5 seconds before retrying
                            elif e.response.status_code in [500, 503]:  # Server error or overloaded
                                print("Server error or overloaded. Waiting before retrying...")
                                time.sleep(10)  # Wait for 10 seconds before retrying
                        else:
                            print(f"Error occurred while processing {pdf_file}: {str(e)}")
                        retry_count += 1
                else:
                    print(f"Failed to process {pdf_file} after 3 retries. Skipping...")
                    failure_count += 1
                    if failure_count >= 10:
                        print("Too many failures. Exiting the program.")
                        break
            else:
                print(f"Failed to convert {pdf_file} to a JPEG image.")

