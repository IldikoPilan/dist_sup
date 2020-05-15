from collections import Counter
import codecs
import os
from helpers import print_table

def get_general_stats(bio_cnt, entity_name_cnt):
    """
    Computes general statistics: number of entities,
    unique entities, percentage of entity tokens and 
    total nr. of tokens.
    """
    ne_tkns =  bio_cnt['B']+bio_cnt['I']
    ent_perc = ne_tkns/bio_cnt['O']*100
    rows = ['{:<15}{:<5}'.format('# NE', bio_cnt['B']),
            '{:<15}{:<5}'.format('# NE (unique)', len(entity_name_cnt.keys())),
            '{:<15}{:<5} ({:<5.2f}%)'.format('# NE tkns', ne_tkns, ent_perc),
            '{:<15}{:<5}'.format('# All tkns', bio_cnt['B']+bio_cnt['I']+bio_cnt['O'])]
    print_table('{:<15}{:<5}{:<10}'.format('General info', '', ''), rows)

def get_span_stats(len_cnt):
    """
    Computes statistics about span, that is whether entities 
    consist of single or multiple tokens.
    """
    multi_tkn = sum([cnt for ent_len, cnt in len_cnt.items() if int(ent_len) > 1])
    header = '{:<15}{:<5}'.format('NE span', '#')
    rows = ['{:<15}{:<5}'.format('Single-tkn', len_cnt['1']),
            '{:<15}{:<5}'.format('Multi-tkn', multi_tkn)]  
    print_table(header, rows) 

def get_cat_stats(bio_cnt, entity_cnt):
    """ Computes statistics about the entity category 
    distribution in the data.
    """
    header = '{:<13}{}'.format('NE category','#')
    rows = []
    for ent, cnt in entity_cnt.items():
        rows.append('{:<13}{}'.format(ent, cnt))
    pad_size = len(header)+2
    rows.append('-'*pad_size)
    rows.append('{:<13}{}'.format('All', bio_cnt['B']))
    print_table(header, rows)

def get_common_ne(entity_name_cnt, lower):
    """ Prints the 20 most common tagged entities. 
    """
    header = '{:<5}{:<6}{:<30}{}'.format('Rank', 'Count', 'Entity', 'Category')
    rows = []
    for ix, (ent_name, cnt) in enumerate(entity_name_cnt.most_common(20)):
        rows.append('{:<5}{:<6}{:<30}{}'.format(ix+1, cnt, ent_name[0], ent_name[1]))
    print_table(header, rows)

def get_stats(data_dir, tkn_col, lower):
    """
    Reads tagged files and calculates different types of statistics 
    over named entities (NE): general information, span, entity category
    distrubution and most common entities.  
    """
    entity_cnt = Counter()
    bio_cnt = Counter()
    len_cnt = Counter()
    entity_name_cnt = Counter()
    for filename in os.listdir(data_dir):
        name, ext = os.path.splitext(filename)
        if ext == '.ner':
            with codecs.open(os.path.join(data_dir, filename), 'r') as f:
                lines = f.readlines()
                ent_len = 0
                ne = []
                for l_ix, line in enumerate(lines):
                    if not line.startswith('#') and not line == '\n':
                        line_elems = line.strip().split('\t')
                        token = line_elems[tkn_col]

                        tag = line_elems[-1]
                        if '-' in tag:
                            prefix, entity = tag.split('-')
                        else:
                            prefix = tag
                            entity = None
                        bio_cnt[prefix] += 1
                        next_tag = None
                        if l_ix < len(lines)-1:
                            next_tag = lines[l_ix+1].strip().split('\t')[-1]
                        if prefix == 'B' or prefix == 'I':
                            if prefix == 'B':
                                entity_cnt[entity] += 1
                            ent_len += 1
                            ne.append(token)
                            if not next_tag or next_tag[0] in ['O', 'B']:
                                len_cnt[str(ent_len)] += 1
                                if lower:
                                    entity_name_cnt[(' '.join(ne).lower(), entity)] += 1
                                else:
                                    entity_name_cnt[(' '.join(ne), entity)] += 1
                                ent_len = 0
                                ne = []

    get_general_stats(bio_cnt,entity_name_cnt)
    get_span_stats(len_cnt)
    get_cat_stats(bio_cnt, entity_cnt)
    get_common_ne(entity_name_cnt, lower)

