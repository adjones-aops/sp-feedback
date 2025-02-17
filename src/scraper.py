# src/scraper.py

import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def authenticate_and_get_page(url: str, timeout: int = 300):
    """
    Opens a Chrome browser, waits for manual login/MFA, then navigates to the given URL.

    Args:
        url (str): The target URL to scrape after authentication.
        timeout (int): Maximum seconds to wait for manual login.

    Returns:
        driver, page_source: The Selenium driver instance and the HTML page source after navigation.
    """
    # Set up Chrome options (do not run headless because you need to complete MFA manually)
    options = Options()
    # Uncomment the following line if you want a non-headless browser (required for MFA)
    # options.headless = False

    # Initialize the WebDriver (ensure that chromedriver is in your PATH)
    driver = webdriver.Chrome(options=options)

    # Open the base site so that you can log in
    driver.get("https://artofproblemsolving.com")
    print("Browser opened. Please log in and complete MFA.")

    # Wait until an element indicating a successful login is present.
    # In this case, we're waiting for the "Sign out" button, which has the id "header-logout"
    wait = WebDriverWait(driver, timeout)
    try:
        wait.until(EC.presence_of_element_located((By.ID, "header-logout")))
    except Exception as e:
        print("Error or timeout waiting for login:", e)
        driver.quit()
        return None, None

    print("Login successful. Navigating to the self-paced feedback page...")
    # Navigate to the target feedback page
    driver.get(url)

    # Wait for a key element on the feedback page to load.
    # Here we wait for at least one element with the class "card" which wraps individual feedback entries.
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "card")))
    except Exception as e:
        print("Error or timeout waiting for the feedback page to load:", e)
        driver.quit()
        return None, None

    # Optionally, sleep a little extra time if needed to ensure full load
    time.sleep(2)

    page_source = driver.page_source
    return driver, page_source


if __name__ == "__main__":
    FEEDBACK_URL = "https://artofproblemsolving.com/reports/self-paced-feedback"
    driver, page_html = authenticate_and_get_page(FEEDBACK_URL)
    if page_html:
        # Determine output directory relative to this file.
        output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, "feedback_page.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(page_html)
        print(f"Page source saved to {filepath}")
    else:
        print("Failed to retrieve the page.")
