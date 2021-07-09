from sqlalchemy import Boolean, Column, Integer, String, DateTime

from .database import Base


# TODO delete items after they are processed?
class XMLTrans(Base):
    """
    Temporary database for the XML's
    """
    __tablename__ = "xml"

    id = Column(Integer, primary_key=True, index=True)
    etranslation_id = Column(String, unique=True, index=True)
    xml_content = Column(String)
    filename = Column(String, index=True)

    source = Column(String)
    target = Column(String)

    created = Column(DateTime)
    finished = Column(DateTime, default=None)

    is_translated = Column(Boolean, default=False)
