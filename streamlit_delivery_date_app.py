import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from io import StringIO

# Automatically install the correct version of chromedriver
chromedriver_autoinstaller.install()

# Set up Chrome options for headless browser
chrome_options = Options()
chrome_options.add_argument("--headless")  # Optional: run in headless mode (no browser UI)
chrome_options.add_argument("--disable-gpu")  # To avoid issues on some systems
chrome_options.add_argument("--no-sandbox")  # To avoid issues on some systems

# Initialize WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Function to load Excel file into a list (considering headers)
def load_excel(file, column_name):
    """Load the Excel file and return the specified column as a list."""
    df = pd.read_excel(file)
    return df[column_name].tolist()  # Return the values of the specified column

# Function to scrape delivery location and time for a given URL and pincode
def scrape_delivery_data(driver, url, pincode):
    driver.get(url)
    time.sleep(5)  # Wait for JavaScript to load content

    try:
        # Step 1: Open the pincode update pop-up
        change_pincode_button = driver.find_element(By.ID, "contextualIngressPtLabel")
        change_pincode_button.click()
        time.sleep(2)  # Wait for the pincode pop-up to appear

        # Step 2: Enter the new pincode
        pincode_input = driver.find_element(By.ID, "GLUXZipUpdateInput")
        pincode_input.clear()
        pincode_input.send_keys(pincode)
        time.sleep(1)

        # Submit the updated pincode
        submit_button = driver.find_element(By.ID, "GLUXZipUpdate")
        submit_button.click()
        time.sleep(5)  # Wait for the page to refresh

        # Parse the updated page source
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract delivery location
        anchor = soup.select_one("a#contextualIngressPtLink")
        delivery_location = anchor.get("aria-label") if anchor else "N/A"

        # Extract delivery time
        span = soup.select_one("#deliveryBlockContainer #deliveryBlock_feature_div #deliveryBlockMessage #mir-layout-DELIVERY_BLOCK .a-spacing-base span")
        delivery_time = span.get("data-csa-c-delivery-time") if span else "N/A"

        return delivery_location, delivery_time
    except Exception as e:
        print(f"Error while processing {url} with pincode {pincode}: {e}")
        return "Error", "Error"

# Streamlit app
def main():
    # Streamlit title and description
    st.title("Amazon Delivery Location and Time Scraper")
    st.write("Upload your Excel files containing pincodes and URLs, and get delivery location and time details.")

    # File upload widget for pincodes and URLs
    pincode_file = st.file_uploader("Upload Pincode File (Excel)", type=["xlsx"])
    url_file = st.file_uploader("Upload URL File (Excel)", type=["xlsx"])

    # If both files are uploaded
    if pincode_file and url_file:
        # Load the Excel files
        pincodes = load_excel(pincode_file, 'Pincode')
        urls = load_excel(url_file, 'URL')

        # Set up Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Optional: run in headless mode (no browser UI)
        service = Service(chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Output results
        results = []

        # Process each URL and pincode combination
        for url in urls:
            for pincode in pincodes:
                # st.write(f"Processing URL: {url} with Pincode: {pincode}")
                delivery_location, delivery_time = scrape_delivery_data(driver, url, pincode)
                results.append([url, pincode, delivery_location, delivery_time])

        # Convert results to DataFrame
        df_results = pd.DataFrame(results, columns=["URL", "Pincode", "Delivery Location", "Delivery Time"])

        # Display the results in the app
        st.write("Delivery Details:", df_results)

        # Provide an option to download the results as a CSV
        csv = df_results.to_csv(index=False)
        st.download_button(
            label="Download Results as CSV",
            data=csv,
            file_name="delivery_results.csv",
            mime="text/csv"
        )

        # Close the browser
        driver.quit()

if __name__ == "__main__":
    main()
