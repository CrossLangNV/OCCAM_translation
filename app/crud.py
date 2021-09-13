import datetime

from sqlalchemy.orm import Session

from . import models, schemas


def get_xml_trans(db: Session, xml_trans_id: int):
    return db.query(models.XMLTrans).filter(models.XMLTrans.id == xml_trans_id).first()


def get_xml_by_etranslation_id(db: Session, etranslation_id: str):
    return db.query(models.XMLTrans).filter(models.XMLTrans.etranslation_id == etranslation_id).first()


def get_xmls_trans(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.XMLTrans).offset(skip).limit(limit).all()


def create_xml_trans(db: Session,
                     xml_trans: schemas.XMLTransCreate):
    db_xml_trans = models.XMLTrans(etranslation_id=xml_trans.etranslation_id,
                                   xml_content=xml_trans.xml_content,
                                   filename=xml_trans.filename,
                                   source=xml_trans.source,
                                   target=xml_trans.target,
                                   use_tm=xml_trans.use_tm,
                                   created=datetime.datetime.now(),
                                   xml_document_id=xml_trans.xml_document_id
                                   )
    db.add(db_xml_trans)
    db.commit()
    db.refresh(db_xml_trans)
    return db_xml_trans


def get_document(db: Session, document_id: str):
    return db.query(models.XMLDocument).filter(models.XMLDocument.id == document_id).first()


def get_documents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.XMLDocument).offset(skip).limit(limit).all()


def create_xml_document(db: Session, xml_document: schemas.XMLDocumentCreate):
    db_xml_document = models.XMLDocument(
        source=xml_document.source,
        target=xml_document.target
    )
    db.add(db_xml_document)
    db.commit()
    db.refresh(db_xml_document)
    return db_xml_document


def get_lines(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.XMLDocumentLine).offset(skip).limit(limit).all()


def create_xml_document_line(db: Session, line: schemas.XMLDocumentLineCreate, document_id: int):
    db_xml_document_line = models.XMLDocumentLine(
        **line.dict(), document_id=document_id
    )
    db.add(db_xml_document_line)
    db.commit()
    db.refresh(db_xml_document_line)
    return db_xml_document_line
