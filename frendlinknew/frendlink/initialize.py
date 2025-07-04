import sqlite3
import random

def add_friend(user_id, friend_id, cursor):
    cursor.execute("INSERT INTO Friends (user_id, friend_id) VALUES (?, ?)", (user_id, friend_id))
    cursor.execute("INSERT INTO Friends (user_id, friend_id) VALUES (?, ?)", (friend_id, user_id))

def add_50_random_friendships():
    conn = sqlite3.connect('friendlink.db')
    cursor = conn.cursor()

    user_ids = list(range(1, 51))  # Assuming user_ids are from 1 to 50

    added_pairs = set()
    friendships_to_add = 50

    while friendships_to_add > 0:
        u1, u2 = random.sample(user_ids, 2)  # pick two distinct users

        # Avoid duplicates and self-friendship
        pair = tuple(sorted((u1, u2)))
        if pair not in added_pairs:
            add_friend(u1, u2, cursor)
            added_pairs.add(pair)
            friendships_to_add -= 1

    conn.commit()
    conn.close()

# Run the function
add_50_random_friendships()
