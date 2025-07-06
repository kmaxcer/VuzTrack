from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Открытие страницы
driver.get("https://priem.mirea.ru/accepted-entrants-list/")
time.sleep(2)

html = driver.page_source

rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
res = []
for i, row in enumerate(rows):
    if "Общий конкурс" in row.text:
        res.append(rows[i - 1].text)
        res.append(rows[i].text)
        res.append(rows[i].find_element(By.TAG_NAME, "a").get_attribute("href"))

driver.quit()


from db.models import insert_parsing_source


for i in range(0, len(res), 3):
    direction = ' '.join(res[i].split('\n')[1].split()[:-2])

    program_name = res[i].split('\n')[0]
    link = res[i + 2]

    print('Вуз МИРЭА')
    print('Специальность:', direction)
    print('Программа:', program_name)
    print('Ссылка для парсинга:', link)

    data_for_db = {
        "university_id": 1,
        "program_name": direction,
        "profile": program_name,
        "data_url": link,
        "file_type": "html",
        "parser_key": "mirea",
        "enabled": 1
    }

    insert_parsing_source(data_for_db)