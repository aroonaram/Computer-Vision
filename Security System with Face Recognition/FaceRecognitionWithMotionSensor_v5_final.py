#! /usr/bin/python

# import the necessary packages
from picamera import PiCamera
from time import sleep
from datetime import datetime
import boto3
from gpiozero import MotionSensor
import os
import curses
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
pir = 8
GPIO.setup(pir,GPIO.IN)
sleep(2)
print(datetime.now())


#Determine faces from encodings.pickle file model created from train_model.py
encodingsP = "encodings.pickle"

#pir = MotionSensor(14)
ACCESS_KEY = 'AKIAWV5DMNMLSP363Y57'
SECRET_KEY = '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'

print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(encodingsP, "rb").read())
# initialize the video stream and allow the camera sensor to warm up
# Set the ser to the followng
# src = 0 : for the build in single web cam, could be your laptop webcam
# src = 2 : I had to set it to 2 inorder to use the USB webcam attached to my laptop
#vs = VideoStream(src=2,framerate=10).start()
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)


# start the FPS counter
fps = FPS().start()

def faceRecognition():
    print("Face recognition started...")
    #Initialize 'currentname' to trigger only when a new person is identified.
    currentname = "unknown"
    frame = vs.read()
    frame = imutils.resize(frame, width=500)
    # Detect the fce boxes
    boxes = face_recognition.face_locations(frame)
    # compute the facial embeddings for each face bounding box
    encodings = face_recognition.face_encodings(frame, boxes)
    names = []

    # loop over the facial embeddings
    for encoding in encodings:
        matches = face_recognition.compare_faces(data["encodings"],
            encoding)
        name = "Unknown" #if face is not recognized, then print Unknown
        if True in matches:
            print("Match found")
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}
            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1
            name = max(counts, key=counts.get)
            if currentname != name:
                currentname = name
                print(currentname)
        names.append(name)

    # loop over the recognized faces
    for ((top, right, bottom, left), name) in zip(boxes, names):
        # draw the predicted face name on the image - color is in BGR
        cv2.rectangle(frame, (left, top), (right, bottom),
            (0, 255, 225), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
            .8, (0, 255, 255), 2)
    fps.update()
    return frame, names


    

def notifyUnknown(FrameImg):
    
    client = boto3.client('s3',
                      aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)
    savefile = "Unknown.jpg"
    curtime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    client.upload_file(savefile,'picamerastore','Unknown'+curtime+'.jpg')
    print('Done') 


try:
    while True:
        if GPIO.input(pir) == True:
            print('Motion detected')
            
            FrameImg,namesList = faceRecognition()
            print(namesList)
            
            cv2.imshow("Facial Recognition is Running", FrameImg)
            key = cv2.waitKey(1) & 0xFF
            if "Unknown" in namesList:
                print("Intruder Detected")
                cv2.imwrite('Unknown.jpg',FrameImg)
                notifyUnknown(FrameImg)
                
            # sleep(30)
finally:
    GPIO.cleanup()
    # stop the timer and display FPS information
    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    # do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()
    
