from typing import Set, Any
import operator
from flask import Flask, render_template, redirect, request, url_for, session, Response, jsonify, abort
# from flask_mysqldb import MySQL
# from flaskapp import app

from flask_mail import Mail, Message
import pygal
from pygal.style import Style
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import time
from pathlib import Path

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import time

from PIL import Image
import requests

app = Flask(__name__)
app.secret_key = "FRAS"

from api.api import *

camera = None
course_camera = None
date_camera = ""
checkAttendance = True
check = False

is_submit = False
message_send = ""
message_acknowledge = False

# app = Flask(__name__)
mail = Mail(app)


@app.errorhandler(404)
def redirect_404_page(msg):
    return f"<h3> 404 Not Found <h3><p>{msg}<p>", 404


@app.before_request
def before_request_func():
    global message_acknowledge
    # print(message_acknowledge)
    if message_acknowledge:
        message_acknowledge = False
        global is_submit, message_send
        is_submit, message_send = False, ""


def end_video_feed():
    try:
        global camera
        if camera is not None:
            camera.release()
        camera = None
    except:
        e = sys.exec_info()[0]
        print(e)


# ----------------------------------------------------------------------
#               O N L Y   A D M I N   R O U T E S
# ----------------------------------------------------------------------
# -------------------- Users ------------------------------------------
def users_validate_inputs(inputs, method="POST"):
    error_message = {}
    # Check First Name
    if not inputs['first_name']:
        error_message['first_name'] = "Empty field"

    # Check Last Name
    if not inputs['last_name']:
        error_message['last_name'] = "Empty field"

    # Check Email
    if not inputs['email']:
        error_message['email'] = "Empty field"
    else:
        if method == "POST":
            response = requests.get(domain_name + f"/api/users/{inputs['email']}", params={"key": app.secret_key})
            if response.status_code != 200:
                error_message['email'] = "Error identifying student"
            elif response.json() is not None:
                error_message['email'] = "Email has already exists"

    if inputs['user_role'] is None:
        error_message['user_role'] = "Unselected field"

    if method == "POST":
        if not inputs['pass']:
            error_message['pass'] = "Empty field"
    return error_message


@app.route("/users/add_user_submit", methods=['POST'])
def add_user():
    request_payload = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'pass': request.form['pass'],
        'user_role': request.form.get('user_role')
    }

    error_message = users_validate_inputs(request_payload)
    print(request_payload)
    print(error_message)

    try:
        if not error_message:
            requests.post(domain_name + "/api/create_account", json=request_payload, params={"key": app.secret_key})
            global is_submit, message_send
            is_submit, message_send = True, "Successfully Created Users"
            return redirect("/users")
    except:
        return 'error', 500

    response = requests.get(domain_name + "/api/users", params={"key": app.secret_key}).json()
    return render_template("users.html", cred=session['cred'],
                           modal_error=True, modal_request_data=request_payload, error_message=error_message,
                           data=response)


@app.route("/users")
def users():
    end_video_feed()
    if 'cred' not in session:
        return redirect('/')

    if not session['cred']['admin']:
        return redirect('/home')

    response = requests.get(domain_name + "/api/users", params={"key": app.secret_key}).json()

    global is_submit, message_send, message_acknowledge
    if is_submit:
        message_acknowledge = True
    return render_template("users.html", cred=session['cred'], data=response,
                           submit=is_submit, submit_message=message_send)


# ---------------------- Course -------------------------------------------

