from django.urls import reverse
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from authentication.views import authenticate_user

class SubdomainMiddleware(MiddlewareMixin):
    def process_request(self, request):
        host = request.get_host()
        subdomain = host.split('.')[0]

        if subdomain == 'welcome':
            if request.path == reverse('signin'):
                return redirect(f'http://accounts.upskillph.org{reverse("signin")}')
            if request.path == reverse('signup'):
                return redirect(f'http://accounts.upskillph.org{reverse("signup")}')
            
            # Check if user is authenticated for other paths on the welcome subdomain
            if not authenticate_user(request):
                return redirect(f'http://accounts.upskillph.org{reverse("signin")}')
        
        elif subdomain == 'accounts':
            if request.path not in [reverse('signup'), reverse('signin')]:
                return redirect(f'http://welcome.upskillph.org{request.path}')
        
        return None
