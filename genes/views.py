import json.decoder

from django.utils import timezone

from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView, ListView
from django.views.generic.edit import UpdateView
from django.forms.models import model_to_dict

# settings import
from django.conf import settings

# models import
from urllib3.connectionpool import xrange

from .models import Gene, GeneDocument, GeneApproval, MissingGenesFromAliasesImport
from taxon.models import Taxon
from annotations.models import Annotation

# forms import
from .forms import GeneImportDocumentForm, GeneAddForm, GeneEditForm

# tasks import
from .tasks import process_genes_task, process_aliases_task, test_task

# choices import
import curate.choices as choices

# pubmed fetch import
from Bio import Entrez

# itertools import
from itertools import tee

# timezone import
import pytz



# Create your views here.
class BaseGeneView(TemplateView):
    model = Gene
    template_name = 'gene/base_gene.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(BaseGeneView, self).get_context_data()
        # get the last 10 genes in reverse order
        gene_list = Gene.objects.all().order_by('-id')[:10:-1]
        context['latest_genes'] = gene_list

        return context


class GeneView(TemplateView):
    model = Gene
    template_name = 'gene/gene.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(GeneView, self).get_context_data(**kwargs)
        gene = Gene.objects.get(pk=self.kwargs['pk'])
        context['gene'] = gene

        # Get the related annotations
        related_annotations = Annotation.objects.filter(internal_gene=gene)
        if related_annotations.count() > 0:
            context['related_annotations'] = related_annotations
            context['latest_annotations'] = related_annotations.order_by('-id')[:5]

        # Get the pubmed info if possible
        if gene.pubmed_id:
            # Need to set a contact email
            Entrez.email = settings.ENTREZ_EMAIL
            Entrez.api_key = settings.ENTREZ_API_KEY
            pubmed_dict = {}
            # remove any spaces in the pmid list
            ids = gene.pubmed_id.replace(' ', '')
            handle = Entrez.esummary(db='pubmed', id=ids, retmode='xml', rettype="medline")
            records = Entrez.parse(handle)
            for record in records:
                title = record["Title"]
                curr_id = record['Id']
                pubmed_dict[curr_id] = title
            context['pubmed'] = pubmed_dict
        user = self.request.user
        if not user.is_authenticated:
            context['logged_in'] = False
            return context

        context['logged_in'] = True
        if user.is_superuser:
            context['superuser'] = True
        else:
            context['superuser'] = False
        # Get the count of changes that been approved for this gene
        #change_count = GeneApproval.objects.filter(source_gene=gene, status=choices.ApprovalStates.APPROVED).count()
        # The 1 subtracted is to account for the original being saved as a historicalrecord
        change_count = gene.history.all().count() - 1
        if change_count > 0:
            context['change_count'] = change_count

        return context


class GeneEditView(UpdateView):
    model = Gene
    template_name = 'gene/edit_gene.html'
    form_class = GeneEditForm
    success_url = reverse_lazy('genes:import_success')

    def get_context_data(self, **kwargs):
        context = super(GeneEditView, self).get_context_data(**kwargs)
        gene = Gene.objects.get(pk=self.kwargs['pk'])
        context['gene'] = gene
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

    def post(self, request, **kwargs):
        # update requestor field
        requestor = request.user
        curr_time = timezone.now()

        # get the comments from the form
        comments = request.POST.get('comments')

        existing_gene = get_object_or_404(Gene, pk=self.kwargs['pk'])

        # initialize the changed gene to the same as the existing
        changed_gene = GeneApproval()
        for field in existing_gene._meta.fields:
            setattr(changed_gene, field.name, getattr(existing_gene, field.name))
        # Change the values
        changed_gene.pk = None # will get the next pk available
        changed_gene.synonyms = request.POST.get('synonyms')
        changed_gene.summary = request.POST.get('summary')
        changed_gene.description = request.POST.get('description')
        if request.POST.get('pubmed_id'):
            changed_gene.pubmed_id = request.POST.get('pubmed_id')
        else:
            changed_gene.pubmed_id = None

        # add new values
        changed_gene.requestor = requestor
        changed_gene.datetime = curr_time
        changed_gene.comments = comments
        changed_gene.source_gene = existing_gene

        changed_gene.status = choices.ApprovalStates.PENDING
        changed_gene.action = choices.ApprovalActions.INITIAL

        if requestor.is_superuser:
            # Set it to approved
            changed_gene.status = choices.ApprovalStates.APPROVED
            changed_gene.action = choices.ApprovalActions.APPROVE
            # save it to the db as a GeneApproval model
            changed_gene.save()

            # Save the existing gene once before changes so the initial history is created
            # if it hasn't already
            if existing_gene.history.all().count() == 0:
                existing_gene.save()

            # Save the existing gene with the updated fields
            existing_gene.synonyms = changed_gene.synonyms
            existing_gene.summary = changed_gene.summary
            existing_gene.description = changed_gene.description
            existing_gene.pubmed_id = changed_gene.pubmed_id

            existing_gene.save()
            
        # save it to the db as a GeneApproval model
        changed_gene.save()
        # go to the request submitted page or success
        if requestor.is_superuser:
            return render(self.request, 'gene/gene_import_success.html')
        else:
            return render(self.request, 'gene/gene_request.html')


