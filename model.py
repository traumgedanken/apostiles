from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

BaseClass = declarative_base()


class User(BaseClass):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default='keeper')
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(Date, nullable=False)


class Document(BaseClass):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    name = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    author_info = Column(String, nullable=False)

    apostile_id = Column(Integer, ForeignKey('apostile.id'),
                         nullable=False)


class Apostile(BaseClass):
    __tablename__ = 'apostile'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    is_archived = Column(Boolean, nullable=False, default=False)
    institution_id = Column(Integer, ForeignKey('trusted_institutions.id'),
                            nullable=False)


class TrustedInstitution(BaseClass):
    __tablename__ = 'trusted_institutions'

    id = Column(Integer, primary_key=True)
    person_name = Column(String, nullable=False)
    sign_image_url = Column(String)
    stamp_image_url = Column(String)
    info_type = Column(String, nullable=False)
    info_id = Column(Integer, nullable=False)


class AuthorityInfo(BaseClass):
    __tablename__ = 'authority_info'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    position = Column(String, nullable=False)


class PersonInfo(BaseClass):
    __tablename__ = 'person_info'

    id = Column(Integer, primary_key=True)
    registration_date = Column(Date, nullable=False)
    exparation_date = Column(Date, nullable=False)


class CourtInfo(BaseClass):
    __tablename__ = 'court_info'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)


class NotaryInfo(BaseClass):
    __tablename__ = 'notary_info'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    license_number = Column(Integer, nullable=False)
    location = Column(String, nullable=False)
    registration_date = Column(String)


class DepartmentInfo(BaseClass):
    __tablename__ = 'department_info'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    registration_date = Column(String)
    expiration_date = Column(String)


def db_session():
    db_url = 'postgres://xexdpwud:OsOi5RKcsKW3hypB0xLPnc5f6sjmwBM6@isilo.db.elephantsql.com:5432/xexdpwud'
    engine = create_engine(db_url, echo=True)
    BaseClass.metadata.create_all(engine)
    return sessionmaker(engine)()
