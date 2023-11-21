import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://minorproject2-bcf48-default-rtdb.firebaseio.com"
})

ref = db.reference('Drivers')

data = {
    "321654":
        {
            "name": "Preeti Routray",
            "occupation": "Owner",
            "current_location": "XYZ Street",
            "total_car_unlocks": 7,
            "last_unlock": "Evening",
            "DL Number": 46985663285,
            "last_log_time": "2022-12-11 00:54:34"
        },

    "963852":
        {
            "name": "Elon Musk",
            "occupation": "Driver",
            "current_location": "XYZ Street",
            "total_car_unlocks": 7,
            "last_unlock": "Evening",
            "DL Number": 9897923285,
            "last_log_time": "2022-12-11 00:44:52"
        }}

for key, value in data.items():
    ref.child(key).set(value)