from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from annotations import documents as annotations_documents


class OntologyTermDocumentSerializer(DocumentSerializer):
    class Meta:
        document = annotations_documents.OntologyTermDocument
        fields = (
            'id',
            'onto_term',
            'term_name',
            'term_definition',
            'term_synonyms',
            'term_is_obsolete',
            'aspect',
        )

