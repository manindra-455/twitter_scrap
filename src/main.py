import csv
import pandas as pd
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# List of user-agents to choose from
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    # Add more user agents as needed
]

# Function to get a random user-agent
def get_random_user_agent():
    return random.choice(user_agents)

# Configure Selenium options with a random user-agent
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (optional)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(f"user-agent={get_random_user_agent()}")

# Initialize the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Input and output file paths
input_file = 'twitter_scraping/data/twitter_links.csv'  # Input file with profile URLs
output_file = 'twitter_scraping/data/Final_data.csv'  # Output file for the extracted data

# Read CSV without headers
profile_links = pd.read_csv(input_file, header=None, names=['ProfileURL'])

# Initialize a list to store profile data
profile_data = []

# Define function to scrape a Twitter profile
def scrape_profile(url):
    driver.get(url)
    # Wait until page loads and try to capture elements, with up to 10 seconds wait
    wait = WebDriverWait(driver, 5)

    try:
        # Bio
        bio = wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@data-testid="UserDescription"]//span'))).text
    except:
        try:
            # Alternative path for Bio
            bio = wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@data-testid="UserDescription"]/div/span'))).text
        except:
            bio = None

    try:
        # Following Count
        following_count = wait.until(EC.visibility_of_element_located((By.XPATH, '//a[contains(@href, "/following")]/span[1]/span'))).text
    except:
        try:
            # Alternative path for Following Count
            following_count = wait.until(EC.visibility_of_element_located((By.XPATH, '//a[@href="/following"]/span[1]'))).text
        except:
            following_count = None

    try:
        # Followers Count
        followers_count = wait.until(EC.visibility_of_element_located((By.XPATH, '//a[contains(@href, "/verified_followers")]/span[1]/span'))).text
    except:
        try:
            # Alternative path for Followers Count
            followers_count = wait.until(EC.visibility_of_element_located((By.XPATH, '//a[@href="/verified_followers"]/span[1]'))).text
        except:
            followers_count = None

    try:
        # Location
        location = wait.until(EC.visibility_of_element_located((By.XPATH, '//span[@data-testid="UserLocation"]'))).text
    except:
        try:
            # Alternative path for Location
            location = wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@data-testid="UserProfileHeader_Items"]//span[@data-testid="UserLocation"]'))).text
        except:
            location = None

    try:
        # Website
        website = wait.until(EC.visibility_of_element_located((By.XPATH, '//a[@data-testid="UserUrl"]'))).text
    except:
        try:
            # Alternative path for Website
            website = wait.until(EC.visibility_of_element_located((By.XPATH, '//a[contains(@href, "https://t.co/") and @data-testid="UserUrl"]'))).text
        except:
            website = None

    return {
        "Bio": bio,
        "Following Count": following_count,
        "Followers Count": followers_count,
        "Location": location,
        "Website": website
    }

# Loop through each profile link
for index, row in profile_links.iterrows():
    url = row['ProfileURL']
    print(f"Scraping profile: {url}")
    profile_info = scrape_profile(url)
    profile_info['ProfileURL'] = url
    profile_data.append(profile_info)
   
    # Print each profile's data to the terminal in the desired format
    print(f"Profile URL: {url}")
    print(f"Bio: {profile_info['Bio']}")
    print(f"Following Count: {profile_info['Following Count']}")
    print(f"Followers Count: {profile_info['Followers Count']}")
    print(f"Location: {profile_info['Location']}")
    print(f"Website: {profile_info['Website']}")
    print("-" * 50)  # Separator for better readability in the terminal


# After completion, write the results to CSV
keys = profile_data[0].keys()  # Column headers
with open(output_file, 'w', newline='', encoding='utf-8') as output_csv:
    dict_writer = csv.DictWriter(output_csv, fieldnames=keys)
    dict_writer.writeheader()
    dict_writer.writerows(profile_data)

# Close the WebDriver
driver.quit()

print("Scraping complete. Data saved to", output_file)
