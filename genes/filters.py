from django_filters_facet import Facet, FacetedFilterSet

from .models import Gene

class GeneFilterSet(FacetedFilterSet):
    class Meta:
        model = Gene
        fields = ["gene_type", "species"]

    def configure_facets(self):
        self.filters["gene_type"].facet = Facet()
        self.filters["species"].facet = Facet()