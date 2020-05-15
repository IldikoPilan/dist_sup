""" 
Baseline tagging relying on lexical matches with the NorMedTerm list 
(https://github.com/ltgoslo/NorMedTerm) of categorized medical entities. 
Optional pre-processing and statistical information.
Author: Ildikó Pilán
Dependencies: ufal.udpipe (https://pypi.org/project/ufal.udpipe/)
"""

import sys
import os
import codecs
import argparse
from ufal.udpipe import Model, Pipeline, ProcessingError 
from helpers import load_terms, normalize_tkns, ent_categories
from stats import get_stats

def process_text(path_to_file, input_format, model, out_file):
    """ Apply NLP processing to text (tokenize, tag, parse) and 
    save output in CONLLU format.
    """
    pipeline = Pipeline(model, input_format, Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')  
    error = ProcessingError()
    with codecs.open(path_to_file) as f:
        text = f.read()
        processed = pipeline.process(text, error)
        if error.occurred():
            print("Error when running UDPipe: ")
            print(error.message)
            print("\n")
            sys.exit(1)
        with codecs.open(out_file, 'w', 'utf-8') as of:
            of.write(processed)

def baseline_tag(tokenized_f, ordered_terms, out_file, tkn_col=1, lower=True):
    """
    Performs lexical baseline tagging with the BIO-scheme and saves output.
    Adds token-level entity annotation based on matches with the provided 
    term list. Takes the longest possible match. 
    Annotations are added as an additional column at the end of each line.
    """
    stop_words = ['av', 'i', 'på', 'til', 'hos']
    out = ''
    with codecs.open(tokenized_f, 'r') as f:
        lines = f.readlines()
        prev_tag = None
        ent_end = 0
        for l_ix, line in enumerate(lines):
            if line.startswith('#') or line == '\n': # handling UDPipe-style output
                out += line
            else:
                line_elems = line.strip().split('\t')
                token_orig = line_elems[tkn_col]
                if lower:
                    token = token_orig.lower()
                else:
                    token = token_orig
                if not prev_tag or (l_ix >= ent_end): 
                    for term, entity in ordered_terms:
                        if lower:
                            term_tkns = [tkn.lower() for tkn in term.split(' ')]
                        else:
                            term_tkns = term.split(' ')
                        if token == term_tkns[0]: 
                            if token not in stop_words:
                                ent_end = l_ix+len(term_tkns)
                                tkns_ahead = normalize_tkns(lines[l_ix:ent_end], tkn_col, lower)
                                if term_tkns == tkns_ahead:
                                    prev_tag = 'B-'+entity
                                    break
                                else:
                                    prev_tag = 'O'
                            else:
                                prev_tag = 'O'
                        else:
                            prev_tag = 'O'
                elif prev_tag.startswith('B') and (l_ix < ent_end):
                    prev_tag = 'I-'+entity
                elif prev_tag.startswith('I') and (l_ix < ent_end): 
                    prev_tag = 'I-'+entity
                else:
                    prev_tag = 'O'
                line_elems.append(prev_tag)
                out += '\t'.join(line_elems)+'\n'
    with codecs.open(out_file, 'w', 'utf-8') as of:
        of.write(out)
 
def parse_args():
    """ Parse command-line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', help="path to directory with .txt or .conllu/.vert \
                                               file(s)", type=str, required=True)
    # optional args
    parser.add_argument('--actions', '-a', help="'p' (parsing), 't' (tagging), 's' (statistics), \
                                                'pt', 'pts'(default) or 'ts'",
                        type=str, default='pts')
    parser.add_argument('--column', '-c', help="column index of tokens in .conllu/.vert files \
                                                (default=1)", type=int, default=1)
    parser.add_argument('--entities', '-e', help="entities from NorMedTerm (all by default)", 
                        type=str, default=','.join(ent_categories))
    parser.add_argument('--input_format', '-if', help="format of raw text files: 'conllu'(default), \
                                                       'horizontal', 'vertical' or 'tokenize'", 
                        type=str, default='horizontal')
    parser.add_argument('--lower', '-l', help="lowercase during term-matching",
                        type=bool, default=True)
    parser.add_argument('--model', '-m', help="path to Norwegian UDPipe model",
                        type=str, default='')
    parser.add_argument('--output', '-o', help="directory to save output (.ner files) in", type=str)
    parser.add_argument('--terms', '-t', help="path to NorMedTerm term list", type=str, 
                        default='NorMedTerm.csv')
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    categories = args.entities.split(',')
    if not args.output:
        out_dir = args.input # will save tagged output in input folder
    else:
        out_dir = args.output
    if 'p' in args.actions:
        if not args.model:
            raise ValueError('Provide path to UDPipe model with action "p" (parse)')
        else:
            model = Model.load(args.model)
            if not model:
                print("Cannot load model from file '%s'\n" % model_path)
                sys.exit(1)
            print('Processing with UDPipe...')
            cnt = 0
            for filename in os.listdir(args.input):
                name, ext = os.path.splitext(filename)
                if ext == '.txt':
                    cnt += 1
                    out_file = os.path.join(args.input, name+'.conllu')
                    process_text(os.path.join(args.input,filename), args.input_format, model, out_file)
            print('{} parsed texts saved in "{}"'.format(cnt, args.input))
            args.column = 1 # overwrite any user provided col to UdPipe default used here
    if 't' in args.actions:         
        print('Loading NorMedTerm')
        ordered_terms = load_terms(args.terms, categories)
        print('Loaded {} terms'.format(len(ordered_terms)))
        if out_dir != args.input and not os.path.exists(out_dir):
            os.mkdir(out_dir)
        print('Performing baseline tagging on...')
        t_cnt = 0
        for filename in os.listdir(args.input):
            name, ext = os.path.splitext(filename)
            if ext == '.conllu' or ext == '.vert':
                t_cnt += 1
                print('\t...',filename)
                out_file = os.path.join(out_dir, name + '.ner')
                baseline_tag(os.path.join(args.input,filename), ordered_terms, out_file, 
                                          args.column, args.lower)
        print('{} tagged files saved in "{}"'.format(t_cnt, out_dir))
    if 's' in args.actions:
        print('Computing statistics...')
        get_stats(out_dir, args.column, args.lower)
        
if __name__ == '__main__':
    main()
