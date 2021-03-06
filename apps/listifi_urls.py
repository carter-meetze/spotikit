"""playlistmaker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
#from django.contrib import admin

#urlpatterns = [

 #   path('polls/', include('polls.urls')),
  #  path('admin/', admin.site.urls),


from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from .listifi_views import AuthUser, login_render
from django.urls import path
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.views.generic import TemplateView
from .listifi_forms import entry

urlpatterns = [
    # defining url for form

    # url(r'/', TemplateView.as_view(template_name='listifi_login.html')),

    url(r'^listifi/listifi/listifi/listifi_entry.html', AuthUser.as_view()),

    url(r'listifi_entryform.html', entry),

    url(r'^admin/', admin.site.urls),

    url(r'^spotikit/listifi/listifi/listifi/listifi_login.html', TemplateView.as_view(template_name='listifi_login.html')),

    url(r'^listifi/listifi/listifi/listifi_result.html', AuthUser.as_view()),

    url(r'listifi/listifi/listifi/listifi_cookies.html', TemplateView.as_view(template_name='listifi_cookies.html')),

    url(r'listifi/listifi/listifi/listifi_help.html', TemplateView.as_view(template_name='listifi_help.html')),

    url(r'listifi/listifi/listifi/listifi_error.html', TemplateView.as_view(template_name='listifi_error.html')),

    url(
        r'favicon.ico$',
        RedirectView.as_view(
            url=staticfiles_storage.url('favicon.ico'),
            permanent=False),
        name="favicon")

]


