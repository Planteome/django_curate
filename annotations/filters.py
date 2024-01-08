from django_filters_facet import Facet, FacetedFilterSet

from .models import Annotation, AnnotationOntologyTerm

class AnnotationFilterSet(FacetedFilterSet):
    class Meta:
        model = Annotation
        fields = ['aspect', 'taxon', 'db']

    def configure_facets(self):
        self.filters["aspect"].facet = Facet()
        self.filters["taxon"].facet = Facet()
        self.filters["db"].facet = Facet()