def add_course_validate_inputs(inputs):
    error_message = {}
    # Check title_id
    if inputs['title_id']:
        if len(inputs['title_id'].split()) != 2:
            error_message['title_id'] = "Incorrect format"
        else:
            response = requests.get(domain_name + f"/api/courses/title/{inputs['title_id'].replace(' ', '_')}",
                                    params={"key": app.secret_key})
            if response.status_code != 200:
                error_message['title_id'] = "Error identifying title ID"
            elif response.json() is not None:
                error_message['title_id'] = "Duplicate course"
    else:
        error_message['title_id'] = "Empty field"

    # Check title
    if not inputs['title']:
        error_message['title'] = "Empty field"

    # Check User Id
    if not inputs['user_id']:
        error_message['user_id'] = "Empty field"

    # Check Units
    if not inputs['units']:
        error_message['units'] = "Empty field"

    # Check Days
    if not inputs['days']:
        error_message['days'] = "Empty field"

    # Check Time
    if inputs['start_time'] and inputs['end_time']:
        print("HERE " + inputs['start_time'])
        if datetime.strptime(inputs['start_time'], "%H:%M") >= datetime.strptime(inputs['end_time'], "%H:%M"):
            error_message['time'] = "End time must be after start time"
    else:
        error_message['time'] = "Empty Field"

    # Check Date
    if inputs['start_dt'] and inputs['end_dt']:
        print(inputs['start_time'])
        if datetime.strptime(inputs['start_dt'], "%Y-%m-%d") >= datetime.strptime(inputs['end_dt'], "%Y-%m-%d"):
            error_message['date'] = "End date must be after start date"
    else:
        error_message['date'] = "Empty Field"
    return error_message


@app.route("/home/add_course_submit", methods=['POST'])
def add_course():
    request_payload = {
        'title_id': request.form['title_id'],
        'title': request.form['title'],
        'units': request.form['units'],
        'user_id': request.form['user_id'],
        'days': request.form.getlist('days'),
        'start_time': request.form['start_time'],
        'end_time': request.form['end_time'],
        'start_dt': request.form['start_dt'],
        'end_dt': request.form['end_dt']
    }
    try:
        error_message = add_course_validate_inputs(request_payload)

        if not error_message:
            request_payload['days'] = "".join(request_payload['days'])
            requests.post(domain_name + "/api/courses", json=request_payload, params={"key": app.secret_key})

            global is_submit, message_send
            is_submit, message_send = True, "Successfully Added Course"
            return redirect("/home")
    except:
        return 'error', 500

    response = requests.get(domain_name + "/api/courses/all/" + str(session['cred']['id']),
                            params={"key": app.secret_key}).json()
    return render_template("home.html", cred=session['cred'],
                           modal_error=True, modal_request_data=request_payload, error_message=error_message,
                           data=response)


# ---------------------- Students -------------------------------------------
def students_validate_inputs(inputs, method="POST"):
    error_message = {}
    # Check First Name
    if not inputs['first_name']:
        error_message['first_name'] = "Empty field"

    # Check Last Name
    if not inputs['last_name']:
        error_message['last_name'] = "Empty field"

    # Check Email
    if not inputs['email']:
        error_message['email'] = "Empty field"
    else:
        if method == "POST":
            response = requests.get(domain_name + f"/api/students/{inputs['email']}", params={"key": app.secret_key})
            if response.status_code != 200:
                error_message['email'] = "Error identifying student"
            elif response.json() is not None:
                error_message['email'] = "Email has already exists"
    return error_message


@app.route("/students/edit_student_submit", methods=['POST'])
def edit_student():
    request_payload = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email']
    }
    error_message = students_validate_inputs(request_payload, "PUT")
    if not error_message:
        try:
            requests.put(domain_name + f"/api/students/{request_payload['email']}",
                         json=request_payload, params={"key": app.secret_key})
            global is_submit, message_send
            is_submit, message_send = True, "Successfully Edited Student"
            return redirect("/students")
        except:
            return 'error', 500

    response = requests.get(domain_name + "/api/students", params={"key": app.secret_key}).json()
    return render_template("students.html", cred=session['cred'],
                           modal_edit_error=True, modal_request_data=request_payload, error_message=error_message,
                           data=response)


@app.route("/students/add_student_submit", methods=['POST'])
def add_student():
    request_payload = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email']
    }
    error_message = students_validate_inputs(request_payload)
    print(request_payload)
    try:
        if not error_message:
            requests.post(domain_name + "/api/students", json=request_payload, params={"key": app.secret_key})
            global is_submit, message_send
            is_submit, message_send = True, "Successfully Added Student"
            return redirect("/students")
    except:
        return 'error', 500

    response = requests.get(domain_name + "/api/students", params={"key": app.secret_key}).json()
    return render_template("students.html", cred=session['cred'],
                           modal_error=True, modal_request_data=request_payload, error_message=error_message,
                           data=response)


