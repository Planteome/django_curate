from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views


app_name = 'taxon'
urlpatterns = [
    path('<int:ncbiID>', views.TaxonView.as_view(), name='taxon'),
    path('import/', views.TaxonImportView.as_view(), name='taxon_import'),
    path('import_success/', views.TemplateView.as_view(template_name='taxon/taxon_import_success.html'), name='import_success'),
    path('add/', views.TaxonAddView.as_view(), name='taxon_add'),
    path('', views.TaxonBaseView.as_view(), name='base_taxon')

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
