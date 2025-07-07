import os
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from db.init_db import Session, Parser_links


def setup_driver():
    options = Options()
    options.add_argument('--headless')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def parse_applicants_from_url(driver, url: str):
    driver.get(url)

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
    )

    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) >= 9:
            applicant_id = cols[1].text.strip()
            priority = cols[2].text.strip()
            original = cols[4].text.strip()
            agreement = cols[5].text.strip()
            ege_score = cols[10].text.strip()


def run_parse_only():
    session = Session()
    driver = setup_driver()

    links = session.query(Parser_links).all()

    for link in links:
        if link.parser_type.strip().lower() != "selenium":
            continue

        try:
            applicants = parse_applicants_from_url(driver, link.url)
            for a in applicants:
                print(a)

        except Exception:
            print(f"Ошибка")

    driver.quit()
    session.close()


if __name__ == "__main__":
    run_parse_only()