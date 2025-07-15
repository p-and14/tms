from pydantic import BaseModel, EmailStr


class BaseMessage(BaseModel):
    type: str
    
    
class EmailNotificationData(BaseModel):
    email_to: EmailStr
    email_from: EmailStr
    message: str
    subject: str


class EmailNotification(BaseMessage):
    type: str = "email_notifications"
    data: EmailNotificationData
