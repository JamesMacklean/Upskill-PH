from django.urls import reverse
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse, Http404, HttpResponseRedirect
from scholarium.info import *
import jwt

class SubdomainMiddleware(MiddlewareMixin):
    API_SECRET_KEY = API_SECRET_KEY

    def process_request(self, request):
        host = request.get_host()
        subdomain = host.split('.')[0]

        if subdomain == 'welcome':
            # Check if user is authenticated for other paths on the welcome subdomain
            try:
                user_token = request.session['user_token']
            except:
                if request.path in [reverse('signup'), reverse('signin')]:
                    return redirect(f'{ACCOUNTS_DOMAIN}{request.path}')
                else:
                    request.session['original_url'] = request.get_full_path()
                    print(f"original_url: {request.session['original_url']}")
                    
                return HttpResponseRedirect(f'{ACCOUNTS_DOMAIN}{reverse("signin")}')
        elif subdomain == 'accounts':
            if request.path not in [reverse('signup'), reverse('signin')]:
                return redirect(f'{DOMAIN}{request.path}')
            
        return None

    def authenticate_user(self, request):
        try:
            # PRINT SESSION ITEMS
            for key, value in request.session.items():
                print('{}: {}'.format(key, value))

            try:   
                user_token = request.session['user_token']
                payload = jwt.decode(user_token, self.API_SECRET_KEY, algorithms=['HS256'])

                # SAVE JWT PAYLOAD INTO SESSIONS
                for key, value in payload.items():
                    if key == 'data':
                        for key, value in payload['data'].items():
                            if key not in request.session:
                                request.session[key] = value
                                request.session.modified = True
                return True
            
            except jwt.ExpiredSignatureError:
                self.signout(request)
                return False
            
        except KeyError:
            self.signout(request)
            return False

    def signout(self, request):   
        # PRINT COOKIES
        for key, value in request.COOKIES.items():
            print(f'{key}: {value}')
        # CLEAR SESSIONS
        try:   
            for key in list(request.session.keys()):
                del request.session[key]
                request.session.modified = True
        except KeyError as e:
            print(str(e))
        # return redirect(f'{ACCOUNTS_DOMAIN}{reverse("signin")}')    
        return HttpResponseRedirect(reverse('signin'))
    
# class AuthenticationMiddleware():
#     API_SECRET_KEY = API_SECRET_KEY

#     def authenticate_user(self, request):
#         try:
#             # user_token = request.COOKIES.get('jwt') 
#             # PRINT SESSION ITEMS
#             for key, value in request.session.items():
#                 print('{}: {}'.format(key, value))

#             try:   
#                 user_token = request.session['user_token']
#                 payload = jwt.decode(user_token, self.API_SECRET_KEY, algorithms=['HS256'])

#                 response = HttpResponse()
                
#                 # SAVE JWT PAYLOAD INTO SESSIONS
#                 for key, value in payload.items():
#                     if key == 'data':
#                         for subkey, subvalue in payload['data'].items():
#                             if subkey not in request.session:
#                                 request.session[subkey] = subvalue
#                                 request.session.modified = True
#                             response.set_cookie(subkey, subvalue)
#                 return True
            
#             except jwt.ExpiredSignatureError:
#                 self.signout(request)
#                 return False
            
#         except KeyError:
#             self.signout(request)
#             return False

#     def signout(self, request):   
#         # CLEAR SESSIONS
#         try:   
#             for key in list(request.session.keys()):
#                 del request.session[key]
#                 request.session.modified = True
#         except KeyError as e:
#             print(str(e))
        
#         return HttpResponseRedirect(reverse('signin'))
#         # return redirect(f'{ACCOUNTS_DOMAIN}{reverse("signin")}')