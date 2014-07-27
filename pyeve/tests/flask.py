__author__ = 'Rudy'

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask('pyeve')

app.config['SQLALCHEMY_DATABASE_URL'] = 'mysql+pymysql://root:cycki@192.168.1.3/eve'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

@app.route('/')
def index():
    return 'HOWDY !!!'

if __name__ == '__main__':
    app.run()
