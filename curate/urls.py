"""curate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import include, path, reverse_lazy
from django.views.generic import RedirectView, TemplateView
from .views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('taxon/', include('taxon.urls')),
    path('gene/', include('genes.urls')),
    path('dbxref/', include('dbxrefs.urls')),
    path('annotations/', include('annotations.urls')),
    path('celery-progress/', include('celery_progress.urls')),
    path('about', TemplateView.as_view(template_name='about_us.html'), name='about'),
    path('contact', TemplateView.as_view(template_name='contact.html'), name='contact'),
    path('import', TemplateView.as_view(template_name='import_base.html'), name='import'),
    path('', HomeView.as_view(template_name='home.html')),
]
