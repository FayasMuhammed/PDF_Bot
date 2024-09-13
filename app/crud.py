from sqlalchemy.orm import Session
from . import models
import bcrypt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
import fitz
from sentence_transformers import SentenceTransformer

from sentence_transformers import SentenceTransformer
import numpy






def get_user(db: Session):
    return db.query(models.User).all()


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()).decode('utf-8')


def create_user(db: Session,user_name=str,user_mail=str,user_password=str):
    hashed_password=hash_password(user_password)
    db_user=models.User(name=user_name,mail=user_mail,password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user





def delete_user(db:Session,user_id:int):
    user=db.query(models.User).filter(models.User.id==user_id).first()
    if user is None:
        return None
    db.delete(user)
    db.commit()
    return user



pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")



def authenticate_user(db:Session,username:str,password:str):
    user=db.query(models.User).filter(models.User.name==username).first()
    if not user:
        return False
    if not user or not pwd_context.verify(password,user.password):
        return False
    return user




def save_file_to_db(db: Session, user_id: int, file_path: str):
    db_file = models.UploadedFile(user_id=user_id, file_path=file_path)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


# get user id for file upload

def get_current_user_id(Authorize: AuthJWT = Depends()) -> int:
    try:
        Authorize.jwt_required()
        user_id = Authorize.get_jwt_subject()
        return user_id
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    


# extracting text from pdf file


def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    try:

        pdf_document = fitz.open(pdf_path)
        

        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text("text")

    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
    finally:

        pdf_document.close()

    return text








vectorizer_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def vectorize_text(text):

    vectors = vectorizer_model.encode(text)

    if isinstance(vectors, numpy.ndarray):
        if vectors.ndim == 1:

            vectors = [vectors]
    return vectors






