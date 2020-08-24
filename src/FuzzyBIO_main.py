#!/usr/bin/env python
# coding: utf-8

# ##This script will: 
# 
# - turn the BIOHD annotations into FuzzyBIO annotations
# - train NER models (10-fold CV) using distilbert (cased)
# - analyse the results of the NER models trained using FuzzyBIO and using BIOHD
# 
# optional: 
# - Link the extracted entities to the concept normalization annotations provided with perfect entities 
# - Train concept normalization models (10-fold CV) using distilbert (uncased)
# - Analyse the results of these models on perfect data, imperfect BIOHD and imperfect FuzzyBIO data 

# In[6]:


## import all modules

from Fuzzify_Annotations import Fuzzify

from BERTforNERktrain import BERTforNER

from ExtractSimplifiedConcepts import AnnotateImperfect 

from CollectNERResults import NER_results

from ConceptNormalisationBERT import ConceptNorm

from ConceptNormResults import ConceptNormEval


# In[ ]:


import pickle 
import pandas as pd
import os

def load_obj(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f, encoding='latin1')
    

def save_obj(obj, name):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


# In[8]:


def main(data, folddict, outfolder, ConceptNorm = False, txt_dict = None, concept_dict = None, modelpath = None): 
    ##making the fuzzybio annotations
    data.columns = ['sent_id', 'word', 'tag']
    data_agg = data.groupby('sent_id').agg(list)
    data_agg = data_agg.reset_index()

    nwdata= Fuzzify().main(data, tagtype = 'ADR')
    
    save_obj(nwdata, outfolder + "fuzzy_data")
    
    os.mkdir(outfolder + "/NER/FuzzyBIO/") 
    os.mkdir(outfolder + "/NER/BIOHD/") 
    ##NER for Fuzzy data
    BERTforNER().main(outfolder + "/NER/FuzzyBIO/", nwdata, folddict)
    
    ##NER for BIOHD data
    BERTforNER().main(outfolder + "/NER/BIOHD/", data, folddict)

    ##NER Results -- all evaluation is done on the BIOHD tagged data
    predfolder1 = outfolder + '/NER/BIOHD/'
    predfolder2 = outfolder + "/NER/FuzzyBIO/"
    
    NER_results().main(data, folddict, predfolder1, predfolder2)   
    
    if ConceptNorm == True:
        f, f2, f3 = AnnotateImperfect().main(data, nwdata, folddict, concept_dict, txt_dict, predfolder1, predfolder2, tagtype = 'ADR')
        ##f3 are the perfect annotations
        os.mkdir(outfolder + "/ConceptNorm/") 
        
        ConceptNorm().main(f3, preddata1= f, preddata2=f2, outpath = outfolder + '/ConceptNorm/')
        
        ConceptNormEval().main(modelpath, predpath= outfolder + '/ConceptNorm/', orig_data =f3, basic_extr=f, simplify_extr=f2)


# In[ ]:


## Example usage with CADEC 

data = load_obj('./data/CADEC_BIOHD')
folddict = load_obj('./data/folddict_CADEC')
txtdict = load_obj('./data/txtdict_CADEC')
conceptdict = load_obj('./data/conceptdict_CADEC')

modelpath = './data/mednorm_raw_10n_40l_5w_64dim.bin'

os.mkdir('./Results/") 
outfolder = './Results/'

main(data, folddict, outfolder, ConceptNorm = True, txt_dict = txtdict, concept_dict = conceptdict, modelpath = modelpath): 

