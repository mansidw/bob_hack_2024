from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import json
import re
from bs4 import BeautifulSoup

# Set up the Selenium WebDriver (you might need to install the appropriate driver)

# Path to your JSON file
file_path = "data.json"
bob = [
    "https://www.bankofbaroda.in/personal-banking/accounts/saving-accounts",
    "https://www.bankofbaroda.in/personal-banking/accounts/salary-accounts",
    "https://www.bankofbaroda.in/personal-banking/accounts/current-accounts",
    "https://www.bankofbaroda.in/personal-banking/accounts/term-deposit",
    "https://www.bankofbaroda.in/personal-banking/loans/home-loan",
    "https://www.bankofbaroda.in/personal-banking/loans/vehicle-loan",
    "https://www.bankofbaroda.in/personal-banking/loans/personal-loan",
    "https://www.bankofbaroda.in/personal-banking/loans/baroda-yoddha-loans",
    "https://www.bankofbaroda.in/personal-banking/loans/education-loan",
    "https://www.bankofbaroda.in/personal-banking/loans/other-loans",
    "https://www.bankofbaroda.in/personal-banking/loans/gold-loan",
    "https://www.bankofbaroda.in/personal-banking/loans",
    "https://www.bankofbaroda.in/personal-banking/investments",
    "https://www.bankofbaroda.in/personal-banking/insurance",
    "https://www.bankofbaroda.in/personal-banking/digital-products",
    "https://www.bankofbaroda.in/personal-banking/other-services",
]

for i in bob:
    driver = webdriver.Chrome()
    driver.get(i)
    time.sleep(10)
    html = driver.page_source

    soup = BeautifulSoup(html, "html.parser")

    # print(soup.find_all("a"))

    urls = []
    for link in soup.find_all("a"):
        print(link.get("href"))
        if i in link.get("href"):
            print("yes inn")
            urls.append(link.get("href"))

    # Load the JSON file into a dictionary
    with open(file_path, "r") as file:
        data = json.load(file)

    # Modify the dictionary (e.g., add a new key-value pair)
    match = re.search(r"^(?:[^/]*\/){4}(.*)", i)

    # Extract the matched group
    if match:
        result = match.group(1)
    else:
        result = ""
    new_key = result
    new_value = urls
    data[new_key] = new_value

    # Write the updated dictionary back to the JSON file
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

    # print(f"Added {new_key}: {new_value} to the JSON file.")

    # Close the browser
    driver.quit()
