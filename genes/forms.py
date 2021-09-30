from django import forms
from django.db.models import Q

# models import
from .models import Gene, GeneDocument, GeneApproval
from taxon.models import Taxon


class GeneImportDocumentForm(forms.ModelForm):
    document = forms.FileField(label="Species gene file")
    class Meta:
        model = GeneDocument
        fields = ('document', 'species')


class GeneAddForm(forms.ModelForm):
    class Meta:
        model = Gene
        fields = '__all__'

    # Limit the species choices to species and subspecies, and order them alphabetically
    species = forms.ModelChoiceField(
        queryset=Taxon.objects.order_by('name').filter(rank__contains='species'))

    #Limit the gene_type field to only ones that already exist in db
    # get the distinct attributes from one column
    entries = Gene.objects.values_list('gene_type', 'gene_type').distinct()
    # change the entries to a valid format for choice field
    gene_type_choices = [e for e in entries]
    gene_type = forms.ChoiceField(
        choices=gene_type_choices)


class GeneEditForm(forms.ModelForm):
    class Meta:
        model = GeneApproval
        fields = '__all__'
