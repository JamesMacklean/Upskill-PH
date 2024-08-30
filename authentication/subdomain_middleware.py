from django.urls import reverse
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseRedirect
from scholarium import settings
from scholarium.info import *
import time

class SubdomainMiddleware(MiddlewareMixin):
    API_SECRET_KEY = API_SECRET_KEY

    SUBDOMAIN_URL_PATTERNS = {
        'welcome': 'welcome_urlpatterns',
        'accounts': 'accounts_urlpatterns',
        # Add more subdomains here as needed
    }

    def process_request(self, request):
        host = request.get_host()
        subdomain = host.split('.')[0]

        path = request.path.rstrip('/')
        
        # Check for authentication if required by subdomain
        if subdomain in ['welcome', 'accounts']:
            return self.handle_authentication(request, subdomain, path)

        return None

    def handle_authentication(self, request, subdomain, path):
        # IF AUTHENTICATED SI USER
        try:
            user_token = request.session['user_token']
            expires = request.session['expires']
            current_time = int(time.time())

            if current_time >= expires:
                return self.signout(request, f'http://{settings.ACCOUNTS_DOMAIN}')

            if subdomain == 'accounts':
                # Redirect authenticated users from accounts to home
                print("AUTHENTICATED EH BA'T KA NASA ACCOUNTS? BALIK WELCOME", flush=True)
                return redirect(f'http://{settings.DOMAIN}{path}')
            elif subdomain == 'welcome':
                # Redirect to the home page if the path is not in the welcome_urlpatterns
                welcome_urlpatterns = [p.pattern for p in globals().get('welcome_urlpatterns', [])]
                print("AUTHENTICATED", flush=True)
                if not any(path == p for p in welcome_urlpatterns):
                    print(f"PERO ANG PUPUNTAHANG {path} AY WALA SA WELCOME_URLPATTERNS", flush=True)
                    return redirect(f'http://{settings.DOMAIN}')
        
        # ELSE HINDI AUTHENTICATED SI USER
        except KeyError:
            if subdomain == 'welcome':
                print("HINDI KA AUTHENTICATED! BALIK ACCOUNTS", flush=True)
                return self.signout(request, f'http://{settings.ACCOUNTS_DOMAIN}')
            elif subdomain == 'accounts':
                # Redirect to the home page if the path is not in the welcome_urlpatterns
                accounts_urlpatterns = [p.pattern for p in globals().get('accounts_urlpatterns', [])]
                print("HINDI KA AUTHENTICATED!")
                if not any(path == p for p in accounts_urlpatterns):
                    print(f"PERO ANG PUPUNTAHANG {path} AY WALA SA ACCOUNTS_URLPATTERNS", flush=True)
                    return redirect(f'http://{settings.ACCOUNTS_DOMAIN}')

        return None

    def signout(self, request, redirect_domain):
        for key in list(request.session.keys()):
            del request.session[key]
        request.session.modified = True
        request.session['original_url'] = request.get_full_path()
        return HttpResponseRedirect(f'{redirect_domain}{reverse("signin")}')
