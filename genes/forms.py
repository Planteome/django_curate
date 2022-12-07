from django import forms
from django.db.models import Q

# models import
from .models import Gene, GeneDocument, GeneApproval
from taxon.models import Taxon

# crispy forms import
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field


class GeneImportDocumentForm(forms.ModelForm):
    document = forms.FileField(label="Species gene file")
    class Meta:
        model = GeneDocument
        fields = ('document', 'species')

    # Limit the species choices to species and subspecies, and order them alphabetically
    species = forms.ModelChoiceField(
        queryset=Taxon.objects.order_by('name').filter(rank__contains='species'))


class GeneAddForm(forms.ModelForm):
    class Meta:
        model = Gene
        exclude = ['data_source_name', 'data_source_object_id', 'phenotype']

    # Limit the species choices to species and subspecies, and order them alphabetically
    species = forms.ModelChoiceField(
        queryset=Taxon.objects.order_by('name').filter(rank__contains='species'))

    gene_type = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        super(GeneAddForm, self).__init__(*args, **kwargs)

        #Limit the gene_type field to only ones that already exist in db
        # get the distinct attributes from one column
        self.fields['gene_type'].choices = Gene.objects.values_list('gene_type', 'gene_type').distinct()


class GeneEditForm(forms.ModelForm):
    class Meta:
        model = GeneApproval
        fields = [
            "symbol",
            "name",
            "gene_id",
            "synonyms",
            "summary",
            "location",
            "description",
            "pubmed_id",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['symbol'].widget.attrs = {'rows': 2, 'class': 'col-md-8'}
        self.fields['name'].widget.attrs = {'rows': 2, 'class': 'col-md-8'}
        self.fields['gene_id'].widget.attrs = {'rows': 2, 'class': 'col-md-8', 'readonly': True}
        self.fields['synonyms'].widget.attrs = {'rows': 2, 'class': 'col-md-8'}
        self.fields['summary'].widget.attrs = {'rows': 2, 'class': 'col-md-8'}
        self.fields['description'].widget.attrs = {'rows': 2, 'class': 'col-md-8'}
        self.fields['location'].widget.attrs = {'class': 'col-md-8', 'readonly': True}
        self.fields['pubmed_id'].widget.attrs = {'class': 'col-md-8'}
