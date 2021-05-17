from flask import Flask

app = Flask(__name__)
app.secret_key = "wkim123"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = '131pythonproject@gmail.com'
app.config['MAIL_PASSWORD'] = '131Project#1'