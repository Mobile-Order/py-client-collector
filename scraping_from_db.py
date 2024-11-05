import csv
import random
import re

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from urllib.parse import urlparse
import requests
from sympy.physics.units import length
import requests
import json
from email_validator import validate_email, EmailNotValidError

counter=0
excluded_domains = ["e-food", "wolt", "box", "xo", "vrisko", "instagram", "google-maps"]

def contains_numbers(s):
    return any(char.isdigit() for char in s)

def email_validator_address(input_text):
    email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

    # Find all email-like patterns in the input text
    matches = re.findall(email_regex, input_text)

    if matches:
        for email in matches:
            try:
                emailinfo = validate_email(email, check_deliverability=False)
                print(f"Valid email found: {emailinfo.normalized}")
                return emailinfo.normalized
            except EmailNotValidError as e:
                print(f"Invalid email '{email}': {str(e)}")
                continue  # Skip to the next email if current is invalid
    else:
        print("No valid email found.")
        return "null"


def transliterate_greek(text):
    greek_to_english = {
        'Α': 'A', 'Β': 'B', 'Γ': 'G', 'Δ': 'D', 'Ε': 'E', 'Ζ': 'Z', 'Η': 'I', 'Θ': 'Th',
        'Ι': 'I', 'Κ': 'K', 'Λ': 'L', 'Μ': 'M', 'Ν': 'N', 'Ξ': 'X', 'Ο': 'O', 'Π': 'P',
        'Ρ': 'R', 'Σ': 'S', 'Τ': 'T', 'Υ': 'Y', 'Φ': 'F', 'Χ': 'Ch', 'Ψ': 'Ps', 'Ω': 'O',
        'α': 'a', 'β': 'b', 'γ': 'g', 'δ': 'd', 'ε': 'e', 'ζ': 'z', 'η': 'i', 'θ': 'th',
        'ι': 'i', 'κ': 'k', 'λ': 'l', 'μ': 'm', 'ν': 'n', 'ξ': 'x', 'ο': 'o', 'π': 'p',
        'ρ': 'r', 'σ': 's', 'ς': 's', 'τ': 't', 'υ': 'y', 'φ': 'f', 'χ': 'ch', 'ψ': 'ps', 'ω': 'o',
        'Ά': 'A', 'Έ': 'E', 'Ή': 'I', 'Ί': 'I', 'Ό': 'O', 'Ύ': 'Y', 'Ώ': 'O',
        'ά': 'a', 'έ': 'e', 'ή': 'i', 'ί': 'i', 'ό': 'o', 'ύ': 'y', 'ώ': 'o', 'ϊ': 'i', 'ϋ': 'y'
    }

    # Replace each Greek character with its English equivalent
    transliterated_text = ''.join(greek_to_english.get(char, char) for char in text)
    return transliterated_text.lstrip(':')

# get cafeterias for a municipality url
def get_cafeterias_maps_urls(url):
    if is_valid_url(url):
        driver.get(url)
    else:
        return []
    try:
        language_button = driver.find_element(By.XPATH, "//button[@jscontroller='soHxf']")
        language_button.click()
        print("Clicked language selector button.")
    except NoSuchElementException:
        print("Language selector button not found.")

    # Now select "English (United States)" from the language options
    time.sleep(random.randint(3, 15))  # Brief pause to ensure language menu is loaded
    try:
        # Locate "English (United States)" and click it
        english_us_option = driver.find_element(By.XPATH,
                                                "//span[contains(@class, 'VfPpkd-StrnGf-rymPhb-b9t22c') and .//span[text()='English'] and .//span[text()='United States']]")
        english_us_option.click()
        print("Selected 'English (United States)' language.")
    except NoSuchElementException:
        print("English (United States) language option not found.")

    time.sleep(random.randint(3, 15))  # Brief pause after language selection

    try:
        reject_button = driver.find_element(By.XPATH,"//button[@aria-label='Reject all']")
        reject_button.click()
        print("Clicked 'Reject All' button.")
    except NoSuchElementException:
        print("No 'Reject All' button found, proceeding without clicking.")
    # Scroll to load all results
    scrollable_div = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//div[@role='feed']"))
    )
    last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
    while True:
        driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", scrollable_div)
        time.sleep(random.randint(3, 15))  # Wait to load content
        new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
        if new_height == last_height:
            break  # Break the loop if no new content is loaded
        last_height = new_height
    # Get the HTML content of the page
    time.sleep(random.randint(3, 15))
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    # Extract the cafe names and URLs
    results = []
    # The structure may need adjustment depending on the actual HTML. Adjust the selectors as needed.
    for a_tag in soup.find_all('a', href=True, attrs={'aria-label': True}):
        name = a_tag['aria-label']
        url = a_tag['href']
        # Skip entries with the name "Εισοδος"
        if name == "Είσοδος" or name == "Sign in":
            print("Skipping link with name 'Εισοδος'")
            continue
        # Append as a dictionary instead of a formatted string
        results.append({"name": name, "pin": url})
    # Print the results
    for result in results:
        print(result)
    return results

