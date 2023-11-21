import cv2
import os
import face_recognition
import pickle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,
                              {"databaseURL": "https://minorproject2-bcf48-default-rtdb.firebaseio.com",
                               "storageBucket": "minorproject2-bcf48.appspot.com"
})

folderPath = 'Images'
pathList = os.listdir(folderPath)
imgList = []
DriversId = []
for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    DriversId.append(os.path.splitext(path)[0])

    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]

        encodeList.append(encode)

    return encodeList

encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, DriversId]
print(encodeListKnownWithIds)

file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()