import json
import random
import re
import time
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

counter=0
excluded_domains = ["e-food", "wolt", "box", "xo", "vrisko", "instagram", "google-maps"]

def remove_non_bmp(text):
    return "".join(c for c in text if c <= "\U0000FFFF")  # Keeps only BMP characters

def contains_numbers(s):
    return any(char.isdigit() for char in s)

def is_valid_url(url):
    # Check if the URL is well-formed
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        print(f"Invalid URL format: {url}")
        return False

    # Check if the URL is reachable by making a HEAD request
    try:
        response = requests.head(url, timeout=5)
        # A status code <400 is usually a good indicator the URL is reachable
        if response.status_code < 400:
            return True
        else:
            print(f"URL unreachable, status code: {response.status_code} for {url}")
            return False

    except requests.RequestException as e:
        print(f"Error reaching URL {url}: {e}")
        return False




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
        language_button = driver.find_element(By.XPATH, "//button[@jscontroller='O626Fe']")
        language_button.click()
        print("Clicked language selector button.")
    except NoSuchElementException:
        print("Language selector button not found.")
    # time.sleep(1000)
    # Now select "English (United States)" from the language options
    # time.sleep(random.randint(3, 10))  # Brief pause to ensure language menu is loaded
    try:
       # Initialize ActionChains
        actions = ActionChains(driver)
        x=0
        while x<15:
            x+=1
            print(x)
            actions.send_keys(Keys.ARROW_DOWN).perform()
        time.sleep(1)
       # Locate "English (United States)" and click it
        english_us_option = driver.find_element(By.XPATH, "//li[contains(@class, 'W7g1Rb-rymPhb-ibnC6b') and @data-lc='en']")
       #  time.sleep(10)
       #  english_us_option.click()
       #  button = driver.find_element_by_xpath("//span[contains(@class, 'RBHQF-ksKsZd') and @jscontroller='LBaJxb' and @jsname='m9ZlFb']")
        driver.execute_script("arguments[0].click();", english_us_option)
        print("Selected 'English (United States)' language.")
    except NoSuchElementException:
        print("English (United States) language option not found.")
    # time.sleep(1000)
    time.sleep(random.randint(3, 7))  # Brief pause after language selection

    try:
        reject_button = driver.find_element(By.XPATH,"//button[@aria-label='Reject all']")
        reject_button.click()
        print("Clicked 'Reject All' button.")
    except NoSuchElementException:
        print("No 'Reject All' button found, proceeding without clicking.")
    # Scroll to load all results
    scrollable_div = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[@role='feed']"))
    )
    last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
    while True:
        driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", scrollable_div)
        time.sleep(2)  # Wait to load content
        new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
        if new_height == last_height:
            break  # Break the loop if no new content is loaded
        last_height = new_height
    # Get the HTML content of the page
    time.sleep(random.randint(3, 7))
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
        return {"phone":  "null", "useeClientLocation": { "street": "null", "number": "null" , "area": "null" , "zip": "null" ,"longitude": "null", "latitude":"null"}, "website": "null", "category": "null"}
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
    time.sleep(random.randint(3, 7))
    # Get page content
    html_content = driver.page_source
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the anchor tag containing the specified ServiceLogin URL structure
    href_tag = soup.find('a', href=re.compile(r'https://accounts\.google\.com/ServiceLogin\?hl=en'))
    if not href_tag:
        href_tag = soup.find('a', href=re.compile(r'https://accounts\.google\.com/ServiceLogin\?hl=el'))
    longitude="null"
    latitude="null"
    if href_tag:
        href = href_tag['href']

        # Extract the 'continue' parameter that contains the encoded Google Maps URL
        continue_url_match = re.search(r'continue=([^&]+)', href)
        if continue_url_match:
            encoded_url = continue_url_match.group(1)
            decoded_url = requests.utils.unquote(encoded_url)

            # Extract latitude and longitude from the decoded Google Maps URL
            match = re.search(r'@([-+]?\d*\.\d+),([-+]?\d*\.\d+)', decoded_url)
            if match:
                latitude = match.group(1)
                longitude = match.group(2)
                print(f"Latitude: {latitude}, Longitude: {longitude}")
            else:
                print("Latitude and longitude not found in the Maps URL.")
    else:
        print("No matching ServiceLogin href found.")
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
            area_postal_code_part = address_parts[length-1].strip()
            # Split street and number (assuming number is the last word)
            street_parts = street_number_part.rsplit(' ', 3)
            street = street_parts[0]
            numbers = re.findall(r'\d+', street_number_part)
            if len(numbers)>0:
                number = numbers[len(numbers)-1]
            else:
                number = "null"
            i = 1
            while i < len(street_parts) and not contains_numbers(street_parts[i]):
                street = street+" "+street_parts[i]
                i += 1
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
            if i==len(address_parts):
                i=1
                street_number_part=address_parts[0].strip()
                while i < (len(address_parts)-1):
                    street_number_part+=" "+address_parts[i].strip()
                    i+=1
            # Second part: Area and Postal Code
            i=length-2
            area_postal_code_part = address_parts[length - 1].strip()
            while i > 0 and not contains_numbers(area_postal_code_part):
                area_postal_code_part = address_parts[i].strip()
                i-=1
            # Split street and number (assuming number is the last word)
            street_parts = street_number_part.rsplit(' ', 3)
            street = street_parts[0]
            numbers = re.findall(r'\d+', street_number_part)
            if len(numbers)>0:
                number = numbers[len(numbers)-1]
            else:
                number = "null"
            i=1
            while i < len(street_parts) and not contains_numbers(street_parts[i]):
                street = street+" "+street_parts[i]
                i += 1
            # Split area and postal code, identifying postal code by checking for a space within it
            area_parts = area_postal_code_part.rsplit(' ', 2)
            if len(area_parts) >= 2:
                area = area_parts[0].strip()
                postal_code = " ".join(area_parts[1:]).strip()  # Join to handle postal codes with spaces
                postal_code = postal_code.replace(" ", "")
    # Translate Street and Area to English using deep-translator
    # if street and greek_adress:
    street = transliterate_greek(street)
    # if area and greek_adress:
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
        f"Phone: {phone_number}, Street: {street}, Number: {number}, Area: {area}, Postal Code: {postal_code}, Website: {website}, Category: {category}, Longitude: {longitude}, Latitude: {latitude}")
    # Append parsed details to the row and write to CSV
    result = {"phone": phone_number, "useeClientLocation": { "street": street , "number": number, "area": area, "zip": postal_code,"longitude": longitude, "latitude": latitude}, "website": website, "category": category}
    # csvwriter.writerow(row)
    print("Data saved for this URL.\n")
    print("Done with this URL.\n")
    return result

