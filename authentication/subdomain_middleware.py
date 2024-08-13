from django.urls import reverse
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse, Http404, HttpResponseRedirect
from scholarium.info import *
from scholarium import settings
import jwt

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
                if request.path in accounts_redirect_paths or any(request.path.startswith(prefix) for prefix in accounts_redirect_prefixes):
                    return redirect('home')
            except:
                # KUNG HINDI AUTHENTICATED PERO SA SIGNIN GUSTO PUMUNTA, DALHIN SA ACCOUNTS
                if request.path in accounts_redirect_paths or any(request.path.startswith(prefix) for prefix in accounts_redirect_prefixes):
                    return redirect(f'{settings.ACCOUNTS_DOMAIN}{request.path}')
                # KUNG HINDI AUTHENTICATED AT PUMUNTA SA IBANG PAGE, ISAVE ANG URL, DALHIN SA SIGNIN
                else:
                    request.session['original_url'] = request.get_full_path()
                    print(f"original_url: {request.session['original_url']}")
                    return HttpResponseRedirect(f'{settings.ACCOUNTS_DOMAIN}{reverse("signin")}')
                
        elif subdomain == 'accounts':
            # KUNG HINDI SIGNIN ANG PUPUNTAHAN, DALHIN SA WELCOME
            if request.path not in accounts_redirect_paths and not any(request.path.startswith(prefix) for prefix in accounts_redirect_prefixes):
                return redirect(f'{settings.DOMAIN}{request.path}')
                # return redirect(f'{domain}{request.path}')
            else:
                # KUNG AUTHENTICATED PERO SA SIGNIN GUSTO PUMUNTA, DALHIN SA HOME
                try:
                    user_token = request.session['user_token']
                    return redirect ('home')
                # KUNG HINDI AUTHENTICATED PERO SA SIGNIN GUSTO PUMUNTA, HAYAAN LANG
                except:
                    pass
        
        # FOR TEST CODE
        # FOR http://127.0.0.1:8000
        else:
            
            try:
                user_token = request.session['user_token']
                if request.path in accounts_redirect_paths or any(request.path.startswith(prefix) for prefix in accounts_redirect_prefixes):
                    return redirect ('home')
            except:
                if request.path in accounts_redirect_paths or any(request.path.startswith(prefix) for prefix in accounts_redirect_prefixes):
                    pass
                else:
                    request.session['original_url'] = request.get_full_path()
                    print(f"original_url: {request.session['original_url']}")
                    return HttpResponseRedirect(f'{domain}{reverse("signin")}')
            
        return None