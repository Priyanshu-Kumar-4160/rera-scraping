import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def get_project_links(driver):
    driver.get("https://rera.odisha.gov.in/projects/project-list")

    try:
        # ✅ Wait for Search button and click it via JavaScript
        search_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "btnSearch"))
        )
        driver.execute_script("arguments[0].click();", search_button)
        print("✅ Clicked search button.")

        time.sleep(5)  # Allow time for results to load

        # ✅ Wait for the table to be present
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "tblList"))
        )
        print("✅ Table detected.")

        # ✅ Parse the rendered page source using BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        table = soup.find("table", id="tblList")
        if not table:
            print("❌ Table still not found after rendering.")
            return []

        rows = table.find_all("tr")[1:7]  # Skip header and get top 6 rows
        links = []
        for row in rows:
            a_tag = row.find("a", href=True)
            if a_tag:
                href = a_tag['href']
                full_link = "https://rera.odisha.gov.in" + href
                links.append(full_link)

        return links

    except Exception as e:
        print(f"❌ Error clicking search or loading table: {e}")
        return []

def get_project_details(driver, url):
    driver.get(url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    try:
        reg_no = soup.find("label", string="Rera Regd. No").find_next("div").text.strip()
        name = soup.find("label", string="Project Name").find_next("div").text.strip()
    except:
        reg_no = name = "N/A"

    return {
        "Rera Regd. No": reg_no,
        "Project Name": name
    }

def main():
    print("🚀 Starting Selenium browser...")
    options = Options()
    options.add_argument("--headless")  # Run without opening a browser
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    print("📥 Getting project list...")
    links = get_project_links(driver)

    if not links:
        print("❌ No project links found. Exiting.")
        driver.quit()
        return

    print("🔍 Scraping project details...")
    all_data = []
    for url in links:
        print(f"🔗 Scraping: {url}")
        data = get_project_details(driver, url)
        all_data.append(data)

    driver.quit()

    # ✅ Save to CSV
    df = pd.DataFrame(all_data)
    df.to_csv("rera_projects.csv", index=False)
    print("✅ Data saved to rera_projects.csv")

if __name__ == "__main__":
    main()
