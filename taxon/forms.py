from django import forms

from .models import TaxonomyDocument, Taxon


class TaxonomyImportDocumentForm(forms.ModelForm):
    class Meta:
        model = TaxonomyDocument
        fields = ('document', )


class TaxonomyAddForm(forms.ModelForm):
    class Meta:
        model = Taxon
        fields = '__all__'
