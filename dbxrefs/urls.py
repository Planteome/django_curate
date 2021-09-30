from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views


app_name = 'dbxrefs'
urlpatterns = [
    path('<int:pk>', views.DBXrefView.as_view(), name='dbxref'),
    path('<int:pk>/edit', views.DBXrefEditView.as_view(), name='dbxref_edit'),
    path('import/', views.DBXrefImportView.as_view(), name='dbxref_import'),
    path('import_success/', views.TemplateView.as_view(template_name='dbxrefs/dbxref_import_success.html'),
       name='import_success'),
    path('add/', views.DBXrefAddView.as_view(), name='dbxref_add'),
    path('', views.BaseDBXrefView.as_view(), name='base_dbxref')

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
