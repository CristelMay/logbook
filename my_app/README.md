# My App - Sample Django App

This is a **sample Django app** demonstrating the proper structure and best practices for creating apps in this template.

## 📁 App Structure

```
my_app/
├── __init__.py                      # Makes this a Python package
├── admin.py                         # Admin panel configuration
├── apps.py                          # App configuration
├── models.py                        # Database models
├── views.py                         # View functions ✓ (has samples)
├── urls.py                          # URL patterns ✓ (configured)
├── tests.py                         # Unit tests
├── migrations/                      # Database migrations
│   └── __init__.py
└── templates/                       # Templates folder
    └── my_app/                      # ← Namespace folder (same as app name)
        ├── index.html               # ✓ Sample index page
        └── detail.html              # ✓ Sample detail page
```

## 🎯 Key Concepts Demonstrated

### 1. **Double Template Folder Pattern**

```
my_app/templates/my_app/index.html
         ^^^^^^^^ ^^^^^^
         folder   namespace
```

**Why?** Django searches all apps' `templates/` folders. The inner folder prevents conflicts:

- ✅ Good: `my_app/templates/my_app/index.html`
- ❌ Bad: `my_app/templates/index.html` (could conflict with other apps)

### 2. **URL Configuration**

**my_app/urls.py:**

```python
app_name = 'my_app'  # Namespace for URLs

urlpatterns = [
    path('', views.index_view, name='index'),
    path('detail/<int:item_id>/', views.detail_view, name='detail'),
]
```

**logbook/urls.py:**

```python
path('my-app/', include('my_app.urls')),
```

**Result:**

- `/my-app/` → index_view
- `/my-app/detail/1/` → detail_view with item_id=1

### 3. **Using URLs in Templates**

```django
{% url 'my_app:index' %}              {# /my-app/ #}
{% url 'my_app:detail' item_id=1 %}   {# /my-app/detail/1/ #}
```

### 4. **Template Inheritance**

All app templates extend the base template:

```django
{% extends 'base.html' %}

{% block title %}My Page{% endblock %}

{% block content %}
    <!-- Your content here -->
{% endblock %}
```

## 🚀 Try It Out

1. **Start the server:**

   ```bash
   python manage.py runserver
   ```

2. **Visit the URLs:**
   - Homepage: http://127.0.0.1:8000/
   - Sample App: http://127.0.0.1:8000/my-app/
   - Detail Page: http://127.0.0.1:8000/my-app/detail/1/

## 📝 Creating Your Own App

Follow this pattern when creating new apps:

```bash
# 1. Create the app
python manage.py startapp your_app_name

# 2. Create template structure
mkdir -p your_app_name/templates/your_app_name

# 3. Add to INSTALLED_APPS in logbook/settings.py
INSTALLED_APPS = [
    # ...
    'your_app_name',
]

# 4. Create urls.py
# (copy from my_app/urls.py and modify)

# 5. Include in main urls.py
path('your-url/', include('your_app_name.urls')),
```

## 🗑️ Removing This Sample App

To remove this sample app after learning:

1. Remove from `INSTALLED_APPS` in `logbook/settings.py`
2. Remove from `logbook/urls.py`
3. Delete the `my_app/` folder
4. Remove the button from `theme/templates/home.html`

---

**Happy coding! 🎉**
