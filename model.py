import json

from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

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

    def get_id(self):
        return self.email


class Document(BaseClass):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    country = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    author_name = Column(String, nullable=False)
    author_info = Column(String, nullable=False)
    stamp_info = Column(String, nullable=False)


class Apostile(BaseClass):
    __tablename__ = 'apostiles'

    id = Column(Integer, primary_key=True)
    number = Column(Integer, nullable=False, unique=True)
    date = Column(Date, nullable=False)
    is_archived = Column(Boolean, nullable=False, default=False)
    trusted_id = Column(Integer, nullable=False)
    trusted_type = Column(String, nullable=False)
    document_id = Column(Integer, ForeignKey('documents.id'),
                         nullable=False)


class TrustedInstitution(BaseClass):
    __tablename__ = 'trusted_institutions'

    id = Column(Integer, primary_key=True)
    institution_name = Column(String, nullable=False)
    person_name = Column(String, nullable=False)
    person_position = Column(String, nullable=False)
    sign_image_url = Column(String, nullable=False)
    stamp_info = Column(String)
    location = Column(String, nullable=False)
    is_archived = Column(Boolean, nullable=False)

    def info(self):
        return {
            'type': 'Організація',
            'location': self.location,
            'person_name': self.institution_name,
            'description': f'Відповідальна людина: {self.person_position} {self.person_name}',
            'sign_image_url': self.sign_image_url,
            'stamp_info': self.stamp_info,
            'change_state_url': f'/trusted/institution/change/{self.id}',
            'edit_url': f'/trusted/institution/edit/{self.id}',
            'is_archived': '+' if self.is_archived else '-'
        }

    def short(self):
        return f'{self.institution_name} (організація)'


class TrustedPerson(BaseClass):
    __tablename__ = 'trusted_persons'

    id = Column(Integer, primary_key=True)
    person_name = Column(String, nullable=False)
    sign_image_url = Column(String, nullable=False)
    stamp_info = Column(String)
    location = Column(String, nullable=False)
    licence_number = Column(String, nullable=False)
    is_archived = Column(Boolean, nullable=False)

    def info(self):
        return {
            'type': 'Особа',
            'location': self.location,
            'person_name': self.person_name,
            'description': f'Номер ліцензії: №{self.licence_number}',
            'sign_image_url': self.sign_image_url,
            'stamp_info': self.stamp_info,
            'change_state_url': f'/trusted/person/change/{self.id}',
            'edit_url': f'/trusted/person/edit/{self.id}',
            'is_archived': '+' if self.is_archived else '-'
        }

    def short(self):
        return f'{self.person_name} (особа)'


def db_session() -> Session:
    db_url = 'postgres://xexdpwud:OsOi5RKcsKW3hypB0xLPnc5f6sjmwBM6@isilo.db.elephantsql.com:5432/xexdpwud'
    engine = create_engine(db_url)
    BaseClass.metadata.create_all(engine)
    return sessionmaker(engine)()