def get_facebook_cafeteria(cafeteria_name, area_name, category):
    search_query = f"{cafeteria_name} {area_name} Facebook"
    print(f"Searching for: {search_query}")
    # Navigate to Google and search for the cafeteria name
    driver.get("https://www.google.com/")
    # time.sleep(random.randint(3, 7))
    # Click on the "Reject All" button if it appears
    try:
        reject_button = driver.find_element(By.ID, "W0wltc")
        reject_button.click()
        print("Clicked 'Reject All' button.")
    except NoSuchElementException:
        print("No 'Reject All' button found, proceeding without clicking.")
    time.sleep(random.randint(3, 7))
    try:
        # search_box = driver.find_element(By.NAME, "q")
        # print(search_query)
        # search_box.send_keys(search_query)
        # search_box.send_keys(Keys.RETURN)
        query = f"{cafeteria_name}"
        query = remove_non_bmp(query)
        query = query+" "+category+" "+area_name+" Facebook"  # Adds a space before "Facebook"
        google_search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

        driver.get(google_search_url)
    except NoSuchElementException as e:
        print("Search box element not found.")
    # Wait for the results to load
    time.sleep(random.randint(3, 7))
    # Initialize URL as None in case no valid URL is found
    first_valid_url = None
    try:
        # Find all <a> elements with jsname="UWckNb"
       all_results=[]
       while len(all_results)==0 :
        all_results = driver.find_elements(By.XPATH, "//a[@jsname='UWckNb']")
        time.sleep(10)

        for result in all_results:
            url = result.get_attribute("href")
            # Check if the URL does not contain any excluded domain
            if url and "facebook.com" in url:
                first_valid_url = url
                print(f"Found Facebook URL: {first_valid_url}")
                break  # Stop after finding the first Facebook link
        # If no valid URL was found, output None
        if first_valid_url is None:
            print(f"No valid URL found for {cafeteria_name}.")
            first_valid_url = "null"
    except NoSuchElementException:
        first_valid_url = "null"
        print(f"No URLs found for {cafeteria_name}.")
    return {"facebook": first_valid_url}