#get cafeteria info from a maps url
def get_cafeterias_infos_from_maps(url):
    print(f"Processing URL: {url}")
    # Open the URL with Selenium
    if is_valid_url(url):
        driver.get(url)
    else:
        return {"phone":  "null", "street": "null", "number": "null" , "area": "null" , "zip": "null" ,"website": "null", "category": "null"}
    try:
        # Try to find the button by its XPath
        button = driver.find_element(By.XPATH, "//button[@aria-label='Απόρριψη όλων']")
        # If found, click the button
        button.click()
        print("Button clicked.")
    except NoSuchElementException:
        # If no button is found, print a message and continue
        print("Button with aria-label 'Απόρριψη όλων' not found. Skipping...")
    # Give the page some time to load
    time.sleep(random.randint(3, 15))
    # Get page content
    html_content = driver.page_source
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    greek_phone=True
    greek_adress=True
    # Search for elements that contain 'Τηλέφωνο:', 'Διεύθυνση:', 'Ιστότοπος:' in the aria-label
    phone_label_elements = soup.find_all(
        lambda tag: tag.has_attr('aria-label') and 'Τηλέφωνο:' in tag['aria-label'])
    if not phone_label_elements:
        phone_label_elements = soup.find_all(
            lambda tag: tag.has_attr('aria-label') and 'Phone:' in tag['aria-label'])
        greek_phone=False
    adress_elements = soup.find_all(
        lambda tag: tag.has_attr('aria-label') and 'Διεύθυνση:' in tag['aria-label'])
    if not adress_elements:
        adress_elements = soup.find_all(
            lambda tag: tag.has_attr('aria-label') and 'Address:' in tag['aria-label'])
        greek_adress = False
    website_elements = soup.find_all(
        lambda tag: tag.has_attr('aria-label') and 'Ιστότοπος:' in tag['aria-label'])
    if not website_elements:
        website_elements = soup.find_all(
            lambda tag: tag.has_attr('aria-label') and 'Website:' in tag['aria-label'])
        greek_website = False
    # Extract data, defaulting to an empty string if not found
    phone_number = "null"
    address = "null"
    website = "null"
    if phone_label_elements and greek_phone:
        aria_label = phone_label_elements[0]['aria-label']
        phone_number = aria_label.split('Τηλέφωνο:')[-1].strip()  # Extract text after 'Τηλέφωνο:'
        phone_number = phone_number.replace(" ", "")
        # Regular expression to separate country code and phone number
        match = re.match(r'(\+\d{1,2})(\d+)', phone_number)
        if match:
            country_code = match.group(1)
            phone_number = match.group(2)
        else:
            country_code = '+30'
    elif phone_label_elements:
        aria_label = phone_label_elements[0]['aria-label']
        phone_number = aria_label.split('Phone:')[-1].strip()  # Extract text after 'Τηλέφωνο:'
        phone_number = phone_number.replace(" ", "")
        # Regular expression to separate country code and phone number
        match = re.match(r'(\+\d{1,2})(\d+)', phone_number)
        if match:
            country_code = match.group(1)
            phone_number = match.group(2)
        else:
            country_code = '+30'
    if adress_elements and greek_adress:
        aria_label = adress_elements[0]['aria-label']
        address = aria_label.split('Διεύθυνση:')[-1].strip()  # Extract text after 'Διεύθυνση:'
        print(address)
    elif adress_elements:
        aria_label = adress_elements[0]['aria-label']
        address = aria_label.split('Address:')[-1].strip()  # Extract text after 'Διεύθυνση:'
        print(address)
    if website_elements:
        website = website_elements[0]['href']  # Extract href for the website
    street, number, area, postal_code = "null", "null", "null", "null"
    if address:
        address_parts = address.split(',')
        length = len(address_parts)
        if len(address_parts) == 2:
            # First part: Street and Number
            street_number_part = address_parts[0].strip()
            # Second part: Area and Postal Code
            if greek_adress:
                area_postal_code_part = address_parts[length-1].strip()
            else:
                area_postal_code_part = address_parts[length - 2].strip()
            # Split street and number (assuming number is the last word)
            street_parts = street_number_part.rsplit(' ', 1)
            if len(street_parts) == 2:
                street = street_parts[0]
                numbers = re.findall(r'\d+', street_number_part)
                if len(numbers)>0:
                    number = numbers[0]
                else:
                    number = "null"
            # Split area and postal code, identifying postal code by checking for a space within it
            area_parts = area_postal_code_part.rsplit(' ', 2)
            if len(area_parts) >= 2:
                area = area_parts[0].strip()
                postal_code = " ".join(area_parts[1:]).strip()  # Join to handle postal codes with spaces
                postal_code = postal_code.replace(" ", "")
            # Translate Street and Area to English
        if len(address_parts) >= 3:
            # First part: Street and Number
            street_number_part = address_parts[0].strip()
            i=0
            while i < len(address_parts) and not contains_numbers(street_number_part):
                street_number_part = address_parts[i].strip()
                i+=1
            # Second part: Area and Postal Code
            if greek_adress:
                area_postal_code_part = address_parts[length - 1].strip()
            else:
                area_postal_code_part = address_parts[length - 2].strip()
            # Split street and number (assuming number is the last word)
            street_parts = street_number_part.rsplit(' ', 1)
            if len(street_parts) == 2:
                street = street_parts[0]
                numbers = re.findall(r'\d+', street_number_part)
                if len(numbers) > 0:
                    number = numbers[0]
                else:
                    number = "null"
            # Split area and postal code, identifying postal code by checking for a space within it
            area_parts = area_postal_code_part.rsplit(' ', 2)
            if len(area_parts) >= 2:
                area = area_parts[0].strip()
                postal_code = " ".join(area_parts[1:]).strip()  # Join to handle postal codes with spaces
                postal_code = postal_code.replace(" ", "")
    # Translate Street and Area to English using deep-translator
    if street and greek_adress:
        street = transliterate_greek(street)
    if area and greek_adress:
        area = transliterate_greek(area)
    # Extract the "category" (e.g., "Καφετέρια") from the HTML
    category = "null"
    category_button = soup.find("button", class_="DkEaL")
    if category_button:
        category = category_button.text.strip()
        category = transliterate_greek(category)
    else:
        print("Category button not found.")
    print(
        f"Phone: {phone_number}, Street: {street}, Number: {number}, Area: {area}, Postal Code: {postal_code}, Website: {website}, Category: {category}")
    # Append parsed details to the row and write to CSV
    result = {"phone": phone_number, "street": street , "number": number, "area": area, "zip": postal_code,"website": website, "category": category}
    # csvwriter.writerow(row)
    print("Data saved for this URL.\n")
    print("Done with this URL.\n")
    return result

