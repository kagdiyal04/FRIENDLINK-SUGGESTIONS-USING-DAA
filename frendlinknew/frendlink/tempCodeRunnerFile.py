from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

# Import backend functions
from main import (
    init_db, is_name_unique, add_user, get_user_id_by_name, login,
    add_friend, delete_friend, suggest_friends, get_user_id_name,
    ignore_suggestion, get_friends
)

# Set consistent DB path
DB_PATH = os.path.join(os.path.dirname(__file__), 'friendlink.db')

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize DB only once
init_db()

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('suggestions'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form.get('username')
    password = request.form.get('password')
    user_id = login(username, password)
    if user_id:
        session['user_id'] = user_id
        session['username'] = username
        return redirect(url_for('suggestions'))
    else:
        return render_template('login.html', error="Invalid username or password")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age', type=int)
        location = request.form.get('location')
        interests = request.form.get('interests')
        password = request.form.get('password')
        photo = request.form.get('photo', '')

        if not is_name_unique(name):
            return render_template('register.html', error="Username already taken")

        add_user(name, age, location, interests, password, photo)

        # Add friends if any
        friend_names = request.form.get('friends', '')
        user_id = get_user_id_by_name(name)
        if user_id and friend_names:
            for fname in friend_names.split(","):
                fid = get_user_id_by_name(fname.strip())
                if fid:
                    add_friend(user_id, fid)

        return redirect(url_for('home'))
    else:
        return render_template('register.html')

@app.route('/suggestions')
def suggestions():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    user_id = session['user_id']

    # Get suggestions
    mutual_ids, similar_dict = suggest_friends(user_id)

    # Mutual friends: [(user_id, name)]
    mutual_suggestions = [(uid, get_user_id_name(uid)) for uid in mutual_ids]

    # Similar suggestions with details
    similar_suggestions = []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for uid, detail in similar_dict.items():
        cursor.execute("SELECT name, location FROM Users WHERE user_id = ?", (uid,))
        row = cursor.fetchone()
        if row:
            name, location = row
            similar_suggestions.append({
                'user_id': uid,
                'name': name,
                'location': location,
                'details': detail  # contains things like "age, interest: music, similarity: 43%"
            })

    conn.close()

    # Current friends
    friend_ids = get_friends(user_id)
    friends = [(fid, get_user_id_name(fid)) for fid in friend_ids]

    return render_template('suggestions.html',
                           mutual_suggestions=mutual_suggestions,
                           similar_suggestions=similar_suggestions,
                           friend_list=friends,
                           username=session.get('username'))

@app.route('/add_friend/<int:friend_id>')
def add_new_friend(friend_id):
    if 'user_id' not in session:
        return redirect(url_for('home'))
    add_friend(session['user_id'], friend_id)
    return redirect(url_for('suggestions'))

@app.route('/ignore/<int:ignored_id>')
def ignore(ignored_id):
    if 'user_id' not in session:
        return redirect(url_for('home'))
    ignore_suggestion(session['user_id'], ignored_id)
    return redirect(url_for('suggestions'))

@app.route('/delete_friend', methods=['POST'])
def delete_existing_friend():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    friend_id = request.form.get('friend_id', type=int)
    if friend_id:
        delete_friend(session['user_id'], friend_id)
    return redirect(url_for('suggestions'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
