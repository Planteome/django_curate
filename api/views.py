from django.shortcuts import render

from django.db.models import Q

from annotations.documents import AnnotationDocument as ESAnnotationDocument
from annotations.documents import OntologyTermDocument as ESOntologyTermDocument
from genes.documents import GeneDocument as ESGeneDocument
from dbxrefs.models import DBXref
from taxon.models import Taxon

from .serializers import OntologyTermDocumentSerializer, GeneDocumentSerializer, DBXrefSerializer, TaxonSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

# Create your views here.
class OntologyTermAPIView(APIView):
    document_class = ESOntologyTermDocument
    renderer_classes = [JSONRenderer]

    def get(self, request, *args, **kwargs):
        max_items = 5
        q = request.GET.get('q')

        if q:
            if ':' in q:
                q = q.replace(':', '\":\"')
            search_term = "*" + q + "*"
            # Use the boosts (^10) to order the results
            terms = ESOntologyTermDocument.search().extra(size=max_items).query("multi_match", query=search_term,
                                                          fields=["onto_term^10", "term_name^5", "term_definition^3", "term_synonyms"])
            #Convert to JSON
            serializers = OntologyTermDocumentSerializer(terms, many=True)
            for element in serializers.data:
                del element['ESscore']
            return Response(serializers.data)
        else:
            return Response(None)


class GeneAPIView(APIView):
    document_class = ESGeneDocument
    renderer_classes = [JSONRenderer]

    def get(self, request, *args, **kwargs):
        max_items = 5
        q = request.GET.get('q')

        if q:
            if ':' in q:
                q = q.replace(':', '\":\"')
            search_term = "*" + q + "*"
            # Use the boosts (^10) to order the results
            terms = ESGeneDocument.search().extra(size=max_items).query("multi_match", query=search_term,
                                                          fields=["gene_id^10", "name^5", "symbol^3",
                                                                  "summary", "description", "synonyms"])
            #Convert to JSON
            serializers = GeneDocumentSerializer(terms, many=True)
            for element in serializers.data:
                del element['ESscore']

            return Response(serializers.data)
        else:
            return Response(None)


class GenesAndTermsAPIView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, *args, **kwargs):
        max_items = 5
        q = request.GET.get('q')

        if q:
            if ':' in q:
                q = q.replace(':', '\":\"')
            search_term = "*" + q + "*"
            gene_terms = ESGeneDocument.search().extra(size=max_items).query("multi_match", query=search_term,
                                                          fields=["gene_id^10", "name^5", "symbol^3",
                                                                  "summary", "description", "synonyms"])
            onto_terms = ESOntologyTermDocument.search().extra(size=max_items).query("multi_match", query=search_term,
                                                          fields=["onto_term^10", "term_name^5", "term_definition^3", "term_synonyms"])
            genes_serializer = GeneDocumentSerializer(gene_terms, many=True)
            onto_serializer = OntologyTermDocumentSerializer(onto_terms, many=True)

            combined_data = genes_serializer.data + onto_serializer.data
            def ESscore(e):
                return e['ESscore']
            combined_data.sort(reverse=True, key=ESscore)

            # Now that they are sorted, remove the ESscore fields
            for element in combined_data:
                del element['ESscore']

            return Response(combined_data)
        else:
            return Response(None)



#DBXrefs are few enough in number no need to index in elasticsearch, but an autocomplete endpoint might still be nice
class DBXrefAPIView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, *args, **kwargs):
        max_items = 5
        search_term = request.GET.get('q')

        if search_term:
            queryset = DBXref.objects.filter(
                Q(dbname__icontains=search_term) |
                Q(fullname__icontains=search_term)
            )[:max_items]
            serializers = DBXrefSerializer(queryset, many=True)
            return Response(serializers.data)
        else:
            return Response(None)


class TaxonAPIView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, *args, **kwargs):
        max_items = 5
        search_term = request.GET.get('q')

        if search_term:
            queryset = Taxon.objects.filter(
                Q(name__icontains=search_term) |
                Q(related_synonyms__icontains=search_term) |
                Q(exact_synonyms__icontains=search_term)
            )[:max_items]
            serializers = TaxonSerializer(queryset, many=True)
            return Response(serializers.data)
        else:
            return Response(None)