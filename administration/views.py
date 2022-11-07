from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User

# Create your views here.
def main(request):
    """"""
    if not request.user.is_staff:
        raise Http404

    template_name = "administration/admin_main.html"
    context = {}

    return render(request, template_name, context)

def partner(request):
    """"""
    if not request.user.is_staff:
        raise Http404

    template_name = "administration/admin_partner.html"
    context = {}

    return render(request, template_name, context)

def staff(request):
    """"""
    if not request.user.is_staff:
        raise Http404

    template_name = "administration/admin_staff.html"
    context = {}
    staff_checker = User.objects.all().filter(is_staff=True)
    
    staff_users = []
    
    for staff in staff_checker:
        staff_users.append(staff)
        
    context['staff_users'] = staff_users

    return render(request, template_name, context)