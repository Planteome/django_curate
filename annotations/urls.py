from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views


app_name = 'annotations'
urlpatterns = [
    path('<int:pk>', views.AnnotationView.as_view(), name='annotation'),
    path('<int:pk>/edit', views.AnnotationEditView.as_view(), name='annotation_edit'),
    path('<int:pk>/changes', views.AnnotationChangeView.as_view(), name='annotation_changes'),
    path('import/', views.AnnotationImportView.as_view(), name='annotation_import'),
    path('import_success/', views.TemplateView.as_view(template_name='annotations/annotation_import_success.html'), name='import_success'),
    path('request/', views.TemplateView.as_view(template_name='annotations/annotation_request.html'), name='request_success'),
    path('add/', views.AnnotationAddView.as_view(), name='annotation_add'),
    path('add_by_gene/<int:pk>', views.AnnotationAddByGeneView.as_view(), name='annotation_add_by_gene'),
    path('add_search_gene/', views.AnnotationSearchGeneView.as_view(), name='annotation_add_search'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('approval/', views.ApprovalView.as_view(), name='approval'),
    path('by-reference/<slug:id>', views.SearchByReferenceView.as_view(), name='by-reference'),
    path('by-taxon/<int:id>', views.SearchByTaxonView.as_view(), name='by-taxon'),
    path('ontology_update/', views.OntologyUpdateView.as_view(), name='ontology-update'),
    path('add_ontology_term/', views.OntologyTermAddView.as_view(), name='add_onto_term'),
    path('onto_term/<int:pk>', views.OntologyTermView.as_view(), name='onto_term'),
    path('link_internal/<int:pk>', views.LinkInternalView.as_view(), name='link_internal'),
    path('link_with_gene/<int:annot_pk>/<int:gene_pk>', views.LinkInternalGeneView.as_view(), name='link_with_gene'),
    path('', views.BaseAnnotationView.as_view(), name='base_annotation')

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
