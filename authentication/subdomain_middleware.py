from django.urls import reverse
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse, HttpResponseRedirect
from scholarium.info import *
from scholarium import settings
import time

class SubdomainMiddleware(MiddlewareMixin):
    API_SECRET_KEY = API_SECRET_KEY

    # Define allowed paths for each subdomain in a dictionary
    SUBDOMAIN_PATHS = {
        'welcome': [
            '',  # Home page
            'account/',
            'administrator/',
            'administrator/users/',
            'administrator/users/<int:user_id>/',
            'administrator/partner/<int:partner_id>/',
            'administrator/license-codes/<slug>/',
            'certificate/',
            'dashboard/',
            'partner/',
            'partner/<slug:program_slug>/application/',
            'profile/',
            'profile/edit/',
            'program/<slug>/',
            'sessions/',
            'guidelines/',
            'privacy/',
            'contact/',
            'lakip/',
            'lakip/apply/',
            'signout/'
        ],
        'accounts': [
            'signin/',
            'signout/',
            'signup/',
            'success/<user_hash>/',
            'verify/<user_hash>/'
        ],
        'misamis-occidental': [
            'lakip/',
            'lakip/apply/'
        ]
    }

    def process_request(self, request):
        host = request.get_host()
        subdomain = host.split('.')[0]
        path = request.path.rstrip('/')

        allowed_paths = self.SUBDOMAIN_PATHS.get(subdomain, [])
        
        # Convert path patterns with URL parameters to simple patterns
        path_patterns = [p.split('/')[0] for p in allowed_paths] + [p.rstrip('/').split('<')[0] for p in allowed_paths]
        if path in path_patterns or any(path.startswith(prefix) for prefix in path_patterns):
            return None  # Allow the request to proceed

        if subdomain in ['welcome', 'accounts', 'misamis-occidental']:
            return HttpResponse(status=404)

        # Handle authentication logic for other subdomains if needed
        try:
            user_token = request.session['user_token']
            expires = request.session['expires']
            current_time = int(time.time())
            if current_time >= expires:
                return self.signout(request, f'http://{settings.ACCOUNTS_DOMAIN}')
        except KeyError:
            return self.signout(request, f'http://{settings.ACCOUNTS_DOMAIN}')
        
        return None
    
    def signout(self, request, redirect_domain):
        """
        Signs out the user by clearing session data and printing relevant information.
        """
        for key, value in request.COOKIES.items():
            print(f'{key}: {value}', flush=True)

        try:
            for key in list(request.session.keys()):
                del request.session[key]
            request.session.modified = True
        except KeyError as e:
            print(str(e), flush=True)
        
        request.session['original_url'] = request.get_full_path()
        print(f"original_url: {request.session['original_url']}", flush=True)
        return HttpResponseRedirect(f'{redirect_domain}{reverse("signin")}')
