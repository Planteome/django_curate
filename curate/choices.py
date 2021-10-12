# Global set of choices to use in models
import django.db.models as models

#### NOTE!!!! ####
# Any changes to any of these will require a a 'makemigrations' and 'migrate' to be
#  run to propagate to the db
#################


# approval actions
class ApprovalActions(models.IntegerChoices):
    APPROVE = 1, "Approve"
    REJECT = 2, "Reject"
    MORE_INFO = 3, "More info requested"
    INITIAL = 4, "Initial request, awaiting moderator"


# approval states
class ApprovalStates(models.IntegerChoices):
    PENDING = 1, "Pending"
    APPROVED = 2, "Approved"
    REJECTED = 3, "Rejected"


# evidence codes (for gafs)
# from https://planteome.org/evidence_codes and http://geneontology.org/docs/guide-go-evidence-codes/
class EvidenceCode(models.IntegerChoices):
    IEP = 1, "Inferred from Expression Pattern"
    IDA = 2, "Inferred from Direct Assay"
    IMP = 3, "Inferred from Mutant Phenotype"
    IGI = 4, "Inferred from Genetic Interaction"
    IPI = 5, "Inferred from Physical Interaction"
    IAGP = 6, "Inferred by Association of Genotype from Phenotype"
    IC = 7, "Inferred by Curator"
    IEA = 8, "Inferred from Electronic Annotation"
    ISS = 9, "Inferred from Sequence or structural Similarity"
    NAS = 10, "Non-traceable Author Statement"
    TAS = 11, "Traceable Author Statement"
    ND = 12, "No biological Data available"
    ISM = 13, "Inferred from Sequence Model"
    RCA = 14, "Inferred from Reviewed Computational Analysis"
    EXP = 15, "Inferred from Experiment"
    HTP = 16, "Inferred from High Throughput Experiment"
    HDA = 17, "Inferred from High Throughput Direct Assay"
    HMP = 18, "Inferred from High Throughput Mutant Phenotype"
    HGI = 19, "Inferred from High Throughput Genetic Interaction"
    HEP = 20, "Inferred from High Throughput Expression Pattern"
    IBA = 21, "Inferred from Biological aspect of Ancestor"
    IBD = 22, "Inferred from Biological aspect of Descendant"
    IKR = 23, "Inferred from Key Residues"
    IRD = 24, "Inferred from Rapid Divergence"
    ISO = 25, "Inferred from Sequence Orthology"
    ISA = 26, "Inferred from Sequence Alignment"
    IGC = 27, "Inferred from Genomic Context"


# ontology aspect codes (that we use)
class AspectCode(models.IntegerChoices):
    A = 1, "PO Plant Anatomy"
    G = 2, "PO Plant Growth"
    T = 3, "TO Trait"
    E = 4, "PECO Experimental condition"
    S = 5, "PSO Stress"
    P = 6, "GO Biological Process"
    C = 7, "GO Cellular Component"
    F = 8, "GO Molecular Function"


# annotation object types
class AnnotationObject(models.IntegerChoices):
    protein = 1, "protein"
    germplasm = 2, "germplasm"
    gene_model = 3, "gene model"
    mRNA = 4, "mRNA"
    gene = 5, "gene"
    QTL = 6, "QTL"
    gene_product = 7, "gene product"
    tRNA = 8, "tRNA"
    miRNA = 9, "miRNA"
    RNA = 10, "RNA"
    antisense_lncRNA = 11, "antisense_lncRNA"
    snoRNA = 12, "snoRNA"
    pseudogene = 13, "pseudogene"
    rRNA = 14, "rRNA"
    snRNA = 15, "snRNA"
    lnc_RNA = 16, "lnc_RNA"
    antisense_RNA = 17, "antisense_RNA"
    uORF = 18, "uORF"
