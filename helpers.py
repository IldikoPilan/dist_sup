import codecs
import csv

global ent_categories
ent_categories=['ABBREV','ANAT_LOC','CONDITION','DISCIPLINE', 'MICROORGANISM','ORGANIZATION',
                'OTHER','PERSON', 'PHYSIOLOGY', 'PROCEDURE', 'SUBSTANCE', 'TOOL']

def load_terms(terms_f, 
               categories=ent_categories,
               resources=['MO', 'PROC', 'ICD', 'FAM_HIST', 'FEST', 'ICPC', 'LABV', 'ALOC'],
               exclude_auto=False):
    """
    Loads NorMedTerm as list of (term, entity_cat) tuples.
    Orders terms in decreasing order of length (based on nr. of characters).
    @ terms_f:      str;  path to NorMedTerm
    @ categories:   list; entity categories to use
    @ resources:    list; resource IDs from which to include entries
    @ exclude_auto: bool; whether to exclude automatically mapped entries
    """
    selected = []
    with codecs.open(terms_f, 'r') as f:
        csv_reader = csv.reader(f, delimiter='\t', quotechar='"')
        mapped_terms = list(csv_reader)
        for row in mapped_terms:
            term, category, resource, icd_code, method = row
            if category in categories and resource in resources and \
              (method in ['manual', 'N/A'] or not exclude_auto):
                selected.append((term, category)) 
    ordered_list = sorted(selected, key=lambda x: len(x[0]), reverse=True) 
    return ordered_list 

def normalize_tkns(lines, tkn_col, lower):
    tokens = []
    for line in lines: 
        if not line.startswith('#') and line != '\n':
            if lower:
                token = line.strip().split("\t")[tkn_col].lower()
            else:
                token = line.strip().split("\t")[tkn_col]
            if not token[-1].isalnum():
                tokens.append(token[:-1])
            else:
                tokens.append(token)
    return tokens

def print_table(header, rows, style='-'):
    pad_size = len(header)+2
    print(style*pad_size)
    print(header)
    print(style*pad_size)
    for row in rows:
        print(row)
    print(style*pad_size+'\n')
