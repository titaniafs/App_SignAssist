from flask import Flask, render_template, Response, request, redirect
from nltk.chat.util import Chat, reflections
from googletrans import Translator
from chat_pairs import pairs
from RunMediapipe import *
import tensorflow as tf
import numpy as np
import cv2
import os
import re

app = Flask(__name__)

camera = None
switch = 0
cam_act = ""
capture = False
target_language = ""

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils
model = tf.keras.models.load_model('model_CPM_new.h5', compile=False)
model.compile(optimizer=tf.keras.optimizers.Adam(), loss='binary_crossentropy')
sequence = []

holistic = MediaPipedeploy()
chat = Chat(pairs, reflections)


def translate_text(text, target_language):
    if text is None:
        return ""
    translator = Translator()
    translation = translator.translate(text, dest=target_language)
    translated_text = translation.text
    return translated_text


def gen_frames():
    global switch, sequence, cam_act, camera, capture, target_language

    if cam_act == "":
        cam_act = "Camera Mati"

    while True:
        if switch == 1:
            if camera is None:
                camera = cv2.VideoCapture(0)
            success, frame = camera.read()
            if success:
                image, results = holistic.mediapipe_detection(frame)
                holistic.draw_styled_landmarks(image, results)

                keypoints = holistic.extract_keypoints(results)
                sequence.append(keypoints)
                sequence = sequence[-15:]

                if len(sequence) >= 15:
                    res = model.predict(np.expand_dims(sequence, axis=0))[0]
                    action = holistic.actions[np.argmax(res)]
                    image = holistic.prob_viz(res, image)

                    if capture:
                        if action is None:
                            action = ""
                        action = translate_text(
                            action, target_language=target_language)

                    cv2.rectangle(image, (0, 0), (640, 40), (245, 117, 16), -1)
                    cv2.putText(image, action, (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                try:
                    ret, buffer = cv2.imencode('.jpg', image)
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                except Exception as e:
                    pass
        else:
            if cam_act != "":
                image = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(image, f" {cam_act}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                try:
                    ret, buffer = cv2.imencode('.jpg', image)
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                except Exception as e:
                    pass
            else:
                pass


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == "GET":
        return render_template("index.html")


@app.route("/directory")
def directory():
    return render_template("sign-language.html")


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/get")
def home():
    msg = request.args.get("msg")
    return chat.respond(msg)


@app.route('/requests', methods=['POST', 'GET'])
def tasks():
    global switch, camera, cam_act, capture, target_language
    if request.method == 'POST':
        if request.form.get('stop') == 'Stop/Start':
            if switch == 1:
                switch = 0
                if camera is not None:
                    camera.release()
                    camera = None
                cam_act = "Camera Mati"
            else:
                switch = 1
                cam_act = ""

        elif request.form.get('translate') == 'Translate':
            global capture
            target_language = request.form.get('target_language')
            capture = not capture

    elif request.method == 'GET':
        return redirect('/#livesign')
    return redirect('/#livesign')


if __name__ == '__main__':
    app.run()


if camera is not None:
    camera.release()
cv2.destroyAllWindows()
