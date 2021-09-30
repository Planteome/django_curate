from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from django.views.generic.edit import UpdateView

# models import
from .models import DBXref, DBXrefDocument

# forms import
from .forms import DBXrefImportDocumentForm, DBXrefAddForm, DBXrefEditForm

# pandas import
import pandas

# yaml import
from yaml import safe_load


# Create your views here.
class BaseDBXrefView(TemplateView):
    model = DBXref
    template_name = 'dbxrefs/base_dbxref.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(BaseDBXrefView, self).get_context_data(**kwargs)
        dbxrefs = DBXref.objects.all()
        context['dbxrefs'] = dbxrefs
        return context


class DBXrefView(TemplateView):
    model = DBXref
    template_name = 'dbxrefs/dbxref.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(DBXrefView, self).get_context_data(**kwargs)
        dbxref = DBXref.objects.get(pk=self.kwargs['pk'])
        context['dbxref'] = dbxref
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


class DBXrefImportView(FormView):
    model = DBXref
    template_name = 'dbxrefs/import_dbxref.html'
    form_class = DBXrefImportDocumentForm

    def get_context_data(self, **kwargs):
        context = super(DBXrefImportView, self).get_context_data(**kwargs)
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
        form = DBXrefImportDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            file = DBXrefDocument(document=request.FILES['document'])
            file.save()
            self.handle_uploaded_dbxrefs(file)
            return HttpResponseRedirect('/dbxref/import_success/')

    def handle_uploaded_dbxrefs(self, file):
        # All dbxrefs
        dbxrefs_lst = []

        # process into a pandas dataframe, replace 'Nan' with empty string
        dbxrefs = pandas.json_normalize(safe_load(file.document)).fillna('')

        for index, line in dbxrefs.iterrows():
            database = line['database']
            fullname = line['name']
            genericURL = line['generic_urls'][0]
            if line['entity_types']:
                if 'example_id' in line['entity_types'][0]:
                    exampleID = line['entity_types'][0]['example_id']
                else:
                    exampleID = None
                if 'url_syntax' in line['entity_types'][0]:
                    xrefURL = line['entity_types'][0]['url_syntax']
                else:
                    # if no xrefURL defined, use the genericURL
                    xrefURL = genericURL
            else:
                exampleID = None
                xrefURL = genericURL
            if line['synonyms']:
                synonyms = line['synonyms']
            else:
                synonyms = None

            dbxrefs_lst.append(DBXref(dbname=database, fullname=fullname, genericURL=genericURL,
                                      exampleID=exampleID, xrefURL=xrefURL, synonyms=synonyms))
        # Now load them into the db
        DBXref.objects.bulk_create(dbxrefs_lst)

class DBXrefEditView(UpdateView):
    model = DBXref
    template_name = 'dbxrefs/edit_dbxref.html'
    fields = [
        "dbname",
        "fullname",
        "genericURL",
        "exampleID",
        "xrefURL"
    ]
    success_url = reverse_lazy('dbxrefs:import_success')

    def get_context_data(self, **kwargs):
        context = super(DBXrefEditView, self).get_context_data(**kwargs)
        dbxref = DBXref.objects.get(pk=self.kwargs['pk'])
        context['dbxref'] = dbxref
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


class DBXrefAddView(FormView):
    form_class = DBXrefAddForm
    model = DBXref
    template_name = 'dbxref/add_dbxref.html'
    success_url = reverse_lazy('dbxrefs:import_success')

    def get(self, request):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(DBXrefAddView, self).get_context_data(**kwargs)
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
        form = DBXrefAddForm(request.POST)
        if form.is_valid():
            dbname = form.cleaned_data['dbname']
            fullname = form.cleaned_data['fullname']
            genericURL = form.cleaned_data['genericURL']
            exampleID = form.cleaned_data['exampleID']
            xrefURL = form.cleaned_data['xrefURL']
            DBXref.objects.create(dbname=dbname, fullname=fullname, genericURL=genericURL,
                                  exampleID=exampleID, xrefURL=xrefURL)

            return HttpResponseRedirect('/dbxrefs/import_success/')
        else:
            return self.render_to_response(self.get_context_data())
