import os
import dotenv

from fastapi import FastAPI, UploadFile, File
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse


dotenv.load_dotenv()

## path of directory where clinic files reside
data_path = os.environ.get("DATA_PATH")
if not os.path.exists(data_path):
    os.mkdir(data_path)
        
app = FastAPI()

## onboarding clinics endpoint
@app.post('/uploadclinicfile')
async def upload_file(uploaded_file: UploadFile = File()):
    if not uploaded_file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    if uploaded_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    # print("----------------------------------->",uploaded_file.filename)
    file_path = os.path.join(data_path, uploaded_file.filename)
    
    try:
        print("Uploading the file...")
        with open(file_path, "wb") as f:
            content = await uploaded_file.read()
            f.write(content)

        print("File uploaded sucessfully.")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="internal server error")

    return JSONResponse(content={"message": f"Uploaded and ready to be Ingested: {uploaded_file.filename} sucessfully."}, 
                        status_code=200)
    


    