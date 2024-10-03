import sqlite3
import os
from pathlib import Path

from flask import Flask, g, render_template, request, session, \
    flash, redirect, url_for, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

# internal postgresql://ece444_deploy_dbtest_dhzl_user:lSRv6dycgmocbXfsOGE2OrYR6XpgOGR8@dpg-crvgm0e8ii6s73e87iqg-a/ece444_deploy_dbtest_dhzl

# external postgresql://ece444_deploy_dbtest_dhzl_user:lSRv6dycgmocbXfsOGE2OrYR6XpgOGR8@dpg-crvgm0e8ii6s73e87iqg-a.oregon-postgres.render.com/ece444_deploy_dbtest_dhzl

basedir = Path(__file__).resolve().parent

# configuration
DATABASE = "flaskr.db"
USERNAME = "admin"
PASSWORD = "admin"
SECRET_KEY = "change_me"
SQLALCHEMY_TRACK_MODIFICATIONS = False

url = os.getenv('DATABASE_URL', f'sqlite:///{Path(basedir).joinpath(DATABASE)}')

if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_DATABASE_URI = "postgresql://ece444_deploy_dbtest_dhzl_user:lSRv6dycgmocbXfsOGE2OrYR6XpgOGR8@dpg-crvgm0e8ii6s73e87iqg-a.oregon-postgres.render.com/ece444_deploy_dbtest_dhzl"


# create and initialize a new Flask app
app = Flask(__name__)
# load the config
app.config.from_object(__name__)
# init sqlalchemy
db = SQLAlchemy(app)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in.')
            return jsonify({'status': 0, 'message': 'Please log in.'}), 401
        return f(*args, **kwargs)
    return decorated_function


from .models import Post

@app.route('/')
def index():
    """Searches the database for entries, then displays them."""
    entries = db.session.query(Post)
    return render_template('index.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    """Adds new post to the database."""
    if not session.get('logged_in'):
        abort(401)
    new_entry = Post(request.form['title'], request.form['text'])
    db.session.add(new_entry)
    db.session.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login/authentication/session management."""
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    """User logout/authentication/session management."""
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))


@app.route('/delete/<int:post_id>', methods=['GET'])
@login_required
def delete_entry(post_id):
    """Deletes post from database."""
    result = {'status': 0, 'message': 'Error'}
    try:
        new_id = post_id
        db.session.query(Post).filter_by(id=new_id).delete()
        db.session.commit()
        result = {'status': 1, 'message': "Post Deleted"}
        flash('The entry was deleted.')
    except Exception as e:
        result = {'status': 0, 'message': repr(e)}
    return jsonify(result)


@app.route('/search/', methods=['GET'])
def search():
    query = request.args.get("query")
    entries = db.session.query(Post)
    if query:
        return render_template('search.html', entries=entries, query=query)
    return render_template('search.html')


if __name__ == "__main__":
    app.run()