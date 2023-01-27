from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import Gene

from taxon.models import Taxon
from annotations.models import Annotation


@registry.register_document
class GeneDocument(Document):
    # Foreign keys need to be treated specially or get error
    species = fields.ObjectField(properties={
        'name': fields.TextField(),
        'pk': fields.IntegerField(),
    })

    class Index:
        name = 'genes'

    class Django:
        model = Gene
        fields = [
            'symbol',
            'name',
            'gene_id',
            'summary',
            'description',
        ]
        related_models = [Taxon, Annotation]
