from django.urls import resolve, reverse, get_resolver, URLResolver, get_urlconf
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
                
        accounts_urlconf = 'authentication.accounts.urls'
        accounts_resolver = get_resolver(accounts_urlconf)
        misocc_urlconf = 'authentication.misamis_occidental.urls'
        misocc_resolver = get_resolver(misocc_urlconf)
               
        if subdomain == 'welcome': 
            try:
                user_token = request.session['user_token']
                expires = request.session['expires']
                current_time = int(time.time())  
                if current_time >= expires:
                    # The session has expired, sign out the user
                    return self.signout(request, f'http://{settings.ACCOUNTS_DOMAIN}')
                try:
                    match = accounts_resolver.resolve(request.path)
                except:
                    match = None
                if match:
                    raise Http404("Page not found.")
                
            except KeyError:
                print(f'WELCOME: Unauthenticated.', flush=True)
                return self.signout(request, f'http://{settings.ACCOUNTS_DOMAIN}')                       
                
        elif subdomain == 'accounts': 
            try:
                match = accounts_resolver.resolve(request.path)
            except:
                match = None
  
            if match:
                print(f'ACCOUNTS MATCH! {match}', flush=True)
                request.urlconf = accounts_urlconf
                try:
                    user_token = request.session['user_token']
                    expires = request.session['expires']
                    current_time = int(time.time())  
                    if current_time >= expires:
                        # The session has expired, sign out the user
                        return self.signout(request, f'http://{settings.ACCOUNTS_DOMAIN}')
                    return redirect(f'http://{settings.DOMAIN}')
                except KeyError:
                    print(f'ACCOUNTS: Unauthenticated.', flush=True)
            else:
                print(f"HINDI MATCH! {match}", flush = True)
                try:
                    user_token = request.session['user_token']
                    return redirect(f'http://{settings.DOMAIN}{request.path}')
                except KeyError:
                    print(f"WALANG GANITONG PATH SA ACCOUNTS! {request.path}", flush = True)
                    if request.path=='' or request.path =='/':
                        return self.signout(request, f'http://{settings.ACCOUNTS_DOMAIN}')
                    else:
                        raise Http404("Page not found.")
        
        elif subdomain == 'misamis-occidental':
            request.urlconf = 'authentication.misamis_occidental.urls'

    
        # FOR TEST CODE
        # FOR http://127.0.0.1:8000
        else:
            
            try:
                user_token = request.session['user_token']
                expires = request.session['expires']
                current_time = int(time.time())  # Get the current time in seconds since the epoch (UNIX time)
                if current_time >= expires:
                    # The session has expired, sign out the user
                    return self.signout(request, f'http://{host}')
                try:
                    match = accounts_resolver.resolve(request.path)
                except:
                    match = None
                    
                if match:
                    raise Http404("Page not found.")
            except KeyError:
                try:
                    match = accounts_resolver.resolve(request.path)
                except:
                    match = None
                    
                if not match:
                    return self.signout(request, f'http://{host}')
            
        return None
    
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