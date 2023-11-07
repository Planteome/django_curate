from django.shortcuts import render

# Create your views here.
from annotations.documents import AnnotationDocument as ESAnnotationDocument
from annotations.documents import OntologyTermDocument as ESOntologyTermDocument


from .serializers import OntologyTermDocumentSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

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
            return Response(serializers.data)
        else:
            return Response(None)