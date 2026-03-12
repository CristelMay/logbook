# logbook - Django Project Template

A clean, modern Django boilerplate with TailwindCSS, PostgreSQL support, Django REST Framework, and production-ready configurations.

---

## 🚀 Features

- **Django 5.1.7** - Latest stable version
- **TailwindCSS** - Utility-first CSS framework with hot reload
- **PostgreSQL** - Production database with SQLite fallback for development
- **Django REST Framework** - RESTful API support
- **WhiteNoise** - Static file serving for production
- **CORS** - Pre-configured CORS headers
- **Environment Variables** - Secure configuration with python-dotenv
- **Production Ready** - Gunicorn, logging, and security settings

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Node.js & npm** ([Download](https://nodejs.org/))
- **PostgreSQL** (Optional, for production - [Download](https://www.postgresql.org/download/))
- **Git** ([Download](https://git-scm.com/downloads))

---

## 🛠️ Getting Started

### 1️⃣ Clone the Repository

```bash
git clone <your-repository-url>
cd django-template
```

### 2️⃣ Create Virtual Environment

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3️⃣ Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and update the values:

```env
ENV=development
SECRET_KEY=your-secret-key-here
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432
```

**Generate a new SECRET_KEY:**

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5️⃣ Install TailwindCSS Dependencies

```bash
python manage.py tailwind install
```

If you encounter a "cross-env not recognized" error:

```bash
npm install --save-dev cross-env
```

### 6️⃣ Run Migrations

```bash
python manage.py migrate
```

### 7️⃣ Create a Superuser

```bash
python manage.py createsuperuser
```

### 8️⃣ Run the Development Server

You'll need **two terminal windows**:

**Terminal 1 - Django Server:**

```bash
python manage.py runserver
```

**Terminal 2 - TailwindCSS Watcher:**

```bash
python manage.py tailwind start
```

### 9️⃣ Access the Application

- **Homepage:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/

---

## 📁 Project Structure

```
django-template/
│
├── logbook/                # Project configuration package
│   ├── __init__.py
│   ├── settings.py        # Django settings
│   ├── urls.py            # URL routing
│   ├── wsgi.py            # WSGI configuration
│   └── asgi.py            # ASGI configuration
│
├── theme/                  # TailwindCSS theme app
│   ├── apps.py
│   ├── templates/         # Shared base templates
│   │   ├── base.html
│   │   └── home.html
│   ├── static_src/        # Tailwind source files (auto-generated)
│   │   ├── package.json   # Node.js dependencies for Tailwind
│   │   ├── node_modules/  # TailwindCSS packages (git-ignored)
│   │   ├── tailwind.config.js
│   │   └── src/
│   └── static/            # Compiled CSS (auto-generated)
│
├── my_app/                 # Sample app (you can delete this)
│   ├── templates/
│   │   └── my_app/        # App-specific templates
│   ├── views.py
│   ├── urls.py
│   └── README.md          # Sample app documentation
│
├── static/                 # Static files (CSS, JS, images)
├── media/                  # User-uploaded files
├── staticfiles/           # Collected static files (production)
│
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
├── Aptfile                # System dependencies (for Render, Heroku)
└── README.md              # This file
```

---

## 🎨 Creating a New App

```bash
python manage.py startapp your_app_name
```

Then:

1. Add the app to `INSTALLED_APPS` in `logbook/settings.py`
2. Create your models in `your_app_name/models.py`
3. **Create templates** following Django's app structure:
   ```bash
   mkdir -p your_app_name/templates/your_app_name
   # Put your templates in: your_app_name/templates/your_app_name/
   ```
4. Create URL patterns in `your_app_name/urls.py`
5. Include app URLs in `logbook/urls.py`

**Why the double folder?** Django looks for templates in all apps' `templates/` folders. The extra app-name folder prevents naming conflicts between apps.

---

## 🗄️ Database Configuration

### Development (SQLite)

By default, the project uses SQLite in development. No additional setup required.

### Production (PostgreSQL)

Set `ENV=production` in your `.env` file and configure database credentials:

```env
ENV=production
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=5432
```

---

## 🚀 Deployment

### Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Using Gunicorn

```bash
gunicorn logbook.wsgi:application
```

### Environment Variables for Production

- Set `ENV=production`
- Generate a strong `SECRET_KEY`
- Set `ALLOWED_HOSTS` to your domain
- Configure `CORS_ALLOWED_ORIGINS` if using a separate frontend
- Set database credentials

### Deployment Platforms

This template is ready for:

- **Render** - Uses `Aptfile` for system dependencies
- **Heroku** - Add `Procfile` with: `web: gunicorn logbook.wsgi`
- **Railway** - Works out of the box
- **DigitalOcean App Platform** - Configure build/run commands

---

## 📦 Tailwind Configuration

The TailwindCSS setup uses `django-tailwind`. To customize:

1. Navigate to `theme/static_src/`
2. Edit `tailwind.config.js` for Tailwind settings
3. Edit `src/styles.css` for custom styles

---

## 🧪 Running Tests

```bash
python manage.py test
```

---

## 📝 Useful Commands

| Command                            | Description               |
| ---------------------------------- | ------------------------- |
| `python manage.py runserver`       | Start development server  |
| `python manage.py tailwind start`  | Start TailwindCSS watcher |
| `python manage.py makemigrations`  | Create new migrations     |
| `python manage.py migrate`         | Apply migrations          |
| `python manage.py createsuperuser` | Create admin user         |
| `python manage.py collectstatic`   | Collect static files      |
| `python manage.py shell`           | Open Django shell         |
| `python manage.py test`            | Run tests                 |

---

## 🔒 Security Notes

- Never commit `.env` file to version control
- Generate a new `SECRET_KEY` for production
- Set `DEBUG = False` in production
- Configure `ALLOWED_HOSTS` properly
- Use HTTPS in production
- Keep dependencies updated: `pip list --outdated`

---

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django Tailwind Package](https://django-tailwind.readthedocs.io/)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Open a pull request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 💡 Tips

- Use `django-browser-reload` for automatic page refresh during development
- Check `logbook/settings.py` for all available configurations
- Customize the base template in `theme/templates/base.html`
- Add your custom CSS in `theme/static_src/src/styles.css`
- Check out `my_app/` for a complete example of proper Django app structure

## 🗑️ Removing the Sample App

The `my_app/` folder is a sample demonstrating proper app structure. To remove it:

1. Delete from `INSTALLED_APPS` in `logbook/settings.py`
2. Remove `path('my-app/', include('my_app.urls')),` from `logbook/urls.py`
3. Delete the `my_app/` folder
4. Remove the "View Sample App" button from `theme/templates/home.html`

---

**Happy Coding! 🎉**
