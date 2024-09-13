import os
from dotenv import load_dotenv
from pydantic import BaseModel
from datetime import timedelta



load_dotenv()

class Settings(BaseModel):
    authjwt_secret_key: str = os.getenv("AUTHJWT_SECRET_KEY")
    authjwt_access_token_expires: timedelta = timedelta(days=1)
    
settings = Settings()


