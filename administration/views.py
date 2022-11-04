from django.shortcuts import render
from django.http import HttpResponse, Http404


# Create your views here.
def main(request):
    """"""
    if not request.user.is_staff:
        raise Http404

    template_name = "admin_main.html"
    context = {}

    return render(request, template_name, context)

def partner(request):
    """"""
    if not request.user.is_staff:
        raise Http404

    template_name = "admin_partner.html"
    context = {}

    return render(request, template_name, context)

def staff(request):
    """"""
    if not request.user.is_staff:
        raise Http404

    template_name = "admin_staff.html"
    context = {}

    return render(request, template_name, context)