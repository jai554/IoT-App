import serial
import time
import pyrebase
import cv2
import matplotlib.pyplot as plt
import numpy as np
import imutils
import easyocr

x = ''

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

#start video capture
vid = cv2.VideoCapture(0)

while True:
    ret, frame = vid.read()

    if x == '':
        x = ser.read()
        time.sleep(0.5)

    if x == b'a':
        # time.sleep(2)
        # ret, frame = vid.read()
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # cv2.imshow('frame', gray)

        print("Vehicle Detected!")

        #start image processing
        result = cv2.imwrite("temp.jpg", frame)
        print("Image captured!")

        img = cv2.imread("temp.jpg")
        grayIMG = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        inv = cv2.subtract(150, grayIMG)

        bfilter = cv2.bilateralFilter(inv, 11, 17, 17)  # Noise reduction
        edged = cv2.Canny(bfilter, 100, 200)  # Edge detection

        keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(keypoints)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

        location = None
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 10, True)
            if len(approx) == 4:
                location = approx
                break

        mask = np.zeros(grayIMG.shape, np.uint8)
        new_image = cv2.drawContours(mask, [location], 0, 255, -1)
        new_image = cv2.bitwise_and(img, img, mask=mask)

        (x, y) = np.where(mask == 255)
        (x1, y1) = (np.min(x), np.min(y))
        (x2, y2) = (np.max(x), np.max(y))
        cropped_image = grayIMG[x1:x2 + 1, y1:y2 + 1]

        reader = easyocr.Reader(['en'])
        result = reader.readtext(cropped_image)

        text = result[0][-2]

        print(text)
        #end of image processing

        #query pyrebase
        resultPlates = db.child("CarLists").order_by_child("PlateNo").equal_to(text).get()
        print(resultPlates)
        #end pyrebase query

        #if plate matches database
        if (resultPlates == text):
            var = 'b'
            x = var.encode()
            ser.write(x)
            time.sleep(0.5)
            plate = text + "\n"
            ser.write(plate.encode())
            time.sleep(0.5)
        elif (resultPlates != text):
            var = 'c'
            x = var.encode()
            ser.write(x)
            time.sleep(0.5)

        #reset value x
        x = ''

    # wait to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vid.release()
cv2.destroyAllWindows()
ser.close()
