from typing import List

from pydantic import BaseModel


class XMLTransBase(BaseModel):
    etranslation_id: str
    xml_content: str
    filename: str
    source: str
    target: str
    use_tm: bool
    xml_document_id: int


class XMLTransCreate(XMLTransBase):
    pass


class XMLTransOut(BaseModel):
    """Allowed information to return"""
    id: str


class XMLTrans(XMLTransBase, XMLTransOut):
    class Config:
        orm_mode = True


class XMLDocumentLineBase(BaseModel):
    text: str
    full_match: str


class XMLDocumentLineCreate(XMLDocumentLineBase):
    pass


class XMLDocumentLine(XMLDocumentLineBase):
    id: int
    document_id: int

    class Config:
        orm_mode = True


class XMLDocumentBase(BaseModel):
    source: str
    target: str


class XMLDocumentCreate(XMLDocumentBase):
    pass


class XMLDocument(XMLDocumentBase):
    id: int
    lines: List[XMLDocumentLine] = []

    class Config:
        orm_mode = True
