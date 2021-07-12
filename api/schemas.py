from typing import List

from pydantic import BaseModel


class XMLTransBase(BaseModel):
    etranslation_id: str
    xml_content: str
    filename: str
    source: str
    target: str


class XMLTransCreate(XMLTransBase):
    pass


class XMLTrans(XMLTransBase):
    id: int

    class Config:
        orm_mode = True


class XMLDocumentLineBase(BaseModel):
    text: str
    match: str


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
