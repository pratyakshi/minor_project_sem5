import pickle
import cv2
import os
import firebase_admin
import numpy as np
import cvzone
import face_recognition
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,
                              {"databaseURL": "https://minorproject2-bcf48-default-rtdb.firebaseio.com",
                               "storageBucket": "minorproject2-bcf48.appspot.com"
})

bucket = storage.bucket()
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')

folderModePath = 'Resources/Modes'
modePath = os.listdir(folderModePath)
imgModeList = []

for path in modePath:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

file = open("EncodeFile.p", 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, DriversIds = encodeListKnownWithIds

modeType = 0
counter = 0
id = -1
imgDriver = []

while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.35)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurrFrame = face_recognition.face_locations(imgS)
    encodeCurrFrame = face_recognition.face_encodings(imgS, faceCurrFrame)

    imgBackground[162:162+480, 55:55+640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    for encodeFace, faceloc in zip(encodeCurrFrame, faceCurrFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDist = face_recognition.face_distance(encodeListKnown, encodeFace)
        print("matches", matches)
        print("faceDist", faceDist)

        matchIndex = np.argmin(faceDist)

        if matches[matchIndex]:
            y1, x2, y2, x1 = faceloc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
            id = DriversIds[matchIndex]
            print(id)
            if counter == 0:
                counter = 1
                modeType = 1

    if counter != 0:
        if counter == 1:
            driversInfo = db.reference(f'Drivers/{id}').get()
            print(driversInfo)

            blob = bucket.get_blob(f'Images/{id}.png')
            array = np.frombuffer(blob.download_as_string(), np.uint8)
            imgDriver = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

            ref = db.reference(f'Drivers/{id}')
            driversInfo['total_car_unlocks'] += 1
            ref.child('total_car_unlocks').set(driversInfo['total_car_unlocks'])

        if 10 < counter <= 20:
            modeType = 2

        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

        if counter <= 10:
            cv2.putText(imgBackground, str(driversInfo['total_car_unlocks']), (861, 125),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
            cv2.putText(imgBackground, str(driversInfo['last_unlock']), (1006, 550),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(imgBackground, str(id), (1006, 493),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            (w, h), _ = cv2.getTextSize(driversInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
            offset = (414 - w) // 2
            cv2.putText(imgBackground, str(driversInfo['name']), (808 + offset, 445),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)
            imgBackground[175:175 + 216, 909:909 + 216] = imgDriver

        counter += 1

        if counter >= 20:
            counter = 0
            modeType = 0
            driversInfo = []
            imgDriver = []
            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    cv2.imshow("Driver's Login Details", imgBackground)
    cv2.waitKey(1)