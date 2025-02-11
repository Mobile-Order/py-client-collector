import csv
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

url = "http://localhost:8080/api/v1/usee-client?size=10000"

payload = {}
headers = {
  'Cookie': 'auth_token=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJkZXYiLCJyb2xlIjoiUk9MRV9BRE1JTiIsImlzcyI6InVzZWUtYXBwIiwiZXhwIjoxNzM5MTg4OTc5LCJpYXQiOjE3MzgzMjQ5NzksImp0aSI6IjZlN2E0OWM4LTRlZjMtNGFmMC05M2UwLWMzYTg2YmI0NjJlMyJ9.HUc93KLiu2jV1OhHNF_vD_YBaP06zKM5Ip9ZQJM1Jjs; Path=/; Expires=Tue, 18 Jun 2052 12:02:58 GMT;'
}

response = requests.request("GET", url, headers=headers, data=payload)
re = response.json()
print(re.keys())
useeClients = re["returnobject"]["page"]["content"]



with open("output.csv", "w", newline="", encoding="utf-8") as csvfile:
    # Use the keys of the first dictionary in `useeClients` as column headers
    fieldnames = useeClients[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Write header
    writer.writeheader()

    # Write rows
    writer.writerows(useeClients)