@app.route("/students", methods=['GET', 'POST'])
def students():
    end_video_feed()
    if 'cred' not in session:
        return redirect('/')

    if not session['cred']['admin']:
        return redirect('/home')

    response = requests.get(domain_name + "/api/students",
                            params={"key": app.secret_key}).json() if request.method == "GET" else \
        requests.post(domain_name + "/api/students/search", json={'name': request.form['name']}).json()

    search_message = "No Result"
    global is_submit, message_send, message_acknowledge
    if is_submit:
        message_acknowledge = True

    return render_template("students.html", cred=session['cred'], data=response, search_message=search_message,
                           submit_message=message_send, submit=is_submit)


# ----------------------- add/drop student to/from course-------------------
def add_students_course_validate_inputs(inputs):
    error_message = {}
    request_id = {}
    course_id = requests.get(domain_name + f"/api/courses/title/{inputs['title_id']}",
                             params={"key": app.secret_key}).json()['id']
    request_id['course_id'] = course_id
    if inputs['email']:
        student_response = requests.get(domain_name + f"/api/students/{inputs['email']}",
                                        params={"key": app.secret_key}).json()
        if student_response is None:
            error_message['email'] = "No such student email"
        else:
            response = requests.get(domain_name + f"/api/roster/{course_id}/{student_response['id']}",
                                    params={"key": app.secret_key})
            if response.status_code != 200:
                error_message['email'] = "Error identifying student"
            elif response.json() is not None:
                error_message['email'] = "Student exist in Roster"
            request_id['student_id'] = student_response['id']
    else:
        error_message['email'] = "Empty field"
    return error_message, request_id


@app.route("/<title_id>/roster/add_student_submit", methods=['POST'])
def roster_add_student(title_id):
    request_payload = {
        'title_id': title_id,
        'email': request.form['email']
    }
    try:
        error_message, retrieve_id = add_students_course_validate_inputs(request_payload)
        print(error_message)
        print(retrieve_id)
        if not error_message:
            requests.post(domain_name + f"/api/attendees/{retrieve_id['course_id']}",
                          json={"student_id": retrieve_id['student_id']},
                          params={"key": app.secret_key})
            global is_submit, message_send
            is_submit, message_send = True, "Successfully Added Student"
            return redirect(f"/{title_id}/roster")

        response = requests.get(domain_name + f"/api/roster/{retrieve_id['course_id']}",
                                params={"key": app.secret_key}).json()

        search, message = False, "No Data"
        return render_template("roster.html",
                               search=search, cred=session['cred'], course=title_id, data=response, message=message,
                               error_message=error_message, modal_request_data=request_payload, modal_add_error=True)

    except:
        return 'error', 500


@app.route("/<title_id>/roster/drop_student", methods=['POST'])
def roster_delete_student(title_id):
    try:
        student_id = requests.get(domain_name + f"/api/students/{request.form['email']}",
                                  params={"key": app.secret_key}).json()['id']
        course_id = requests.get(domain_name + f"/api/courses/title/{title_id}",
                                 params={"key": app.secret_key}).json()['id']
        requests.delete(domain_name + f"/api/attendees/{course_id}",
                        json={"student_id": student_id},
                        params={"key": app.secret_key})
        global is_submit, message_send
        is_submit, message_send = True, "Successfully Dropped Student"
        return redirect(f"/{title_id}/roster")
    except:
        return 'error', 500


# ----------------------------------------------------------------------
#               E N D   O F   A D M I N   R O U T E S
# ----------------------------------------------------------------------


# ---------------------------------------------------------
#                   F R O N T P A G E
# ---------------------------------------------------------
@app.route("/", methods=['GET', 'POST'])
def hello():
    end_video_feed()
    error, cred = False, {"email": "", "pass": ""}
    if request.method == 'POST':
        cred = {"email": request.form['email'], "pass": request.form['password']}
        response = requests.post(domain_name + '/api/login',
                                 json={"email": cred['email'], "pass": cred['pass']})
        if response.status_code == 201:  # valid credential will return 201 status code
            session['cred'] = response.json()
            return redirect("/home")
        else:
            error = True

    return render_template("frontpage.html", error=error, cred=cred)


