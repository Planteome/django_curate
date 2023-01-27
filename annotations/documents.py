from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import Annotation

from taxon.models import Taxon
from genes.models import Gene


@registry.register_document
class AnnotationDocument(Document):
    # Foreign keys need to be treated special or get error
    species = fields.ObjectField(properties={
        'name': fields.TextField(),
        'pk': fields.IntegerField(),
    })
    db = fields.ObjectField(properties={
        'dbname': fields.TextField(),
        'fullname': fields.TextField(),
        'pk': fields.IntegerField(),
    })

    class Index:
        name = 'annotations'

    class Django:
        model = Annotation
        fields = [
            'db_obj_id',
            'db_obj_symbol',
            'ontology_id',
            'db_reference',
            'evidence_code',
            'aspect',
            'db_obj_name',
            'db_obj_synonym',
            'db_obj_type',
            'assigned_by',
            'gene_product_form_id',
        ]
        related_models = [Taxon, Gene]
