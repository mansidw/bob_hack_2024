from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Set up the Selenium WebDriver (you might need to install the appropriate driver)
driver = webdriver.Chrome()

# Navigate to the URL
driver.get("https://www.bankofbaroda.in/personal-banking/loans/gold-loan")

# Wait for some time to manually solve the CAPTCHA (or handle it with a service)
# time.sleep(60)  # Adjust this sleep time based on the time you need to solve the CAPTCHA

# After solving the CAPTCHA, extract the page source
html = driver.page_source

# Use BeautifulSoup to parse the HTML
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, "html.parser")

# Find all the links
urls = []
for link in soup.find_all("a"):
    print(link.get("href"))

# Close the browser
driver.quit()
