Upgraded blog with users.

What it does:
This is a small blog app with user accounts and comments. Anyone can read posts. People can register and log in to leave comments. The first user (id 1) is treated as the admin and can create, edit, and delete posts.

Main pieces:
main.py holds the app, routes, models, and login logic. forms.py defines the WTForms for posts, login, register, and comments. Templates are in templates. Static files (CSS, JS, images) are in static. The database file is instance/posts.db.

User accounts:
Register at /register and login at /login. Passwords are hashed before saving. User records are stored in the users table with name, email, and password hash. Flask-Login keeps the session and exposes current_user for templates and route checks.

Admin posts flow:
The admin is hardcoded as user id 1. Admin-only routes use a decorator that aborts with 403 if the current user is not id 1. Admin can:
- Create a post at /new-post
- Edit a post at /edit-post/<id>
- Delete a post at /delete/<id>
Posts are stored in the blog_posts table with title, subtitle, body, image URL, date, and a foreign key to the author (users.id).

Comments flow:
Only logged-in users can submit comments. On a post page, the comment form posts back to the same route. If the user is not logged in, they are redirected to login. When a comment is submitted, a Comment row is created and linked to both the current user and the current post.
Comments are stored in the comments table with:
- text (the comment body)
- author_id (users.id)
- post_id (blog_posts.id)
The post page loads post.comments and shows each comment with the author name.

Templates and UI:
The navbar shows Login/Register when logged out and Log Out when logged in. The post page shows an Edit button only for admin. CKEditor is used for post bodies and comment input.

Requirements:
See requirements.txt. Core packages are Flask, Flask-Login, Flask-SQLAlchemy, Flask-WTF, Flask-CKEditor, and Werkzeug.

Run it:
Create a virtual environment, install requirements, then run python main.py.
You can also host it on hosting providers.
Heroku                                $5                      Eco & Basic

render                                  $0                      Individual

Cyclic                                   $0                      Free Forever

Glitch                                   $0                      Starter

Vercel                                  $0                       Hobby

PythonAnywhere                          $0                       Beginner 

Google Cloud                            $0                       Free


Notes:
The secret key is hardcoded and should be moved to an environment variable for real use. The database is created automatically on startup. Gravatar is not used.
