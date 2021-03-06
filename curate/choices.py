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
    IEP = 1, "Inferred from Expression Pattern (IEP)"
    IDA = 2, "Inferred from Direct Assay (IDA)"
    IMP = 3, "Inferred from Mutant Phenotype (IMP)"
    IGI = 4, "Inferred from Genetic Interaction (IGI)"
    IPI = 5, "Inferred from Physical Interaction (IPI)"
    IAGP = 6, "Inferred by Association of Genotype from Phenotype (IAGP)"
    IC = 7, "Inferred by Curator (IC)"
    IEA = 8, "Inferred from Electronic Annotation (IEA)"
    ISS = 9, "Inferred from Sequence or structural Similarity (ISS)"
    NAS = 10, "Non-traceable Author Statement (NAS)"
    TAS = 11, "Traceable Author Statement (TAS)"
    ND = 12, "No biological Data available (ND)"
    ISM = 13, "Inferred from Sequence Model (ISM)"
    RCA = 14, "Inferred from Reviewed Computational Analysis (RCA)"
    EXP = 15, "Inferred from Experiment (EXP)"
    HTP = 16, "Inferred from High Throughput Experiment (HTP)"
    HDA = 17, "Inferred from High Throughput Direct Assay (HDA)"
    HMP = 18, "Inferred from High Throughput Mutant Phenotype (HMP)"
    HGI = 19, "Inferred from High Throughput Genetic Interaction (HGI)"
    HEP = 20, "Inferred from High Throughput Expression Pattern (HEP)"
    IBA = 21, "Inferred from Biological aspect of Ancestor (IBA)"
    IBD = 22, "Inferred from Biological aspect of Descendant (IBD)"
    IKR = 23, "Inferred from Key Residues (IKR)"
    IRD = 24, "Inferred from Rapid Divergence (IRD)"
    ISO = 25, "Inferred from Sequence Orthology (ISO)"
    ISA = 26, "Inferred from Sequence Alignment (ISA)"
    IGC = 27, "Inferred from Genomic Context (IGC)"


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
