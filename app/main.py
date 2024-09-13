from fastapi import FastAPI,Depends,HTTPException,status,File, UploadFile, APIRouter
from .routes import router
from . import models,crud,schemas,config
from .database import engine,get_db
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.security import OAuth2PasswordRequestForm
import os
from app.qdrant_utils import *



if not os.path.exists("files"):
    os.makedirs("files")





# creating the model which defined in models
models.Base.metadata.create_all(bind=engine)




app=FastAPI()

app.include_router(router)


@app.get("/")
async def read_root():
    return {"message":"hello, FastApi!"}


@app.get("/users/")
def read_users(db: Session=Depends(get_db)):
    users=crud.get_user(db)
    return users


@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user:schemas.UserCreate, db:Session=Depends(get_db)):
    user_created=crud.create_user(db,user_name=user.name,user_mail=user.mail,user_password=user.password)
    return user_created


@app.put("/users/{user_id}",response_model=schemas.UserResponse)
def update_user(user_id:int,user_update:schemas.UserUpdate,db:Session=Depends(get_db)):
    user=crud.get_user_by_id(db,user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404,detail="user not found")
    
    if user_update.name is not None:
        user.name=user_update.name
    
    if user_update.mail is not None:
        user.mail=user_update.mail

    if user_update.password is not None:
        user.password=crud.hash_password(user_update.password)

    
    db.commit()
    db.refresh(user)

    return user


@app.delete("/users/{user_id}")
def delete_user(user_id:int,db:Session=Depends(get_db)):
    user=crud.delete_user(db,user_id=user_id)
    if user is None:
        return HTTPException(status_code=404,detail="user not found")
    return {"message":"user deleted successfully"}

# jwt configration

@AuthJWT.load_config
def get_config():
    return config.Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request, exc):
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


@app.post("/login/")
def login(form_data:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db),Authorize:AuthJWT=Depends()):
    user=crud.authenticate_user(db,form_data.username,form_data.password)
    if not user:
        raise HTTPException(status_code=401,detail="Invalid username or password")
    
    access_token=Authorize.create_access_token(subject=user.id)
    return {"access_token":access_token,"token_type":"bearer"}



@app.get("/protected/")
def protected(Authorize: AuthJWT=Depends()):
    Authorize.jwt_required()

    current_user=Authorize.get_jwt_subject()
    return {"message":f"hello {current_user}, you have access to this route!"}



# jwt configuration ends


@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db), user_id: int = Depends(crud.get_current_user_id)):
    try:
        collection_name="Vectorized_file"
        vector_size=384
        file_location = f"qdrant_storage_new2/{file.filename}"
        file_content = await file.read()
        with open(file_location, "wb") as f:
            f.write(file_content)
            crud.save_file_to_db(db, user_id,file_location)
            extracted_text=crud.extract_text_from_pdf(file_location)
            print("Extracted text:", extracted_text)
            vectors=crud.vectorize_text(extracted_text)

            create_collection_if_not_exists(collection_name,vector_size)
            
            insert_vectors_to_qdrant(vectors,user_id,file.filename,extracted_text,collection_name)
            optimize_collection(collection_name)
        return {"filename": file.filename, "message": "File uploaded and text vectorized successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    

    # docker run -d --name qdrant -p 6333:6333 -p 6334:6334 -v "C:/Users/DELL/Desktop/PDF Bot/PDF_Bot_Backend/qdrant_storage_new2:/qdrant/storage" qdrant/qdrant



@app.post("/ask/")
async def ask_question(question_request: schemas.QuestionRequest):
    try:
        # print("Endpoint /ask/ hit!") 
        question_vector = vectorize_question(question_request.question)
        

        search_results = search_qdrant(question_vector, limit=3)

        # print("Search results:", search_results)

        if search_results is None:
            raise HTTPException(status_code=404, detail="No search results found.")
        if len(search_results) == 0:
            raise HTTPException(status_code=404, detail="Search results are empty.")

        answers = process_search_results(search_results)
        

        if not answers:
            response = "No relevant information found."
        else:
            response = " ".join(answers) 
        
        return {"response": response}
    
    except Exception as e:

        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))




