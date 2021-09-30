from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views


app_name = 'genes'
urlpatterns = [
    path('<int:pk>', views.GeneView.as_view(), name='gene'),
    path('<int:pk>/edit', views.GeneEditView.as_view(), name='gene_edit'),
    path('<int:pk>/changes', views.GeneChangeView.as_view(), name='gene_changes'),
    path('import/', views.GeneImportView.as_view(), name='gene_import'),
    path('import_aliases/', views.GeneAliasImportView.as_view(), name='alias_import'),
    path('import_success/', views.TemplateView.as_view(template_name='gene/gene_import_success.html'), name='import_success'),
    path('add/', views.GeneAddView.as_view(), name='gene_add'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('approval/', views.ApprovalView.as_view(), name='approval'),
    path('', views.BaseGeneView.as_view(), name='base_gene')

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)