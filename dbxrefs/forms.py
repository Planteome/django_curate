from django import forms

# models import
from .models import DBXref, DBXrefDocument


class DBXrefImportDocumentForm(forms.ModelForm):
    document = forms.FileField(label="Database xrefs (external references) file")
    class Meta:
        model = DBXrefDocument
        fields = ('document',)


class DBXrefAddForm(forms.ModelForm):
    class Meta:
        model = DBXref
        fields = '__all__'


class DBXrefEditForm(forms.ModelForm):
    class Meta:
        model = DBXref
        fields = '__all__'