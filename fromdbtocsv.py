import csv
import requests


# Function to process each row in the CSV and transform it into the required JSON structure
def process_row(row):
    return {
        "name": row["name"],
        "pin": row["pin"],
        "phone": row["phone"],
        "useeClientLocation": row["useeClientLocation"],
        "website": row["website"],
        "facebook": row["facebook"],
        "emails": row["emails"],
        "category": row["category"],
        "type": row["type"],
    }


# Base URL for the API
base_url = "http://localhost:8080/api/v1/usee-client"

# Headers for the request
headers = {
    'Cookie': "auth_token=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJkZXYiLCJyb2xlIjoiUk9MRV9BRE1JTiIsImlzcyI6InVzZWUtYXBwIiwiZXhwIjoxNzQwMTI4MjAxLCJpYXQiOjE3MzkyNjQyMDEsImp0aSI6IjRiMGYzMzQxLWE3ZmUtNDQwNC04ODEwLWQ5YmRiNmMxNDk2YSJ9.LKdJ29Sawq9IBHBAUru3HtQe3Bq_t3VCSW_Hc4sir-w; Path=/; Expires=Sat, 29 Jun 2052 08:56:41 GMT;"
}

# Initialize variables
useeClients = []
page = 0
size = 1000  # Number of items per page
has_more_pages = True

# Fetch all pages
while has_more_pages:
    # Construct the URL with pagination parameters
    url = f"{base_url}?page={page}&size={size}"
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Error fetching page {page}: {response.status_code}")
        break

    # Parse the JSON response
    data = response.json()
    content = data["returnobject"]["page"]["content"]

    # Append the results to the useeClients array
    useeClients.extend(content)

    # Check if there are more pages
    total_pages = data["returnobject"]["page"]["totalPages"]
    if page >= total_pages - 1:  # Pages are zero-indexed
        has_more_pages = False
    else:
        page += 1

print(f"Total clients fetched: {len(useeClients)}")

# Write the results to a CSV file
with open("output.csv", "w", newline="", encoding="utf-8") as csvfile:
    # Use the keys of the first dictionary in `useeClients` as column headers
    fieldnames = useeClients[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Write header
    writer.writeheader()

    # Write rows
    writer.writerows(useeClients)