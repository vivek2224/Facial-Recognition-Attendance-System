from flask import jsonify, request, Blueprint
from flaskapp import app
from db.db import mysql_con

books = [
    {'id': 0,
     'title': 'A Fire Upon the Deep',
     'author': 'Vernor Vinge',
     'first_sentence': 'The coldsleep itself was dreamless.',
     'year_published': '1992'},
    {'id': 1,
     'title': 'The Ones Who Walk Away From Omelas',
     'author': 'Ursula K. Le Guin',
     'first_sentence': 'With a clamor of bells that set the swallows soaring, the Festival of Summer came to the city Omelas, bright-towered by the sea.',
     'published': '1973'},
    {'id': 2,
     'title': 'Dhalgren',
     'author': 'Samuel R. Delany',
     'first_sentence': 'to wound the autumnal city.',
     'published': '1975'}
]


# extract param
# request.args.get('')

# extract body
# request.json

@app.route("/test_api", methods=['GET', 'POST'])
def api_test():
    if request.args.get('key') != app.secret_key:
        return jsonify({"message": "unauthorized key"}), 401

    if request.method == 'POST':
        data = request.json
        books.append(data)
        return jsonify(data)
    #print(request.args.get('key'))
    return jsonify(books)



@app.route("/test_DB", methods=['GET'])
def db_test():
    try:
        if request.args.get('key') != app.secret_key:
            return jsonify({"message": "unauthorized key"}), 401
        mysql_cur = mysql_con.cursor();
        mysql_cur.execute('SELECT * FROM courses limit 10')
        result = mysql_cur.fetchall()
        mysql_cur.close()
    except:
        return jsonify({"message": "error"}), 500
    return jsonify(result)
