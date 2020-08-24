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

FuzzyBIO_main.ipynb 


BERT implementation is based on Huggingface Transformers [2] with a ktrain wrapper [1]
main. normlaization optional. 

Data provided is CADEC data set [4]. For all datasets we provide the fold dicts and for all concept dicts?


## References 

[1] Maiya, A. S. (2020). ktrain: A Low-Code Library for Augmented Machine Learning. Retrieved from http://arxiv.org/abs/2004.10703

[2] Wolf, T., Debut, L., Sanh, V., Chaumond, J., Delangue, C., Moi, A., … Brew, J. (2019). Transformers: State-of-the-art Natural Language Processing. ArXiv. Retrieved from https://huggingface.co

[3] Belousov, M., Dixon, W. G., & Nenadic, G. (n.d.). MedNorm: A Corpus and Embeddings for Cross-terminology Medical Concept Normalisation. https://doi.org/10.17632/b9x7xxb9sz.1

[4] Karimi, S., Metke-Jimenez, A., Kemp, M., & Wang, C. (2015). Cadec: A corpus of adverse drug event annotations. Journal of Biomedical Informatics, 55, 73–81. https://doi.org/10.1016/J.JBI.2015.03.010