# ---------------------------------------------------------
#                   H O M E
# ---------------------------------------------------------
@app.route("/home", methods=['GET', 'POST'])
def home():
    end_video_feed()
    if 'cred' not in session:
        return redirect('/')
    # response = requests.get(domain_name + "/api/users/" + session['cred']['email'], params={"key": app.secret_key}).json()
    if request.method == 'GET':
        response = \
            requests.get(domain_name + "/api/courses",
                         params={"key": app.secret_key}).json() if session['cred']['admin'] else \
                requests.get(domain_name + "/api/courses/all/" + str(session['cred']['id']),
                             params={"key": app.secret_key}).json()
        message = "No Data"
    else:
        response = \
            requests.post(domain_name + "/api/courses/search",
                          json={"title_id": request.form['search'].replace(' ', '_')},
                          params={"key": app.secret_key}).json() if session['cred']['admin'] else \
                requests.post(domain_name + "/api/courses/search/" + str(session['cred']['id']),
                              json={"title_id": request.form['search'].replace(' ', '_')},
                              params={"key": app.secret_key}).json()
        message = "No Result"

    global is_submit, message_send, message_acknowledge
    if is_submit:
        message_acknowledge = True

    return render_template("home.html", cred=session['cred'], data=response, message=message,
                           submit_message=message_send, submit=is_submit)


def authorize_course(title_id):
    # authorization
    while True:
        response = requests.get(domain_name + f"/api/courses/title/{title_id}", params={"key": app.secret_key})
        if response.status_code == 200:
            break
    if response.json() is None:
        return abort(404, description="Invalid Course")
    elif response.json()['user_id'] is not session['cred']['id'] and not session['cred']['admin']:
        return abort(401, description="Permission Denied")
    return response.json()


# ---------------------------------------------------------
#                   R O S T E R
# ---------------------------------------------------------
@app.route("/<title_id>/roster", methods=['GET', 'POST'])
def roster(title_id):
    end_video_feed()
    if 'cred' not in session:
        return redirect('/')

    response = authorize_course(title_id)

    req_form = ""
    if request.method == 'GET':
        response = requests.get(domain_name + "/api/roster/" + str(response['id']),
                                params={"key": app.secret_key}).json()
        search, message = False, "No Data"
    else:
        req_form = request.form['search']
        response = requests.post(domain_name + "/api/roster/" + str(response['id']),
                                 json={"name": req_form},
                                 params={"key": app.secret_key}).json()
        search, message = True, "No Result"

    global is_submit, message_send, message_acknowledge
    if is_submit:
        message_acknowledge = True

    return render_template("roster.html",
                           search=search, cred=session['cred'], course=title_id, data=response, message=message,
                           submit_message=message_send, submit=is_submit)


# ---------------------------------------------------------
#                A T T E N D A N C E
# ---------------------------------------------------------
def generate_bar_graph(status):
    custom_style = Style(
        font_family="'Helvetica Neue', Helvetica, Arial, sans-serif",
        background='transparent',
        colors=['#79F9AC', '#FFE451', '#FB5E5E'],
        label_font_size=18,
        major_label_font_size=20,
        legend_font_size=20
    )
    bar_chart = pygal.Bar(style=custom_style, legend_box_size=30)
    bar_chart.add('Present', status['present'])
    bar_chart.add('Tardy', status['tardy'])
    bar_chart.add('Absent', status['absent'])
    return bar_chart.render_data_uri()


