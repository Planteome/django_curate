import time
from itertools import islice

from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

from celery import shared_task
from celery_progress.backend import ProgressRecorder

# pandas import
import pandas

# settings import
from django.conf import settings

# Models imports
from .models import Annotation, AnnotationDocument, AnnotationOntologyTerm
from taxon.models import Taxon
from dbxrefs.models import DBXref
from genes.models import Gene

# Elasticsearch imports
from .documents import AnnotationDocument as ESAnnotationDocument
from .documents import OntologyTermDocument as ESOntologyTermDocument

# choice import
import curate.choices as choices

# datetime import
from datetime import datetime

#requests import
from requests.packages.urllib3 import Retry
from requests.adapters import HTTPAdapter
import requests


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
    # specifically, db, taxon, and internal_gene, ontology_term as foreign keys
    # and evidence_code, aspect, and db_obj_type as choice from curate.choices
    # date needs to be converted to a python datetime object
    # For the foreign keys, get them in a query first to be more efficient

    # list of unique db and taxon from file
    db_lst = annotations[0].drop_duplicates().tolist()
    taxon_lst = annotations[12].drop_duplicates().tolist()
    # remove the "[Tt]axon:" from the taxon_lst so it is just the number left
    taxon_lst = [int(temp_taxon.replace('T', 't').replace('taxon:', '')) for temp_taxon in taxon_lst]
    # list of unique ontology terms
    ontology_term_lst = annotations[4].drop_duplicates().tolist()

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
        gene_id_dict[gene.gene_id.lower()] = gene

    # get the ontology terms, create them if needed first
    ontology_term_objects = (AnnotationOntologyTerm(onto_term=term) for term in ontology_term_lst)
    AnnotationOntologyTerm.objects.bulk_create(ontology_term_objects, ignore_conflicts=True)
    ontology_term_dict = AnnotationOntologyTerm.objects.in_bulk(ontology_term_lst, field_name='onto_term')
    ontology_term_list = list(ontology_term_dict.keys())
    onto_terms_qs = AnnotationOntologyTerm.objects.filter(onto_term__in=ontology_term_list)
    ESOntologyTermDocument().update(onto_terms_qs)


    # use the choices fields for the evidence_code, aspect and db_obj_type
    ev_code_dict = {e.name: e.value for e in choices.EvidenceCode}
    aspect_code_dict = {e.name: e.value for e in choices.AspectCode}
    object_type_dict = {e.name: e.value for e in choices.AnnotationObject}

    for index, line in annotations.iterrows():
        db = line[0]
        db_obj_id = line[1]
        db_obj_symbol = line[2]
        qualifier = line[3]
        ontology_term = line[4]
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
        if db_obj_symbol.lower() in gene_id_dict:
            internal_gene = gene_id_dict[db_obj_symbol.lower()]
        elif db_obj_id.lower() in gene_id_dict:
            internal_gene = gene_id_dict[db_obj_id.lower()]
        elif db_obj_name.lower() in gene_id_dict:
            internal_gene = gene_id_dict[db_obj_name.lower()]
        elif db_obj_synonym.lower() in gene_id_dict:
            internal_gene = gene_id_dict[db_obj_synonym.lower()]
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
                                          qualifier=qualifier, ontology_term=ontology_term_dict[ontology_term],
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

    # call the shared function to see if any ontology terms need to be updated
    update_ontology_terms(ontology_term_lst, progress_recorder)

    # bulk_create doesn't trigger the Elasticsearch indexing, so do it manually
    # as described at https://github.com/django-es/django-elasticsearch-dsl/issues/32#issuecomment-736046572
    # except that mysql doesn't return DB ids like postgres, so have to build list manually
    new_annotation_last_id = Annotation.objects.last().id + 1
    annotations_id = [num for num in range(annotation_start_id, new_annotation_last_id)]
    if len(annotations_id) > batch_size:
        batch = [annotations_id[i:i + batch_size] for i in range(0, len(annotations_id), batch_size)]
        for index in range(len(batch)):
            progress_recorder.set_progress(index * batch_size, len(annotations_id),
                                           description="Updating ElasticSearch documents")
            new_annotations_qs = Annotation.objects.filter(id__in=batch[index])
            ESAnnotationDocument().update(new_annotations_qs)
    else:
        new_annotations_qs = Annotation.objects.filter(id__in=annotations_id)
        ESAnnotationDocument().update(new_annotations_qs)


# task for updating all ontology terms, use in case of a new release at main site (planteome)
@shared_task(bind=True)
def process_all_ontology_terms_task(self):
    progress_recorder = ProgressRecorder(self)
    # Get all terms in DB
    onto_terms_dict = AnnotationOntologyTerm.objects.in_bulk(field_name='onto_term')

    terms_lst = list(onto_terms_dict.keys())
    terms_to_update = update_ontology_terms(terms_lst, progress_recorder)

    if terms_to_update:
        # Need to manually update the ES documents because they won't be for bulk_update
        # TODO: this works, but is a bit slow. Might need to optimize
        batch_size = 100
        if len(terms_to_update) > batch_size:
            batch = [terms_to_update[i:i + batch_size] for i in range(0, len(terms_to_update), batch_size)]
            for index in range(len(batch)):
                progress_recorder.set_progress(index * batch_size, len(terms_to_update),
                                               description="Updating ElasticSearch documents")
                batch_qs = Annotation.objects.filter(ontology_term_id__in=batch[index])
                ESAnnotationDocument().update(batch_qs)
        else:
            batch_qs = Annotation.objects.filter(ontology_term_id__in=terms_to_update)
            ESAnnotationDocument().update(batch_qs)


