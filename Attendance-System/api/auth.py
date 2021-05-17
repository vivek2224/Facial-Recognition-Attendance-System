import bcrypt
from flask import jsonify, request

from db.db import mysql_con
from flaskapp import app


@app.route("/api/login", methods=['POST'])
def api_test():
    if request.args.get('key') != app.secret_key:
        return jsonify({"message": "unauthorized key"}), 401
    try:
        req_body = request.json
        hash_pass = bcrypt.hashpw(req_body['pass'], bcrypt.gensalt())
        print(hash_pass)
        mysql_cur = mysql_con.cursor()
        mysql_cur.execute("SELECT * FROM USER WHERE email = %s AND BINARY pass = %s",
                          req_body['email'], hash_pass)
        mysql_cur.close()
    except Exception as e:
        return jsonify({"message": e}), 500
