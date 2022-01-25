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
    path('search/', views.SearchView.as_view(), name='search'),
    path('approval/', views.ApprovalView.as_view(), name='approval'),
    path('by-reference/<slug:id>', views.SearchByReferenceView.as_view(), name='by-reference'),
    path('by-taxon/<int:id>', views.SearchByTaxonView.as_view(), name='by-taxon'),
    path('', views.BaseAnnotationView.as_view(), name='base_annotation')

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
