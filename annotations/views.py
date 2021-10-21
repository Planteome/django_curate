from django.utils import timezone

from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView, ListView
from django.views.generic.edit import UpdateView

# models import
from urllib3.connectionpool import xrange

from .models import Annotation, AnnotationDocument, AnnotationApproval
from taxon.models import Taxon
from dbxrefs.models import DBXref

# forms import
from .forms import AnnotationImportDocumentForm, AnnotationAddForm

# choices import
import curate.choices as choices

# tasks import
from .tasks import process_annotations_task

# itertools import
from itertools import tee


# Create your views here.
class BaseAnnotationView(TemplateView):
    model = Annotation
    template_name = 'annotations/base_annotation.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(BaseAnnotationView, self).get_context_data()
        # get the last 10 annotations in reverse order
        annotation_list = Annotation.objects.all().order_by('-id')[:10:-1]
        context['latest_annotations'] = annotation_list

        return context


class AnnotationImportView(FormView):
    model = Annotation
    template_name = 'annotations/import_annotations.html'
    form_class = AnnotationImportDocumentForm

    def get_context_data(self, **kwargs):
        context = super(AnnotationImportView, self).get_context_data(**kwargs)
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
        form = AnnotationImportDocumentForm(request.POST, request.FILES)
        user = self.request.user

        if form.is_valid():
            file = AnnotationDocument(document=request.FILES['document'])
            file.save()
            # Pass the new uploaded file to the task to be processed
            annotations_lst = process_annotations_task.delay(file.document.name, user.pk)
            return render(self.request, 'annotations/display_progress.html',
                          context={'task_id': annotations_lst.task_id})


class AnnotationView(TemplateView):
    model = Annotation
    template_name = 'annotations/annotation.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(AnnotationView, self).get_context_data(**kwargs)
        annotation = Annotation.objects.get(pk=self.kwargs['pk'])
        context['annotation'] = annotation
        user = self.request.user
        if not user.is_authenticated:
            context['logged_in'] = False
            return context

        context['logged_in'] = True
        if user.is_superuser:
            context['superuser'] = True
        else:
            context['superuser'] = False

        # get the dbxref so it can be used to generate external link
        context['dbxref'] = DBXref.objects.get(dbname=annotation.db)
        # get the reverse evidence code dict and pass the short code to the template
        ev_code_dict = {e.value: e.name for e in choices.EvidenceCode}
        context['ev_code_short'] = ev_code_dict[annotation.evidence_code]
        # get the with_from URL
        with_from_db = annotation.with_from.split(':')[0]
        return context