# shared function for updating ontology terms to current
def update_ontology_terms(terms_lst, progress_recorder):
    # Get all terms in DB
    onto_terms_dict = AnnotationOntologyTerm.objects.in_bulk(terms_lst, field_name='onto_term')
    # AmiGO uses its own abbreviations that are different for the aspect codes
    amigo_aspect_code_dict = {e.name: e.value for e in choices.AspectCodeAmigo}

    # set the number to get from API at once. There is a limit to how many the API can handle
    batch_size = 50
    # dict to store what the API says
    current_terms = {}
    if len(terms_lst) > batch_size:
        batch = [terms_lst[i:i + batch_size] for i in range(0, len(terms_lst), batch_size)]
        for index in range(len(batch)):
            search_string = settings.AMIGO_BASE_URL + "api/entity/terms?"
            # progress_recorder line here
            progress_recorder.set_progress(index * batch_size, len(terms_lst),
                                           description="Updating ontology terms in database")
            # query the AMiGO API for definitions
            for term in batch[index]:
                search_string += "&entity=" + term
            # use the urllib3/requests to retry in case the API doesn't respond correctly right away
            s = requests.Session()
            https_retries = Retry(connect=3, backoff_factor=2, status_forcelist=[502, 503, 504])
            adapter = HTTPAdapter(max_retries=https_retries)
            s.mount('http://', adapter)
            s.mount('https://', adapter)
            req = s.get(search_string)
            result = req.json()
            for term in result["data"]:
                current_terms[term["id"]] = {'name': term.get('annotation_class_label', ''),
                                             'definition': term.get('description', ''),
                                             'is_obsolete': term.get('is_obsolete', False),
                                             'synonym': term.get('synonym', ''),
                                             'aspect': term.get('source', "not_defined")
                                             }
    else:
        search_string = settings.AMIGO_BASE_URL + "api/entity/terms?"
        for term in terms_lst:
            search_string += "&entity=" + term
        s = requests.Session()
        https_retries = Retry(connect=3, backoff_factor=2, status_forcelist=[502, 503, 504])
        adapter = HTTPAdapter(max_retries=https_retries)
        s.mount('http://', adapter)
        s.mount('https://', adapter)
        req = s.get(search_string)
        result = req.json()
        for term in result["data"]:
            current_terms[term["id"]] = {'name': term.get('annotation_class_label', ''),
                                         'definition': term.get('description', ''),
                                         'is_obsolete': term.get('is_obsolete', False),
                                         'synonym': term.get('synonym', ''),
                                         'aspect': term.get('source', "not_defined")
                                         }

    # compare the terms in local DB and from API to see which ones need to be updated
    terms_to_update = []
    for term in onto_terms_dict:
        local_name = onto_terms_dict[term].term_name
        amigo_name = current_terms[term]['name']
        local_definition = onto_terms_dict[term].term_definition
        amigo_definition = current_terms[term]['definition']
        local_is_obsolete = onto_terms_dict[term].term_is_obsolete
        amigo_is_obsolete = current_terms[term]['is_obsolete']
        local_synonyms = onto_terms_dict[term].term_synonyms
        # Japanese synonyms have characters that won't work in the database, so don't include them
        amigo_synonyms = [x for x in current_terms[term]['synonym'] if "Japanese" not in x]
        # convert the synonyms list to a string
        amigo_synonyms = ', '.join(amigo_synonyms)
        local_aspect = onto_terms_dict[term].aspect
        # Use the amigo_aspect_code_dict to translate to mysql int choice
        amigo_aspect = amigo_aspect_code_dict[current_terms[term]['aspect']]
        # put in list to check all at the same time
        local_term = [local_name, local_definition, local_is_obsolete, local_synonyms, local_aspect]
        amigo_term = [amigo_name, amigo_definition, amigo_is_obsolete, amigo_synonyms, amigo_aspect]
        # if anything is different, update term
        if local_term != amigo_term:
            onto_terms_dict[term].term_name = amigo_name
            onto_terms_dict[term].term_definition = amigo_definition
            onto_terms_dict[term].term_is_obsolete = amigo_is_obsolete
            onto_terms_dict[term].term_synonyms = amigo_synonyms
            onto_terms_dict[term].aspect = amigo_aspect
            terms_to_update.append(onto_terms_dict[term])
    if terms_to_update:
        progress_recorder.set_progress(0,2,description="Updating ontology terms in database")
        AnnotationOntologyTerm.objects.bulk_update(terms_to_update, ['term_name', 'term_definition', 'term_is_obsolete',
                                                                     'term_synonyms', 'aspect'])
        # return the list of changed ids
        terms_ids = [term.id for term in terms_to_update]

        # Update the ES Ontology term documents
        terms_qs = AnnotationOntologyTerm.objects.filter(onto_term__in=terms_ids)
        progress_recorder.set_progress(1,2,description="Updating ontology terms in ElasticSearch")
        ESOntologyTermDocument().update(terms_qs)

        return terms_ids
    else:
        return None
