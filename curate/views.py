import json

from django.db.models import Count
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from django.http import HttpResponseRedirect, HttpResponse
from django.core.serializers.json import DjangoJSONEncoder

# models import
from taxon.models import Taxon


class HomeView(TemplateView):
    template_name = 'home.html'
    model = Taxon

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        taxons = Taxon.objects.annotate(num_annotations=Count('annotation')).values()
        # add the annotated field to the json results
        taxonsJS = json.dumps(list(taxons), cls=DjangoJSONEncoder)
        context['taxonsJS'] = taxonsJS
        return context