@app.route("/<title_id>/attendance", methods=['GET', 'POST'])
def attendance(title_id):
    end_video_feed()
    if 'cred' not in session:
        return redirect('/')
    response = authorize_course(title_id)
    lec_date_response = requests.get(domain_name + f"/api/courses/get_lec_dates/{title_id}",
                                     params={"key": app.secret_key}).json()

    lec_date_future_data = []
    lec_date_upcoming_data = []
    lec_date_current_data = []
    lec_date_past_data = []

    now = datetime.now()
    now_time_String, now_date_String = now.strftime("%H:%M:%S"), now.strftime("%b %d %Y")
    now_time, now_date = datetime.strptime(now_time_String, "%H:%M:%S"), datetime.strptime(now_date_String, "%b %d %Y")
    print("TIME: " + now_time_String)
    print("DATE: " + now_date_String)

    first_future_date_detect = False
    for lec_date_String in lec_date_response['lec_date']:
        temp = lec_date_String.split()
        lec_date = datetime.strptime(f"{temp[2]} {temp[1]} {temp[3]}", '%b %d %Y')
        lec_date_format = lec_date.strftime('%Y-%m-%d')
        status_response = requests.get(domain_name + "/api/attendants/count_attendances/"
                                                     f"{response['id']}/{lec_date_format}",
                                       params={"key": app.secret_key}).json()
        print(status_response['status']['absent'])
        data = {"lec_date": f"{temp[0].rstrip(temp[-1])} {temp[2]} {temp[1]}, {temp[3]}",
                "lec_date_format": lec_date_format,
                "status": status_response['status'],
                "graph": generate_bar_graph(status_response['status'])
                }
        if lec_date < now_date:  # if current date is greater than lecture date
            lec_date_past_data.append(data)
        elif lec_date == now_date:  # if the current date is equal to lecture date
            start_time, end_time = datetime.strptime(response['start_time'], '%H:%M'), \
                                   datetime.strptime(response['end_time'], '%H:%M')
            if now_time > end_time:  # current time past lecture
                lec_date_past_data.append(data)
            elif start_time > now_time:  # current time is before lecture
                lec_date_upcoming_data.append(data)
                first_future_date_detect = True
            else:  # lecture is currently occurring
                first_future_date_detect = True
                lec_date_current_data.append(data)
        else:  # if current data is less than lecture date
            if first_future_date_detect:
                lec_date_future_data.append(data)
            else:
                lec_date_upcoming_data.append(data)
                first_future_date_detect = True

    print("Past:")
    print(lec_date_past_data)
    print("Current:")
    print(lec_date_current_data)
    print("Upcoming:")
    print(lec_date_upcoming_data)
    print("Future: ")
    print(lec_date_future_data)

    global is_submit, message_send, message_acknowledge
    if is_submit:
        message_acknowledge = True
    return render_template("attendance.html", cred=session['cred'], course=title_id,
                           course_time=response['start_time'] + "-" + response['end_time'],
                           future_data=lec_date_future_data, upcoming_data=lec_date_upcoming_data,
                           current_data=lec_date_current_data, past_data=lec_date_past_data,
                           submit=is_submit, submit_message=message_send)


# ---------------------------------------------------------
#             A T T E N D A N C E   L I S T
# ---------------------------------------------------------

# ----------------- Change status ------------------
@app.route("/manually_change_status", methods=['POST'])
def change_status():
    end_video_feed()
    email, title, date, status = request.form['email'], \
                                 request.form['course'], \
                                 request.form['date'], \
                                 request.form['status']
    try:
        student_id = requests.get(domain_name + f"/api/students/{email}",
                                  params={"key": app.secret_key}).json()['id']
        course_id = requests.get(domain_name + f"/api/courses/title/{title}",
                                 params={"key": app.secret_key}).json()['id']
        requests.put(domain_name + "/api/attendants/change_status",
                     json={"student_id": student_id, "course_id": course_id, "student_status": status, "date": date})

        global is_submit, message_send
        is_submit, message_send = True, "Status Changed Successfully"

        return redirect(f"/{title}/attendance/list/{date}")
    except:
        return "error", 500


# --------------------------------------------------

@app.route("/attendance_list/generate", methods=['POST'])
def attendance_list_generate():
    title, date = request.form['course'], request.form['date']
    try:
        course_id = requests.get(domain_name + f"/api/courses/title/{title}",
                                 params={"key": app.secret_key}).json()['id']
        response = requests.get(domain_name + f"/api/roster/{course_id}",
                                params={"key": app.secret_key}).json()
        if not response:
            global is_submit, message_send
            is_submit, message_send = True, "Can't generate for empty roster"
            return redirect(f"/{title}/attendance")

        requests.post(domain_name + "/api/attendance_list/generate", json={'course_id': course_id, 'date': date})
    except:
        return "error", 500
    return redirect(f"/{title}/attendance/list/{date}")