class AnnotationEditView(UpdateView):
    model = Annotation
    template_name = 'annotations/annotation_edit.html'

    fields = [
        "db",
        "db_obj_id",
        "db_obj_symbol",
        "qualifier",
        "ontology_id",
        "db_reference",
        "evidence_code",
        "with_from",
        "aspect",
        "db_obj_name",
        "db_obj_synonym",
        "db_obj_type",
        "assigned_by",
        "annotation_extension",
        "gene_product_form_id",
        # "internal_gene", TODO: fix this so it doesn't take minutes to return because it is trying to add "every" gene to the select box in the form
    ]

    success_url = reverse_lazy('annotations:import_success')

    def get_context_data(self, **kwargs):
        context = super(AnnotationEditView, self).get_context_data(**kwargs)
        annotation = Annotation.objects.get(pk=self.kwargs['pk'])
        context['annotation'] = annotation
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
        # update status and requestor fields
        status = choices.ApprovalStates.PENDING
        requestor = self.request.user
        curr_time = timezone.now()

        # get the comments from the form
        comments = request.POST.get('comments')

        existing_annotation = get_object_or_404(Annotation, pk=self.kwargs['pk'])

        # if user is superuser, skip approval
        if requestor.is_superuser:
            changed = False
            if request.POST.get('db') != existing_annotation.db:
                existing_annotation.db.id = request.POST.get('db')
                changed = True
            if request.POST.get('db_obj_id') != existing_annotation.db_obj_id:
                existing_annotation.db_obj_id = request.POST.get('db_obj_id')
                changed = True
            if request.POST.get('db_obj_symbol') != existing_annotation.db_obj_symbol:
                existing_annotation.db_obj_symbol = request.POST.get('db_obj_symbol')
                changed = True
            if request.POST.get('qualifier') != existing_annotation.qualifier:
                existing_annotation.qualifier = request.POST.get('qualifier')
                changed = True
            if request.POST.get('ontology_id') != existing_annotation.ontology_id:
                existing_annotation.ontology_id = request.POST.get('ontology_id')
                changed = True
            if request.POST.get('db_reference') != existing_annotation.db_reference:
                existing_annotation.db_reference = request.POST.get('db_reference')
                changed = True
            if request.POST.get('evidence_code') != existing_annotation.evidence_code:
                existing_annotation.evidence_code = request.POST.get('evidence_code')
                changed = True
            if request.POST.get('with_from') != existing_annotation.with_from:
                existing_annotation.with_from = request.POST.get('with_from')
                changed = True
            if request.POST.get('aspect') != existing_annotation.aspect:
                existing_annotation.aspect = request.POST.get('aspect')
                changed = True
            if request.POST.get('db_obj_name') != existing_annotation.db_obj_name:
                existing_annotation.db_obj_name = request.POST.get('db_obj_name')
                changed = True
            if request.POST.get('db_obj_synonym') != existing_annotation.db_obj_synonym:
                existing_annotation.db_obj_synonym = request.POST.get('db_obj_synonym')
                changed = True
            if request.POST.get('db_obj_type') != existing_annotation.db_obj_type:
                existing_annotation.db_obj_type = request.POST.get('db_obj_type')
                changed = True
            if request.POST.get('assigned_by') != existing_annotation.assigned_by:
                existing_annotation.assigned_by = request.POST.get('assigned_by')
                changed = True
            if request.POST.get('annotation_extension') != existing_annotation.annotation_extension:
                existing_annotation.annotation_extension = request.POST.get('annotation_extension')
                changed = True
            if request.POST.get('gene_product_form_id') != existing_annotation.gene_product_form_id:
                existing_annotation.gene_product_form_id = request.POST.get('gene_product_form_id')
                changed = True
            # TODO: uncomment this section of internal_gene is fixed above
            # if request.POST.get('internal_gene') != existing_annotation.internal_gene:
            #    existing_annotation.internal_gene = request.POST.get('internal_gene')
            #    changed = True

            if changed:
                existing_annotation.save()
                return render(self.request, 'annotations/annotation_import_success.html')
            else:
                return HttpResponse("No changes to annotation were found")

        else:
            # initialize the changed gene to the same as the existing
            changed_annotation = AnnotationApproval()
            for field in existing_annotation._meta.fields:
                setattr(changed_annotation, field.name, getattr(existing_annotation, field.name))
            # Change the values
            changed_annotation.pk = None  # will get the next pk available
            changed_annotation.db.id = request.POST.get('db')
            changed_annotation.db_obj_id = request.POST.get('db_obj_id')
            changed_annotation.db_obj_symbol = request.POST.get('db_obj_symbol')
            changed_annotation.qualifier = request.POST.get('qualifier')
            changed_annotation.ontology_id = request.POST.get('ontology_id')
            changed_annotation.db_reference = request.POST.get('db_reference')
            changed_annotation.evidence_code = request.POST.get('evidence_code')
            changed_annotation.with_from = request.POST.get('with_from')
            changed_annotation.aspect = request.POST.get('aspect')
            changed_annotation.db_obj_name = request.POST.get('db_obj_name')
            changed_annotation.db_obj_synonym = request.POST.get('db_obj_synonym')
            changed_annotation.db_obj_type = request.POST.get('db_obj_type')
            changed_annotation.assigned_by = request.POST.get('assigned_by')
            changed_annotation.annotation_extension = request.POST.get('annotation_extension')
            changed_annotation.gene_product_form_id = request.POST.get('gene_product_form_id')
            # changed_annotation.internal_gene = request.POST.get('internal_gene')

            # add new values
            changed_annotation.status = status
            changed_annotation.action = choices.ApprovalActions.INITIAL
            changed_annotation.requestor = requestor
            changed_annotation.datetime = curr_time
            changed_annotation.comments = comments
            changed_annotation.source_annotation = existing_annotation

            # save it to the db as a GeneApproval model
            changed_annotation.save()
            # go to the request submitted page
            return render(self.request, 'annotations/annotation_request.html')


