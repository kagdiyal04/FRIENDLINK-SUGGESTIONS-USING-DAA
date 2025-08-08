# FRIENDLINK-SUGGESTIONS-USING-DAA
FriendLink is a smart friend suggestion system using Flask, SQLite, and HTML/CSS. It suggests friends via BFS (mutual connections) and Jaccard Similarity (age, location, interests). Users can add/delete friends, upload photos, and ignore suggestions. I developed the backend, logic, and UI integration.
# FriendLink: Smart Friend Suggestion System

**FriendLink** is a smart friend recommendation web app that suggests connections based on mutual friends and profile similarities. It is built using Flask (Python), SQLite for storage, and simple HTML/CSS for the user interface. The system allows users to register with personal details including interests, age, and location, and supports uploading profile photos. Once registered or logged in, users can add direct friends, view suggestions based on mutual friends (using BFS traversal), or discover new people with similar interests and demographics using Jaccard Similarity. The suggestions update dynamically every time a user logs in, helping maintain relevant and personalized recommendations. Additional features include ignoring unwanted suggestions, deleting existing friends, and managing user profiles. This project was developed to simulate social network dynamics and recommend meaningful connections efficiently using graph and set-based algorithms.

## Features

- User registration with age, location, interests, password, profile photo
- Login and session handling via Flask
- Friend suggestion through:
  - Mutual friends using **BFS**
  - Similar interests, age, or location using **Jaccard Similarity**
- Ability to ignore or delete friends
- Web interface with dynamic suggestion updates on login

## Technologies Used

- **Frontend**: HTML, CSS
- **Backend**: Python with Flask
- **Database**: SQLite
- **Algorithms**:
  - Breadth-First Search (BFS)
  - Jaccard Similarity

## Folder Structure

friendlink/
├── app.py # Flask routes
├── main.py # Core backend logic and algorithms
├── friendlink.db # SQLite database
├── static/
│ └── style.css
├── templates/
│ ├── login.html
│ ├── register.html
│ └── suggestions.html
└── README.md

markdown
Copy
Edit

## Setup Instructions

1. Clone the repository:
git clone https://github.com/kagdiyal04/friendlink.git
cd friendlink

markdown
Copy
Edit

2. Install Flask:
pip install flask

markdown
Copy
Edit

3. Run the application:
python app.py

markdown
Copy
Edit

4. Open your browser and visit:
http://localhost:5000/

pgsql
Copy
Edit

## Author Role

I designed and implemented the backend (database, algorithms, friend suggestion logic), integrated it with Flask, built the web interface, and ensured a smooth user experience for registration, login, and recommendation handling.

## License

This project is for academic and educational purposes. Feel free to modify or extend with credit.
This file includes:

Description

Features

Tech stack

Folder layout

How to run

Your contribution



