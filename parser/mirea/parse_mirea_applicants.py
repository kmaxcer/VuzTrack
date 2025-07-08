import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from db.init_db import Session, Parser_links, Applicants, Aplications, Parser_applicants, Ege_results


def setup_driver():
    options = Options()
    options.add_argument('--headless')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def parse_applicants_from_url(driver, url, program_id, parser_link_id):
    driver.get(url)

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
    )

    subjects = []
    try:
        thead = driver.find_element(By.CSS_SELECTOR, "table thead")
        headers = thead.find_elements(By.TAG_NAME, "th")
        for header in headers:
            if header.text.strip().startswith("Оценки"):
                lines = header.text.strip().split("\n")
                subjects = [x.strip() for x in lines[1:] if x.strip()]
                break
    except Exception:
        pass

    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    res = []

    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) >= 11:
            rank = cols[0].text.strip()
            applicant_id = cols[1].text.strip()
            priority = cols[2].text.strip()
            original = cols[4].text.strip()
            ege_score = cols[10].text.strip()

            scores_text = cols[7].text.strip()
            score_values = [int(x) for x in scores_text.split() if x.isdigit()]
            subject_scores = dict(zip(subjects, score_values))

            res.append({
                "parser_link_id": parser_link_id,
                "program_id": program_id,
                "rank": rank,
                "total_score": ege_score,
                "is_original": None,
                "snils_hash": applicant_id,
                "priority": priority,
                "status": "в конкурсе",
                "subject_scores": subject_scores
            })

    return res


def run_parse():
    session = Session()
    driver = setup_driver()

    links = session.query(Parser_links).all()

    for link in links:
        if link.parser_type.strip().lower() != "selenium":
            continue

        try:
            applicants = parse_applicants_from_url(driver,
                                                   link.url,
                                                   link.parser_link_id,
                                                   link.program_id
                                                   )
            SUBJECT_FIELD_MAP = {
                "Математика": "math_score",
                "Русский язык": "russian_score",
                "Физика": "physics_score",
                "Информатика": "informatics_score",
                "Химия": "chemistry_score",
                "Биология": "biology_score",
                "География": "geography_score",
                "Литература": "literature_score",
                "История": "history_score",
                "Обществознание": "social_score",
                "Иностранный язык": "foreign_score",
            }

            for applicant in applicants:
                # 1. Добавляем в Applicants (если нужно — можно добавить проверку на дубликаты)
                applicant_entry = Applicants(
                    registry_number=applicant["snils_hash"],
                )
                session.add(applicant_entry)
                session.flush()  # теперь доступен applicant_entry.applicant_id

                applicant_id = applicant_entry.registry_number

                # 2. Добавляем предметные баллы в Ege_results
                subject_scores = applicant.get("subject_scores", {})
                score_args = {}

                for subject, value in subject_scores.items():
                    db_field = SUBJECT_FIELD_MAP.get(subject)
                    if db_field:
                        score_args[db_field] = value

                ege = Ege_results(
                    applicant_id=applicant_id,
                    year=2025,
                    created_at=int(time.time()),
                    **score_args
                )
                session.add(ege)

                aplication_entry = Aplications(
                    applicant_id=applicant_id,
                    program_id=applicant["program_id"],
                    ege_total_score=applicant["total_score"],
                    priority=applicant["priority"],
                    is_original=applicant["is_original"],
                    status=applicant["status"]
                )
                session.add(aplication_entry)

                parser_applicants_entry = Parser_applicants(
                    parser_link_id=applicant["parser_link_id"],
                    program_id=applicant["program_id"],
                    rank=applicant["rank"],
                    total_score=applicant["total_score"],
                    is_original=applicant["is_original"],
                    snils_hash=applicant["snils_hash"]
                )
                session.add(parser_applicants_entry)

            session.commit()


        except Exception:
            print("Ошибка")

    driver.quit()
    session.close()


if __name__ == "__main__":
    run_parse()