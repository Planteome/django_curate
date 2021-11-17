from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from django.http import HttpResponseRedirect, HttpResponse

from django import forms

# models import
from .models import Taxon, TaxonomyDocument
from annotations.models import Annotation
from genes.models import Gene

# forms import
from .forms import TaxonomyImportDocumentForm, TaxonomyAddForm

# serializers import
from django.core import serializers

# regex import
import re


# Create your views here.
class TaxonBaseView(TemplateView):
    model = Taxon
    template_name = 'taxon/base_taxon.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(TaxonBaseView, self).get_context_data(**kwargs)
        taxons = Taxon.objects.all()
        taxonsJS = serializers.serialize("json", taxons)
        context['taxons'] = taxons
        context['taxonsJS'] = taxonsJS
        return context


class TaxonView(TemplateView):
    model = Taxon
    template_name = 'taxon/taxon.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(TaxonView, self).get_context_data(**kwargs)
        if 'ncbiID' in self.kwargs:
            taxon = Taxon.objects.get(ncbi_id=self.kwargs['ncbiID'])
        else:
            taxon = Taxon.objects.get(ncbi_id=1)
        context['taxon'] = taxon
        # taxon root term (ncbi_id = 1) does not have a parent
        if taxon.ncbi_id != 1:
            parent = Taxon.objects.get(ncbi_id=taxon.parent)
            context['parent'] = parent
        # get the last 10 annotations in reverse order
        annotation_list = Annotation.objects.filter(taxon=taxon).order_by('-id')[:10:1]
        context['latest_annotations'] = annotation_list
        # get the gene count
        gene_count = Gene.objects.filter(species=taxon).count()
        if gene_count > 0:
            context['gene_count'] = gene_count
        return context


class TaxonImportView(FormView):
    model = Taxon
    template_name = 'taxon/import_taxon.html'
    form_class = TaxonomyImportDocumentForm
    success_url = reverse_lazy('taxon:import_success')

    def get_context_data(self, **kwargs):
        context = super(TaxonImportView, self).get_context_data(**kwargs)
        user = self.request.user
        if not user.is_authenticated:
            context['logged_in'] = False
            return context

        context['logged_in'] = True
        if user.is_superuser:
            context['superuser'] = True
        else:
            context['superuser'] = False
        return context

    def get(self, request):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        form = TaxonomyImportDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            file = TaxonomyDocument(document=request.FILES['document'])
            file.save()
            self.handle_uploaded_taxonomy(request.FILES['document'])
            return HttpResponseRedirect('/taxon/import_success/')

    def handle_uploaded_taxonomy(self, file):
        # All taxons
        taxon_lst = []
        # Current info for taxon, used as we fill up data
        curr_taxon = ''
        curr_parent = ''
        curr_rank = ''
        curr_name = ''
        curr_related = ''
        curr_exact = ''

        # regexes
        id_match = re.compile('^ID\s+\:\s*(\d+)\s*')
        parentID_match = re.compile('PARENT ID\s+\:\s*(\d+)\s*')
        rank_match = re.compile('RANK\s+\:\s*([^\n]+)\s*')
        name_match = re.compile('SCIENTIFIC NAME\s+\:\s*([^\n]+)\s*')
        related_synonym_match = re.compile('COMMON NAME\s+\:\s*([^\n]+)\s*')
        exact_synonym_match = re.compile('SYNONYM\s+\:\s*([^\n]+)\s*')
        end_match = re.compile('\/\/')
        for line in file:
            line = line.decode('UTF-8')
            end = end_match.search(line)
            if end:
                taxon_lst.append(Taxon(ncbi_id=curr_taxon, name=curr_name, parent=curr_parent, rank=curr_rank, exact_synonyms=curr_exact,
                                       related_synonyms=curr_related))

                # clear out the previous taxon
                curr_taxon = ''
                curr_parent = ''
                curr_rank = ''
                curr_name = ''
                curr_related = ''
                curr_exact = ''
            else:
                if id_match.search(line):
                    curr_taxon = id_match.search(line).group(1)
                if parentID_match.search(line):
                    curr_parent = parentID_match.search(line).group(1)
                if name_match.search(line):
                    curr_name = name_match.search(line).group(1)
                if rank_match.search(line):
                    curr_rank = rank_match.search(line).group(1)
                if related_synonym_match.search(line):
                    if not curr_related:
                        curr_related = related_synonym_match.search(line).group(1)
                    else:
                        curr_related = curr_related + "|" + related_synonym_match.search(line).group(1)
                if exact_synonym_match.search(line):
                    if not curr_exact:
                        curr_exact = exact_synonym_match.search(line).group(1)
                    else:
                        curr_exact = curr_exact + "|" + exact_synonym_match.search(line).group(1)

        # Now put them all in the db at once
        Taxon.objects.bulk_create(taxon_lst)


class TaxonAddView(FormView):
    model = Taxon
    form_class = TaxonomyAddForm
    template_name = 'taxon/add_taxon.html'
    success_url = reverse_lazy('taxon:import_success')

    def get_context_data(self, **kwargs):
        context = super(TaxonAddView, self).get_context_data(**kwargs)
        user = self.request.user
        if not user.is_authenticated:
            context['logged_in'] = False
            return context

        context['logged_in'] = True
        if user.is_superuser:
            context['superuser'] = True
        else:
            context['superuser'] = False

        # Get the current taxons so we can find the parents with the form
        # TODO: add autocomplete to the form for the parent
        taxons = Taxon.objects.all()
        taxon_dict = {}
        for taxon in taxons:
            taxon_dict[taxon.name] = taxon.ncbi_id
        context['taxons'] = taxon_dict
        return context

    def get(self, request):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        form = TaxonomyAddForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            rank = form.cleaned_data['rank']
            related = form.cleaned_data['related_synonyms']
            exact = form.cleaned_data['exact_synonyms']
            ncbiID = form.cleaned_data['ncbi_id']
            parent = form.cleaned_data['parent']

            Taxon.objects.create(name=name, rank=rank, related_synonyms=related, exact_synonyms=exact, ncbi_id=ncbiID, parent=parent)
            return HttpResponseRedirect('/taxon/import_success/')
        else:
            return self.render_to_response(self.get_context_data())
