from django.shortcuts import render

def home(request):
    
    template_name = "misamis_occidental/home.html"
    context = {}
    
    return render(request,template_name, context)