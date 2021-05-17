import bcrypt
import sys
from flask import jsonify, request
import requests

from db.db import mysql_con
from flaskapp import app

from datetime import datetime, timedelta


# test api
@app.route("/api/generate_pass", methods=['POST'])
def api_gen_pass():
    try:
        req_body = request.json
        hash_pass = bcrypt.hashpw(req_body['pass'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return jsonify({"hash_pass": hash_pass})
    except:
        return jsonify({"message": "error"}), 500


domain_name = 'http://127.0.0.1:5000'


def api_add_escape(string):  # for SQL wildcard
    string = string.replace('%', '\%')
    string = string.replace('_', '\_')
    return string


# -----------------LOGIN---------------------------
@app.route("/api/login", methods=['POST'])
def api_login():
    try:
        req_body = request.json  # retrieve json content
        mysql_cur = mysql_con.cursor()
        mysql_con.ping(reconnect=True)
        mysql_cur.execute("SELECT * FROM users WHERE email = %s", (req_body['email']))
        res_data = mysql_cur.fetchone()
        mysql_cur.close()
        if bcrypt.checkpw(req_body['pass'].encode('utf-8'), res_data['pass'].encode('utf-8')):  # compare password
            return jsonify({
                "id": res_data['id'],
                "email": res_data['email'],
                "first_name": res_data['first_name'],
                "last_name": res_data['last_name'],
                "admin": True if (res_data['user_role'] == "admin") else False,
                "pass": res_data['pass']}), 201
        else:
            return jsonify({"message": "invalid credentials"}), 401
    except:
        return jsonify({"message": "error"}), 500


# -----------------REGISTER---------------------------
# Should ask team about registration
# Might need a secret key...
@app.route("/api/create_account", methods=['POST'])
def api_create_account():
    try:
        req_body = request.json
        res_body = requests.get(f"{domain_name}/api/users/{req_body['email']}", params={"key": app.secret_key})
        if res_body.json() is not None:
            return jsonify({"message": "account conflict"}), 403
        mysql_cur = mysql_con.cursor()
        hash_pass = bcrypt.hashpw(req_body['pass'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        mysql_con.ping(reconnect=True)
        mysql_cur.execute("INSERT INTO users (first_name, last_name, email, pass, user_role) " +
                          "VALUES (%s, %s, %s, %s, %s)",
                          (req_body['first_name'], req_body['last_name'], req_body['email'], hash_pass,
                           req_body['user_role']))
        mysql_con.commit()
        mysql_cur.close()
        return jsonify({"email": req_body['email'], "user_role": req_body['user_role'], "pass": hash_pass}), 201
    except:
        return jsonify({"message": "error"}), 500


# ----------------USERS-------------------
@app.route("/api/users", methods=['GET'])  # only admin could query this
def api_users():
    try:
        if request.args.get('key') != app.secret_key:
            return jsonify({"message": "unauthorized key"}), 401

        mysql_cur = mysql_con.cursor()
        mysql_con.ping(reconnect=True)
        mysql_cur.execute("SELECT * FROM users")
        res_body = mysql_cur.fetchall()
        mysql_cur.close()
        return jsonify(res_body)
    except:
        return jsonify({"message": "error"}), 500


@app.route("/api/users/<email>", methods=['GET', 'PUT', 'DELETE'])
def api_users_by_email(email):
    try:
        if request.args.get('key') != app.secret_key:
            return jsonify({"message": "unauthorized key"}), 401

        mysql_cur = mysql_con.cursor()
        mysql_con.ping(reconnect=True)
        if request.method == 'GET':
            mysql_cur.execute("SELECT * FROM users WHERE email = %s", email)
            res_body = mysql_cur.fetchone()
        elif request.method == 'PUT':
            req_body = request.json
            mysql_cur.execute("UPDATE users SET first_name = %s, last_name = %s "
                              "WHERE id = (SELECT id FROM users WHERE email = %s)",
                              (req_body['first_name'], req_body['last_name'], email))
            mysql_con.commit()
            res_body = req_body
            res_body['email'] = email
        else:
            mysql_cur.execute("DELETE FROM users WHERE id = (select id from users where email = %s)", email)
            mysql_con.commit()
            res_body = {'email': email}
        mysql_cur.close()
    except:
        return jsonify({"message": "error"}), 500
    return jsonify(res_body), 200


# ----------------COURSES-------------------
@app.route("/api/courses", methods=['GET', 'POST'])  # for admin
def api_courses():
    if request.args.get('key') != app.secret_key:
        return jsonify({"message": "unauthorized key"}), 401

    try:
        mysql_cur = mysql_con.cursor()
        mysql_con.ping(reconnect=True)
        if request.method == 'GET':
            mysql_cur.execute("SELECT C.*, C_dt.days, C_dt.start_time, C_dt.end_time FROM courses C "
                              "LEFT JOIN course_dt_time C_dt ON C.id = C_dt.course_id ")
            res_body = mysql_cur.fetchall()
            status = 200
        else:
            req_body = request.json
            print(req_body)
            mysql_cur.execute(f"INSERT INTO courses (user_id, title, title_id, units, start_dt, end_dt) "
                              f"VALUE ({req_body['user_id']}, '{req_body['title']}', '{req_body['title_id'].replace(' ', '_')}', "
                              f"{req_body['units']}, '{req_body['start_dt']}', '{req_body['end_dt']}')")
            mysql_con.commit()
            mysql_cur.close()
            mysql_cur = mysql_con.cursor()
            mysql_con.ping(reconnect=True)
            mysql_cur.execute(f"INSERT INTO course_dt_time (course_id, days, start_time, end_time) "
                              f"VALUE ((select id from courses where title_id = '{req_body['title_id'].replace(' ', '_')}'), '{req_body['days']}', "
                              f"'{req_body['start_time']}', '{req_body['end_time']}')")
            mysql_con.commit()
            res_body = req_body
            status = 201
        mysql_cur.close()
    except:
        return jsonify({"message": "error"}), 500
    return jsonify(res_body), status


@app.route("/api/courses/<id>", methods=['GET', 'PUT', 'DELETE'])
def api_courses_by_id(id):
    if request.args.get('key') != app.secret_key:
        return jsonify({"message": "unauthorized key"}), 401
    try:
        mysql_cur = mysql_con.cursor()
        mysql_con.ping(reconnect=True)
        if request.method == 'GET':
            mysql_cur.execute("SELECT C.*, C_dt.days, C_dt.start_time, C_dt.end_time FROM courses C "
                              "LEFT JOIN course_dt_time C_dt ON C.id = C_dt.course_id "
                              "WHERE C.id = %s", str(id))
            res_body = mysql_cur.fetchone()
        elif request.method == 'PUT':
            req_body = request.json
            mysql_cur.execute("UPDATE courses SET user_id = %s, title = %s, start_dt = %s, end_dt = %s "
                              "WHERE id = " + str(id),
                              (str(req_body['user_id']), req_body['title'], req_body['start_dt'], req_body['end_dt']))
            mysql_con.commit()
            res_body = req_body
            res_body['id'] = id
        else:
            mysql_cur.execute("DELETE FROM courses WHERE id = " + str(id))
            mysql_con.commit()
            res_body = {'id': id}
        mysql_cur.close()
    except:
        return jsonify({"message": "error"}), 500
    return jsonify(res_body), 200


@app.route("/api/courses/title/<title_id>", methods=['GET'])  # GET course by title
def api_courses_by_title(title_id):
    if request.args.get('key') != app.secret_key:
        return jsonify({"message": "unauthorized key"}), 401
    try:
        mysql_cur = mysql_con.cursor()
        mysql_con.ping(reconnect=True)
        mysql_cur.execute("SELECT C.*, C_dt.days, C_dt.start_time, C_dt.end_time FROM courses C "
                          "LEFT JOIN course_dt_time C_dt ON C.id = C_dt.course_id "
                          "WHERE C.title_id = %s", title_id)
        res_body = mysql_cur.fetchone()
        print(res_body)
        mysql_cur.close()
        return jsonify(res_body), 200
    except:
        return jsonify({"message": "error"}), 500


@app.route("/api/courses/all/<user_id>", methods=['GET'])  # GET all course by user_id
def api_courses_by_user_id(user_id):
    if request.args.get('key') != app.secret_key:
        return jsonify({"message": "unauthorized key"}), 401
    try:
        mysql_cur = mysql_con.cursor()
        mysql_con.ping(reconnect=True)
        mysql_cur.execute("SELECT C.*, C_dt.days, C_dt.start_time, C_dt.end_time FROM courses C "
                          "LEFT JOIN course_dt_time C_dt ON C.id = C_dt.course_id "
                          "WHERE C.user_id = " + str(user_id))
        res_body = mysql_cur.fetchall()
        mysql_cur.close()
        return jsonify(res_body), 200
    except:
        return jsonify({"message": "error"}), 500


@app.route("/api/courses/<title>/<user_id>", methods=['GET'])  # GET specific course by user_id
def api_course_by_user_id_and_title(title, user_id):
    if request.args.get('key') != app.secret_key:
        return jsonify({"message": "unauthorized key"}), 401
    try:
        mysql_cur = mysql_con.cursor()
        mysql_con.ping(reconnect=True)
        mysql_cur.execute("SELECT C.*, C_dt.days, C_dt.start_time, C_dt.end_time FROM courses C "
                          "LEFT JOIN course_dt_time C_dt ON C.id = C_dt.course_id "
                          "WHERE user_id = %s AND title = %s", (str(user_id), title))
        res_body = mysql_cur.fetchone()
        mysql_cur.close()
        return jsonify(res_body), 200
    except:
        return jsonify({"message": "error"}), 500


@app.route("/api/courses/search", methods=['POST'])  # course search for admin
def api_course_all_search():
    try:
        req_body = request.json
        req_body['title_id'] = api_add_escape(req_body['title_id'])
        mysql_cur = mysql_con.cursor()
        mysql_con.ping(reconnect=True)
        mysql_cur.execute("SELECT C.*, C_dt.days, C_dt.start_time, C_dt.end_time FROM courses C "
                          "LEFT JOIN course_dt_time C_dt ON C.id = C_dt.course_id "
                          f"WHERE title_id LIKE '%{req_body['title_id']}%'")
        res_body = mysql_cur.fetchall()
        mysql_cur.close()
        return jsonify(res_body), 200
    except:
        return jsonify({"message": "error"}), 500


@app.route("/api/courses/search/<user_id>", methods=['POST'])
def api_course_search(user_id):
    try:
        req_body = request.json
        req_body['title_id'] = api_add_escape(req_body['title_id'])
        mysql_cur = mysql_con.cursor()
        mysql_con.ping(reconnect=True)
        mysql_cur.execute("SELECT C.*, C_dt.days, C_dt.start_time, C_dt.end_time FROM courses C "
                          "LEFT JOIN course_dt_time C_dt ON C.id = C_dt.course_id "
                          f"WHERE C.user_id = {str(user_id)} AND title_id LIKE '%{req_body['title_id']}%'")
        res_body = mysql_cur.fetchall()
        mysql_cur.close()
        return jsonify(res_body), 200
    except:
        return jsonify({"message": "error"}), 500


# ----------------Student-------------------
@app.route("/api/students", methods=['GET', 'POST'])
def api_students():
    if request.args.get('key') != app.secret_key:
        return jsonify({"message": "unauthorized key"}), 401

    try:
        mysql_cur = mysql_con.cursor()
        mysql_con.ping(reconnect=True)
        if request.method == 'GET':
            mysql_cur.execute("SELECT * FROM students ORDER BY id ASC")
            res_body = mysql_cur.fetchall()
            status = 200
        else:
            req_body = request.json
            print(req_body)
            mysql_cur.execute("INSERT INTO students (first_name, last_name, email) " +
                              "VALUES ( %s, %s, %s)",
                              (req_body['first_name'], req_body['last_name'], req_body['email']))
            mysql_con.commit()
            res_body = req_body
            status = 201
        mysql_cur.close()
    except:
        return jsonify({"message": "error"}), 500
    return jsonify(res_body), status


@app.route("/api/students/<email>", methods=['GET', 'PUT'])
def api_students_by_id(email):
    if request.args.get('key') != app.secret_key:
        return jsonify({"message": "unauthorized key"}), 401
    try:
        mysql_cur = mysql_con.cursor()
        mysql_con.ping(reconnect=True)
        if request.method == "GET":
            mysql_cur.execute(f"SELECT * FROM students WHERE email = \'{email}\'")
            res_body = mysql_cur.fetchone()
        else:
            req_body = request.json
            print(req_body)
            mysql_cur.execute(f"UPDATE students "
                              f"SET first_name = '{req_body['first_name']}', last_name = '{req_body['last_name']}' "
                              f"WHERE email = '{email}'")
            mysql_con.commit()
            res_body = req_body
        return jsonify(res_body), 200
    except:
        return jsonify({"message": "error"}), 500


@app.route("/api/students/search", methods=['POST'])
def api_students_search():
    req_body = request.json
    try:
        mysql_cur = mysql_con.cursor()
        mysql_con.ping(reconnect=True)
        req_body['name'] = api_add_escape(req_body['name'])
        mysql_cur.execute(f"SELECT * FROM students "
                          f"WHERE first_name LIKE '%{req_body['name']}%' OR last_name LIKE '%{req_body['name']}%' "
                          f"ORDER BY id ASC")
        res_body = mysql_cur.fetchall()
        return jsonify(res_body)
    except:
        return jsonify({"message": "error"}), 500


# ----------------Attendant /Attendance List-------------------
'''
@app.route("/api/attendance_list/<course_id>/<day>", methods=['GET', 'POST'])  # add post for filter
def api_attendance_list_by_course_id_day(course_id, day):
    if request.args.get('key') != app.secret_key:
        return jsonify({"message": "unauthorized key"}), 401

    query = ("SELECT A.id, S.id student_id, C.id course_id, title_id, first_name, last_name, email, A.student_status "
             "FROM attendants A "
             "INNER JOIN courses C ON C.id = A.course_id INNER JOIN students S ON S.id = A.student_id "
             f"WHERE C.id = {course_id} AND A.created_at BETWEEN \'{day}\' AND (SELECT DATE_ADD(\'{day}\', INTERVAL 1 DAY))")
    query_sort = " ORDER BY last_name ASC"
    try:
        mysql_cur = mysql_con.cursor()
        if request.method == 'GET':
            mysql_cur.execute(query + query_sort)
            res_body = mysql_cur.fetchall()
        else:
            req_body = request.json
            req_body['name'] = api_add_escape(req_body['name'])
            req_body['name'] = '%' + req_body['name'] + '%'
            mysql_cur.execute(query + " AND student_status = %s AND (first_name LIKE %s OR last_name LIKE %s)" + query_sort,
                              (req_body['student_status'], req_body['name'], req_body['name']))
            res_body = mysql_cur.fetchall()
        mysql_cur.close()
    except:
        return jsonify({"message": "error"}), 500
    return jsonify(res_body)


@app.route("/api/attendant/<course_id>", methods=['POST', 'DELETE'])
def api_attendant_by_course_id(course_id):
    try:
        mysql_cur = mysql_con.cursor()
        if request.method == 'POST':
            mysql_cur.execute("INSERT INTO attendants (course_id, student_id) SELECT C.id, S.id FROM attendees A "
                              "INNER JOIN courses C ON C.id = A.course_id INNER JOIN students S ON S.id = A.student_id "
                              "WHERE C.id = " + str(course_id))
            mysql_con.commit()
            status = 201
        else:
            mysql_cur.execute("DELETE FROM attendants WHERE course_id = " + str(course_id))
            mysql_con.commit()
            status = 200
    except:
        return jsonify({"message": "error"}), 500
    return jsonify({"course_id": course_id}), status
'''


@app.route("/api/attendance_list/generate", methods=['POST'])
def api_attendance_list_gen():
    print("Call this api")
    try:
        req_body = request.json
        print(req_body['date'])
        print(req_body['course_id'])
        mysql_cur = mysql_con.cursor()
        mysql_con.ping(reconnect=True)
        mysql_cur.execute(f"INSERT INTO attendants (student_id, course_id, lec_date) "
                          f"SELECT student_id, course_id, '{req_body['date']}' FROM attendees "
                          f"WHERE course_id = {req_body['course_id']}")
        mysql_con.commit()
        mysql_con.close()
        return jsonify({"course_id": req_body['course_id'], "lec_date": req_body['date']}), 200
    except:
        return jsonify({"message": "error"}), 500


@app.route("/api/attendance_list/delete", methods=['DELETE'])
def api_attendance_list_delete():
    try:
        req_body = request.json
        print(req_body['course_id'])
        mysql_cur = mysql_con.cursor()
        mysql_con.ping(reconnect=True)
        mysql_cur.execute(f"DELETE INTO attendants  "
                          f"WHERE course_id = {req_body['course_id']}")
        mysql_con.commit()
        mysql_con.close()
        return jsonify({req_body}), 200
    except:
        return jsonify({"message": "error"}), 500


@app.route("/api/attendance_list/<course_id>/<day>", methods=['GET'])
def api_attendance_list_by_course_id_day(course_id, day):
    if request.args.get('key') != app.secret_key:
        return jsonify({"message": "unauthorized key"}), 401

    query = ("SELECT C.id course_id, S.id student_id, first_name, last_name, email, student_status "
             "FROM attendants A INNER JOIN courses C ON A.course_id = C.id "
             "INNER JOIN students S ON A.student_id = S.id "
             f"WHERE A.lec_date = '{day}' AND C.id = '{course_id}'")
    query_sort = " ORDER BY last_name ASC"
    try:
        mysql_cur = mysql_con.cursor()
        mysql_con.ping(reconnect=True)
        mysql_cur.execute(query + query_sort)
        res_body = mysql_cur.fetchall()
        mysql_con.close()
        return jsonify(res_body), 200
    except:
        return jsonify({"message": "error"}), 500


@app.route("/api/courses/get_lec_dates/<title_id>", methods=['GET'])
def api_course_get_lec_dates(title_id):
    if request.args.get('key') != app.secret_key:
        return jsonify({"message": "unauthorized key"}), 401
    try:
        res_body = requests.get(domain_name + f"/api/courses/title/{title_id}", params={"key": app.secret_key}).json()
        weekdate_map = {'M': 0, 'T': 1, 'W': 2, 'R': 3, 'F': 4}
        start_dt_str, end_dt_str = res_body['start_dt'].split(), res_body['end_dt'].split()
        start_dt = datetime.strptime(f"{start_dt_str[2]} {start_dt_str[1]} {start_dt_str[3]}", '%b %d %Y')
        end_dt = datetime.strptime(f"{end_dt_str[2]} {end_dt_str[1]} {end_dt_str[3]}", '%b %d %Y')
        date_diff = (end_dt - start_dt).days + 1

        lec_date_list = []
        for i in range(date_diff):
            date = (start_dt + timedelta(days=i))
            weekday = date.weekday()
            match = False
            for lec_day in list(res_body['days']):
                if weekdate_map[lec_day] == weekday:
                    match = True
            if match:
                lec_date_list.append(date)
        return jsonify({"course_id": res_body['id'], "lec_date": lec_date_list}), 200

    except:
        return jsonify({"message": "error"}), 500


@app.route("/api/attendants/count_attendances/<course_id>/<day>", methods=['GET'])
def api_attendants_get_count(course_id, day):
    try:
        if request.args.get('key') != app.secret_key:
            return jsonify({"message": "unauthorized key"}), 401

        mysql_cur = mysql_con.cursor()
        mysql_con.ping(reconnect=True)
        mysql_cur.execute("SELECT present, tardy, absent FROM "
                          "(SELECT 0 as id, COUNT(student_status) as present FROM attendants "
                          f"WHERE course_id = {course_id} AND lec_date = '{day}'"
                          "AND student_status = 'present') P "
                          "INNER JOIN "
                          "(SELECT 0 as id, COUNT(student_status) as tardy FROM attendants "
                          f"WHERE course_id = {course_id} AND lec_date = '{day}' "
                          "AND student_status = 'tardy') T ON P.id = T.id "
                          "INNER JOIN "
                          "(SELECT 0 as id, COUNT(student_status) as absent FROM attendants "
                          f"WHERE course_id = {course_id} AND lec_date = '{day}' "
                          "AND student_status = 'absent') A ON P.id = A.id")
        res_body = mysql_cur.fetchone()
        mysql_con.close()

        return jsonify({"course_id": course_id, "lec_date": day, "status": res_body}), 200
    except:
        return jsonify({"message": "error"}), 500


@app.route("/api/attendants/get_status", methods=['GET'])
def api_attendants_get_status():
    try:
        if request.args.get('key') != app.secret_key:
            return jsonify({"message": "unauthorized key"}), 401
        req_body = request.json
        mysql_cur = mysql_con.cursor()
        mysql_con.ping(reconnect=True)
        mysql_cur.execute(f"SELECT * FROM attendants "
                          f"WHERE student_id = {req_body['student_id']} AND course_id = {req_body['course_id']} "
                          f"AND lec_date = '{req_body['date']}'")
        res_body = mysql_cur.fetchone()
        mysql_con.close()
        return jsonify(res_body), 200
    except:
        return jsonify({"message": "error"}), 500


@app.route("/api/attendants/change_status", methods=['PUT'])
def api_attendants_change_status():
    try:
        req_body = request.json
        mysql_cur = mysql_con.cursor()
        mysql_con.ping(reconnect=True)
        mysql_cur.execute(f"UPDATE attendants SET student_status = '{req_body['student_status']}' "
                          f"WHERE student_id = {req_body['student_id']} AND course_id = {req_body['course_id']} "
                          f"AND lec_date = '{req_body['date']}'")
        mysql_con.commit()
        mysql_con.close()
        return jsonify(
            {"student_id": req_body['student_id'],
             "course_id": req_body['course_id'],
             "date": req_body['date'],
             "student_status": req_body['student_status']
             }
        ), 200
    except:
        return jsonify({"message": "error"}), 500


# ----------------Attendees /Roster-------------------
@app.route("/api/roster/<course_id>", methods=['GET', 'POST', 'DELETE'])  # add post for filter
def api_roster_by_course_id(course_id):
    if request.args.get('key') != app.secret_key:
        return jsonify({"message": "unauthorized key"}), 401

    query = ("SELECT C.id course_id, S.id student_id, first_name, last_name, email, image FROM attendees A "
             "INNER JOIN courses C ON C.id = A.course_id INNER JOIN students S ON S.id = A.student_id "
             f"WHERE C.id = {course_id}")
    query_sort = " ORDER BY last_name ASC"
    try:
        mysql_cur = mysql_con.cursor()
        mysql_con.ping(reconnect=True)
        if request.method == 'GET':
            mysql_cur.execute(query + query_sort)
            res_body = mysql_cur.fetchall()
        elif request.method == 'POST':
            req_body = request.json
            req_body['name'] = api_add_escape(req_body['name'])
            req_body['name'] = '%' + req_body['name'] + '%'
            mysql_cur.execute(query + " AND (first_name LIKE %s OR last_name LIKE %s)" + query_sort,
                              (req_body['name'], req_body['name']))
            res_body = mysql_cur.fetchall()
        else:
            mysql_cur.execute("DELETE FROM attendees WHERE course_id = " + str(course_id))
            mysql_con.commit()
            res_body = {"course_id", course_id}
        mysql_cur.close()
    except:
        return jsonify({"message": "error"}), 500
    return jsonify(res_body)


@app.route("/api/roster/<course_id>/<student_id>", methods=['GET'])
def api_roster_by_course_id_student_id(course_id, student_id):
    if request.args.get('key') != app.secret_key:
        return jsonify({"message": "unauthorized key"}), 401
    try:

        mysql_cur = mysql_con.cursor()
        mysql_con.ping(reconnect=True)
        mysql_cur.execute(f"SELECT * FROM attendees WHERE course_id = {course_id} and student_id = {student_id}")
        res_body = mysql_cur.fetchone()
        mysql_con.close()
        return jsonify(res_body), 200
    except:
        return jsonify({"message": "error"}), 500


@app.route("/api/attendees/<course_id>", methods=['POST', 'DELETE'])
def api_attendees_by_course_id(course_id):  # add new student or delete student to roster
    try:
        mysql_cur = mysql_con.cursor()
        req_body = request.json
        mysql_con.ping(reconnect=True)
        if request.method == 'POST':
            mysql_cur.execute("INSERT INTO attendees (course_id, student_id) VALUE "
                              f"({course_id}, {req_body['student_id']})")
            mysql_con.commit()
            status = 201
        else:
            mysql_cur.execute("DELETE FROM attendees WHERE "
                              f"course_id = {course_id} AND student_id = {req_body['student_id']}")
            mysql_con.commit()
            status = 200
        mysql_cur.close()
    except:
        return jsonify({"message": "error"}), 500
    return jsonify({"course_id": course_id, "student_id": req_body['student_id']}), status


# Useful of student deletion
@app.route("/api/attendees/remove_all/<student_id>", methods = ['DELETE'])
def api_attendees_remove_by_student(student_id):
    try:
        mysql_cur = mysql_con.cursor()
        mysql_con.ping(reconnect=True)
        mysql_cur.execute("DELETE FROM attendees WHERE student_id = {student_id}")
        mysql_con.commit()
        mysql_cur.close()
        return jsonify({"student_id": student_id})
    except:
        return jsonify({"message": "error"}), 500


@app.route("/api/attendants/remove_all/<student_id>", methods=['DELETE'])
def api_attendants_remove_by_student(student_id):
    try:
        mysql_cur = mysql_con.cursor()
        mysql_con.ping(reconnect=True)
        mysql_cur.execute("DELETE FROM attendants WHERE student_id = {student_id}")
        mysql_con.commit()
        mysql_cur.close()
        return jsonify({"student_id": student_id})
    except:
        return jsonify({"message": "error"}), 500


@app.route("/api/attendees/contain_image/<course_id>", methods=['GET'])
def api_attendees_contain_image(course_id):
    try:
        if request.args.get('key') != app.secret_key:
            return jsonify({"message": "unauthorized key"}), 401
        mysql_cur = mysql_con.cursor()
        mysql_con.ping(reconnect=True)
        mysql_cur.execute(f"SELECT * FROM attendees "
                          f"WHERE course_id = {course_id} AND image IS NOT NULL")
        res_body = mysql_cur.fetchone()
        result = True if res_body else False
        return jsonify({"is_contain": result}), 200
    except:
        return jsonify({"message": "error"}), 500


@app.route("/api/attendees/upload_image", methods=['PUT'])
def api_attendees_upload_image():
    try:
        mysql_cur = mysql_con.cursor()
        req_body = request.json
        mysql_con.ping(reconnect=True)
        if request.method == 'PUT':
            mysql_cur.execute(f"UPDATE attendees SET image = \'{req_body['image']}\' "
                              f"WHERE student_id = {req_body['student_id']} AND course_id = {req_body['course_id']}")
            mysql_con.commit()
            mysql_con.close()
        return jsonify(
            {"course_id": req_body['course_id'], "student_id": req_body['student_id'], "image": req_body['image']}
        ), 200
    except:
        return jsonify({"message": "error"}), 500


@app.route("/api/attendees/get_image/<course_id>/<student_id>", methods=['GET'])
def api_attendees_get_image(course_id, student_id):
    try:
        mysql_cur = mysql_con.cursor()
        req_body = request.json
        mysql_con.ping(reconnect=True)
        mysql_cur.execute("SELECT image FROM attendees "
                          f"WHERE student_id = {student_id} AND course_id = {course_id}")
        res_body = mysql_cur.fetchone()
        return jsonify(res_body), 200
    except:
        return jsonify({"message": "error"}), 500


# remove students
# call
