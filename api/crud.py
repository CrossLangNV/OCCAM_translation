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
                                   created=datetime.datetime.now()
                                   )
    db.add(db_xml_trans)
    db.commit()
    db.refresh(db_xml_trans)
    return db_xml_trans
