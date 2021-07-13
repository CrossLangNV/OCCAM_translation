import io
import os
import tempfile
from time import sleep
from typing import List
from typing import Optional

from fastapi import Depends, FastAPI
from fastapi import UploadFile, File, Response, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse
from xml_orm.orm import XLIFFPageXML

from connector.translate_connector import ETranslationConnector
from tm.tm_connector import MouseTmConnector
from . import crud, models, schemas
from .database import SessionLocal, engine
from .models import XMLDocument
from .schemas import XMLDocumentCreate, XMLDocumentLineCreate

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# def clear_data(session):
#     meta = db.metadata
#     for table in reversed(meta.sorted_tables):
#         print() 'Clear table %s' % table)
#         session.execute(table.delete())
#     session.commit()
b = 0
if b:
    db = next(get_db())

    db.drop_all()

    # clear_data

    # db.query(models.XMLTrans).delete()
    # db.commit()


# SessionLocal().query(models.XMLTrans).delete()

@app.get("/")
async def root():
    return {"message": "FASTAPI for the microservice: translation of layout XML."}


class SourceTarget(BaseModel):
    source: Optional[str] = None
    target: str


@app.post("/translate/xml/blocking")
async def translate_page_xml(file: UploadFile = File(...),
                             source: str = Header(...),
                             target: str = Header(...),
                             db: Session = Depends(get_db),
                             ) -> Response:  # TODO type of response
    """

    Args:
        file: XML in Page or XLIFF-Page format.

    Returns:
        The XML expanded with a translation
    """

    xml = XLIFFPageXML.from_page(file.file, source_lang=source)

    db_xml_trans = _submit_page_xml_translation(xml, source, target,
                                                filename=file.filename,
                                                db=db)

    # r = await submit_page_xml_translation(file=file,
    #                             source=source,
    #                             target=target)

    # TODO wait for response to be done
    # return r

    while True:
        r = _read_page_xml_translation(db_xml_trans.etranslation_id, target=target, db=db)
        if r.status_code < 300:
            return r
        else:
            sleep(1)  # Time in seconds

    # Re-Use the non-blocking
    # @app.post("/similar_terms/self/")
    # async def align_voc_self(vocs: SingleVoc) -> Dict[str, str]:
    #     result = align_vocs(DoubleVoc(voc1=vocs.voc, voc2=vocs.voc))
    #
    #     return await result


class XMLTransOut(BaseModel):
    id: str


@app.post("/translate/xml", response_model=XMLTransOut)
async def submit_page_xml_translation(file: UploadFile = File(...),
                                      source: str = Header(...),
                                      target: str = Header(...),
                                      db: Session = Depends(get_db)
                                      ) -> Response:  # TODO type of response
    """ Async

    Args:
        file: XML in Page or XLIFF-Page format.

    Returns:
        The id to check if the XML is finished translating
    """

    xml = XLIFFPageXML.from_page(file.file, source_lang=source)

    db_xml_trans = _submit_page_xml_translation(xml, source=source, target=target,
                                                filename=file.filename,
                                                db=db)

    return XMLTransOut(id=db_xml_trans.etranslation_id)  # db_xml_trans # Response({'id': id_doc})


@app.get("/translate/xml/{xml_id}")
async def read_page_xml_translation(xml_id: str,
                                    db: Session = Depends(get_db),
                                    ) -> Response:
    """ Retrieve xml

    Args:
        file: XML in Page or XLIFF-Page format.

    Returns:
        The XML expanded with a translation
    """

    db_xml_trans = crud.get_xml_by_etranslation_id(db=db,
                                                   etranslation_id=xml_id)

    # db_xml_trans = crud.create_xml_trans(db=db,
    #                                      xml_trans=xml_trans,
    #
    #                                      )

    return _read_page_xml_translation(db_xml_trans.etranslation_id, target=db_xml_trans.target, db=db)