class GeneImportView(FormView):
    model = Gene
    template_name = 'gene/import_gene.html'
    form_class = GeneImportDocumentForm
    #success_url = reverse_lazy('gene:import_success')

    def get_context_data(self, **kwargs):
        context = super(GeneImportView, self).get_context_data(**kwargs)
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
        form = GeneImportDocumentForm(request.POST, request.FILES)
        user = self.request.user
        if form.is_valid():
            species = form.cleaned_data['species']
            file = GeneDocument(document=request.FILES['document'], species=species)
            file.save()
            # pass the new uploaded file id so it can be looked up in the task
            genes_lst = process_genes_task.delay(file.document.name, species.pk, user.pk)
            return render(self.request, 'gene/display_progress.html', context={'task_id': genes_lst.task_id})


class GeneAddView(FormView):
    form_class = GeneAddForm
    model = Gene
    template_name = 'gene/add_gene.html'
    success_url = reverse_lazy('genes:import_success')

    def get(self, request):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(GeneAddView, self).get_context_data(**kwargs)
        user = self.request.user
        if not user.is_authenticated:
            context['logged_in'] = False
            return context

        context['logged_in'] = True
        if user.is_superuser:
            context['superuser'] = True
        else:
            context['superuser'] = False

        # Get the current species so we can find the species with the form
        # TODO: add autocomplete to the form for the species
        species = Taxon.objects.all()
        species_dict = {}
        for taxon in species:
            species_dict[taxon.name] = taxon.ncbi_id
        context['species'] = species_dict
        return context

    def post(self, request, *args, **kwargs):
        form = GeneAddForm(request.POST)
        if form.is_valid():
            symbol = form.cleaned_data['symbol']
            name = form.cleaned_data['name']
            gene_id = form.cleaned_data['gene_id']
            gene_type = form.cleaned_data['gene_type']
            species = form.cleaned_data['species']
            synonyms = form.cleaned_data['synonyms']
            location = form.cleaned_data['location']
            summary = form.cleaned_data['summary']
            description = form.cleaned_data['description']
            phenotype = form.cleaned_data['phenotype']
            data_source_object_id = form.cleaned_data['data_source_object_id']
            data_source_name = form.cleaned_data['data_source_name']
            pubmed_id = form.cleaned_data['pubmed_id']
            Gene.objects.create(symbol=symbol, name=name, gene_id=gene_id, gene_type=gene_type, species=species,
                                synonyms=synonyms, location=location, summary=summary, description=description,
                                phenotype=phenotype, data_source_object_id=data_source_object_id,
                                data_source_name=data_source_name, pubmed_id=pubmed_id,
                                changed_by=self.request.user)

            return HttpResponseRedirect('/gene/import_success/')
        else:
            return self.render_to_response(self.get_context_data())


