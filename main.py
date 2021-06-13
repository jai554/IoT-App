import serial
import time
import pyrebase
import cv2
import easyocr
from datetime import datetime
from datetime import date

x = ''
plate = ''
plateDB = ''
emailDB = ''
isAllowed = 1

#Initialize Firebase connectivity
firebaseConfig = {
    "apiKey": "AIzaSyAfOI781AB_XrB811LNe8gXTOaUOdGI2U0",
    "authDomain": "iot-app-ef7df.firebaseapp.com",
    "databaseURL": "https://iot-app-ef7df-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "iot-app-ef7df",
    "storageBucket": "iot-app-ef7df.appspot.com",
    "messagingSenderId": "15952090625",
    "appId": "1:15952090625:web:d3d0abe9cf96d6d874d200",
    "measurementId": "G-3M2DTXN3JE"}
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

#establish serial communication
ser = serial.Serial('com3', 9600)

#import plate cascade
plateCascade = cv2.CascadeClassifier("cascade.xml")
minArea = 500

#start video capture
vid = cv2.VideoCapture(0)
vid.set(3, 640)
vid.set(4, 480)
vid.set(10,150)

while True:
    ret, frame = vid.read()
    plate = ""

    if x == '':
        x = ser.read()

    if x == b'a':
        print("Vehicle Detected!")

        #start image processing
        cv2.imwrite("temp.jpg", frame)
        print("Image captured!")

        img = cv2.imread("temp.jpg")
        grayIMG = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        inv = cv2.subtract(150, grayIMG)

        numberPlates = plateCascade.detectMultiScale(grayIMG, 1.1, 4)

        for (x, y, w, h) in numberPlates:
            area = w*h
            if area > minArea:
                imgRoi = img[y:y + h, x:x + w]
                cv2.imwrite("cropped.jpg",imgRoi)
                cv2.imshow("ROI", imgRoi)

                reader = easyocr.Reader(['en'])
                result = reader.readtext(imgRoi)

                try:
                    plate = result[0][-2]
                except IndexError:
                    print("Plate not detected!")
                    var = 'd'
                    x = var.encode()
                    ser.write(x)

        print("From Camera: " + plate)

        #end of image processing

        #query pyrebase
        #search for plate numbers
        try:
            resultPlates = db.child("CarLists").order_by_child("PlateNo").equal_to(plate).get()
        except IndexError:
            print("Plate not found in database")

        try:
            for PlatesDB in resultPlates.each():
                plateDB = PlatesDB.val()['PlateNo']
                print("From DB: " + plateDB)
            for PlatesDB in resultPlates.each():
                isAllowed = PlatesDB.val()['IsAllowed']
                print("Is Allowed: " + str(isAllowed))
            for PlatesDB in resultPlates.each():
                emailDB = PlatesDB.val()['OwnedBy']
        except IndexError:
            print("Plate not found in database")
        #end pyrebase query

        #if plate matches database
        if ((plateDB == plate) and (isAllowed == 1) and (plateDB != "") and (plate != "")):
            print("Gate Open")
            var = 'b'
            x = var.encode()
            ser.write(x)
            time.sleep(0.5)
            plateArd = plate + "\n"
            ser.write(plateArd.encode())

            #add timestamp into firebase
            now = datetime.now()
            today = date.today()
            current_time = now.strftime("%H:%M:%S")
            day = today.strftime("%d/%m/%Y")

            data = {"PlateNo":plate, "Date" : day,"Time": current_time, "IsAllowed": isAllowed, "OwnedBy": emailDB}
            db.child("AccessHistory").push(data)

            time.sleep(10)

        if ((plateDB == plate) and (isAllowed == 0)):
            print("Blocked access!")
            var = 'c'
            x = var.encode()
            ser.write(x)
            time.sleep(0.5)

            now = datetime.now()
            today = date.today()
            current_time = now.strftime("%H:%M:%S")
            day = today.strftime("%d/%m/%Y")

            data = {"PlateNo": plate, "Date": day, "Time": current_time, "IsAllowed": isAllowed, "OwnedBy": emailDB}
            db.child("AccessHistory").push(data)

            time.sleep(10)

        #reset value x
        x = ''

    # wait to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vid.release()
cv2.destroyAllWindows()
ser.close()
