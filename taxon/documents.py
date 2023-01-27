from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import Taxon

from genes.models import Gene
from annotations.models import Annotation


@registry.register_document
class TaxonDocument(Document):

    class Index:
        name = 'taxons'

    class Django:
        model = Taxon
        fields = [
            'name',
            'related_synonyms',
            'exact_synonyms',
            'ncbi_id',
        ]
        related_models = [Gene, Annotation]
