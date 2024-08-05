from django.http import HttpResponseForbidden
from django.urls import reverse
from django.shortcuts import redirect

class SubdomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.process_request(request)
        if response:
            return response
        return self.get_response(request)

    def process_request(self, request):
        host = request.get_host()
        subdomain = host.split('.')[0]

        if subdomain == 'welcome':
            if request.path == reverse('signin'):
                # Redirect to accounts subdomain for signin
                return redirect(f'http://accounts.upskillph.org{reverse("signin")}')
            if request.path == reverse('signup'):
                return redirect(f'http://accounts.upskillph.org{reverse("signup")}')
        elif subdomain == 'accounts':
            if request.path not in [reverse('signup'), reverse('signin')]:
                return HttpResponseForbidden("Forbidden")  # Restrict access to non-signin/signup views
        return None
