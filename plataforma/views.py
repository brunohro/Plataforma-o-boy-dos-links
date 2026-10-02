from django.shortcuts import render

def index(request):
    return render(request, 'plataforma/index.html')

def painel_adm(request):
    return render(request, 'plataforma/adm/painel_adm.html')