def get_facebook_cafeteria(cafeteria_name, area_name):
    search_query = f"{cafeteria_name} {area_name} Facebook"
    print(f"Searching for: {search_query}")
    # Navigate to Google and search for the cafeteria name
    driver.get("https://www.google.com/")
    time.sleep(random.randint(3, 15))
    # Click on the "Reject All" button if it appears
    try:
        reject_button = driver.find_element(By.ID, "W0wltc")
        reject_button.click()
        print("Clicked 'Reject All' button.")
    except NoSuchElementException:
        print("No 'Reject All' button found, proceeding without clicking.")
    time.sleep(random.randint(3, 15))
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)
    # Wait for the results to load
    time.sleep(random.randint(3, 15))
    # Initialize URL as None in case no valid URL is found
    first_valid_url = None
    try:
        # Find all <a> elements with jsname="UWckNb"
        all_results = driver.find_elements(By.XPATH, "//a[@jsname='UWckNb']")

        for result in all_results:
            url = result.get_attribute("href")
            # Check if the URL does not contain any excluded domain
            if url and not any(domain in url for domain in excluded_domains):
                first_valid_url = url
                print(f"Found URL: {first_valid_url}")
                break
        # If no valid URL was found, output None
        if first_valid_url is None:
            print(f"No valid URL found for {cafeteria_name}.")
    except NoSuchElementException:
        first_valid_url = None
        print(f"No URLs found for {cafeteria_name}.")
    return {"facebook": first_valid_url}

