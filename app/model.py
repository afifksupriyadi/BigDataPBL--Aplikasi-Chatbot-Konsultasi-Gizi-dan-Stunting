from pydantic import BaseModel, Field

class UserRegistration(BaseModel):
    username: str
    password: str

class QueryInput(BaseModel):
    question: str
    session_id: str = Field(default=None)  # Session ID untuk melacak percakapan

class QueryResponse(BaseModel):
    answer: str
    user_id: int  # User ID ditambahkan di response agar dapat digunakan oleh frontend jika diperlukan
    session_id: str  # Session ID untuk melacak percakapan aktif
