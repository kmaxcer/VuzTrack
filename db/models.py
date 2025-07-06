import sqlite3
from db.config import DB_PATH


def insert_parsing_source(data):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""INSERT INTO parsing_sources
                (university_id, program_name, profile, data_url, file_type, parser_key, enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    data['university_id'],  # например, 1
                    data['program_name'],  # строка
                    data['profile'],  # строка (код + направление)
                    data['data_url'],  # ссылка
                    data.get('file_type', 'html'),  # default html
                    data.get('parser_key', 'mirea'),
                    data.get('enabled', 1)
                ))

    conn.commit()
    conn.close()
    print(f"✅ Добавлено: {data['program_name']}")