def fetch_email(url):
    if is_valid_url(url):
        driver.get(url)
        print("valid")
    else:
        return []
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
    emails = []
    try:
        time.sleep(random.randint(3, 7))  # Wait for the page to load
        # Locate email element containing "@" in text
        email_element = driver.find_elements(By.XPATH, "//span[contains(text(), '@')]")
        for element in email_element:
            print(element.text)
            # email=email_validator_address(element.text)
            emails.append(element.text)
        # email = email_validator_address(email_element.text)
        # email = email_element.text
        return emails
    except Exception as e:
        print(f"Could not fetch email from {url}")
        return []


def fetch_clients(page):
    url = f"http://localhost:8080/api/v1/usee-client?size=100&page={page}"
    headers = {
        'Cookie': "auth_token=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJkZXYiLCJyb2xlIjoiUk9MRV9BRE1JTiIsImlzcyI6InVzZWUtYXBwIiwiZXhwIjoxNzQwMTI4MjAxLCJpYXQiOjE3MzkyNjQyMDEsImp0aSI6IjRiMGYzMzQxLWE3ZmUtNDQwNC04ODEwLWQ5YmRiNmMxNDk2YSJ9.LKdJ29Sawq9IBHBAUru3HtQe3Bq_t3VCSW_Hc4sir-w; Path=/; Expires=Sat, 29 Jun 2052 08:56:41 GMT;"
    }
    response = requests.get(url, headers=headers)
    return response.json().get("returnobject", {}).get("page", {}).get("content", [])


def process_clients(useeClients):
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--lang=en")
    options.add_argument("--disable-usb-discovery")
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.facebook.com/")

    try:
        decline_button = driver.find_element(By.XPATH,
                                             "//div[@aria-label='Decline optional cookies' and @role='button']")
        decline_button.click()
        print("Clicked 'Decline optional cookies' button.")
    except Exception:
        print("No Decline optional cookies!")

    for client in useeClients:
        if client.get("facebook") != "null" and client.get("emails"):
            continue
        name = client.get("name", "")
        area = client.get("useeClientLocation", {}).get("area", "")
        category = client.get("category", "")
        website = get_facebook_cafeteria(name, area, category)  # Assume function exists
        client["facebook"] = website.get("facebook")

    time.sleep(2)

    for client in useeClients:
        if client.get("emails"):
            continue
        source = client.get("facebook", "")
        emails = fetch_email(source)  # Assume function exists
        client["emails"] = emails

    driver.quit()
    return useeClients


def update_clients(useeClients):
    url = "http://localhost:8080/api/v1/usee-client/"
    headers = {
        'Content-Type': 'application/json',
        'Cookie': "auth_token=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJkZXYiLCJyb2xlIjoiUk9MRV9BRE1JTiIsImlzcyI6InVzZWUtYXBwIiwiZXhwIjoxNzQwMTI4MjAxLCJpYXQiOjE3MzkyNjQyMDEsImp0aSI6IjRiMGYzMzQxLWE3ZmUtNDQwNC04ODEwLWQ5YmRiNmMxNDk2YSJ9.LKdJ29Sawq9IBHBAUru3HtQe3Bq_t3VCSW_Hc4sir-w; Path=/; Expires=Sat, 29 Jun 2052 08:56:41 GMT;"
    }
    for data_entry in useeClients:
        payload = json.dumps(data_entry)
        response = requests.put(url, headers=headers, data=payload)
        print(response.text)


