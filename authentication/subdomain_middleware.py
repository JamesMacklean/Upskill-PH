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
        
        # path = request.path.rstrip('/')
        # accounts_redirect_paths = [
        #     reverse('signup').rstrip('/'), 
        #     reverse('signin').rstrip('/')
        # ]
        # accounts_redirect_prefixes = [
        #     '/success/',
        #     '/verify/'
        # ]
        
        accounts_urlconf = 'authentication.accounts.urls'
        accounts_resolver = get_resolver(accounts_urlconf)
        misocc_urlconf = 'authentication.misamis_occidental.urls'
        misocc_resolver = get_resolver(misocc_urlconf)
        
                        
        if subdomain == 'welcome':
            for resolver in [accounts_resolver, misocc_resolver]:
                try:
                    resolver.resolve(request.path)
                    print(f'RESOLVING! {resolver.resolve(request.path)}',flush=True)
                    raise Http404("Page not found.")
                except Http404:
                    continue
                
            try:
                user_token = request.session['user_token']
                expires = request.session['expires']
                current_time = int(time.time())  
                if current_time >= expires:
                    # The session has expired, sign out the user
                    return self.signout(request, f'http://{settings.ACCOUNTS_DOMAIN}')
                
                
            except KeyError:
                print(f'WELCOME: Unauthenticated.', flush=True)
                return self.signout(request, f'http://{settings.ACCOUNTS_DOMAIN}')
                # try:
                #     user_token = request.session['user_token']
                #     expires = request.session['expires']
                #     current_time = int(time.time())  
                #     if current_time >= expires:
                #         # The session has expired, sign out the user
                #         return self.signout(request, f'http://{settings.ACCOUNTS_DOMAIN}')
                    
                #     # if path in accounts_redirect_paths or any(path.startswith(prefix) for prefix in accounts_redirect_prefixes):
                #     #     return redirect('home')
                # except KeyError:
                #     # if path in accounts_redirect_paths or any(path.startswith(prefix) for prefix in accounts_redirect_prefixes):
                #     #     return redirect(f'http://{settings.ACCOUNTS_DOMAIN}{path}')
                #     # else:
                #         # if path in accounts_redirect_paths or any(path.startswith(prefix) for prefix in accounts_redirect_prefixes):
                #         #     return redirect(f'http://{settings.ACCOUNTS_DOMAIN}{request.path}')
                #         # else:                            
                
        elif subdomain == 'accounts':
            
            
            
            try:
                match = accounts_resolver.resolve(request.path)
            except:
                match = None
            
            # KUNG ANG PATH AY PANG-ACCOUNTS    
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
            # KUNG HINDI PANG-ACCOUNTS
            else:
                try:
                    user_token = request.session['user_token']
                    return redirect(f'http://{settings.DOMAIN}{request.path}')
                except KeyError:
                    raise Http404("Page not found.")
                # CHECK IF AUTHENTICATED          
                # try:
                #     user_token = request.session['user_token']
                #     expires = request.session['expires']
                #     current_time = int(time.time())  
                #     if current_time >= expires:
                #         # The session has expired, sign out the user
                #         return self.signout(request, f'http://{settings.ACCOUNTS_DOMAIN}')
                #     return redirect(f'http://{settings.DOMAIN}{request.path}')
                # except KeyError:
                    
            #     if path in accounts_redirect_paths or any(path.startswith(prefix) for prefix in accounts_redirect_prefixes):
            #         return redirect('home')
            #     else:
            #         return redirect(f'http://{settings.DOMAIN}{request.path}')
            # except KeyError:
            #     # KUNG HINDI SA SIGNIN PUPUNTA, DALHIN SA WELCOME
            #     if path not in accounts_redirect_paths and not any(path.startswith(prefix) for prefix in accounts_redirect_prefixes):
            #         return redirect(f'http://{settings.DOMAIN}{request.path}')
            # The path does not exist, redirect to the main domain
                # return redirect(f'http://{settings.ACCOUNTS_DOMAIN}{request.path}')

        
        elif subdomain == 'misamis-occidental':
            request.urlconf = 'authentication.misamis_occidental.urls'

    
        # FOR TEST CODE
        # FOR http://127.0.0.1:8000
        # else:
            
        #     try:
        #         user_token = request.session['user_token']
        #         expires = request.session['expires']
        #         current_time = int(time.time())  # Get the current time in seconds since the epoch (UNIX time)
        #         if current_time >= expires:
        #             # The session has expired, sign out the user
        #             return self.signout(request, f'http://{host}')
                    
        #         if path in accounts_redirect_paths or any(path.startswith(prefix) for prefix in accounts_redirect_prefixes):
        #             return redirect ('home')
        #     except KeyError:
        #         if path not in accounts_redirect_paths and not any(path.startswith(prefix) for prefix in accounts_redirect_prefixes):
        #             return self.signout(request, f'http://{host}')
            
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