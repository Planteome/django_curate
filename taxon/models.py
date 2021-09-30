from django.db import models


# Create your models here.
class Taxon(models.Model):
    name = models.CharField(max_length=255)
    rank = models.CharField(max_length=32)
    related_synonyms = models.TextField(max_length=2000, blank=True)
    exact_synonyms = models.TextField(max_length=2000, blank=True)
    ncbi_id = models.PositiveIntegerField(primary_key=True)
    parent = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class TaxonomyDocument(models.Model):
    document = models.FileField(upload_to='taxonomy/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
