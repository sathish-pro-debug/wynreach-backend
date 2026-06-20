from pydantic import BaseModel


class AITemplateRequest(BaseModel):
    prompt: str


class AITemplateResponse(BaseModel):
    layout: str
    name: str
    font: str
    logo: str
    logoColor: str
    bgColor: str
    accentColor: str
    buttonColor: str
    buttonTextColor: str
    buttonText: str
    headerImg: str
    tag: str
    title: str
    subtitle: str
    body: str
    footerText: str