class AnnotationAddView(FormView):
    form_class = AnnotationAddForm
    model = Annotation
    template_name = 'annotations/annotation_add.html'
    success_url = reverse_lazy('annotations:import_success')

    def get(self, request):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(AnnotationAddView, self).get_context_data(**kwargs)
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
        form = AnnotationAddForm(request.POST)
        if form.is_valid():
            db_obj_symbol = form.cleaned_data['db_obj_symbol']

            return HttpResponseRedirect('/annotations/annotation_import_success/')
        else:
            return self.render_to_response(self.get_context_data())


class ApprovalView(ListView):
    model = AnnotationApproval
    # Both the added and changed approval use the same template
    template_name = 'annotations/annotation_approval.html'
    context_object_name = 'annotations'
    paginate_by = 25

    def get_queryset(self):
        queryset = AnnotationApproval.objects.filter(Q(status=choices.ApprovalStates.PENDING))
        return queryset

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        # Need to set the context object_list to the query so that pagination works
        self.object_list = super().get_queryset().order_by('datetime')
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

        return context

    def post(self, request, *args, **kwargs):
        # list of new annotations to approve
        approve_list = request.POST.getlist('approvalChkbox')
        for approved_annotation_id in approve_list:
            # add the gene to the database
            approved_annotation = AnnotationApproval.objects.get(pk=approved_annotation_id)
            if approved_annotation.source_annotation:
                #update existing annotation
                org_annotation = Annotation.objects.get(pk=approved_annotation.source_annotation_id)
                org_annotation.db = approved_annotation.db
                org_annotation.db_obj_id = approved_annotation.db_obj_id
                org_annotation.db_obj_symbol = approved_annotation.db_obj_symbol
                org_annotation.qualifier = approved_annotation.qualifier
                org_annotation.ontology_id = approved_annotation.ontology_id
                org_annotation.db_reference = approved_annotation.db_reference
                org_annotation.evidence_code = approved_annotation.evidence_code
                org_annotation.with_from = approved_annotation.with_from
                org_annotation.aspect = approved_annotation.aspect
                org_annotation.db_obj_name = approved_annotation.db_obj_name
                org_annotation.db_obj_synonym = approved_annotation.db_obj_synonym
                org_annotation.db_obj_type = approved_annotation.db_obj_type
                org_annotation.assigned_by = approved_annotation.assigned_by
                org_annotation.annotation_extension = approved_annotation.annotation_extension
                org_annotation.gene_product_form_id = approved_annotation.gene_product_form_id

                # update the changed_by field in the model
                org_annotation.changed_by = approved_annotation.requestor

                # add the updated date
                org_annotation.date = timezone.now().date()

                # change the AnnotationApproval model
                approved_annotation.action = choices.ApprovalActions.APPROVE
                approved_annotation.status = choices.ApprovalStates.APPROVED

                # Go ahead and save
                org_annotation.save()
                approved_annotation.save()

            else:
                # new annotation
                Annotation.objects.create(db=approved_annotation.db,
                                          db_obj_id=approved_annotation.db_obj_id,
                                          db_obj_symbol=approved_annotation.db_obj_symbol,
                                          qualifier=approved_annotation.qualifier,
                                          ontology_id=approved_annotation.ontology_id,
                                          db_reference=approved_annotation.db_reference,
                                          evidence_code=approved_annotation.evidence_code,
                                          with_from=approved_annotation.with_from,
                                          aspect=approved_annotation.aspect,
                                          db_obj_name=approved_annotation.db_obj_name,
                                          db_obj_synonym=approved_annotation.db_obj_synonym,
                                          db_obj_type=approved_annotation.db_obj_type,
                                          taxon=approved_annotation.taxon,
                                          date=approved_annotation.datetime.date(),
                                          assigned_by=approved_annotation.assigned_by,
                                          gene_product_form_id=approved_annotation.gene_product_form_id,
                                          changed_by=approved_annotation.requestor,
                                          )
                # change the AnnotationApproval model
                approved_annotation.action = choices.ApprovalActions.APPROVE
                approved_annotation.status = choices.ApprovalStates.APPROVED

                # Go ahead and save
                approved_annotation.save()

        # rejections
        reject_list = request.POST.getlist('rejectChkbox')
        for reject_annotation_id in reject_list:
            reject_annotation = AnnotationApproval.objects.get(pk=reject_annotation_id)
            # Only have to change the AnnotationApproval model status
            reject_annotation.action = choices.ApprovalActions.REJECT
            reject_annotation.status = choices.ApprovalStates.REJECTED
            reject_annotation.save()

        # Ones to request more info from requestor
        request_info_list = request.POST.getlist('requestInfoChkbox')
        for request_annotation_id in request_info_list:
            request_annotation = AnnotationApproval.objects.get(pk=request_annotation_id)
            request_annotation.action = choices.ApprovalActions.MORE_INFO
            # add a comment to the comment box so we know this has been requested for more info
            #  if it hasn't already
            if "More info requested" not in request_annotation.comments:
                request_annotation.comments = request_annotation.comments + "\nMore info requested"
            # TODO: add email or something to communicate with requestor
            request_annotation.save()

        return render(self.request, 'annotations/annotation_import_success.html')


