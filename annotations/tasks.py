import time
from itertools import islice

from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

from celery import shared_task
from celery_progress.backend import ProgressRecorder

# pandas import
import pandas

# Models imports
from .models import Annotation, AnnotationDocument
from taxon.models import Taxon
from dbxrefs.models import DBXref
from genes.models import Gene

# Elasticsearch imports
from .documents import AnnotationDocument as ESAnnotationDocument

# choice import
import curate.choices as choices

# datetime import
from datetime import datetime

# regex import
import re

#####
# NOTE!!!!
# Celery will have to be restarted if any changes are made to the tasks below


# Decorator to tell celery this is a worker task
@shared_task(bind=True)
def process_annotations_task(self, file_id, user_id):
    progress_recorder = ProgressRecorder(self)
    # All annotations
    annotations_lst = []
    file = AnnotationDocument.objects.get(document=file_id).document
    annotations = pandas.read_csv(file, sep='\t', na_filter=False, comment='!', header=None)
    total_annotations_to_save = len(annotations)

    # some of these need to be fixed for foreign keys
    # specifically, db, taxon, and internal_gene as foreign keys
    # and evidence_code, aspect, and db_obj_type as choice from curate.choices
    # date needs to be converted to a python datetime object
    # For the foreign keys, get them in a query first to be more efficient

    # list of unique db and taxon from file
    db_lst = annotations[0].drop_duplicates().tolist()
    taxon_lst = annotations[12].drop_duplicates().tolist()
    # remove the "[Tt]axon:" from the taxon_lst so it is just the number left
    taxon_lst = [int(temp_taxon.replace('T', 't').replace('taxon:', '')) for temp_taxon in taxon_lst]

    # Get the objects from the dbs and put in dict
    db_dict = {}
    for db in db_lst:
        db_dict[db] = DBXref.objects.get(Q(synonyms__icontains=db) | Q(dbname=db))
    taxon_dict = Taxon.objects.in_bulk(taxon_lst, field_name='ncbi_id')

    # finding the internal_gene is a bit tricky, as it can be from db_obj_id, symbol, name, or synonym
    # put them all in a list and look up all of them at once
    gene_id_lst = annotations[1].drop_duplicates().tolist()
    gene_id_lst.extend(annotations[2].drop_duplicates().tolist())
    gene_id_lst.extend(annotations[9].drop_duplicates().tolist())
    # The weird join + split here is because they can have multiple synonyms separated by '|'
    gene_id_lst.extend('|'.join(annotations[10].drop_duplicates().tolist()).split('|'))

    gene_id_objects = Gene.objects.filter(species__in=taxon_lst, gene_id__in=gene_id_lst)
    gene_id_dict = {}
    for gene in gene_id_objects:
        gene_id_dict[gene.gene_id] = gene

    # use the choices fields for the evidence_code, aspect and db_obj_type
    ev_code_dict = {e.name: e.value for e in choices.EvidenceCode}
    aspect_code_dict = {e.name: e.value for e in choices.AspectCode}
    object_type_dict = {e.name: e.value for e in choices.AnnotationObject}

    for index, line in annotations.iterrows():
        db = line[0]
        db_obj_id = line[1]
        db_obj_symbol = line[2]
        qualifier = line[3]
        ontology_id = line[4]
        db_reference = line[5]
        evidence_code = line[6]
        with_from = line[7]
        aspect = line[8]
        db_obj_name = line[9]
        db_obj_synonym = line[10]
        db_obj_type = line[11]
        taxon = int(line[12].replace('T', 't').replace('taxon:', ''))
        date = line[13]
        assigned_by = line[14]
        annotation_extension = line[15]
        gene_product_form_id = line[16]

        # try to find the internal gene
        if db_obj_symbol in gene_id_dict:
            internal_gene = gene_id_dict[db_obj_symbol]
        elif db_obj_id in gene_id_dict:
            internal_gene = gene_id_dict[db_obj_id]
        elif db_obj_name in gene_id_dict:
            internal_gene = gene_id_dict[db_obj_name]
        elif db_obj_synonym in gene_id_dict:
            internal_gene = gene_id_dict[db_obj_synonym]
        else:
            internal_gene = None

        evidence_code = ev_code_dict[evidence_code]
        aspect = aspect_code_dict[aspect]
        #db_obj_type is sometimes empty. Set it to "gene_product" in that case per the gaf 2.0 spec
        # http://geneontology.org/docs/go-annotation-file-gaf-format-2.0/#db-object-type-column-12
        db_obj_type = object_type_dict[db_obj_type] if (db_obj_type) else object_type_dict['gene_product']

        # convert the date to python date
        date = datetime.strptime(str(date), '%Y%m%d').date()

        # add to list of annotations
        annotations_lst.append(Annotation(db=db_dict[db], db_obj_id=db_obj_id, db_obj_symbol=db_obj_symbol,
                                          qualifier=qualifier, ontology_id=ontology_id,
                                          db_reference=db_reference, evidence_code=evidence_code,
                                          with_from=with_from, aspect=aspect, db_obj_name=db_obj_name,
                                          db_obj_synonym=db_obj_synonym, db_obj_type=db_obj_type,
                                          taxon=taxon_dict[taxon], date=date,
                                          assigned_by=assigned_by, annotation_extension=annotation_extension,
                                          gene_product_form_id=gene_product_form_id,
                                          internal_gene=internal_gene, changed_by_id=user_id,))
        progress_recorder.set_progress(index, total_annotations_to_save,
                                       description="Processing annotations from file")
    # Get the latest DB id so that we know how many to update in Elasticsearch
    try:
        annotation_start_id = Annotation.objects.last().id + 1
    except AttributeError:
        annotation_start_id = 1
    # Now put them in the database
    # batch load them if there are many
    batch_size = 1000
    if total_annotations_to_save > batch_size:
        batch = [annotations_lst[i * batch_size:(i + 1) * batch_size] for i in range((len(annotations_lst) + batch_size - 1) // batch_size)]
        for index in range(len(batch)):
            progress_recorder.set_progress(index * batch_size, total_annotations_to_save,
                                           description="Putting Annotations in database")
            Annotation.objects.bulk_create(batch[index])
    else:
        Annotation.objects.bulk_create(annotations_lst)

    # bulk_create doesn't trigger the Elasticsearch indexing, so do it manually
    # as described at https://github.com/django-es/django-elasticsearch-dsl/issues/32#issuecomment-736046572
    # except that mysql doesn't return DB ids like postgres, so have to build list manually
    new_annotation_last_id = Annotation.objects.last().id + 1
    annotations_id = [num for num in range(annotation_start_id, new_annotation_last_id)]
    new_annotations_qs = Annotation.objects.filter(id__in=annotations_id)
    ESAnnotationDocument().update(new_annotations_qs)
