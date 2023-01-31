import datetime
import time
from itertools import islice

from celery import shared_task
from celery_progress.backend import ProgressRecorder

# pandas import
import pandas

# Models imports
from .models import Gene, GeneDocument, MissingGenesFromAliasesImport
from taxon.models import Taxon

# Elasticsearch imports
from .documents import GeneDocument as ESGeneDocument

# regex import
import re

# json import
import json

#####
# NOTE!!!!
# Celery will have to be restarted if any changes are made to the tasks below


# Decorator to tell celery this is a worker task
@shared_task(bind=True)
def process_genes_task(self, file_id, species_pk, user_id):
    progress_recorder = ProgressRecorder(self)
    # All genes
    genes_lst = []
    file = GeneDocument.objects.get(document=file_id).document
    species = Taxon.objects.get(pk=species_pk)
    genes = pandas.read_csv(file, sep='\t', na_filter=False)
    total_genes_to_save = len(genes)
    chrLine = genes.columns.str.startswith('Chromosome')
    symbolLine = genes.columns.str.contains('Gene name|Symbol')
    for index, line in genes.iterrows():
        gene_id = line['Gene stable ID']
        gene_chr = line[chrLine][0]
        gene_start = line['Gene start (bp)']
        gene_end = line['Gene end (bp)']
        gene_symbol = line[symbolLine][0]
        gene_type = line['Gene type']
        gene_desc = line['Gene description']

        gene_location = "Chromosome " + str(gene_chr) + ": " + str(gene_start) + " - " + str(gene_end)

        genes_lst.append(Gene(symbol=gene_symbol, gene_id=gene_id, gene_type=gene_type, species=species,
                              location=gene_location, description=gene_desc, changed_by_id=user_id))
        progress_recorder.set_progress(index, total_genes_to_save, description="Processing genes from file")

    # Get the latest DB id so that we know how many to update in Elasticsearch
    gene_last_id = Gene.objects.last().id
    # Now put them in the database
    # batch load them if there are many
    batch_size = 1000
    if total_genes_to_save > batch_size:
        batch = [genes_lst[i * batch_size:(i + 1) * batch_size] for i in range((len(genes_lst) + batch_size - 1) // batch_size)]
        for index in range(len(batch)):
            progress_recorder.set_progress(index * batch_size, total_genes_to_save, description="Putting genes in database")
            Gene.objects.bulk_create(batch[index])
    else:
        Gene.objects.bulk_create(genes_lst)

    # bulk_create doesn't trigger the Elasticsearch indexing, so do it manually
    # as described at https://github.com/django-es/django-elasticsearch-dsl/issues/32#issuecomment-736046572
    # except that mysql doesn't return DB ids like postgres, so have to build list manually
    new_gene_last_id = Gene.objects.last().id
    genes_id = [num for num in range(gene_last_id, new_gene_last_id)]
    new_genes_qs = Gene.objects.filter(id__in=genes_id)
    ESGeneDocument().update(new_genes_qs)

# aliases task
@shared_task(bind=True)
def process_aliases_task(self, file_id, species_pk):
    progress_recorder = ProgressRecorder(self)
    # All genes
    file = GeneDocument.objects.get(document=file_id).document
    species = Taxon.objects.get(pk=species_pk)
    genes = Gene.objects.all().filter(species=species).values('gene_id', 'synonyms', 'pk')
    genes_dict = {gene['gene_id']: {'synonyms': gene['synonyms'], 'pk': gene['pk']} for gene in genes}
    # dict for all the new alias info
    aliases_dict = {}
    # dict of a list for the current synonyms
    curr_synonym_lst = {}
    aliases = pandas.read_csv(file, sep='\t', na_filter=False)
    total_aliases_to_save = len(aliases)
    aliases_without_match = 0
    missing_gene_dict = {}
    for index, line in aliases.iterrows():
        gene_id = line['Gene stable ID']
        symbol = line['Gene Synonym']
        full_name = line['Gene description']
        # Check to make sure we have a matching gene in db
        if gene_id in genes_dict:
            # Get the current gene if it is already in aliases_lst
            gene_synonyms = aliases_dict.get(gene_id, None)
            synonyms = False
            if gene_id not in curr_synonym_lst:
                # Create an empty list for current gene if there isn't one already
                curr_synonym_lst[gene_id] = []
                # Add any that are already in db
                if genes_dict[gene_id]['synonyms']:
                    # filter is here to remove empty synonym strings
                    curr_synonym_lst[gene_id] = list(filter(None, genes_dict[gene_id]['synonyms'].split('|')))
            # if full_name in aliases file and it isn't already a synonym
            if full_name and full_name not in curr_synonym_lst[gene_id]:
                # check to see if we already got the full name for this gene in this aliases file
                if gene_synonyms and re.search(full_name, gene_synonyms):
                    pass
                else:
                    curr_synonym_lst[gene_id].append(full_name)
            if symbol not in curr_synonym_lst[gene_id]:
                if gene_synonyms and re.search(symbol, gene_synonyms):
                    pass
                else:
                    curr_synonym_lst[gene_id].append(symbol)
        else:
            aliases_without_match += 1
            if gene_id not in missing_gene_dict:
                missing_gene_dict[gene_id] = gene_id
        progress_recorder.set_progress(index, total_aliases_to_save, description="Processing aliases from file")
    # Now put them in aliases_dict separated by "|"
    for gene_id in curr_synonym_lst:
        aliases_dict[gene_id] = "|".join(curr_synonym_lst[gene_id])
    # put them in list format
    aliases_lst = []
    # keep a list of the gene_ids to update
    aliases_gene_id_lst = []
    for k, v in aliases_dict.items():
        aliases_lst.append(Gene(pk=genes_dict[k]['pk'], gene_id=k, synonyms=v))
        aliases_gene_id_lst.append(k)
    # Now put them in the database
    # batch load them if there are many
    batch_size = 1000
    if total_aliases_to_save > batch_size:
        batch = [aliases_lst[i * batch_size:(i + 1) * batch_size] for i in
                 range((len(aliases_lst) + batch_size - 1) // batch_size)]
        for index in range(len(batch)):
            progress_recorder.set_progress(index * batch_size, total_aliases_to_save,
                                           description="Putting aliases in database. There were " + str(aliases_without_match) + " aliases that didn't have a match in database.")
            Gene.objects.bulk_update(batch[index], ['synonyms'])
    else:
        Gene.objects.bulk_update(aliases_lst, ['synonyms'])

    # put the missing genes in the model to display on success page
    missing_gene_model = MissingGenesFromAliasesImport()
    missing_gene_list = list(missing_gene_dict.values())
    missing_gene_model.missingGeneList = json.dumps(missing_gene_list)
    missing_gene_model.datetime = datetime.datetime.now()
    missing_gene_model.aliasCount = aliases_without_match
    missing_gene_model.save()

    # Use the list of updated gene_ids to repopulate the Elasticsearch index
    new_genes_qs = Gene.objects.filter(id__in=aliases_gene_id_lst)
    ESGeneDocument().update(new_genes_qs)


# testing task
@shared_task(bind=True)
def test_task(self, seconds):
    progress_recorder = ProgressRecorder(self)
    result = 0
    for i in range(seconds):
        time.sleep(1)
        result += 1
        progress_recorder.set_progress(i+1, seconds)
    return result
