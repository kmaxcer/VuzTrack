import sqlite3

def create_db():
    schema = '''
    CREATE TABLE IF NOT EXISTS universities (
        university_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        short_name TEXT,
        region TEXT,
        url TEXT
    );

    CREATE TABLE IF NOT EXISTS programs (
        program_id INTEGER PRIMARY KEY AUTOINCREMENT,
        university_id INTEGER NOT NULL,
        code TEXT,
        name TEXT NOT NULL,
        profile TEXT,
        education_form TEXT,
        level TEXT,
        year INTEGER DEFAULT 2025,
        budget_seats INTEGER DEFAULT 0,
        FOREIGN KEY (university_id) REFERENCES universities(university_id)
    );

    CREATE TABLE IF NOT EXISTS applicants (
        applicant_id TEXT PRIMARY KEY,
        name TEXT,
        is_hidden INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS applications (
        application_id INTEGER PRIMARY KEY AUTOINCREMENT,
        applicant_id TEXT NOT NULL,
        program_id INTEGER NOT NULL,
        submission_date DATE DEFAULT CURRENT_DATE,
        ege_score INTEGER,
        individual_achievements INTEGER,
        total_score INTEGER,
        priority INTEGER,
        application_type TEXT,
        is_original_docs INTEGER DEFAULT 0,
        consent_to_enroll INTEGER DEFAULT 0,
        FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id),
        FOREIGN KEY (program_id) REFERENCES programs(program_id)
    );

    CREATE TABLE IF NOT EXISTS application_history (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        applicant_id TEXT NOT NULL,
        program_id INTEGER NOT NULL,
        check_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        total_score INTEGER,
        is_present INTEGER DEFAULT 1,
        rank_position INTEGER,
        priority INTEGER,
        FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id),
        FOREIGN KEY (program_id) REFERENCES programs(program_id)
    );

    CREATE TABLE IF NOT EXISTS parsing_sources (
    source_id INTEGER PRIMARY KEY AUTOINCREMENT,
    university_id INTEGER NOT NULL,
    program_name TEXT,
    profile TEXT,
    data_url TEXT NOT NULL,
    file_type TEXT DEFAULT 'html',
    parser_key TEXT,
    last_checked DATETIME,
    enabled INTEGER DEFAULT 1,
    FOREIGN KEY (university_id) REFERENCES universities(university_id)
);
    '''

    conn = sqlite3.connect("vuztrack.sqlite")
    cursor = conn.cursor()
    cursor.executescript(schema)
    conn.commit()
    conn.close()
    print("✅ База данных успешно создана: vuztrack.sqlite")

if __name__ == "__main__":
    create_db()