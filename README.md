# 📝 Upgraded Blog with Users

A modern, feature-rich blogging platform built with Flask that supports user authentication, admin-level blog management, and community comments. Perfect for personal blogs, team blogs, or content platforms.

**Live Demo:** https://blog-website-350379204643.asia-south1.run.app

---

## 🎯 Overview

This application provides a complete blogging solution with:
- **User Authentication** - Secure registration and login with hashed passwords
- **Role-Based Access** - Admin can create/edit/delete posts; regular users can comment
- **Dynamic Content** - Rich text editor (CKEditor) for blog posts and comments
- **Comment System** - Engage with readers through an interactive comment section
- **Responsive Design** - Bootstrap 5 for mobile-friendly interface
- **Database Persistence** - SQLAlchemy ORM with SQLite (or PostgreSQL in production)

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Flask 3.1.3 |
| **Database** | SQLAlchemy 3.0.3 + SQLite |
| **Authentication** | Flask-Login 0.6.3 |
| **Forms** | Flask-WTF 1.2.2 + WTForms 3.2.1 |
| **Rich Text Editor** | Flask-CKEditor 1.0.0 |
| **Frontend Framework** | Bootstrap-Flask 2.5.0 |
| **Security** | Werkzeug 3.1.6 |
| **Deployment** | Gunicorn 25.1.0 |

---

## 📁 Project Structure

```
upgraded-blog-with-users/
│
├── main.py                    # Flask app, routes, database models
├── forms.py                   # WTForm definitions
├── requirements.txt           # Python dependencies
│
├── instance/
│   └── posts.db              # SQLite database (created on first run)
│
├── templates/                 # HTML templates
│   ├── header.html           # Navigation bar
│   ├── footer.html           # Footer component
│   ├── index.html            # Homepage with all posts
│   ├── post.html             # Individual post view + comments
│   ├── about.html            # About page
│   ├── contact.html          # Contact page
│   ├── login.html            # Login form
│   ├── register.html         # Registration form
│   └── make-post.html        # Admin post creation/editing
│
├── static/                    # Static assets
│   ├── css/
│   │   └── styles.css        # Custom styles
│   ├── js/
│   │   └── scripts.js        # Client-side JavaScript
│   └── assets/
│       └── img/              # Images and graphics
│
├── Dockerfile                 # Container configuration
├── Procfile                   # Deployment configuration
├── cloudbuild.yaml           # Google Cloud Build config
├── DEPLOYMENT.md             # Deployment instructions
└── README.md                 # This file
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

### Step-by-Step Setup

1. **Clone or navigate to the project**
   ```bash
   cd upgraded-blog-with-users
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   
   **Windows:**
   ```bash
   venv\Scripts\activate
   ```
   
   **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set environment variables** (Optional but recommended)
   
   Create a `.env` file in the project root:
   ```env
   FLASK_KEY=your-secret-key-here
   DB_URI=sqlite:///posts.db
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=your-app-password
   RECIPIENT_EMAIL=recipient@example.com
   ```

6. **Run the application**
   ```bash
   python main.py
   ```

7. **Open in browser**
   ```
   http://localhost:5000
   ```

---

## 🔐 User Roles & Permissions

### **Admin (User ID: 1)**
- ✅ Create new blog posts
- ✅ Edit own posts
- ✅ Delete posts
- ✅ View all posts
- ✅ Leave comments on any post
- ✅ Full site access

### **Regular Users**
- ✅ Register and login
- ✅ View all blog posts
- ✅ Leave comments on posts
- ✅ View other users' comments
- ❌ Cannot create/edit/delete posts
- ❌ Cannot manage other users

### **Guests (Not Logged In)**
- ✅ View all blog posts
- ✅ View comments
- ❌ Cannot post comments
- ❌ Cannot access admin features

---

## 📋 Key Features Explained

### 1. **User Authentication**
- **Registration** (`/register`): New users create account with name, email, and password
- **Login** (`/login`): Existing users authenticate with email and password
- **Password Security**: All passwords are hashed using Werkzeug before storage
- **Session Management**: Flask-Login handles user sessions automatically

**Database Schema (users table):**
```
- id (Primary Key)
- name (String)
- email (String, Unique)
- password (String, Hashed)
```

### 2. **Blog Post Management**
- **Create** (`/new-post`): Admin-only route to create new posts
- **Edit** (`/edit-post/<id>`): Admin-only route to modify existing posts
- **Delete** (`/delete/<id>`): Admin-only route to remove posts
- **View** (`/post/<id>`): Anyone can view individual posts

**Database Schema (blog_posts table):**
```
- id (Primary Key)
- title (String)
- subtitle (String)
- body (Text, Rich Editor)
- img_url (String)
- date (Date)
- author_id (Foreign Key → users.id)
```

