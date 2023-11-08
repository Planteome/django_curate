from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views


app_name = 'api'
urlpatterns = [
    path('autocomplete_onto_term/', views.OntologyTermAPIView.as_view(), name='autocomplete_onto_term'),
    path('autocomplete_genes/', views.GeneAPIView.as_view(), name='autocomplete_genes'),
    path('autocomplete_dbxrefs/', views.DBXrefAPIView.as_view(), name='autocomplete_dbxrefs'),
    path('autocomplete_taxon/', views.TaxonAPIView.as_view(), name='autcomplete_taxon'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)