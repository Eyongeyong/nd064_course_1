import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import sys, logging

DB_CONNECT_COUNT = 0
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global DB_CONNECT_COUNT

    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row

    DB_CONNECT_COUNT += 1

    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info("Article with ID: '{}' could not be found!".format(post_id))
      return render_template('404.html'), 404
    else:
      title = post['title']
      app.logger.info("Article '{}' got retrieved".format(title))
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('Page "About Us" got accessed!')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            app.logger.info("Article '{}' got created!".format(title))

            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def healthcheck():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    return response

@app.route('/metrics')
def metrics():
    con = get_db_connection()
    posts = con.execute('SELECT * FROM posts').fetchall()
    posts_count = len(posts)

    response = app.response_class(
            response=json.dumps({"db_connect_count":DB_CONNECT_COUNT , "post_count": posts_count}),
            status=200,
            mimetype='application/json'
    )
    return response
# start the application on port 3111
if __name__ == "__main__":
    format_out = '%(levelname)s: %(name)-1s - - [%(asctime)s] - %(message)s'
    logging.basicConfig(format=format_out, level=logging.DEBUG, handlers=[
        logging.StreamHandler(sys.stdout),
        logging.StreamHandler(sys.stderr)
    ])
    app.run(host='0.0.0.0', port='3111')


   
