import ast
import csv
import json

import requests


# Function to safely parse the emails field
def parse_emails(emails_str):
    try:
        # Attempt to load as JSON array
        emails = json.loads(emails_str)
        # Ensure it is a list
        if isinstance(emails, list):
            return emails
    except (json.JSONDecodeError, TypeError):
        pass
    # Default to an empty list if parsing fails
    return []
# Function to process each row in the CSV and transform it into the required JSON structure
def process_row(row):
    # print(row.get("useeClientLocation", {}))
    return {
        # "id": row.get("id", ""),
        "name": row["name"],
        "pin": row.get("pin", ""),
        "phone": row.get("phone", ""),
        # "useeClientLocation": row.get("useeClientLocation", {}),
        "useeClientLocation": ast.literal_eval(row["useeClientLocation"]),
        # 'useeClientLocation':
        #     {
        #     "area": row["useeClientLocation"].get("area", ""),
        #     "street": row["useeClientLocation"].get("street", ""),
        #     "number": row["useeClientLocation"].get("number", ""),
        #     "zip": row["useeClientLocation"].get("zip", ""),
        #     "longitude": row["useeClientLocation"].get("longitude", ""),
        #     "latitude": row["useeClientLocation"].get("latitude", "")
        # },
        "website": row.get("website", ""),
        "facebook": row.get("facebook", ""),
        "emails": ast.literal_eval(row.get("emails", "")),  # Use parse_emails to handle invalid JSON# Convert emails field from string to list
        "category": row.get("category", ""),
        "type": row.get("type", "CAFE"),
        # "notes": row.get("notes", "null"),
        # "approachDetails": row.get("approachDetails", "null")
    }

# Function to read CSV and transform each row into JSON
def read_csv_to_json(filename):
    data = []
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            processed_row = process_row(row)
            data.append(processed_row)
    return data

# Load data from CSV
filename = "output.csv"  # replace with your actual CSV file path
data = read_csv_to_json(filename)

# Now `data` contains all rows in the required JSON structure
# You can then use this data to send to your database API, e.g., with requests

# Example of printing one row to check format

headers = {
  'Content-Type': 'application/json',
  'Cookie': "auth_token=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJkZXYiLCJyb2xlIjoiUk9MRV9BRE1JTiIsImlzcyI6InVzZWUtYXBwIiwiZXhwIjoxNzQwMDYzMDYzLCJpYXQiOjE3MzkxOTkwNjMsImp0aSI6ImMzMTM0YjFmLTBhZjItNDNmNi04YmYyLWNhYTY5OTY3ZTZjNiJ9.45oQjz8qSYQc7LKOjh6znS34206hBFk2b_u68n7L-7g; Path=/; Expires=Fri, 28 Jun 2052 14:51:03 GMT;"
}
# API endpoint URL (replace with your actual endpoint)
url = "http://localhost:8080/api/v1/usee-client/"

# Assuming 'final' is your list of dictionaries
for data_entry in data:
    # Send POST request with each entry as JSON
    print(data_entry)
    # payload=json.dumps(data_entry)
    response = requests.request("POST", url, headers=headers, json=data_entry)
    # print(json.dumps(data_entry, indent=4))
    print(response.text)
    # break




