from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID
class Register(BaseModel): email: EmailStr; password: str=Field(min_length=8); name: str=Field(min_length=1,max_length=100)
class Login(BaseModel): email: EmailStr; password: str
class CommunityIn(BaseModel): name:str; source:str='whatsapp'
class PasteIn(BaseModel): community_id:UUID; text:str
class WebhookMessage(BaseModel): sender:str; text:str; timestamp:datetime|None=None
class WebhookIn(BaseModel): community_id:UUID; messages:list[WebhookMessage]
class IntentIn(BaseModel): title:str; description:str; threshold:float=Field(default=.5,ge=0,le=1); is_active:bool=True
