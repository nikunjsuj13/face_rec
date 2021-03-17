import cv2
import os
import numpy as np
from flask import Flask,request,render_template, redirect,url_for,Response
import imutils
import glob
import face_recognition
import pickle
import time
import sqlite3
from PIL import Image as im
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose, AdminIndexView
from datetime import datetime
import os

app=Flask(__name__)

for i in os.listdir('static'):
    if i.endswith('.jpg'):
        os.remove('static/'+i)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:/Users/nikunjsujit/Desktop/face_detect/face_rec.db'
app.config['SECRET_KEY']='test1234'
db=SQLAlchemy(app)
from models import *
admin=Admin(app,index_view=my_view())
admin.add_view(ModelView(registered_faces,db.session))
admin.add_view(Unknown_faces(name='Unknown faces', endpoint='Unknown_faces'))
admin.add_view(Detected_faces(name='Detected faces', endpoint='Detected_faces'))

def train():
    # Path for face image database
    path = 'registered_faces'
    detector = cv2.CascadeClassifier("haarcascade_frontalface_alt2.xml");
    # function to get the images and label data

    imagePath1 = [os.path.join(path, f) for f in os.listdir(path)]
    imagePaths = []
    for i in imagePath1:
        if i.endswith('.jpg'):
            imagePaths.append(i)

    knownEncodings = []
    knownNames = []
    for imagePath in imagePaths:
        name = os.path.split(imagePath)[1].split("_")[0]
        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # Use Face_recognition to locate faces
        boxes = face_recognition.face_locations(rgb, model='cnn')
        # compute the facial embedding for the face
        encodings = face_recognition.face_encodings(rgb, boxes)
        # loop over the encodings
        for encoding in encodings:
            knownEncodings.append(encoding)
            knownNames.append(name)
    # save emcodings along with their names in dictionary data
    data = {"encodings": knownEncodings, "names": knownNames}
    # use pickle to save data into a file for later use
    print('training done....')
    f = open("face_enc", "wb")
    f.write(pickle.dumps(data))
    f.close()


@app.route("/",methods=["POST", "GET"])
def index():
    return render_template('login.html')

@app.route("/success",methods=["POST", "GET"])
def success():
   return render_template('login.html')

@app.route("/d1",methods=["POST", "GET"])
def gen_frames():

    count=1
    # find path of xml file containing haarcascade file
    cascPathface = "haarcascade_frontalface_alt2.xml"
    # load the harcaascade in the cascade classifier
    faceCascade = cv2.CascadeClassifier(cascPathface)
    # load the known faces and embeddings saved in last file
    data = pickle.loads(open('face_enc', "rb").read())

    camera = cv2.VideoCapture(0)
    while count!=100:
        conn = sqlite3.connect("face_rec.db")
        cursor = conn.cursor()
        success, frame = camera.read() # read the camera frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray,
                                             scaleFactor=1.1,
                                             minNeighbors=5,
                                             minSize=(60, 60),
                                             flags=cv2.CASCADE_SCALE_IMAGE)

        # convert the input frame from BGR to RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # the facial embeddings for face in input
        encodings = face_recognition.face_encodings(rgb)
        names = []
        # loop over the facial embeddings incase
        # we have multiple embeddings for multiple fcaes
        for encoding in encodings:
            # Compare encodings with encodings in data["encodings"]
            # Matches contain array with boolean values and True for the embeddings it matches closely
            # and False for rest
            matches = face_recognition.compare_faces(data["encodings"],
                                                     encoding)
            # set name =inknown if no encoding matches
            name = "Unknown"
            # check to see if we have found a match
            if True in matches:
                # Find positions at which we get True and store them
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}
                # loop over the matched indexes and maintain a count for
                # each recognized face face
                for i in matchedIdxs:
                    # Check the names at respective indexes we stored in matchedIdxs
                    name = data["names"][i]
                    # increase count for the name we got
                    counts[name] = counts.get(name, 0) + 1
                # set name which has highest count
                name = max(counts, key=counts.get)

            # update the list of names
            names.append(name)
            # loop over the recognized faces
            for ((x, y, w, h), name) in zip(faces, names):
                # rescale the face coordinates
                # draw the predicted face name on the image
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                            0.75, (0, 255, 0), 2)
                if name=='Unknown':
                    now = datetime.now()
                    date_time = now.strftime("%m_%d_%H_%M_%S")
                    imgpath='unknown_faces/'+name+'_'+str(count)+'_'+str(date_time)+'.jpg'

                    data2 = frame[y:y + h, x:x + w]
                    #ret,data2 = cv2.imencode('.jpg',frame[y:y+h,x:x+w])
                    cv2.imwrite('static/'+imgpath,data2)
                    cursor.execute(""" INSERT INTO unknown_faces 
                            (time, image) VALUES (?,?)""", (now, imgpath))
                elif type(name)==str:
                    now = datetime.now()
                    date_time = now.strftime("%m_%d_%H_%M_%S")

                    imgpath= 'detected_faces/' + name + '_' + str(count) + '.jpg'

                    data2=frame[y:y+h,x:x+w]
                    #ret, data2 = cv2.imencode('.jpg',data2 )
                    cv2.imwrite('static/'+imgpath, data2)




                    cursor.execute(""" INSERT INTO detected_faces 
                                                (name, image) VALUES (?,?)""", (name,imgpath))



        if not success:
            break
        else:

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
            conn.commit()
            cursor.close()
            conn.close()
        if count==99:

            with app.app_context(),app.test_request_context("http://127.0.0.1:5000/success"):


                return render_template('success.html')
            break

        count+=1


@app.route("/redirect",methods=["POST", "GET"])
def redirect():
    var = request.args.get('var')



    if request.method == "POST":
        name=request.form["nm"]
        count = 1
        for i in os.listdir('registered_faces'):
            if name in i:
                count += 1
        conn = sqlite3.connect('face_rec.db')
        cursor = conn.cursor()
        new_loc='registered_faces/'+name+'_'+str(count)+'.jpg'
        shutil.move('static/'+var,new_loc)
        cursor.execute("""
        INSERT INTO registered_faces (name,image) 
         VALUES (?,?)""",(name,new_loc))
        cursor.execute("""
                DELETE FROM unknown_faces WHERE image=?""", (var,))

        conn.commit()
        cursor.close()
        conn.close()
        train()
        return render_template('success.html')
    return render_template('rename.html',var=var)

@app.route("/det_face",methods=["POST", "GET"])
def det_face():
    img = request.args.get('img')
    name=request.args.get('name')
    count=0
    for i in os.listdir('registered_faces'):
        if name in i:
            count+=1




    conn = sqlite3.connect('face_rec.db')
    cursor = conn.cursor()
    new_loc='registered_faces/'+name+'_'+str(count)+'.jpg'
    shutil.move('static/'+img,new_loc)
    cursor.execute("""
    INSERT INTO registered_faces (name,image) 
     VALUES (?,?)""",(name,new_loc))
    cursor.execute("""
            DELETE FROM detected_faces WHERE image=?""", (img,))

    conn.commit()
    cursor.close()
    conn.close()
    train()
    return render_template('success.html')


@app.route("/sign_in",methods=["POST", "GET"])
def sign_in():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


    #return redirect(url_for("/"))

if __name__=="__main__":
    app.run()