class AnnotationChangeView(TemplateView):
    model = Annotation
    template_name = 'annotations/changes.html'

    def pair_iterable_for_delta_changes(self, iterable):
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(AnnotationChangeView, self).get_context_data(**kwargs)
        annotation_id = self.kwargs['pk']
        # get the gene
        annotation = Annotation.objects.get(pk=annotation_id)
        context['annotation'] = annotation
        # get the gene history
        annotation_iterator = annotation.history.all().order_by('history_date').iterator()
        delta_list = []
        delta_number = 1
        for record_pair in self.pair_iterable_for_delta_changes(annotation_iterator):
            old_record, new_record = record_pair
            delta = new_record.diff_against(old_record)
            delta.history_date = new_record.history_date
            delta.changed_by = new_record.changed_by
            delta.number = delta_number
            delta_number += 1
            delta_list.append(delta)

        context['delta_list'] = delta_list

        return context


class SearchView(ListView):
    model = Annotation
    template_name = 'annotations/search.html'
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
        search_term = self.request.GET.get('search')
        if search_term:
            postresult = Annotation.objects.filter(Q(db_obj_id__icontains=search_term) |
                                                   Q(db_obj_symbol__icontains=search_term) |
                                                   Q(db_obj_name__icontains=search_term) |
                                                   Q(db_obj_synonym__icontains=search_term))
            result = postresult
        else:
            result = None
        return result


class SearchByReferenceView(ListView):
    model = Annotation
    template_name = 'annotations/search.html'
    context_object_name = 'all_search_results'
    paginate_by = 25

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        # Need to set the context object_list to the query so that pagination works
        self.object_list = self.get_queryset().order_by('pk')[:10000]
        context = super(SearchByReferenceView, self).get_context_data(**kwargs)
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
        search_term = self.kwargs['id']
        if search_term:
            postresult = Annotation.objects.filter(Q(db_reference__icontains=search_term))
            result = postresult
        else:
            result = None
        return result
