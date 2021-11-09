from django.forms import model_to_dict
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
from itertools import tee, chain


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
        # get the list of db_references and put it in a dict
        db_reference_dict = {}
        db_references = annotation.db_reference.split("|")
        for db_reference in db_references:
            dbname = db_reference.split(':')[0]
            db_reference_dict[db_reference] = DBXref.objects.get(dbname=dbname)
        context['db_references_dict'] = db_reference_dict
        # Get the count of changes that been approved for this annotation
        change_count = AnnotationApproval.objects.filter(source_annotation=annotation, status=choices.ApprovalStates.APPROVED).count()
        if change_count > 0:
            context['change_count'] = change_count
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
        #"assigned_by", this will be set to "Plantome_curate:username
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

        assigned_by = "Planteome_curate:" + requestor.username

        # get the comments from the form
        comments = request.POST.get('comments')

        existing_annotation = get_object_or_404(Annotation, pk=self.kwargs['pk'])


        # initialize the changed annotation to the same as the existing
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
        changed_annotation.assigned_by = assigned_by
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

        # Set it to approved already if the user was a superuser
        # also create it as a new annotation
        if requestor.is_superuser:
            changed_annotation.status = choices.ApprovalStates.APPROVED
            changed_annotation.action = choices.ApprovalActions.APPROVE
            Annotation.objects.create(db=changed_annotation.db,
                                      db_obj_id=changed_annotation.db_obj_id,
                                      db_obj_symbol=changed_annotation.db_obj_symbol,
                                      qualifier=changed_annotation.qualifier,
                                      ontology_id=changed_annotation.ontology_id,
                                      db_reference=changed_annotation.db_reference,
                                      evidence_code=changed_annotation.evidence_code,
                                      with_from=changed_annotation.with_from,
                                      aspect=changed_annotation.aspect,
                                      db_obj_name=changed_annotation.db_obj_name,
                                      db_obj_synonym=changed_annotation.db_obj_synonym,
                                      db_obj_type=changed_annotation.db_obj_type,
                                      taxon=changed_annotation.taxon,
                                      date=curr_time,
                                      assigned_by=changed_annotation.assigned_by,
                                      gene_product_form_id=changed_annotation.gene_product_form_id,
                                      changed_by=requestor,
                                      internal_gene=changed_annotation.internal_gene,
                                      )

        # save it to the db as a AnnotationApproval model
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
        assigned_by = "Planteome_curate:" + self.request.user.username
        if form.is_valid():
            new_annotation = AnnotationApproval()
            new_annotation.datetime = timezone.now()
            new_annotation.comments = form.cleaned_data['comments']
            new_annotation.action = choices.ApprovalActions.INITIAL
            new_annotation.status = choices.ApprovalStates.PENDING
            new_annotation.requestor = self.request.user
            new_annotation.source_annotation = None
            new_annotation.db = form.cleaned_data['db']
            new_annotation.db_obj_id = form.cleaned_data['db_obj_id']
            new_annotation.db_obj_symbol = form.cleaned_data['db_obj_symbol']
            new_annotation.qualifier = form.cleaned_data['qualifier']
            new_annotation.ontology_id = form.cleaned_data['ontology_id']
            new_annotation.db_reference = form.cleaned_data['db_reference']
            new_annotation.evidence_code = form.cleaned_data['evidence_code']
            new_annotation.with_from = form.cleaned_data['with_from']
            new_annotation.db_obj_name = form.cleaned_data['db_obj_name']
            new_annotation.db_obj_synonym = form.cleaned_data['db_obj_synonym']
            new_annotation.taxon = form.cleaned_data['taxon']
            new_annotation.date = timezone.now().date()
            new_annotation.assigned_by = assigned_by
            new_annotation.annotation_extension = form.cleaned_data['annotation_extension']
            new_annotation.gene_product_form_id = form.cleaned_data['gene_product_form_id']
            # TODO: add lookup for internal_gene

            if self.request.user.is_superuser:
                # go ahead and save it as a new annotation
                Annotation.objects.create(db=new_annotation.db,
                                          db_obj_id=new_annotation.db_obj_id,
                                          db_obj_symbol=new_annotation.db_obj_symbol,
                                          qualifier=new_annotation.qualifier,
                                          ontology_id=new_annotation.ontology_id,
                                          db_reference=new_annotation.db_reference,
                                          evidence_code=new_annotation.evidence_code,
                                          with_from=new_annotation.with_from,
                                          aspect=new_annotation.aspect,
                                          db_obj_name=new_annotation.db_obj_name,
                                          db_obj_synonym=new_annotation.db_obj_synonym,
                                          db_obj_type=new_annotation.db_obj_type,
                                          taxon=new_annotation.taxon,
                                          date=new_annotation.date,
                                          assigned_by=new_annotation.assigned_by,
                                          gene_product_form_id=new_annotation.gene_product_form_id,
                                          internal_gene=None,
                                          changed_by=new_annotation.requestor,
                                          )
                # change the AnnotationApproval model
                new_annotation.action = choices.ApprovalActions.APPROVE
                new_annotation.status = choices.ApprovalStates.APPROVED

                # Go ahead and save
                new_annotation.save()
                return HttpResponseRedirect('/annotations/import_success/')
            else:
                new_annotation.save()
                return HttpResponseRedirect('/annotations/request_success/')

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
        self.object_list = self.get_queryset().order_by('datetime')
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

            # Create as a new annotation
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

    def get_queryset(self):
        annotation = Annotation.objects.get(pk=self.kwargs['pk'])
        qs = AnnotationApproval.objects.filter(source_annotation=annotation, status=choices.ApprovalStates.APPROVED)
        return qs

    def get_context_data(self, **kwargs):
        context = super(AnnotationChangeView, self).get_context_data(**kwargs)
        annotation_id = self.kwargs['pk']
        # get the annotation
        annotation = Annotation.objects.get(pk=annotation_id)
        context['annotation'] = annotation
        annotation_queryset = self.get_queryset().order_by('pk')
        # Need to create the iterator with the original annotation at the beginning
        annotation_iterator = chain([annotation], annotation_queryset.iterator())
        delta_list = []
        delta_number = 1
        for record_pair in self.pair_iterable_for_delta_changes(annotation_iterator):
            old_record, new_record = record_pair
            delta = self.compare_annotations(old_record, new_record)
            delta.datetime = new_record.datetime
            delta.changed_by = new_record.requestor
            delta.number = delta_number
            delta_number += 1
            delta_list.append(delta)

        context['delta_list'] = delta_list

        return context

    # New function to compare annotation records
    # Use the HistoricalChanges class from django-simple-history as base to implement
    # from https://github.com/jazzband/django-simple-history/blob/master/simple_history/models.py#L628
    def compare_annotations(self, obj1, obj2):
        excluded_keys = 'id', 'internal_gene', 'changed_by', 'assigned_by', 'date', 'datetime', 'requestor'
        included_fields = {f.name for f in obj1._meta.fields}

        fields = set(included_fields).difference(excluded_keys)

        changes = []
        changed_fields = []

        old_values = model_to_dict(obj1, fields=fields)
        current_values = model_to_dict(obj2, fields=fields)

        for field in fields:
            old_value = old_values[field]
            current_value = current_values[field]

            if old_value != current_value:
                # Manually change the values if the field is one with the choice fields
                # so that they are the human-readable versions
                if field == 'evidence_code':
                    old_value = obj1.get_evidence_code_display
                    current_value = obj2.get_evidence_code_display
                if field == 'aspect':
                    old_value = obj1.get_aspect_display
                    current_value = obj2.get_aspect_display
                if field == 'db_obj_type':
                    old_value = obj1.get_db_obj_type_display
                    current_value = obj2.get_db_obj_type_display

                # get verbose name for field from model
                # TODO: figure out how to stop the auto-capitalization on the verbose_name
                field = AnnotationApproval._meta.get_field(field).verbose_name.title()
                changes.append(self.ModelChange(field, old_value, current_value))
                changed_fields.append(field)

        return self.ModelDelta(changes, changed_fields, obj1, obj2)

    class ModelChange:
        def __init__(self, field_name, old_value, new_value):
            self.field = field_name
            self.old = old_value
            self.new = new_value

    class ModelDelta:
        def __init__(self, changes, changed_fields, old_record, new_record):
            self.changes = changes
            self.changed_fields = changed_fields
            self.old_record = old_record
            self.new_record = new_record


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
        context = adjust_pagination(context)
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
        context = adjust_pagination(context)
        return context

    def get_queryset(self):
        search_term = self.kwargs['id']
        if search_term:
            postresult = Annotation.objects.filter(Q(db_reference__icontains=search_term))
            result = postresult
        else:
            result = None
        return result


class SearchByTaxonView(ListView):
    model = Annotation
    template_name = 'annotations/search.html'
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
            postresult = Annotation.objects.filter(Q(taxon__ncbi_id=search_term))
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
