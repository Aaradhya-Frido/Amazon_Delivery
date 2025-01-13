from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller

# Automatically install the correct version of ChromeDriver
chromedriver_autoinstaller.install()

# Set up Selenium WebDriver in headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Headless mode (no GUI)
chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
chrome_options.add_argument("--no-sandbox")  # Disable sandbox (needed for headless mode)

# Initialize the driver
driver = webdriver.Chrome(options=chrome_options)

# Open a webpage (Amazon as an example)
driver.get("https://www.amazon.in")

# Get the page title to ensure the driver works
print(driver.title)

# Close the driver
driver.quit()
