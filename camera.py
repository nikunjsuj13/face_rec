import cv2
from imutils.video import WebcamVideoStream
from flask import Flask,request,render_template, redirect,url_for,Response
class VideoCamera(object):
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.

        self.stream = WebcamVideoStream(src=0).start()
    def __del__(self):
        self.stream.stop()
        return render_template('success.html')

    def get_frame(self):
        image=self.stream.read()
        ret,jpeg=cv2.imencode('.jpg',image)
        data=[]
        data.append(jpeg.tobytes())
        #data.append(jpeg)
        return data
