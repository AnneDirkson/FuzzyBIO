# FuzzyBIO
FuzzyBIO is a fuzzy continuous representation of discontinuous entities. This repository contains scripts to transform your data; and analyse the impact on NER and normalization to SNOMED CT.

## Prerequisites 

For installing the required packages:

Using pip 

pip install --upgrade pip pip install -r ./env/requirements.txt

Using conda 

conda env create -f ./env/environment.yml

If you also want to run the concept normalization, you will need to the Word2Vec Model of the SNOMED CT concepts [3]. It can be downloaded here:
https://data.mendeley.com/datasets/b9x7xxb9sz/1#file-232b6c5a-cda2-4c71-a47d-9c89a814d506


## Usage

Use the main function in FuzzyBIO_main.ipynb 

This script will: 

- turn the BIOHD annotations into FuzzyBIO annotations
- train NER models (10-fold CV) using distilbert (cased)
- analyse the results of the NER models trained using FuzzyBIO and using BIOHD

optional if ConceptNorm set to True:
- Link the extracted entities to the concept normalization annotations provided with perfect entities 
- Train concept normalization models (10-fold CV) using distilbert (uncased)
- Analyse the results of these models on perfect data, imperfect BIOHD and imperfect FuzzyBIO data 

BERT implementation is based on Huggingface Transformers [2] with a ktrain wrapper [1]

We provide the CADEC data [4] (BIOHD labelled), text dict, concept dict and folddict. These can be used to understand the input format necessary for these files. Please refers the authors below [4] if you use this data. For all datasets we provide the fold dicts for replication and concept dicts if possible*. 

* For some data sets the data is publicly available but a DUA needs to be signed. 

## Example usage with CADEC (also in FuzzyBIO_main)

data = load_obj('./data/CADEC_BIOHD')

folddict = load_obj('./data/folddict_CADEC')

txtdict = load_obj('./data/txtdict_CADEC')

conceptdict = load_obj('./data/conceptdict_CADEC')

modelpath = './data/mednorm_raw_10n_40l_5w_64dim.bin'

os.mkdir('./Results/") 

outfolder = './Results/'

main(data, folddict, outfolder, ConceptNorm = True, txt_dict = txtdict, concept_dict = conceptdict, modelpath = modelpath)

## Additional notes on linking discontinuous entities 

In our scripts, discontinuous entities are linked according to the following rules: 

- step 1: First entity parts are linked by attaching all I tags to previous B, HI to previous HB and DI to previous DB. (this already solves non-overlapping discontinuous entities). 

- step 2: If the entity part starts with HB, check 4 tags to the left and 4 to the right for entity parts starting with DB. 
  - If there are only two, join the head entity to each non-head entity to form 2 entities
  - If there are more than two, use the sentence endings to determine if they fall in the same sentence. If this still results in more than 4 non-head entity parts, use only those on either the left or right side of the head entity based on which is within shortest distance to the head entity. 

## References 

[1] Maiya, A. S. (2020). ktrain: A Low-Code Library for Augmented Machine Learning. Retrieved from http://arxiv.org/abs/2004.10703

[2] Wolf, T., Debut, L., Sanh, V., Chaumond, J., Delangue, C., Moi, A., … Brew, J. (2019). Transformers: State-of-the-art Natural Language Processing. ArXiv. Retrieved from https://huggingface.co

[3] Belousov, M., Dixon, W. G., & Nenadic, G. (n.d.). MedNorm: A Corpus and Embeddings for Cross-terminology Medical Concept Normalisation. https://doi.org/10.17632/b9x7xxb9sz.1

[4] Karimi, S., Metke-Jimenez, A., Kemp, M., & Wang, C. (2015). Cadec: A corpus of adverse drug event annotations. Journal of Biomedical Informatics, 55, 73–81. https://doi.org/10.1016/J.JBI.2015.03.010
