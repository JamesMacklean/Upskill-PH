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

## BEFORE PUSHING INTO PRODUCTION

1. Search for the comments 'ORIGINAL CODE' and uncomment them.
2. Search for the comments 'FOR TEST CODE' and comment them.
3. Search for the comments 'FOR http:127.0.0.1:8000' and comment them.

## WHEN IN DEVELOPMENT MODE
Since there are no subdomains in development mode, uncomment 'FOR http:127.0.0.1:8000' under the subdomain_middleware.py file
Search for 'FOR TEST CODE' and 'FOR http:127.0.0.1:8000' and uncomment them when in DEVELOPMENT mode

1. Search for the comments 'ORIGINAL CODE' and comment them.
2. Search for the comments 'FOR TEST CODE' and uncomment them.
3. Search for the comments 'FOR http:127.0.0.1:8000' and uncomment them.