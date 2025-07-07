from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db", "vuztrack.sqlite3")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=True)


class Base(DeclarativeBase):
    pass


#ТАБЛИЦА АБИТУРИЕНТОВ
class Applicants(Base):
    __tablename__ = 'applicants'
    applicant_id = Column(Integer, primary_key=True)
    registry_number = Column(String, nullable=False, unique=True)


#ТАБЛИЦА С РЕЗУЛЬТАТАМИ ОДНОГО АБИТУРИЕНТА
class Ege_results(Base):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True)
    applicant_id = Column(String, ForeignKey('applicants'), nullable=False)
    year = Column(Integer)
    math_score = Column(Integer)
    russian_score = Column(Integer)
    physics_score = Column(Integer)
    informatics_score = Column(Integer)
    chemistry_score = Column(Integer)
    biology_score = Column(Integer)
    geography_score = Column(Integer)
    literature_score = Column(Integer)
    history_score = Column(Integer)
    social_score = Column(Integer)
    foreign_score = Column(Integer)
    created_at = Column(Integer)


class Universities(Base):
    __tablename__ = 'universities'
    university_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    website = Column(String)
    created_at = Column(Integer)


class Directions(Base):
    __tablename__ = 'directions'
    direction_id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    edu_level = Column(String, nullable=False)


class Programs(Base):
    __tablename__ = 'programs'
    program_id = Column(Integer, primary_key=True)
    direction_id = Column(Integer, ForeignKey('directions'), nullable=False)
    university_id = Column(Integer, ForeignKey('universities'), nullable=False)
    profile_name = Column(String, nullable=False)
    study_form = Column(String, nullable=False)
    num_budget_places = Column(Integer)
    min_score = Column(Integer)


class Aplications(Base):
    __tablename__ = 'applications'
    id = Column(Integer, primary_key=True)
    applicant_id = Column(String, ForeignKey('applicants'), nullable=False)
    program_id = Column(String, ForeignKey('programs'), nullable=False)
    ege_total_score = Column(Integer)
    priority = Column(Integer)
    is_original = Column(Boolean)
    status = Column(String) # в конкурсе / зачислен / отклонен


class Parser_links(Base):
    __tablename__ = 'parser_links'
    parser_link_id = Column(Integer, primary_key=True)
    university_id = Column(Integer, ForeignKey('universities'), nullable=False)
    program_id = Column(Integer, ForeignKey('programs'), nullable=False)
    url = Column(String, nullable=False)
    parser_type = Column(String, nullable=False) # selenium / bs4...
    last_checked = Column(String, nullable=False)


class Parser_applicants(Base):
    __tablename__ = 'parser_applicants'
    id = Column(Integer, primary_key=True)
    parser_link_id = Column(Integer, ForeignKey('parser_links'), nullable=False)
    program_id = Column(String, ForeignKey('programs'), nullable=False)
    rank = Column(Integer)
    total_score = Column(Integer)
    is_original = Column(Boolean)
    snils_hash = Column(String)


Base.metadata.create_all(engine)


Session = sessionmaker(bind=engine)