class GeneAliasImportView(FormView):
    model = Gene
    template_name = 'gene/import_aliases.html'
    form_class = GeneImportDocumentForm
    success_url = reverse_lazy('genes:import_aliases_success')

    def get_context_data(self, **kwargs):
        context = super(GeneAliasImportView, self).get_context_data(**kwargs)
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
        form = GeneImportDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            species = form.cleaned_data['species']
            file = GeneDocument(document=request.FILES['document'], species=species)
            file.save()
            # pass the new uploaded file id so it can be looked up in the task
            alias_lst = process_aliases_task.delay(file.document.name, species.pk)
            return render(self.request, 'gene/display_progress_aliases.html', context={'task_id': alias_lst.task_id})


class AliasSuccessView(TemplateView):
    model = MissingGenesFromAliasesImport
    template_name = 'gene/gene_alias_import_success.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(AliasSuccessView, self).get_context_data(**kwargs)
        last_missing_genes_from_alias = MissingGenesFromAliasesImport.objects.last()
        # data is stored in json in db, so decode it
        json_dec = json.decoder.JSONDecoder()
        missing_gene_list = json_dec.decode(last_missing_genes_from_alias.missingGeneList)
        missing_alias_count = last_missing_genes_from_alias.aliasCount
        missing_gene_count = len(missing_gene_list)
        if missing_gene_count != 0:
            context['missing_gene_list'] = missing_gene_list
            context['missing_gene_count'] = missing_gene_count
            context['missing_alias_count'] = missing_alias_count
        return context


class ApprovalView(TemplateView):
    model = Gene
    template_name = 'gene/gene_approval.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(ApprovalView, self).get_context_data(**kwargs)
        user = self.request.user
        if not user.is_authenticated:
            context['logged_in'] = False
            return context

        context['logged_in'] = True
        if user.is_superuser:
            context['superuser'] = True
        else:
            context['superuser'] = False

        # get list of genes awaiting approval
        approval_genes = GeneApproval.objects.filter(Q(status=choices.ApprovalStates.PENDING))
        context['approval_genes'] = approval_genes

        return context

    def post(self, request, *args, **kwargs):
        # list of gene edits to approve
        approve_list = request.POST.getlist('approvalChkbox')
        for approved_gene_id in approve_list:
            # update the gene in the database
            approved_gene = GeneApproval.objects.get(pk=approved_gene_id)
            org_gene = Gene.objects.get(pk=approved_gene.source_gene_id)
            # Save the existing gene once before changes so the initial history is created
            # if it hasn't already
            if org_gene.history.all().count() == 0:
                org_gene.save()
            org_gene.synonyms = approved_gene.synonyms
            org_gene.summary = approved_gene.summary
            org_gene.description = approved_gene.description
            org_gene.pubmed_id = approved_gene.pubmed_id

            # change the GeneApproval model
            approved_gene.action = choices.ApprovalActions.APPROVE
            approved_gene.status = choices.ApprovalStates.APPROVED

            # Go ahead and save
            org_gene.save()
            approved_gene.save()

        # rejections
        reject_list = request.POST.getlist('rejectChkbox')
        for reject_gene_id in reject_list:
            reject_gene = GeneApproval.objects.get(pk=reject_gene_id)
            # Only have to change the GeneApproval model status
            reject_gene.action = choices.ApprovalActions.REJECT
            reject_gene.status = choices.ApprovalStates.REJECTED
            reject_gene.save()

        # Ones to request more info from requestor
        requestInfo_list = request.POST.getlist('requestInfoChkbox')
        for request_gene_id in requestInfo_list:
            request_gene = GeneApproval.objects.get(pk=request_gene_id)
            request_gene.action = choices.ApprovalActions.MORE_INFO
            # add a comment to the comment box so we know this has been requested for more info
            #  if it hasn't already
            if "More info requested" not in request_gene.comments:
                request_gene.comments = request_gene.comments + "\nMore info requested"
            #TODO: add email or something to communicate with requestor
            request_gene.save()

        return render(self.request, 'gene/gene_import_success.html')