@app.route("/<title_id>/attendance/list/<day>", methods=['GET', 'POST'])
def attendance_list(title_id, day):
    if 'cred' not in session:
        return redirect('/')
    response = authorize_course(title_id)
    response = requests.get(domain_name + f"/api/attendance_list/{response['id']}/{day}",
                            params={"key": app.secret_key})

    if response.status_code != 200 or not response.json():
        return redirect(f"/{title_id}/attendance")

    global is_submit, message_send, message_acknowledge
    print(is_submit)
    if is_submit:
        message_acknowledge = True
    return render_template("attendance_list.html", cred=session['cred'], course=title_id, day=day,
                           data=response.json(), cam_status=get_cam_status(),
                           submit=is_submit, message=message_send)


# ---------------------------------------------------------
#   F A C I A L    R E C O G N I T I O N    L O G I C
# ---------------------------------------------------------
app.config["IMAGE_UPLOADS"] = os.path.dirname(__file__) + "/static/images"


def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


def markAttendanceCSV(name):
    print(name)
    now = datetime.now()  # current date and time
    date = now.strftime('%m_%d_%Y')
    pathToExcel = os.path.dirname(__file__)
    relative_path = 'Attendance' + date
    pathToExcel += relative_path
    myFile = Path(pathToExcel)
    if not myFile.is_file():
        print("here")
        open(relative_path, 'wb')
    with open(relative_path, 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            dtString = now.strftime('%H:%M:%S')
            f.writelines(f'\n{name},{dtString}')


def markAttendance(student_data, status, course_data, date):
    try:
        print(status)
        markAttendanceCSV(f"{student_data['first_name']} {student_data['last_name']}")
        if status != "absent":
            # update API
            requests.put(domain_name + f"/api/attendants/change_status",
                         json={"student_id": student_data['id'],
                               "course_id": course_data['id'],
                               "date": date,
                               "student_status": status}
                         )
    except:
        print('error')


# -----------CAMERA----------------------


def gen_frames(camera, course, date):  # generate frame by frame from camera

    path = 'static/images'
    images = []
    classNames = []

    print("COURSE ", course)

    # extract data from DB
    while True:
        try:
            course_data = requests.get(domain_name + f"/api/courses/title/{course}",
                                       params={"key": app.secret_key}).json()
            response = requests.get(domain_name + f"/api/roster/{course_data['id']}",
                                    params={"key": app.secret_key}).json()
            break
        except:
            continue

    for cl in response:
        print(cl['image'])
        if cl['image'] is not None:
            curImg = cv2.imread(f"{path}/{cl['image']}")
            images.append(curImg)
            print(images)
            classNames.append({"email": cl['email'], "name": f"{cl['first_name']} {cl['last_name']}"})

    print(classNames)

    encodeListKnown = findEncodings(images)
    print('Encoding Complete')
    while True and camera is not None:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            imgS = frame
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
            faceCurFrame = face_recognition.face_locations(imgS)
            print("===FRAME===")
            print(faceCurFrame)
            encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)
            match = False
            BOX_COLOR = (0, 0, 255)
            status = "absent"
            for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                print(faceDis)
                matchIndex = np.argmin(faceDis)
                # print(matches)
                if matches[matchIndex]:
                    match = True
                    # Compare real-time to course time
                    now = datetime.now()
                    now_time_String, now_date_String = now.strftime("%H:%M:%S"), now.strftime("%b %d %Y")
                    now_time, now_date = datetime.strptime(now_time_String, "%H:%M:%S"), datetime.strptime(
                        now_date_String, "%b %d %Y")
                    start_time, end_time, lec_date = datetime.strptime(course_data['start_time'], '%H:%M'), \
                                                     datetime.strptime(course_data['end_time'], '%H:%M'), \
                                                     datetime.strptime(date, '%Y-%m-%d')

                    try:
                        name, email = classNames[matchIndex]['name'].upper(), classNames[matchIndex]['email'].upper()
                        student_data = requests.get(domain_name + f"/api/students/{email}",
                                                    params={"key": app.secret_key}).json()
                        print(student_data['id'])
                        print(course_data['id'])
                        student_cur_status = requests.get(domain_name + f"/api/attendants/get_status",
                                                          json={"student_id": student_data['id'],
                                                                "course_id": course_data['id'],
                                                                "date": date},
                                                          params={"key": app.secret_key}
                                                          ).json()["student_status"]
                    except:
                        break

                    if student_cur_status == "absent":
                        if now_date < lec_date or (now_date == lec_date and now_time <= start_time):
                            status = "present"
                        elif now_date == lec_date and now_time <= end_time:
                            status = "tardy"
                    else:
                        status = student_cur_status

                    BOX_COLOR = (0, 255, 0) if (status == "present") else (
                        (0, 195, 255) if (status == "tardy") else BOX_COLOR)

                    # print(name)
                    break

            if (not match and faceCurFrame) or match:
                y1, x2, y2, x1 = faceLoc
                cv2.rectangle(frame, (x1, y1), (x2, y2), BOX_COLOR, 2)
                cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), BOX_COLOR, cv2.FILLED)
                if match:
                    cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(frame, email, (x1 + 6, y2 + 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 2)
                    if student_cur_status == 'absent':
                        markAttendance(student_data, status, course_data, date)
                else:
                    print("*** There's a potential intruder")
                    cv2.putText(frame, "UNKNOWN PERSON", (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255),
                                2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


def get_cam_status():
    try:
        global camera
        return camera is not None
    except:
        e = sys.exec_info()[0]
        print(e)
    return False


@app.route("/p_video_feed")
def p_video_feed():
    global camera
    global course_camera
    global date_camera
    return Response(gen_frames(camera, course_camera, date_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/p_start_video_feed")
def p_start_video_feed():
    global camera
    global course_camera
    global date_camera
    course_camera = request.args.get('course')
    date_camera = request.args.get('date')
    course_id = requests.get(domain_name + f"/api/courses/title/{course_camera}",
                             params={"key": app.secret_key}).json()['id']

    is_contain = requests.get(domain_name + f"/api/attendees/contain_image/{course_id}",
                 params={"key": app.secret_key}).json()['is_contain']
    if is_contain:
        camera = cv2.VideoCapture(0)
    else:
        global is_submit, message_send
        is_submit, message_send = True, "No image to scan"
    return redirect(f"/{course_camera}/attendance/list/{date_camera}")


@app.route("/p_end_video_feed")
def p_end_video_feed():
    end_video_feed()
    global course_camera
    global date_camera
    return redirect(f"/{course_camera}/attendance/list/{date_camera}")


# ---------------------------------------------------------
#      U P L O A D / D I S P L A Y   I M A G E
# ---------------------------------------------------------


@app.route("/<course>/upload-image", methods=["POST"])
def upload_image(course):
    if request.method == "POST":

        if request.files:
            image = request.files["image"]
            email = request.form['email']

            course_id, student_id = requests.get(domain_name + f"/api/courses/title/{course}",
                                                 params={"key": app.secret_key}).json()['id'], \
                                    requests.get(domain_name + f"/api/students/{email}",
                                                 params={"key": app.secret_key}).json()['id']
            requests.put(domain_name + "/api/attendees/upload_image",
                         json={
                             "course_id": course_id, "student_id": student_id, "image": image.filename
                         }
                         )
            image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))
            # we should find a way to use relative path

            print("Image saved")

    return redirect(f"/{course}/roster")


@app.route("/display_image/<email>/<course>")
def test_img(email, course):
    try:
        course_id, student_id = requests.get(domain_name + f"/api/courses/title/{course}",
                                             params={"key": app.secret_key}).json()['id'], \
                                requests.get(domain_name + f"/api/students/{email}",
                                             params={"key": app.secret_key}).json()['id']
        response = requests.get(domain_name + f"/api/attendees/get_image/{course_id}/{student_id}",
                                params={"key": app.secret_key}).json()

        # image = os.path.join(app.config['UPLOAD_FOLDER'], 'Bill_Gates.JPG')
        print(response['image'])
        return redirect(url_for('static', filename="/images/" + response['image']))
        # return render_template("image_display.html", url="/images/" + response['image'])
    except:
        redirect_404_page("Not Found")


# ---------------------------------------------------------
#                    L O G O U T
# ---------------------------------------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
