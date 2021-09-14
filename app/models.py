from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


# TODO delete items after they are processed?
class XMLTrans(Base):
    """
    Temporary database for the XML's
    """
    __tablename__ = "xml"

    id = Column(Integer, primary_key=True, index=True)
    etranslation_id = Column(String, unique=True, index=True)
    xml_document_id = Column(Integer, ForeignKey("document.id"))
    xml_content = Column(String)
    filename = Column(String, index=True)

    source = Column(String)
    target = Column(String)
    use_tm = Column(Boolean)

    created = Column(DateTime)
    finished = Column(DateTime, default=None)

    is_translated = Column(Boolean, default=False)


class XMLDocument(Base):
    """
    Table that holds XML document info
    """
    __tablename__ = "document"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String)
    target = Column(String)

    lines = relationship("XMLDocumentLine", back_populates="document")


class XMLDocumentLine(Base):
    """
    Table that holds a single XML document text line
    """
    __tablename__ = "line"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    full_match = Column(String)
    document_id = Column(Integer, ForeignKey("document.id"))

    document = relationship("XMLDocument", back_populates="lines")