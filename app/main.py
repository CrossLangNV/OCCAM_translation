import io
import os
import tempfile
from itertools import cycle
from time import sleep
from typing import List
from typing import Optional

from fastapi import Depends, FastAPI
from fastapi import UploadFile, File, Response, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse
from xml_orm.orm import XLIFFPageXML

from tm.tm_connector import MouseTmConnector
from translation.connector.cef_etranslation import ETranslationConnector
from translation.translate_xml import SentenceParser
from . import crud, models, schemas
from .database import SessionLocal, engine
from .models import XMLDocument
from .schemas import XMLDocumentCreate, XMLDocumentLineCreate, XMLTransOut

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


b = 0
if b:
    db = next(get_db())

    db.drop_all()


@app.get("/")
async def root():
    return {"message": "FASTAPI for the microservice: translation of layout XML."}


@app.post("/translate/xml/blocking")
async def translate_page_xml(file: UploadFile = File(...),
                             source: str = Header(...),
                             target: str = Header(...),
                             use_tm: Optional[bool] = Header(False),
                             db: Session = Depends(get_db),
                             ) -> Response:
    """

    Args:
        file: XML in Page or XLIFF-Page format.

    Returns:
        The XML expanded with a translation
    """

    xml = XLIFFPageXML.from_page(file.file, source_lang=source)

    db_xml_trans = _submit_page_xml_translation(xml, source, target,
                                                filename=file.filename,
                                                use_tm=use_tm,
                                                db=db)

    while True:
        r = _read_page_xml_translation(db_xml_trans.etranslation_id, target=target, use_tm=use_tm, db=db)
        if r.status_code < 300:
            return r
        else:
            sleep(1)  # Time in seconds


@app.post("/translate/xml", response_model=XMLTransOut)
async def submit_page_xml_translation(file: UploadFile = File(...),
                                      source: str = Header(...),
                                      target: str = Header(...),
                                      use_tm: Optional[bool] = Header(False),
                                      db: Session = Depends(get_db)
                                      ):
    """ Async

    Args:
        file: XML in Page or XLIFF-Page format.

    Returns:
        The id to check if the XML is finished translating
    """

    xml = XLIFFPageXML.from_page(file.file, source_lang=source)

    db_xml_trans = _submit_page_xml_translation(xml, source=source, target=target,
                                                filename=file.filename,
                                                use_tm=use_tm,
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

    return _read_page_xml_translation(db_xml_trans.etranslation_id,
                                      target=db_xml_trans.target,
                                      use_tm=db_xml_trans.use_tm,
                                      db=db)


@app.get("/translate/xmls/", response_model=List[schemas.XMLTrans])
def read_trans_xmls(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Returns all the XML's saved in the database.
    """
    users = crud.get_xmls_trans(db, skip=skip, limit=limit)
    return users


def _submit_page_xml_translation(xml, source, target, filename, use_tm, db):
    # ORM of XML
    # convert file to XLIFF Page.

    # Make sure the XML is valid.
    try:
        xml.validate()
    except:
        xml.auto_fix()
        # If it can't be fixed, probably not safe to continue
        xml.validate()

    # translation
    connector = ETranslationConnector()

    # First send trans requests, then request the response.

    # Get sentences from the textlines
    parser = SentenceParser(xml)
    lines_text = parser.get_sentences()

    if use_tm:
        # Create a XML Document object that holds 100% TM matches
        db_xml_document = _parse_text_page_xml(lines_text, source, target, db)
        lines_text = []
        for document_line in db_xml_document.lines:
            # if there's a 100% TM match, don't send the source text to MT, append empty line
            if document_line.full_match:
                lines_text.append('')
            else:
                lines_text.append(document_line.text)
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = os.path.join(tmp_dir, 'tmp_text_lines.txt')
        s_tmp = ''.join(text_i + '\n' for text_i in lines_text)
        with open(tmp_file, 'w') as f:
            f.write(s_tmp)
        # send to MT
        id_doc = connector.trans_doc(source, target, tmp_file)

    xml_trans = schemas.XMLTransCreate(etranslation_id=id_doc,
                                       xml_content=xml.to_bstring(),
                                       filename=filename,
                                       source=source,
                                       target=target,
                                       use_tm=use_tm,
                                       xml_document_id=db_xml_document.id if use_tm else -1)

    db_xml_trans = crud.create_xml_trans(db=db,
                                         xml_trans=xml_trans,
                                         )

    return db_xml_trans


def _read_page_xml_translation(xml_id, target, use_tm, db) -> Response:
    # translation
    connector = ETranslationConnector()

    r = connector.trans_doc_id(xml_id)
    db_xml_trans = crud.get_xml_by_etranslation_id(db=db,
                                                   etranslation_id=xml_id)

    with io.BytesIO(db_xml_trans.xml_content.encode('utf-8')) as f:
        xml_orm = XLIFFPageXML(f)

    if use_tm:
        db_xml_document = crud.get_document(db=db, document_id=db_xml_trans.xml_document_id)

    if r:
        l_trans_sent = list(map(str.strip, r.get('content').decode('UTF-8').splitlines()))
        if use_tm:
            l_trans_sent = _update_trans_text_lines_with_matches(l_trans_sent, db_xml_document)

        # Get sentences from the textlines
        parser = SentenceParser(xml_orm)
        region_lines_new = parser.reconstruct_lines(l_trans_sent)
        l_trans_text = [line for region in region_lines_new for line in region]

    else:
        content = {'message': 'translation not finished.'}
        return JSONResponse(content, status_code=423)

    # Add to XML
    xml_orm.add_targets(l_trans_text, target)

    data = xml_orm.to_bstring()

    basename, ext = db_xml_trans.filename.split('.', 1)

    filename_out = f'{basename}_trans.{ext}'

    return StreamingResponse(io.BytesIO(data),
                             media_type="application/xml",
                             # "text/xml" if readable from casual users (RFC 3023, section 3)
                             headers={
                                 "Content-Disposition": f"attachment;filename={filename_out}"
                             }
                             )


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
            full_match=full_match,
            document_id=db_xml_document.id
        )
        crud.create_xml_document_line(db, xml_document_line, db_xml_document.id)

    return db_xml_document


def _update_trans_text_lines_with_matches(translated_lines, db_xml_document: XMLDocument):
    updated_lines_with_matches = []
    document_lines = db_xml_document.lines
    if len(translated_lines) == 0:
        translated_lines = ['']
    for document_line, translation in zip(document_lines, cycle(translated_lines)):
        if document_line.full_match:
            updated_lines_with_matches.append(document_line.full_match)
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
