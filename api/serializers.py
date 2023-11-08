from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from rest_framework import serializers

from annotations import documents as annotations_documents
from genes import documents as genes_documents
from dbxrefs.models import DBXref


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


class GeneDocumentSerializer(DocumentSerializer):
    class Meta:
        document = genes_documents.GeneDocument
        fields = (
            'id',
            'symbol',
            'name',
            'gene_id',
            'summary',
            'description',
            'synonyms',
        )


class DBXrefSerializer(serializers.ModelSerializer):
    class Meta:
        model = DBXref
        fields = (
            'dbname',
            'fullname',
        )