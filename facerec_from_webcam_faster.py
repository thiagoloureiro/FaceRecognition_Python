import face_recognition
import cv2
import sys
import datetime, timedelta
import requests
import os
from multiprocessing import dummy as multithreading
from pathlib import Path
from gtts import gTTS

import queue
import threading
import time

class Person(object):
    def __init__(self, name, lastUpdate):
        self.name = name
        self.lastUpdate = lastUpdate
        pass

class Voice(object):

    def __init__(self, n):
        self.names = n
        pass

    def hello(self,name):
        self.tts(filename="Hello-" + name + ".mp3", text = "Olá" + str(name)  + "!")
        pass

    def welcome(self):
        self.tts("Welcome.mp3","Bem-Vindo a disruptiv")
        pass

    def helloForAll(self, names):
        self.names += names

    def loop(self):
        print("Calling loop")
        while True:

            if(len(self.names) > 0):
                print("Has name to talk")
                name = self.names[0]
                self.hello(name)

                if len(self.names) == 1:
                    self.welcome()

                self.names.remove(name)

        pass

    def tts(self, filename, text):
        print("filename: " +  filename)

        my_file = Path(filename)
        print("Path:")

        if not my_file.is_file():

            url = 'https://stream.watsonplatform.net/text-to-speech/api/v1/synthesize?voice=pt-BR_IsabelaVoice&accept=audio/mp3&Accept=audio/mp3&text=' + text
            headers = {'Authorization': 'Basic ODQ2NDM0N2YtMTQ2Ni00NGQxLTg4M2EtZjZmOWFkZDkwODQxOnhrZmM0aHVyWlhYdQ=='}
            response = requests.get(url, headers=headers)
            print("response:", response)

            file = open(filename,"wb")
            file.write(response.content)
            file.close()

        os.system("afplay " + filename)
        pass



def getPersonByName(persons,name):
    for person in persons:
        if person.name is name:
            return persons.index(person)
    return -1

old_stdout = sys.stdout

# This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
# other example, but it includes some basic performance tweaks to make things run a lot faster:
#   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
#   2. Only detect faces in every other frame of video.

# PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
# OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
# specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

# Create arrays of known face encodings and their names
known_face_encodings = []

known_face_names = []


# Load Images From folder

imagesDirectory = Path("./images")

if imagesDirectory.is_dir():
    for file in list(imagesDirectory.glob('**/*.jpg')):
        filename = file.name
        filenamePieces = filename.split(".")
        personName = filenamePieces[0]


        personImage = face_recognition.load_image_file("./images/" + filename)
        person_face_encoding = face_recognition.face_encodings(personImage)[0]

        known_face_encodings.append(person_face_encoding)
        known_face_names.append(personName)



# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
lastName = ""
seconds_diff = 0
datetime_start = datetime.datetime.now()
persons_in_scene = []

voice = Voice([])
somethingThread = threading.Thread(target=voice.loop)
somethingThread.start()

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []

        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = ""
            
            # If a match was found in known_face_encodings, just use the first one.
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]


            face_names.append(name)

        new_persons_in_scene = []

        for person_in_scene in face_names:

            position = getPersonByName(persons_in_scene, person_in_scene) 

            if position < 0:
                persons_in_scene.append(Person(person_in_scene, time.time()))
                new_persons_in_scene.append(person_in_scene)

        for old_person in persons_in_scene:

            position = -1
            try:
                position = face_names.index(old_person.name)
            except ValueError:
                ValueError 

            now = time.time()
            if position < 0:
                if now - old_person.lastUpdate > 60:
                    persons_in_scene.remove(old_person)

        if len(new_persons_in_scene) > 0:

            print(datetime.datetime.now())

        voice.helloForAll(new_persons_in_scene)

    process_this_frame = not process_this_frame


    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 2
        right *= 2
        bottom *= 2
        left *= 2

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