def is_valid_url(url):
    # Check if the URL format is well-formed
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        print(f"Invalid URL format: {url}")
        return False

    # Check if the URL is reachable
    try:
        response = requests.head(url, timeout=5)  # Use HEAD to check without downloading content
        if response.status_code < 400:
            print(f"URL is valid and reachable: {url}")
            return True
        else:
            print(f"URL returned an error status: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"URL is not reachable: {url} - {e}")
        return False
def fetch_email(url):
    if is_valid_url(url):
        driver.get(url)
        print("valid")
    else:
        return "null"
    try:
        # Locate and click the "Decline optional cookies" button
        decline_button = driver.find_element(By.XPATH,
                                             "//div[@aria-label='Decline optional cookies' and @role='button']")
        decline_button.click()
        print("Clicked 'Decline optional cookies' button.")

    except Exception as e:
        print("No Decline optional cookies!")

    try:
        # Locate and click the "Close" button
        close_button = driver.find_element(By.XPATH, "//div[@aria-label='Close' and @role='button']")
        close_button.click()
        print("Clicked the Close button.")

    except Exception as e:
        print("No close button!")

    try:
        time.sleep(random.randint(3, 15))  # Wait for the page to load
        # Locate email element containing "@" in text
        email_element = driver.find_element(By.XPATH, "//span[contains(text(), '@')]")
        # for element in email_element:
        #     email=email_validator_address(element.text)
        # email = email_validator_address(email_element.text)
        email = email_element.text
        return email
    except Exception as e:
        print(f"Could not fetch email from {url}")
        return "null"


url = "http://localhost:8080/api/v1/shop/"

payload = {}
headers = {
  'Cookie': 'auth_token=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJkZXYiLCJyb2xlIjoiUk9MRV9BRE1JTiIsImlzcyI6InVzZWUtYXBwIiwiZXhwIjoxNzMxNTM4NDYyLCJpYXQiOjE3MzA2NzQ0NjIsImp0aSI6IjFkYjQ3Mjg1LTU3M2MtNDQzZi1iN2MwLTEwYjEwMDgyZDZjYSJ9.RHPUJ4VwM7B2j2vzow4tKbScO-_QmNo4XIatTHbi03g'
}

response = requests.request("GET", url, headers=headers, data=payload)
re = response.json()
# print(response.text)
shops = re["returnobject"]
shops=shops["shops"]


# Set up Chrome options (optional)
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--lang=en")
# options.add_argument("--headless")  # Optional, run in headless mode

# Initialize the WebDriver
driver = webdriver.Chrome(options=options)
# names_urls = []
driver.get("https://www.facebook.com/")



try:
    # Locate and click the "Decline optional cookies" button
    decline_button = driver.find_element(By.XPATH,
                                         "//div[@aria-label='Decline optional cookies' and @role='button']")
    decline_button.click()
    print("Clicked 'Decline optional cookies' button.")
except Exception as e:
    print("No Decline optional cookies!")
# time.sleep(random.randint(3, 15))
#
# Locate the email input field and enter text
# email_input = driver.find_element(By.NAME, "email")
# email_input.send_keys("**********")  # Replace with your email
#
# # Locate the password input field and enter text
# password_input = driver.find_element(By.NAME, "pass")
# password_input.send_keys("*********")  # Replace with your password
#
# # Wait a bit to make sure inputs are populated
# time.sleep(random.randint(3, 15))
#
# # Locate the login button and click it
# login_button = driver.find_element(By.NAME, "login")
# login_button.click()




for i in range(len(shops)):
    if not shops[i]["facebook"] is None:
        continue
    name = shops[i]["name"]
    area = shops[i]["area"]
    website = get_facebook_cafeteria(name, area)
    shops[i]["facebook"] = website["facebook"]
# Wait to observe result
time.sleep(random.randint(3, 15))
for i in range(len(shops)):
    if not shops[i]["email"].__eq__("null"):
        continue
    source = shops[i]["facebook"]
    email = fetch_email(source)
    shops[i]["email"] = email
    if not email.__eq__("null"):
        counter+=1

headers = {
    'Content-Type': 'application/json',
    'Cookie': 'auth_token=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJkZXYiLCJyb2xlIjoiUk9MRV9BRE1JTiIsImlzcyI6InVzZWUtYXBwIiwiZXhwIjoxNzMxNTM4NDYyLCJpYXQiOjE3MzA2NzQ0NjIsImp0aSI6IjFkYjQ3Mjg1LTU3M2MtNDQzZi1iN2MwLTEwYjEwMDgyZDZjYSJ9.RHPUJ4VwM7B2j2vzow4tKbScO-_QmNo4XIatTHbi03g'
}
# API endpoint URL (replace with your actual endpoint)
url = "http://localhost:8080/api/v1/shop/"

# Assuming 'final' is your list of dictionaries
for data_entry in shops:
    # Send POST request with each entry as JSON
    print(data_entry)
    payload = json.dumps(data_entry)
    response = requests.request("PUT", url, headers=headers, data=payload)

print("All data sent to the API.")
# print(response.text)
print(counter)
driver.quit()

