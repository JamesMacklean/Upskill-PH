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

        # Default to 'welcome' if subdomain is not specified
        urlpatterns_key = self.SUBDOMAIN_URL_PATTERNS.get(subdomain, 'welcome_urlpatterns')
        subdomain_urlpatterns = globals().get(urlpatterns_key, [])

        path = request.path.rstrip('/')
        
        # Redirect or block access if the path does not match any of the subdomain-specific URLs
        if not any(path.startswith(p.pattern) for p in subdomain_urlpatterns):
            return self.redirect_to_home_or_signout(request, subdomain)

        # Check for authentication if required by subdomain
        if subdomain in ['welcome', 'accounts']:
            return self.handle_authentication(request, subdomain, path)

        return None

    def handle_authentication(self, request, subdomain, path):
        try:
            user_token = request.session['user_token']
            expires = request.session['expires']
            current_time = int(time.time())

            if current_time >= expires:
                return self.signout(request, f'http://{settings.ACCOUNTS_DOMAIN}')

            if subdomain == 'accounts':
                # Redirect authenticated users from accounts to home
                if path in ['signin', 'signup', 'verify'] and user_token:
                    return redirect('home')
                else:
                    return redirect(f'http://{settings.DOMAIN}{path}')

            elif subdomain == 'welcome' and not user_token:
                return self.signout(request, f'http://{settings.ACCOUNTS_DOMAIN}')
        except KeyError:
            if subdomain == 'welcome':
                return self.signout(request, f'http://{settings.ACCOUNTS_DOMAIN}')

        return None

    def redirect_to_home_or_signout(self, request, subdomain):
        if subdomain == 'accounts':
            return redirect(reverse('signin'))
        return self.signout(request, f'http://{settings.ACCOUNTS_DOMAIN}')

    def signout(self, request, redirect_domain):
        for key in list(request.session.keys()):
            del request.session[key]
        request.session.modified = True
        request.session['original_url'] = request.get_full_path()
        return HttpResponseRedirect(f'{redirect_domain}{reverse("signin")}')
