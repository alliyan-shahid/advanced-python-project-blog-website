from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from sqlalchemy.exc import OperationalError
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import os
import smtplib
import time
from email.message import EmailMessage

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL")


# Import forms from forms.py
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY', '8BYkEfBA6O6donzWlSihBXOx7c0sKR6b')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI', 'sqlite:///posts.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
ckeditor = CKEditor(app)
Bootstrap5(app)
db = SQLAlchemy(app)          # ✅ Simple, correct initialization

login_manager = LoginManager()
login_manager.init_app(app)


def execute_with_retry(func, retries=3, delay=2):
    """Retry database operations if connection fails"""
    for attempt in range(retries):
        try:
            return func()
        except OperationalError as e:
            if "SSL connection has been closed" in str(e) and attempt < retries - 1:
                print(f"Database connection lost, retrying... (attempt {attempt + 1})")
                time.sleep(delay)
                # Refresh database connection
                db.session.remove()
            else:
                raise



# ---------- User Loader for Flask-Login ----------
@login_manager.user_loader
def load_user(user_id):
    return execute_with_retry(lambda: db.session.get(User, int(user_id)))


# ---------- Database Models ----------
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    author: Mapped["User"] = relationship(back_populates="posts")
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('categories.id'))
    category: Mapped["Category"] = relationship(back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship(back_populates="post", cascade="all, delete-orphan")


class Category(db.Model):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    posts: Mapped[list["BlogPost"]] = relationship(back_populates="category")


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))
    posts: Mapped[list["BlogPost"]] = relationship(back_populates="author")
    comments: Mapped[list["Comment"]] = relationship(back_populates="comment_author")


class Comment(db.Model):
    __tablename__ = 'comments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    comment_author: Mapped["User"] = relationship(back_populates="comments")
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey('blog_posts.id'), nullable=False)
    post: Mapped["BlogPost"] = relationship(back_populates="comments")


# ---------- Create Tables ----------
with app.app_context():
    execute_with_retry(lambda: db.create_all())


# ---------- Admin Decorator ----------
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


# ---------- Routes ----------
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        hash_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        # Check if user already exists
        def check_existing_user():
            return db.session.execute(db.select(User).where(User.email == email)).scalar()
        
        user = execute_with_retry(check_existing_user)
        if user:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        new_user = User(name=name, email=email, password=hash_password)
        def save_user():
            db.session.add(new_user)
            db.session.commit()
        execute_with_retry(save_user)
        login_user(new_user)
        return redirect(url_for("get_all_posts"))

    return render_template("register.html", form=form, current_user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        def query_user():
            return db.session.execute(db.select(User).where(User.email == email)).scalar()
        
        user = execute_with_retry(query_user)

        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_all_posts'))

    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    def query_posts():
        stmt = db.select(BlogPost).options(selectinload(BlogPost.author))
        return db.session.execute(stmt).scalars().all()
    
    posts = execute_with_retry(query_posts)
    def query_categories():
        return db.session.execute(db.select(Category).order_by(Category.name)).scalars().all()
    categories = execute_with_retry(query_categories)

    uncategorized_posts = [post for post in posts if post.category_id is None]
    posts_by_category_id = {}
    for post in posts:
        if post.category_id:
            posts_by_category_id.setdefault(post.category_id, []).append(post)
    category_groups = []
    for category in categories:
        category_posts = posts_by_category_id.get(category.id, [])
        if category_posts:
            category_groups.append({
                "name": category.name,
                "posts": sorted(category_posts, key=lambda p: p.id, reverse=True)
            })
    if uncategorized_posts:
        category_groups.append({
            "name": "Uncategorized",
            "posts": sorted(uncategorized_posts, key=lambda p: p.id, reverse=True)
        })
    admin_user = current_user.is_authenticated and current_user.id == 1
    return render_template("index.html", all_posts=posts, admin_user=admin_user, category_groups=category_groups)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    def query_post():
        stmt = (
            db.select(BlogPost)
            .options(
                selectinload(BlogPost.author),
                selectinload(BlogPost.comments).selectinload(Comment.comment_author)
            )
            .where(BlogPost.id == post_id)
        )
        return db.session.execute(stmt).scalar_one_or_none()
    requested_post = execute_with_retry(query_post)
    if requested_post is None:
        abort(404)
    admin_user = current_user.is_authenticated and current_user.id == 1
    form = CommentForm()

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        new_comment = Comment(
            text=form.comment.data,
            comment_author=current_user,
            post=requested_post
        )
        def save_comment():
            db.session.add(new_comment)
            db.session.commit()
        execute_with_retry(save_comment)
        return redirect(url_for("show_post", post_id=post_id))

    return render_template("post.html", post=requested_post, admin_user=admin_user, form=form)


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    def query_categories():
        return db.session.execute(db.select(Category).order_by(Category.name)).scalars().all()
    categories = execute_with_retry(query_categories)
    form.category_existing.choices = [(0, "Select a category")] + [(cat.id, cat.name) for cat in categories]

    if form.validate_on_submit():
        new_category_name = (form.new_category.data or "").strip()
        selected_category_id = form.category_existing.data

        if new_category_name:
            def query_existing_category():
                return db.session.execute(db.select(Category).where(Category.name == new_category_name)).scalar()
            category = execute_with_retry(query_existing_category)
            if not category:
                category = Category(name=new_category_name)
                db.session.add(category)
                db.session.flush()
        else:
            if not selected_category_id:
                flash("Please select a category or create a new one.")
                return render_template("make-post.html", form=form)
            category = db.get_or_404(Category, selected_category_id)

        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=form.publish_date.data,
            category=category
        )
        def save_post():
            db.session.add(new_post)
            db.session.commit()
        execute_with_retry(save_post)
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = execute_with_retry(lambda: db.get_or_404(BlogPost, post_id))
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body,
        publish_date=post.date,
        new_category=""
    )
    def query_categories():
        return db.session.execute(db.select(Category).order_by(Category.name)).scalars().all()
    categories = execute_with_retry(query_categories)
    edit_form.category_existing.choices = [(0, "Select a category")] + [(cat.id, cat.name) for cat in categories]
    edit_form.category_existing.data = post.category_id or 0

    if edit_form.validate_on_submit():
        new_category_name = (edit_form.new_category.data or "").strip()
        selected_category_id = edit_form.category_existing.data

        if new_category_name:
            def query_existing_category():
                return db.session.execute(db.select(Category).where(Category.name == new_category_name)).scalar()
            category = execute_with_retry(query_existing_category)
            if not category:
                category = Category(name=new_category_name)
                db.session.add(category)
                db.session.flush()
        else:
            if not selected_category_id:
                flash("Please select a category or create a new one.")
                return render_template("make-post.html", form=edit_form, is_edit=True)
            category = db.get_or_404(Category, selected_category_id)

        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        post.date = edit_form.publish_date.data
        post.category = category
        execute_with_retry(lambda: db.session.commit())
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = execute_with_retry(lambda: db.get_or_404(BlogPost, post_id))
    def delete_post_record():
        db.session.delete(post_to_delete)
        db.session.commit()
    execute_with_retry(delete_post_record)
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")

        email_message = EmailMessage()
        email_message['Subject'] = f"New Contact Form Submission from {name}"
        email_message['From'] = SENDER_EMAIL
        email_message['To'] = RECIPIENT_EMAIL
        email_message.set_content(f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage:\n{message}")

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(email_message)

        flash("Your message has been sent successfully!")
        return redirect(url_for('contact'))

    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=False)
