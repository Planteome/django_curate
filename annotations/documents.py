from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import Annotation, AnnotationOntologyTerm

from taxon.models import Taxon
from genes.models import Gene

# json import for ontology term lookup
import requests

## NOTE!!!
# changes in this file seem to require a restart of celery to be picked up by the bulk insert process


@registry.register_document
class AnnotationDocument(Document):
    # Foreign keys need to be treated special or get error
    taxon = fields.ObjectField(properties={
        'name': fields.TextField(),
        'pk': fields.IntegerField(),
    })
    db = fields.ObjectField(properties={
        'dbname': fields.TextField(),
        'fullname': fields.TextField(),
        'pk': fields.IntegerField(),
    })

    ontology_term = fields.ObjectField(properties={
        'onto_term': fields.TextField(),
        'term_definition': fields.TextField(),
        'term_synonyms': fields.TextField(),
        'is_obsolete': fields.BooleanField(),
        'pk': fields.IntegerField(),
    })

    class Index:
        name = 'annotations'

    class Django:
        model = Annotation
        fields = [
            'db_obj_id',
            'db_obj_symbol',
            'db_reference',
            'evidence_code',
            'aspect',
            'db_obj_name',
            'db_obj_synonym',
            'db_obj_type',
            'assigned_by',
            'gene_product_form_id',
        ]
        related_models = [Taxon, Gene, AnnotationOntologyTerm]
