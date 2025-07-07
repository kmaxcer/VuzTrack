from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from db.init_db import Session, Parser_links, Universities, Directions, Programs
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


for i in range(0, len(res), 3):
    direction_raw = res[i].split('\n')[1].split()
    direction = list(filter(lambda x: not x.isdigit(), direction_raw))
    code, direction_name = direction[0], ' '.join(direction[1:])
    program = res[i].split('\n')[0]
    level_code = code.split('.')[1]

    level = (
        'Бакалавриат' if level_code == '03' else
        'Специалитет' if level_code == '05' else
        'Магистратура' if level_code == '04' else
        'Аспирантура' if level_code == '06' else
        'Ординатура'
    )

    link = res[i + 2]
    num_budget = res[i + 1].split('\n')[2].split()[0]

    with Session() as session:
        university = session.query(Universities).filter_by(name='МИРэА').first()
        if not university:
            university = Universities(
                name='МИРэА',
                city='Москва',
                website='https://www.mirea.ru',
                created_at=1947
            )
            session.add(university)
            session.flush()

        direction_entry = session.query(Directions).filter_by(name=direction_name).first()
        if not direction_entry:
            direction_entry = Directions(
                code=code,
                name=direction_name,
                edu_level=level
            )
            session.add(direction_entry)
            session.flush()

        program_entry = session.query(Programs).filter_by(profile_name=program).first()
        if not program_entry:
            program = Programs(
                direction_id=direction_entry.direction_id,
                university_id=university.university_id,
                profile_name=program,
                study_form='В разработке',
                num_budget_places=num_budget,
                min_score=0
            )
            session.add(program)
            session.flush()

            parser_links = Parser_links(
                university_id=university.university_id,
                program_id=program.program_id,
                url=link,
                parser_type='selenium',
                last_checked=str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
            )
            session.add(parser_links)

        session.commit()