def _submit_page_xml_translation(xml, source, target, filename,
                                 db):
    # ORM of XML
    # convert file to XLIFF Page.
    # TODO check if XLIFF. If so, no need to convert to XLIFF from Page.
    # TODO check if ALREADY XLIFF, then no need for "from page"

    # Make sure the XML is valid.
    # TODO this could be removed in the future when we are sure the XML is always valid.
    try:
        xml.validate()
    except:
        xml.auto_fix()
    finally:
        # If it can't be fixed, probably not safe to continue
        xml.validate()

    # translation
    connector = ETranslationConnector()

    # First send trans requests, then request the response.
    lines_text = xml.get_lines_text()

    db_xml_document = _parse_text_page_xml(lines_text, source, target, db)
    lines = []
    for document_line in db_xml_document.lines:
        if document_line.match:
            lines.append('')
        else:
            lines.append(document_line.text)
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = os.path.join(tmp_dir, 'tmp_text_lines.txt')
        s_tmp = ''.join(text_i + '\n' for text_i in lines)
        with open(tmp_file, 'w') as f:
            f.write(s_tmp)
        id_doc = connector.trans_doc(source, target, tmp_file)

    xml_trans = schemas.XMLTransCreate(etranslation_id=id_doc,
                                       xml_content=xml.to_bstring(),
                                       filename=filename,
                                       source=source,
                                       target=target,
                                       xml_document_id=db_xml_document.id)

    db_xml_trans = crud.create_xml_trans(db=db,
                                         xml_trans=xml_trans,
                                         )

    return db_xml_trans


def _read_page_xml_translation(xml_id, target, db):
    # translation
    connector = ETranslationConnector()

    r = connector.trans_doc_id(xml_id)
    db_xml_trans = crud.get_xml_by_etranslation_id(db=db,
                                                   etranslation_id=xml_id)
    db_xml_document = crud.get_document(db=db, document_id=db_xml_trans.xml_document_id)
    if r:
        l_trans_text = list(map(str.strip, r.get('content').decode('UTF-8').splitlines()))
        l_trans_text = _update_trans_text_lines_with_matches(l_trans_text, db_xml_document)
    else:
        content = {'message': 'translation not finished.'}
        return JSONResponse(content, status_code=423)

    xml = XLIFFPageXML(io.BytesIO(db_xml_trans.xml_content.encode('utf-8')))

    # Add to XML
    xml.add_targets(l_trans_text, target)

    data = xml.to_bstring()

    basename, ext = db_xml_trans.filename.split('.', 1)

    filename_out = f'{basename}_trans.{ext}'

    return StreamingResponse(io.BytesIO(data),
                             media_type="application/xml",
                             # "text/xml" if readable from casual users (RFC 3023, section 3)
                             headers={
                                 "Content-Disposition": f"attachment;filename={filename_out}"
                             }
                             )


@app.get("/translate/xmls/", response_model=List[schemas.XMLTrans])
def read_trans_xmls(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_xmls_trans(db, skip=skip, limit=limit)
    return users


def _parse_text_page_xml(lines, source, target, db):
    xml_document = XMLDocumentCreate(
        source=source,
        target=target
    )

    db_xml_document = crud.create_xml_document(db, xml_document)

    for line in lines:
        full_match = _lookup_full_tm_match(line, source + '-' + target)
        xml_document_line = XMLDocumentLineCreate(
            text=line,
            match=full_match,
            document_id=db_xml_document.id
        )
        crud.create_xml_document_line(db, xml_document_line, db_xml_document.id)

    return db_xml_document


def _update_trans_text_lines_with_matches(translated_lines, db_xml_document: XMLDocument):
    updated_lines_with_matches = []
    document_lines = db_xml_document.lines
    for translation, document_line in zip(translated_lines, document_lines):
        if document_line.match:
            updated_lines_with_matches.append(document_line.match)
        else:
            updated_lines_with_matches.append(translation)

    return updated_lines_with_matches


def _lookup_full_tm_match(segment, langpair):
    mouse = MouseTmConnector()

    matches = mouse.lookup_tu(False, "", langpair, segment)

    full_match = ""
    for match in matches:
        if match["match"] >= 1.0:
            full_match = match["translation"]
            break

    return full_match
