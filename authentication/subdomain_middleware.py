from django.urls import reverse
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse, Http404, HttpResponseRedirect
from scholarium.info import *
from scholarium import settings
import jwt, time

class SubdomainMiddleware(MiddlewareMixin):
    API_SECRET_KEY = API_SECRET_KEY

    def process_request(self, request):
        host = request.get_host()
        subdomain = host.split('.')[0]
        domain = f'http://{host}'
        
        accounts_redirect_paths = [
            reverse('signup'), 
            reverse('signin')
        ]
        accounts_redirect_prefixes = [
            '/success/',
            '/verify/'
        ]
        
        if subdomain == 'welcome':
            # Check if user is authenticated for other paths on the welcome subdomain
            try:
                # KUNG AUTHENTICATED PERO SA SIGNIN GUSTO PUMUNTA, DALHIN SA HOME
                user_token = request.session['user_token']
                expires = request.session['expires']
                current_time = int(time.time())  # Get the current time in seconds since the epoch (UNIX time)
                if current_time >= expires:
                    # The session has expired, sign out the user
                    return self.signout(request, settings.ACCOUNTS_DOMAIN)
                
                if request.path in accounts_redirect_paths or any(request.path.startswith(prefix) for prefix in accounts_redirect_prefixes):
                    return redirect('home')
            except KeyError:
                # KUNG HINDI AUTHENTICATED PERO SA SIGNIN GUSTO PUMUNTA, DALHIN SA ACCOUNTS
                if request.path in accounts_redirect_paths or any(request.path.startswith(prefix) for prefix in accounts_redirect_prefixes):
                    return redirect(f'{settings.ACCOUNTS_DOMAIN}{request.path}')
                # KUNG HINDI AUTHENTICATED AT PUMUNTA SA IBANG PAGE, ISAVE ANG URL, DALHIN SA SIGNIN
                else:
                    if request.path in accounts_redirect_paths or any(request.path.startswith(prefix) for prefix in accounts_redirect_prefixes):
                        return redirect(f'{settings.ACCOUNTS_DOMAIN}{request.path}')
                    else:
                        return self.signout(request, settings.ACCOUNTS_DOMAIN)
                
        elif subdomain == 'accounts':
            # Check if user is authenticated for other paths on the welcome subdomain
            try:
                # KUNG AUTHENTICATED PERO SA SIGNIN GUSTO PUMUNTA, DALHIN SA HOME
                user_token = request.session['user_token']
                expires = request.session['expires']
                current_time = int(time.time())  # Get the current time in seconds since the epoch (UNIX time)
                if current_time >= expires:
                    # The session has expired, sign out the user
                    return self.signout(request, settings.ACCOUNTS_DOMAIN)
                
                if request.path in accounts_redirect_paths or any(request.path.startswith(prefix) for prefix in accounts_redirect_prefixes):
                    return redirect('home')
            except KeyError:
                # KUNG HINDI SA SIGNIN PUPUNTA, DALHIN SA WELCOME
                if request.path not in accounts_redirect_paths and not any(request.path.startswith(prefix) for prefix in accounts_redirect_prefixes):
                    return redirect(f'{settings.DOMAIN}{request.path}')
        
        # FOR TEST CODE
        # FOR http://127.0.0.1:8000
        else:
            
            try:
                user_token = request.session['user_token']
                expires = request.session['expires']
                current_time = int(time.time())  # Get the current time in seconds since the epoch (UNIX time)
                if current_time >= expires:
                    # The session has expired, sign out the user
                    return self.signout(request, domain)
                    
                if request.path in accounts_redirect_paths or any(request.path.startswith(prefix) for prefix in accounts_redirect_prefixes):
                    return redirect ('home')
            except KeyError:
                if request.path not in accounts_redirect_paths and not any(request.path.startswith(prefix) for prefix in accounts_redirect_prefixes):
                    return self.signout(request, domain)
            
        return None
    
    def signout(self, request, redirect_domain):
        """
        Signs out the user by clearing session data and printing relevant information.
        """
        # Print cookies
        for key, value in request.COOKIES.items():
            print(f'{key}: {value}')

        # Clear sessions
        try:
            for key in list(request.session.keys()):
                del request.session[key]
            request.session.modified = True
        except KeyError as e:
            print(str(e))
        
        # Save the original URL and redirect to signin
        request.session['original_url'] = request.get_full_path()
        print(f"original_url: {request.session['original_url']}")
        return HttpResponseRedirect(f'{redirect_domain}{reverse("signin")}')