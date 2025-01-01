from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


if __name__ == '__main__':
    
    app.run(debug=True)

