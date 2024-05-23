from flask import Flask, request, render_template, g
import sqlite3

DATABASE = 'crawler.db'

app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    db = get_db()
    cur = db.execute("SELECT url, title, content FROM pages WHERE content LIKE ?", ('%' + query + '%',))
    results = cur.fetchall()
    return render_template('search.html', query=query, results=results)

if __name__ == '__main__':
    app.run(debug=True)
