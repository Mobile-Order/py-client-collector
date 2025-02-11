import json

import requests


# Function to process each row in the CSV and transform it into the required JSON structure
def process_row(row):
    # print(row.get("useeClientLocation", {}))
    return {
        # "id": row.get("id", ""),
        "name": row["name"],
        "pin": row["pin"],
        "phone": row["phone"],
        "useeClientLocation": row["useeClientLocation"],
        # "useeClientLocation": ast.literal_eval(row["useeClientLocation"]),
        # 'useeClientLocation':
        #     {
        #     "area": row["useeClientLocation"].get("area", ""),
        #     "street": row["useeClientLocation"].get("street", ""),
        #     "number": row["useeClientLocation"].get("number", ""),
        #     "zip": row["useeClientLocation"].get("zip", ""),
        #     "longitude": row["useeClientLocation"].get("longitude", ""),
        #     "latitude": row["useeClientLocation"].get("latitude", "")
        # },
        "website": row["website"],
        "facebook": row["facebook"],
        "emails": row["emails"],  # Use parse_emails to handle invalid JSON# Convert emails field from string to list
        "category": row["category"],
        "type": row["type"],
        # "notes": row.get("notes", "null"),
        # "approachDetails": row.get("approachDetails", "null")
    }

url = "http://localhost:8080/api/v1/useeClient/"

payload = {}
headers = {
  'Cookie': 'auth_token=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJkZXYiLCJyb2xlIjoiUk9MRV9BRE1JTiIsImlzcyI6InVzZWUtYXBwIiwiZXhwIjoxNzMxNTM4NDYyLCJpYXQiOjE3MzA2NzQ0NjIsImp0aSI6IjFkYjQ3Mjg1LTU3M2MtNDQzZi1iN2MwLTEwYjEwMDgyZDZjYSJ9.RHPUJ4VwM7B2j2vzow4tKbScO-_QmNo4XIatTHbi03g'
}

response = requests.request("GET", url, headers=headers, data=payload)
re = response.json()
# print(response.text)
useeClients = re["returnobject"]
useeClients=useeClients["useeClients"]
headers = {
    'Content-Type': 'application/json',
    'Cookie': 'auth_token=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJkZXYiLCJyb2xlIjoiUk9MRV9BRE1JTiIsImlzcyI6InVzZWUtYXBwIiwiZXhwIjoxNzMxNTM4NDYyLCJpYXQiOjE3MzA2NzQ0NjIsImp0aSI6IjFkYjQ3Mjg1LTU3M2MtNDQzZi1iN2MwLTEwYjEwMDgyZDZjYSJ9.RHPUJ4VwM7B2j2vzow4tKbScO-_QmNo4XIatTHbi03g'
}
count=0
url = "https://backend.usee.gr/api/v1/usee-client/"
# Assuming 'final' is your list of dictionaries
for data_entry in useeClients:
    # Send POST request with each entry as JSON
    # print(data_entry)
    payload = json.dumps(process_row(data_entry), indent=4)
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    count=count+1
    # print(payload)
#
# print("All data sent to the API.")
# print(count)