# url = "http://localhost:8080/api/v1/usee-client?size=10000"
#
# payload = {}
# headers = {
#   'Cookie': "auth_token=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJkZXYiLCJyb2xlIjoiUk9MRV9BRE1JTiIsImlzcyI6InVzZWUtYXBwIiwiZXhwIjoxNzQwMTI4MjAxLCJpYXQiOjE3MzkyNjQyMDEsImp0aSI6IjRiMGYzMzQxLWE3ZmUtNDQwNC04ODEwLWQ5YmRiNmMxNDk2YSJ9.LKdJ29Sawq9IBHBAUru3HtQe3Bq_t3VCSW_Hc4sir-w; Path=/; Expires=Sat, 29 Jun 2052 08:56:41 GMT;"
# }
#
# response = requests.request("GET", url, headers=headers, data=payload)
# re = response.json()
# useeClients = re["returnobject"]["page"]["content"]


# Set up Chrome options (optional)
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--lang=en")
options.add_argument("--disable-usb-discovery")
# options.add_argument("--headless")  # Optional, run in headless mode

# Initialize the WebDriver
driver = webdriver.Chrome(options=options)
# names_urls = []
driver.get("https://www.facebook.com/")



# try:
#     # Locate and click the "Decline optional cookies" button
#     decline_button = driver.find_element(By.XPATH,
#                                          "//div[@aria-label='Decline optional cookies' and @role='button']")
#     decline_button.click()
#     print("Clicked 'Decline optional cookies' button.")
# except Exception as e:
#     print("No Decline optional cookies!")
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




# for i in range(len(useeClients)):
#     if useeClients[i]["facebook"]!="null":
#         continue
#     name = useeClients[i]["name"]
#     area = useeClients[i]["useeClientLocation"]["area"]
#     website = get_facebook_cafeteria(name, area)
#     useeClients[i]["facebook"] = website["facebook"]
# # Wait to observe result
# time.sleep(random.randint(3, 15))
# for i in range(len(useeClients)):
#     if not useeClients[i]["emails"]==[]:
#         continue
#     source = useeClients[i]["facebook"]
#     emails = fetch_email(source)
#     useeClients[i]["emails"] = emails
#     for email in emails:
#         if not email.__eq__("null"):
#             counter+=1
#
# headers = {
#     'Content-Type': 'application/json',
#     'Cookie': "auth_token=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJkZXYiLCJyb2xlIjoiUk9MRV9BRE1JTiIsImlzcyI6InVzZWUtYXBwIiwiZXhwIjoxNzQwMTI4MjAxLCJpYXQiOjE3MzkyNjQyMDEsImp0aSI6IjRiMGYzMzQxLWE3ZmUtNDQwNC04ODEwLWQ5YmRiNmMxNDk2YSJ9.LKdJ29Sawq9IBHBAUru3HtQe3Bq_t3VCSW_Hc4sir-w; Path=/; Expires=Sat, 29 Jun 2052 08:56:41 GMT;"
# }
# # API endpoint URL (replace with your actual endpoint)
# url = "http://localhost:8080/api/v1/usee-client/"
#
# # Assuming 'final' is your list of dictionaries
# for data_entry in useeClients:
#     # Send POST request with each entry as JSON
#     # print(data_entry)
#     payload = json.dumps(data_entry)
#     response = requests.request("PUT", url, headers=headers, data=payload)
#     print(response.text)
#
# print("All data sent to the API.")
# # print(response.text)
# print(counter)

start_page = 0
page = start_page
while True:
    print(f"Fetching page {page}...")
    useeClients = fetch_clients(page)
    if not useeClients:
        print("No more clients found. Stopping.")
        break
    processed_clients = process_clients(useeClients)
    update_clients(processed_clients)
    print(f"Finished processing page {page}.")
    page += 1
    time.sleep(5)  # Prevent overloading the server

driver.quit()


