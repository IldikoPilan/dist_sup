# Distant supervision for medical entity recognition

Medical Entity Recognition (NER) with distant supervision methods for Norwegian. 
The underlying lexical resource is [NorMedTerm](https://github.com/ltgoslo/NorMedTerm), a list of Norwegian categorized medical entities. The resource is included in this repository. 

## Dependencies 

[ufal.udpipe](https://pypi.org/project/ufal.udpipe/)

## Lexical baseline

Baseline tagging relying on lexical match with terms from NorMedTerm. Performs optional pre-processing and statistical analysis of the tagged entities. The longest possible match is taken. NER tags are added as an additional column at the end of each line.
The 'examples' folder includes some parsed (.conllu) and tagged (.ner) files of medical texts from [Legemiddelhåndboka](https://www.legemiddelhandboka.no/).

### Example runs

#### tagging and statistics for already tokenised files
- `python lex_baseline.py -i <input_folder> -a ts`

#### processing, tagging and statistics with a subset of entity categories

- `python lex_baseline.py -i <input_folder> -a pts -m <path_to_udpipe_model> -e CONDITION,PROCEDURE,SUBSTANCE`

#### help

- `python lex_baseline.py -h`

## Distantly supervised neural model 

Coming soon.

## Acknowledgements

Developed within the [BigMed](https://bigmed.no/) project.

## Terms of use

Distributed under the [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) licence.