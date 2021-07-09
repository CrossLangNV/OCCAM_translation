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
