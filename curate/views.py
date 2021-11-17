import json

from django.db.models import Count, OuterRef, Subquery, IntegerField
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from django.http import HttpResponseRedirect, HttpResponse
from django.core.serializers.json import DjangoJSONEncoder

# models import
from taxon.models import Taxon
from annotations.models import Annotation


class HomeView(TemplateView):
    template_name = 'home.html'
    model = Taxon

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        #taxons = Taxon.objects.annotate(num_annotations=Count('annotation')).values()
        # Had to switch to using subqueries for the annotate counts so I could also get the gene counts
        # Otherwise the query took way too long because it does a bunch of unneeded joins
        # See https://stackoverflow.com/questions/56567841/django-count-and-sum-annotations-interfere-with-each-other
        # and https://stackoverflow.com/questions/29195299/why-is-this-django-1-6-annotate-count-so-slow
        num_annotations_subq = Taxon.objects.annotate(num_annotations=Count('annotation')).filter(pk=OuterRef('pk'))
        num_genes_subq = Taxon.objects.annotate(num_genes=Count('gene')).filter(pk=OuterRef('pk'))
        taxons = Taxon.objects.annotate(num_annotations=Subquery(num_annotations_subq.values('num_annotations'), output_field=IntegerField()),
                                        num_genes=Subquery(num_genes_subq.values('num_genes'), output_field=IntegerField())).values()
        # add the annotated field to the json results
        taxonsJS = json.dumps(list(taxons), cls=DjangoJSONEncoder)
        context['taxonsJS'] = taxonsJS
        annotation_list = Annotation.objects.all().order_by('-id')[:10:1]
        context['latest_annotations'] = annotation_list
        return context
