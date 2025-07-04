import sqlite3
from collections import deque
import os

# ---------- DB PATH FIX ----------
DB_PATH = os.path.join(os.path.dirname(__file__), 'friendlink.db')

# ---------- DATABASE INITIALIZATION ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        age INTEGER,
        location TEXT,
        interests TEXT,
        password TEXT NOT NULL,
        profile_photo TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Friends (
        user_id INTEGER,
        friend_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES Users(user_id),
        FOREIGN KEY (friend_id) REFERENCES Users(user_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS IgnoredSuggestions (
        user_id INTEGER,
        ignored_user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES Users(user_id),
        FOREIGN KEY (ignored_user_id) REFERENCES Users(user_id)
    )
    """)

    conn.commit()
    conn.close()


# ---------- USER FUNCTIONS ----------
def is_name_unique(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    return result is None

def get_user_id_by_name(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM Users WHERE name = ?", (name,))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

def get_user_id_name(uid):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Users WHERE user_id = ?", (uid,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "Unknown"

def add_user(name, age, location, interests, password, photo_path):
    if not interests:
        interests = "none"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Users (name, age, location, interests, password, profile_photo) VALUES (?, ?, ?, ?, ?, ?)",
                   (name, age, location, interests, password, photo_path))
    conn.commit()
    conn.close()

def login(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM Users WHERE name = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        print("Login successful! Your user ID is:", user[0])
        return user[0]
    else:
        print("Login failed! Invalid username or password.")
        return None


# ---------- FRIEND FUNCTIONS ----------
def add_friend(user_id, friend_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Friends (user_id, friend_id) VALUES (?, ?)", (user_id, friend_id))
    cursor.execute("INSERT INTO Friends (user_id, friend_id) VALUES (?, ?)", (friend_id, user_id))
    conn.commit()
    conn.close()

def delete_friend(user_id, friend_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Friends WHERE user_id = ? AND friend_id = ?", (user_id, friend_id))
    cursor.execute("DELETE FROM Friends WHERE user_id = ? AND friend_id = ?", (friend_id, user_id))
    conn.commit()
    conn.close()

def ignore_suggestion(user_id, ignored_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO IgnoredSuggestions (user_id, ignored_user_id) VALUES (?, ?)", (user_id, ignored_id))
    conn.commit()
    conn.close()


# ---------- SUGGESTION HELPERS ----------
def get_friends(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT friend_id FROM Friends WHERE user_id = ?", (user_id,))
    result = cursor.fetchall()
    conn.close()
    return set(r[0] for r in result)

def get_ignored(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT ignored_user_id FROM IgnoredSuggestions WHERE user_id = ?", (user_id,))
    result = cursor.fetchall()
    conn.close()
    return set(r[0] for r in result)


# ---------- BFS BASED SUGGESTION ----------
def bfs_friend_suggestions(user_id):
    visited = set()
    queue = deque()
    suggestions = set()

    direct_friends = get_friends(user_id)
    ignored = get_ignored(user_id)

    queue.append((user_id, 0))
    visited.add(user_id)

    while queue:
        current, level = queue.popleft()
        if level > 2:
            continue
        for friend in get_friends(current):
            if friend not in visited:
                queue.append((friend, level + 1))
                visited.add(friend)
                if level == 1 and friend not in direct_friends and friend != user_id and friend not in ignored:
                    suggestions.add(friend)
    return suggestions


# ---------- JACCARD SIMILARITY BASED ----------
def jaccard_similarity_suggestions(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT age, location, interests FROM Users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        return {}
    age1, location1, interests1 = row
    if not interests1:
        return {}

    interests1 = set(map(str.strip, interests1.lower().split(",")))
    ignored = get_ignored(user_id)
    user_friends = get_friends(user_id)
    suggestions = {}

    cursor.execute("SELECT user_id, name, age, location, interests FROM Users WHERE user_id != ?", (user_id,))
    all_users = cursor.fetchall()

    for uid, name, age2, location2, interests2 in all_users:
        if uid in ignored or uid in user_friends:
            continue
        if not interests2:
            continue
        interests2_set = set(map(str.strip, interests2.lower().split(",")))
        intersection = interests1.intersection(interests2_set)
        union = interests1.union(interests2_set)
        if not union:
            continue
        jaccard_score = len(intersection) / len(union)
        if (location1 == location2 or abs(age1 - age2) <= 3) and jaccard_score >= 0.3:
            similarities = []
            if location1 == location2:
                similarities.append("location")
            if abs(age1 - age2) <= 3:
                similarities.append("age")
            if intersection:
                similarities.append(f"interests: {', '.join(intersection)}")
            percent = int(jaccard_score * 100)
            suggestions[uid] = f"{name} ({', '.join(similarities)}, similarity: {percent}%)"

    conn.close()
    return suggestions

def suggest_friends(user_id):
    mutual_ids = bfs_friend_suggestions(user_id)
    similar = jaccard_similarity_suggestions(user_id)  # Ensure always calculated
    return mutual_ids, similar


# ---------- MAIN MENU ----------
def menu():
    init_db()
    while True:
        print("\n--- FriendLink Smart Friend Suggestion ---")
        print("1. Add New User")
        print("2. Login and See Suggestions")
        print("3. Delete Friend")
        print("4. Exit")
        choice = input("Choose option: ")

        if choice == "1":
            while True:
                name = input("Name: ")
                if is_name_unique(name):
                    break
                print("Name already exists. Try another.")

            age = int(input("Age: "))
            location = input("Location: ")
            interests = input("Interests (comma separated): ")
            password = input("Password: ")
            photo = input("Profile Photo Filename: ")
            add_user(name, age, location, interests, password, photo)

            friend_names = input("Enter names of your direct friends (comma separated): ").split(",")
            friend_names = [f.strip() for f in friend_names]
            new_user_id = get_user_id_by_name(name)
            if new_user_id:
                for fname in friend_names:
                    fid = get_user_id_by_name(fname)
                    if fid:
                        add_friend(new_user_id, fid)
                print("User added and friends linked.")
            else:
                print("User created, but no valid friends linked.")

        elif choice == "2":
            username = input("Enter your Username: ")
            password = input("Enter your Password: ")
            user_id = login(username, password)
            if not user_id:
                continue

            mutual, similar = suggest_friends(user_id)
            if not mutual and not similar:
                print("No friend suggestions found.")
            else:
                if mutual:
                    print("\n--- Mutual Friends Suggestions ---")
                    for uid in mutual:
                        name = get_user_id_name(uid)
                        print(f" - {name} (User ID: {uid})")
                if similar:
                    print("\n--- Similar Users Suggestions ---")
                    for uid, detail in similar.items():
                        print(f" - {detail} (User ID: {uid})")

                to_add = input("\nEnter user ID to send friend request or type 'ignore <ID>': ").strip()
                if to_add.startswith("ignore"):
                    ignored_id = int(to_add.split()[1])
                    ignore_suggestion(user_id, ignored_id)
                    print(f"Ignored user {ignored_id}")
                elif to_add.isdigit():
                    add_friend(user_id, int(to_add))
                    print("Friend added.")

        elif choice == "3":
            username = input("Enter your Username: ")
            password = input("Enter your Password: ")
            user_id = login(username, password)
            if not user_id:
                continue
            friend_username = input("Enter Friend's Username to delete: ")
            friend_id = get_user_id_by_name(friend_username)
            if friend_id:
                delete_friend(user_id, friend_id)
                print("Friend deleted.")
            else:
                print("Friend not found.")

        elif choice == "4":
            print("Exiting.")
            break

        else:
            print("Invalid option.")

if __name__ == "__main__":
    menu()