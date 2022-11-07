# TO INSTALL

1. Add "<app_name>" to "INSTALLED_APPS" in scholarium/settings.py

2. Check for errors:
    python3 manage.py check
3. Run migrations.
    python3 manage.py makemigrations
    python3 manage.py migrate

## TO ADD URLS

1. Add the "<app_name>" to "urlpatterns" in scholarium/urls.py:
    urlpatterns = [
        path('', include('<app_name>.urls')),
    ]
