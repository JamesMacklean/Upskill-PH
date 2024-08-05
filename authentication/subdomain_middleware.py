from django.urls import reverse
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
# from authentication.views import authenticate_user
from scholarium.info import *

import jwt
class SubdomainMiddleware(MiddlewareMixin):
    def process_request(self, request):
        host = request.get_host()
        subdomain = host.split('.')[0]

        if subdomain == 'welcome':
            # Check if user is authenticated for other paths on the welcome subdomain
            if not authenticate_user(request):
                return redirect(f'http://accounts.upskillph.org{reverse("signin")}')
        
        if subdomain == 'accounts':
            if not authenticate_user(request):
                return redirect(f'http://accounts.upskillph.org{reverse("signin")}')
            else:
                return redirect(f'http://welcome.upskillph.org{request.path}')
        
        return None
    
def authenticate_user(request):
    try:
        # user_token = request.COOKIES.get('jwt')    
        # PRINT SESSION ITEMS
        for key, value in request.session.items():
            print('{}: {}'.format(key, value))
                
        try:   
            user_token = request.session['user_token'] 
            payload = jwt.decode(user_token, API_SECRET_KEY, algorithms=['HS256'])

            # SAVE JWT PAYLOAD INTO SESSIONS
            for key,value in payload.items():
                if key == 'data':
                    for key,value in payload['data'].items():
                        if request.session[key]:
                            pass
                        else:
                            request.session[key] = value
                            request.session.modified = True
            return True
        
        except jwt.ExpiredSignatureError:
            signout(request)
            return False
        
    except KeyError:
        signout(request)
        return False

def signout(request):   
    # CLEAR SESSIONS
    try:   
        for key in list(request.session.keys()):
            del request.session[key]
            request.session.modified = True
    except KeyError as e:
        print(str(e))
        
    return redirect(f'http://accounts.upskillph.org{reverse("signin")}')
