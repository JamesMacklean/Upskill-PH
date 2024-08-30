from django.urls import reverse, resolve, Resolver404
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseRedirect
from scholarium import settings
from scholarium.info import *
import time
from .urls import accounts_urlpatterns, welcome_urlpatterns


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
                if self.path_in_urlpatterns(path, self.SUBDOMAIN_URL_PATTERNS['accounts']):
                    return redirect(f'http://{settings.DOMAIN}{path}')
            elif subdomain == 'welcome':
                # Redirect to the home page if the path is not in the welcome_urlpatterns
                print(f"AUTHENTICATED PERO ANG PUPUNTAHANG {path} AY WALA SA WELCOME_URLPATTERNS", flush=True)
                if not self.path_in_urlpatterns(path, self.SUBDOMAIN_URL_PATTERNS['welcome']):
                    return redirect(f'http://{settings.DOMAIN}')
        
        # ELSE HINDI AUTHENTICATED SI USER
        except KeyError:
            if subdomain == 'welcome':
                print("HINDI KA AUTHENTICATED! BALIK ACCOUNTS", flush=True)
                return self.signout(request, f'http://{settings.ACCOUNTS_DOMAIN}/signin')
            elif subdomain == 'accounts':
                print(f"HINDI KA AUTHENTICATED! PERO ANG PUPUNTAHANG {path} AY WALA SA ACCOUNTS_URLPATTERNS", flush=True)
                if not self.path_in_urlpatterns(path, self.SUBDOMAIN_URL_PATTERNS['accounts']):
                    return redirect(f'http://{settings.ACCOUNTS_DOMAIN}/signin')

        return None

    def path_in_urlpatterns(self, path, urlpatterns):
        """
        Check if the path matches any of the patterns in the given urlpatterns.
        """
        for pattern in urlpatterns:
            try:
                match = resolve(path)
                if match:
                    return True
            except Resolver404:
                continue
        return False
    
    def signout(self, request, redirect_domain):
        """
        Signs out the user by clearing session data and printing relevant information.
        """
        # Print cookies
        for key, value in request.COOKIES.items():
            print(f'{key}: {value}', flush=True)

        # Clear sessions
        try:
            for key in list(request.session.keys()):
                del request.session[key]
            request.session.modified = True
        except KeyError as e:
            print(str(e), flush=True)
        
        # Save the original URL and redirect to signin
        request.session['original_url'] = request.get_full_path()
        print(f"original_url: {request.session['original_url']}", flush=True)
        return HttpResponseRedirect(f'{redirect_domain}{reverse("signin")}')