class GeneChangeView(TemplateView):
    model = Gene
    template_name = 'gene/changes.html'

    def pair_iterable_for_delta_changes(self, iterable):
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(GeneChangeView, self).get_context_data(**kwargs)
        gene_id = self.kwargs['pk']
        # get the gene
        gene = Gene.objects.get(pk=gene_id)
        context['gene'] = gene
        # get the gene history
        gene_iterator = gene.history.all().order_by('history_date').iterator()
        delta_list = []
        delta_number = 1
        for record_pair in self.pair_iterable_for_delta_changes(gene_iterator):
            old_record, new_record = record_pair
            delta = new_record.diff_against(old_record)
            delta.number = delta_number
            delta_number += 1
            delta.history_date = new_record.history_date
            delta.changed_by = new_record.changed_by
            delta_list.append(delta)

        context['delta_list'] = delta_list

        return context


class SearchView(ListView):
    model = Gene
    template_name = 'gene/search.html'
    context_object_name = 'all_search_results'
    paginate_by = 25

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        # Need to set the context object_list to the query so that pagination works
        self.object_list = self.get_queryset().order_by('pk')[:10000]
        context = super(SearchView, self).get_context_data(**kwargs)
        context['count'] = self.object_list.count()
        adjacent_pages = 2
        page_number = context['page_obj'].number
        num_pages = context['paginator'].num_pages
        start_page = max(page_number - adjacent_pages, 1)
        if start_page <= 3:
            start_page = 1
        end_page = page_number + adjacent_pages + 1
        if end_page >= num_pages - 1:
            end_page = num_pages + 1
        page_numbers = [n for n in xrange(start_page, end_page) \
                if n > 0 and n <= num_pages]
        context.update({
            'page_numbers': page_numbers,
            'show_first': 1 not in page_numbers,
            'show_last': num_pages not in page_numbers,
            })
        return context

    def get_queryset(self):
        #result = super(SearchView, self).get_queryset()
        search_term = self.request.GET.get('search')
        if search_term:
            postresult = Gene.objects.filter(Q(name__icontains=search_term) |
                                             Q(symbol__icontains=search_term) |
                                             Q(gene_id__icontains=search_term) |
                                             Q(synonyms__icontains=search_term))
            result = postresult
        else:
            result = None
        return result


class SearchByReferenceView(ListView):
    model = Gene
    template_name = 'gene/search.html'
    context_object_name = 'all_search_results'
    paginate_by = 25

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        # Need to set the context object_list to the query so that pagination works
        self.object_list = self.get_queryset().order_by('pk')[:10000]
        context = super(SearchByReferenceView, self).get_context_data(**kwargs)
        context['count'] = self.object_list.count()
        context = adjust_pagination(context)
        return context

    def get_queryset(self):
        search_term = self.kwargs['id']
        if search_term:
            postresult = Gene.objects.filter(Q(pubmed_id__contains=search_term))
            result = postresult
        else:
            result = None
        return result


class SearchByTaxonView(ListView):
    model = Gene
    template_name = 'gene/search.html'
    context_object_name = 'all_search_results'
    paginate_by = 25

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        # Need to set the context object_list to the query so that pagination works
        self.object_list = self.get_queryset().order_by('pk')[:10000]
        context = super(SearchByTaxonView, self).get_context_data(**kwargs)
        context['count'] = self.object_list.count()
        context = adjust_pagination(context)
        return context

    def get_queryset(self):
        search_term = self.kwargs['id']
        if search_term:
            postresult = Gene.objects.filter(Q(species__ncbi_id=search_term))
            result = postresult
        else:
            result = None
        return result


def adjust_pagination(context):
    adjacent_pages = 2
    page_number = context['page_obj'].number
    num_pages = context['paginator'].num_pages
    start_page = max(page_number - adjacent_pages, 1)
    if start_page <= 3:
        start_page = 1
    end_page = page_number + adjacent_pages + 1
    if end_page >= num_pages - 1:
        end_page = num_pages + 1
    page_numbers = [n for n in xrange(start_page, end_page) \
            if n > 0 and n <= num_pages]
    context.update({
        'page_numbers': page_numbers,
        'show_first': 1 not in page_numbers,
        'show_last': num_pages not in page_numbers,
        })
    return context