### 3. **Comments System**
- **Add Comment**: Logged-in users can comment on any post
- **Display Comments**: Comments appear on post pages with author names
- **Comment Form**: Uses CKEditor for rich text comments

**Database Schema (comments table):**
```
- id (Primary Key)
- text (Text, Rich Editor)
- author_id (Foreign Key → users.id)
- post_id (Foreign Key → blog_posts.id)
```

### 4. **Responsive UI**
- **Navigation Bar**: Dynamic - shows Login/Register when logged out, Logout when logged in
- **Admin Controls**: Edit/Delete buttons only visible to admin
- **Rich Text Editing**: CKEditor integrated for both posts and comments
- **Bootstrap 5**: Mobile-responsive design

---

## 📝 Available Routes

| Route | Method | Description | Access |
|-------|--------|-------------|--------|
| `/` | GET | Homepage with all posts | Public |
| `/post/<id>` | GET, POST | View post + submit comments | Public (comments: logged-in only) |
| `/about` | GET | About page | Public |
| `/contact` | GET, POST | Contact form | Public |
| `/new-post` | GET, POST | Create new post | Admin only |
| `/edit-post/<id>` | GET, POST | Edit existing post | Admin only |
| `/delete/<id>` | GET | Delete post | Admin only |
| `/register` | GET, POST | User registration | Public |
| `/login` | GET, POST | User login | Public |
| `/logout` | GET | User logout | Logged-in users only |

---

## 🔧 Configuration

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `FLASK_KEY` | Secret key for sessions | Fallback value provided |
| `DB_URI` | Database connection string | SQLite (local) |
| `SENDER_EMAIL` | Email for contact form | Optional |
| `SENDER_PASSWORD` | Email app password | Optional |
| `RECIPIENT_EMAIL` | Where to send contact emails | Optional |

### Database Setup

The application uses SQLAlchemy ORM:
- **Development**: SQLite database (`instance/posts.db`)
- **Production**: PostgreSQL recommended (set via `DB_URI`)
- **Auto-creation**: Tables are created automatically on first run

---

## 🌐 Deployment

### Hosting Options

| Provider | Cost | Tier | Instructions |
|----------|------|------|--------------|
| **Render** | Free | Individual | See DEPLOYMENT.md |
| **Railway** | Free | Starter | See DEPLOYMENT.md |
| **Heroku** | $5+ | Eco & Basic | See DEPLOYMENT.md |
| **PythonAnywhere** | Free | Beginner | See DEPLOYMENT.md |
| **Google Cloud** | Free | Free tier | See cloudbuild.yaml |
| **Cyclic** | Free | Free Forever | See DEPLOYMENT.md |
| **Glitch** | Free | Starter | See DEPLOYMENT.md |

### Quick Deploy to Google Cloud

```bash
gcloud builds submit
```

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

---

## 🐛 Troubleshooting

### Common Issues

**Database Connection Errors**
- Solution: The app includes retry logic for database operations
- Check `DB_URI` environment variable
- Ensure `instance/` folder exists and has write permissions

**CKEditor Not Loading**
- Solution: Ensure Flask-CKEditor is installed: `pip install Flask-CKEditor`
- Clear browser cache and restart the application

**Login Not Working**
- Solution: Verify `SECRET_KEY` is set
- Check that passwords are being hashed correctly in database

**Static Files Not Loading**
- Solution: Ensure `static/` folder structure is correct
- Run `flask --app main run --debug` for development

---

## 📦 Dependencies

All dependencies are listed in `requirements.txt`. Core packages:

- **Flask** - Web framework
- **Flask-Login** - User authentication
- **Flask-SQLAlchemy** - Database ORM
- **Flask-WTF** - Form security
- **Flask-CKEditor** - Rich text editor
- **Bootstrap-Flask** - Frontend framework
- **Gunicorn** - Production server

---

## 🤝 Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Open a Pull Request

---

## 📄 License

This project is open source and available under the MIT License.

---

## 💡 Future Enhancements

Possible features to add:
- [ ] User profile pages
- [ ] Post categories/tags
- [ ] Search functionality
- [ ] Comment moderation
- [ ] Email notifications
- [ ] Social media sharing
- [ ] Post likes/ratings
- [ ] Draft posts
- [ ] Scheduled posts
- [ ] Multi-language support

---

## 📞 Support

For issues or questions:
- Check the [DEPLOYMENT.md](DEPLOYMENT.md) for deployment help
- Review the troubleshooting section above
- Contact via the contact form on the website

---

**Last Updated:** June 2026  
**Version:** 2.0  
**Status:** ✅ Production Ready


Notes:
The secret key is hardcoded and should be moved to an environment variable for real use. The database is created automatically on startup. Gravatar is not used.
