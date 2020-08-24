#!/usr/bin/env python
# coding: utf-8

# This script employs distilBERT for NER using Huggingface and ktrain. It uses a cyclical learning rate with a max of 1e-2 and chooses 3 or 4 epochs depending on the validation data. Data needs to have the columns sent_id, tag, and word with one word on each row. Fold dict needs to be formatted like the examples with keys for fold numbers (1 to 10) and then nested dictionaries with dev, train and test sections with sent_ids.
# 
# Note: This script does not save the models, just the predictions per fold.

# In[1]:


import pickle 

def load_obj(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f, encoding='latin1')

def save_obj(obj, name):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


# In[2]:


import ktrain
from ktrain import text as txt
import tensorflow as tf
import numpy as np
import pandas as pd

from sklearn.metrics import f1_score
import random 


# In[7]:


class BERTforNER(): 
    
    def __init__(self): 
        self.set_seed(1) 
    
    def reformat_for_bert (self, data, folddict):
        x = folddict['dev']
        y = folddict['train']
        z = folddict['test']

        dev_df = data[data.sent_id.isin(x)]
        train_df = data[data.sent_id.isin(y)]
        test_df = data[data.sent_id.isin(z)]

        nwtrain_df = pd.concat([train_df, dev_df], axis=0)
        nwtrain_df.to_csv('./train.txt', sep = ',', index = False)

        test = test_df.groupby(test_df.sent_id).agg(list)
        X_test1 = [' '.join(w) for w in test.word]
        X_test2 = list(test.word)
        y_test = list(test.tag)
        return X_test1, X_test2, y_test

    def set_seed(self, num):
        random.seed(num)
        np.random.seed(num)
        tf.random.set_seed(num)
        try: 
            torch.manual_seed(num)
        except NameError: 
            pass

    def run_BERT_model (self, data, folddict, foldnum, outpath, MODELNAME, lr, epochs =3): 
    #     base_out_path = 'C:/Users/dirksonar/Documents/Data/Project8_Discourse/eDiseases/BERT/'
        f = folddict[foldnum]
        X_test1, X_test2, y_test = self.reformat_for_bert (data, f)

        sufix = "fold" + str(foldnum)

        ##PREPROCESS
        DATAFILE = './train.txt'

        (trn, val, preproc) = txt.entities_from_txt(DATAFILE,
                                                 sentence_column='sent_id',
                                                 word_column='word',
                                                 tag_column='tag', 
                                                 data_format='gmb',
                                                 use_char=True)

        WV_Path = 'https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.en.300.vec.gz'

    #     WV_Path = '/data/dirksonar/ktrain_data/cc.en.300.vec'
        model = txt.sequence_tagger('bilstm-bert', preproc, bert_model = MODELNAME,  wv_path_or_url=WV_Path)


        learner = ktrain.get_learner(model, train_data=trn, val_data=val, batch_size=32)

        hist1 = learner.fit_onecycle(lr, epochs)

        v1 = learner.validate(class_names=preproc.get_classes())

        predictor1 = ktrain.get_predictor(learner.model, preproc=preproc)   

        hist2 = learner.fit_onecycle(lr, 1)

        v2 = learner.validate(class_names = preproc.get_classes)

        predictor2 = ktrain.get_predictor(learner.model, preproc=preproc)

        if v1 >= v2: 
            chosen = 3
            save_obj(chosen, (outpath + 'chosen_epochs_' + sufix + str(lr)))
            save_obj(v1, (outpath + 'validate_f1' + sufix + str(lr)))

            out = [predictor1.predict(s) for s in X_test1]


        else: 
            chosen =4
            save_obj(chosen, (outpath + 'chosen_epochs_' + sufix + str(lr)))
            save_obj(v2, (outpath + 'validate_f1' + sufix + str(lr)))

            out = [predictor2.predict(s) for s in X_test1]

        outpath2 = outpath + 'predictions_' + sufix + str(lr)
        save_obj(out, outpath2)
        
        
    def main (self, outpath, data, folddict): 
        maxlen=128
        MODELNAME='distilbert-base-cased'
        
        for i in range(1,11):
            self.run_BERT_model (data, folddict, i, outpath, MODELNAME, lr = 1e-2,epochs =3)


# In[8]:


# ##Usage 
# data = load_obj('XXX/NER_Corpus_ADR_Coping')
# folddict = load_obj('XXX/folddict_NER')


# In[9]:


# outpath= '.'
# BERTforNER().main(outpath, data, folddict)


# # In[ ]:




