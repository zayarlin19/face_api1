import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
import face_recognition
import numpy as np
import cv2
import pickle
import os

app = FastAPI()

# File to store the target face encoding
ENCODING_FILE = "target_face.pkl"

def load_encoding():
    if os.path.exists(ENCODING_FILE):
        try:
            with open(ENCODING_FILE, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading encoding: {e}")
    return None

def save_encoding(encoding):
    with open(ENCODING_FILE, 'wb') as f:
        pickle.dump(encoding, f)

# Load on startup
target_face_encoding = load_encoding()

@app.get("/", response_class=HTMLResponse)
async def main_page():
    return """
    <html>
        <head>
            <title>Face Recognition System</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                h1 { color: #333; }
                form { margin: 20px auto; padding: 20px; border: 1px solid #ccc; max-width: 400px; border-radius: 10px; }
                input[type=file] { margin-bottom: 20px; }
                button { background-color: #4CAF50; color: white; padding: 10px 20px; border: none; cursor: pointer; border-radius: 5px; }
                button:hover { background-color: #45a049; }
            </style>
        </head>
        <body>
            <h1>Upload Target Face</h1>
            <p>Upload a photo of the person you want the robot to recognize.</p>
            <form action="/set_target" method="post" enctype="multipart/form-data">
                <input type="file" name="file" accept="image/*" required>
                <br>
                <button type="submit">Upload & Register Face</button>
            </form>
        </body>
    </html>
    """

@app.post("/set_target")
async def set_target_face(file: UploadFile = File(...)):
    """
    Upload an image to set as the 'target' face (the owner).
    """
    global target_face_encoding
    
    # Read image file
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Detect face and get encoding
    encodings = face_recognition.face_encodings(rgb_image)
    
    if len(encodings) > 0:
        target_face_encoding = encodings[0]
        save_encoding(target_face_encoding)
        return {"status": "success", "message": "Target face set and saved successfully! The robot will now recognize this person."}
    else:
        return {"status": "error", "message": "No face detected in the image. Please try a clearer photo."}

@app.post("/verify_face")
async def verify_face(file: UploadFile = File(...)):
    """
    Upload an image to check if it matches the target face.
    """
    global target_face_encoding
    
    if target_face_encoding is None:
        return {"match": False, "error": "No target face set yet"}
    
    # Read image file
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Get encodings from the current frame
    face_locations = face_recognition.face_locations(rgb_image)
    face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
    
    match_found = False
    
    for encoding in face_encodings:
        # Compare with target
        matches = face_recognition.compare_faces([target_face_encoding], encoding, tolerance=0.5) 
        if matches[0]:
            match_found = True
            break
            
    return {"match": match_found}

def main():
    print("Starting Face Recognition API...")
    # 0.0.0.0 is CRITICAL to allow connections from other laptops
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
