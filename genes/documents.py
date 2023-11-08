from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from elasticsearch_dsl import analyzer

from .models import Gene

from taxon.models import Taxon
from annotations.models import Annotation


html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)

@registry.register_document
class GeneDocument(Document):
    # Foreign keys need to be treated specially or get error
    species = fields.ObjectField(properties={
        'name': fields.TextField(),
        'pk': fields.IntegerField(),
    })
    
    id = fields.IntegerField(attr='id')
    
    symbol = fields.TextField(
        analyzer=html_strip,
        fields={
            'raw': fields.TextField(analyzer='keyword'),
            'keyword': fields.Keyword(),
        }
    )
    
    name = fields.TextField(
        analyzer=html_strip,
        fields={
            'raw': fields.TextField(analyzer='keyword'),
            'keyword': fields.Keyword(),
        }
    )
    
    gene_id = fields.TextField(
        analyzer=html_strip,
        fields={
            'raw': fields.TextField(analyzer='keyword'),
            'keyword': fields.Keyword(),
        }
    )
    
    summary = fields.TextField(
        analyzer=html_strip,
        fields={
            'raw': fields.TextField(analyzer='keyword'),
            'keyword': fields.Keyword(),
        }
    )
    
    description = fields.TextField(
        analyzer=html_strip,
        fields={
            'raw': fields.TextField(analyzer='keyword'),
            'keyword': fields.Keyword(),
        }
    )
    
    synonyms = fields.TextField(
        analyzer=html_strip,
        fields={
            'raw': fields.TextField(analyzer='keyword'),
            'keyword': fields.Keyword(),
        }
    )

    class Index:
        name = 'genes'

    class Django:
        model = Gene
        related_models = [Taxon, Annotation]
