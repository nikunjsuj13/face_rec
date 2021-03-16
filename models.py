from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_appbuilder import Model
from flask_admin import BaseView, expose, AdminIndexView
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import sqlite3
import shutil

engine = create_engine('sqlite:///Users/nikunjsujit/Desktop/face_detect/face_rec.db')
session = Session(engine)


app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:////Users/nikunjsujit/Desktop/face_detect/face_rec.db'
app.config['SECRET_KEY']='test1234'
db=SQLAlchemy(app)



class registered_faces(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50))
    image=db.Column(db.String(500))

class detected_faces(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50))
    time=db.Column(db.DateTime(timezone=True))
    image=db.Column(db.String(500))




class unknown_faces(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    time=db.Column(db.DateTime(timezone=True))
    image=db.Column(db.LargeBinary)

class my_view(AdminIndexView):
    @expose('/')
    def index(self):
        conn = sqlite3.connect("face_rec.db")
        cursor = conn.cursor()
        detected_count = db.engine.execute('select count(id) from detected_faces').scalar()
        unknown_count = db.engine.execute('select count(id) from unknown_faces').scalar()
        return self.render('admin/index.html', detected_count=detected_count, unknown_count=unknown_count)



class Unknown_faces(BaseView):
    @expose('/')
    def index(self):
        conn = sqlite3.connect("face_rec.db")
        cursor = conn.cursor()

        #count = db.engine.execute('select count(id) from unknown_faces').scalar()
        nms = cursor.execute('select image,time from unknown_faces')
        im=[]

        for i in nms:
            im.append(i)
            shutil.copy('static/'+i[0], 'static/'+i[0].split('/')[1])
        return self.render('analytics_index.html',im=im)
        conn.commit()

class Detected_faces(BaseView):
    @expose('/')
    def index(self):
        conn = sqlite3.connect("face_rec.db")
        cursor = conn.cursor()

        #count = db.engine.execute('select count(id) from unknown_faces').scalar()
        nms = cursor.execute('select image,name from detected_faces')
        im=[]

        for i in nms:
            im.append(i)
            shutil.copy('static/'+i[0], 'static/'+i[0].split('/')[1])
        return self.render('det_face.html',im=im)
        conn.commit()

if __name__=='__main__':
    app.run()
