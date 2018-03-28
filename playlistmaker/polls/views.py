from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def callback(request):
    print(request.GET)
    if request.GET.get('code'):
        code = request.GET['code']
        # Get access and refresh token by calling spotify token api
        # do whatever with access token
        return HttpResponse("Working")
    else :
        return HttpResponse("Not working")
  #  token = request.getParam('token')
   # print(token)
    # Get auth token from request