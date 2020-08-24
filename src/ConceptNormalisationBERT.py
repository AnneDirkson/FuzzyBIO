#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pickle 
import pandas as pd

def load_obj(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f, encoding='latin1')
    

def save_obj(obj, name):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


# In[2]:


import ktrain
from ktrain import text as txt
# import torch 
import tensorflow as tf
import numpy as np
import pandas as pd

# import matplotlib.pyplot as plt
# import matplotlib
# matplotlib.use("Agg")

from sklearn.metrics import f1_score
import random


# In[26]:


class ConceptNorm(): 
    
    def __init__(self): 
        self.set_seed(1)
    
    
    def set_seed(self, num):
        random.seed(num)
        np.random.seed(num)
        tf.random.set_seed(num)
        
    
    def reformat_for_bert (self, data, foldnum): ##folds are built in ##dev is next fold
        test = data[foldnum]
        if foldnum != 10:
            devnum = foldnum+1
            dev = data[foldnum+1]
        else: 
            devnum = 1
            dev = data[devnum]
        t_ent = []
        t_cui = []
        t_id = []
        t_name = []

        for k in test.keys(): 
            t = test[k]
            if t == []: 
                pass
            else:
                for con in t: 
    #                 print(con[2])
                    try: 
                        c = con[2][0]
                    except: 
                        c = 0
                    if c == 'No code' or c == 'CONCEPT_LESS': 
                        pass
    #                 elif c == 0: 
    #                     pass
                    else: 
                        if type(con[0]) == list: 
                            e = " ".join(con[0])
                            t_ent.append(e)
                        else:
                            t_ent.append(con[0])                  
                        try: 
                            t_cui.append(con[2][0][0])
                            t_name.append(con[2][0][4])
                        except: ##has a 0 so only do not pass for test
                            t_cui.append(0)
                            t_name.append('Unknown')

                        t_id.append(k)

        t_name = [i.lower() for i in t_name]
        t_ent = [i.lower() for i in t_ent]
        testdf = pd.concat([pd.Series(t_id, name = 'id'), pd.Series(t_ent, name = 'entity'), pd.Series(t_cui, name = 'cui_code'), pd.Series(t_name, name = 'cui_name')], axis=1)



        kys = data.keys()
        kys2 = [i for i in kys if i != foldnum]
        kys3 = [i for i in kys2 if i != devnum]


        train = []
        for j in kys3: 
            train.append(data[j])

        t_ent = []
        t_cui = []
        t_id = []
        t_name = []

        for y in train:
            for k in y.keys():

                t = y[k]
                if t == []: 
                    pass
                else:
                    for con in t: 
                        try: 
                            c = con[2][0]
                        except: 
                            c = 0
                        if c == 'No code' or c == 'CONCEPT_LESS': 
                            pass
                        elif c == 0: 
                            pass
                        else: 
                            try: 
                                t_cui.append(con[2][0][0])
                                t_name.append(con[2][0][4])
                                if type(con[0]) == list: 
                                    e = " ".join(con[0])
                                    t_ent.append(e)
                                else:
                                    t_ent.append(con[0]) 
                            except: ##has a 0 so only do not pass for test
                                pass

                            t_id.append(k)
        t_ent = [i.lower() for i in t_ent]
        t_name = [i.lower() for i in t_name]
        traindf = pd.concat([pd.Series(t_id, name = 'id'), pd.Series(t_ent, name = 'entity'), pd.Series(t_cui, name = 'cui_code'), pd.Series(t_name, name = 'cui_name')], axis=1)
    #     traindf2 = pd.concat([traindf, traindf.cui_name.astype('str').str.get_dummies()], axis=1, sort=False)

    #     classdf = pd.concat([devdf, traindf], axis=0)
        classnames = list(set(traindf.cui_code))


        t_ent = []
        t_cui = []
        t_id = []
        t_name = []

        for k in dev.keys(): 
            t = dev[k]
            if t == []: 
                pass
            else:
                for con in t: 
    #                 print(con[2])
                    try: 
                        c = con[2][0]
                    except: 
                        c = 0
                    if c == 'No code' or c == 'CONCEPT_LESS': 
                        pass
    #                 elif c == 0: 
    #                     pass
                    elif con[2] == [0] or con[2] == 0 or con[2][0][0] not in classnames:
                        pass
                    else:

                        try: 
                            t_cui.append(con[2][0][0])
                            t_name.append(con[2][0][4])
                            if type(con[0]) == list: 
                                e = " ".join(con[0])
                                t_ent.append(e)
                            else:
                                t_ent.append(con[0])  
                        except: ##has a 0 so only do not pass for test
                            pass

                        t_id.append(k)
        t_ent = [i.lower() for i in t_ent]
        t_name = [i.lower() for i in t_name]
        devdf = pd.concat([pd.Series(t_id, name = 'id'), pd.Series(t_ent, name = 'entity'), pd.Series(t_cui, name = 'cui_code'), pd.Series(t_name, name = 'cui_name')], axis=1)

        return traindf, testdf, devdf, classnames
    
    def reformat_for_bert_othertestsets (self, data, foldnum): ##folds are built in ##dev is next fold 
        test = data[foldnum]

        t_ent = []
        t_cui = []
        t_id = []
        t_name = []

        for k in test.keys(): 
            t = test[k]
            if t == []: 
                pass
            else:
                for con in t: 
    #                 print(con[2])
                    try: 
                        c = con[2][0]
                    except: 
                        c = 0
                    if c == 'No code' or c == 'CONCEPT_LESS': 
                        pass
    #                 elif c == 0: 
    #                     pass
                    else: 
                        if type(con[0]) == list: 
                            e = " ".join(con[0])
                            t_ent.append(e)
                        else:
                            t_ent.append(con[0])                  
                        try: 
                            t_cui.append(con[2][0][0])
                            t_name.append(con[2][0][4])
                        except: ##has a 0 so only do not pass for test
                            t_cui.append(0)
                            t_name.append('Unknown')

                        t_id.append(k)
    #     nwt_name = []
    #     for i in t_name: 
    #         try: 
    #             i2 = i.lower() 
    #         except: 
    #             print(i)
    #         nwt_name.append(i2)
        t_ent = [i.lower() for i in t_ent]
        t_name = [i.lower() for i in t_name]
        testdf = pd.concat([pd.Series(t_id, name = 'id'), pd.Series(t_ent, name = 'entity'), pd.Series(t_cui, name = 'cui_code'), pd.Series(t_name, name = 'cui_name')], axis=1)

        return testdf
    
    def run_BERT_model (self, data, preddata1, preddata2, foldnum, outpath, lr, epochs): 

        traindf, testdf, devdf, classnames = self.reformat_for_bert (data, foldnum)

        ##other test sets 

        testdf_other1 = self.reformat_for_bert_othertestsets(preddata1, foldnum)
        testdf_other2 = self.reformat_for_bert_othertestsets(preddata2, foldnum)

        sufix = "fold" + str(foldnum)

        t = txt.Transformer(self.MODEL_NAME, maxlen=128, class_names=classnames)
        trn = t.preprocess_train(list(traindf.entity), list(traindf.cui_code))
        val = t.preprocess_test(list(devdf.entity), list(devdf.cui_code))
        model = t.get_classifier()
        learner = ktrain.get_learner(model, train_data=trn, val_data=val, batch_size=32)

        hist1 = learner.fit_onecycle(lr, epochs)

        v1 = hist1.history['val_accuracy'][-1]

        predictor1 = ktrain.get_predictor(learner.model, preproc=t)   

        hist2 = learner.fit_onecycle(lr, 1)

        v2 = hist2.history['val_accuracy'][-1]

        predictor2 = ktrain.get_predictor(learner.model, preproc=t)

        if v1 >= v2: 
            print('The number of chosen epochs is 3')
            chosen = 3
    #         save_obj(chosen, (outpath + 'chosen_epochs_' + sufix + str(lr)))
    #         save_obj(v1, (outpath + 'validate_f1' + sufix + str(lr)))
    #         predictor1.save(base_out_path + 'predictor1_' + sufix )

    #             res_test = predictor1.predict(X_test2)

            out1 = [predictor1.predict(s) for s in testdf.entity]
            out2 = [predictor1.predict(s) for s in testdf_other1.entity]
            out3 = [predictor1.predict(s) for s in testdf_other2.entity]


        else: 
            chosen =4
            print('The number of chosen epochs is 4')
    #         save_obj(chosen, (outpath + 'chosen_epochs_' + sufix + str(lr)))
    #         save_obj(v2, (outpath + 'validate_f1' + sufix + str(lr)))
    #         predictor2.save(base_out_path + 'predictor2_' + sufix )

    #             res_test = predictor2.predict(X_test2)
            out1 = [predictor2.predict(s) for s in testdf.entity]
            out2 = [predictor2.predict(s) for s in testdf_other1.entity]
            out3 = [predictor2.predict(s) for s in testdf_other2.entity]

    #     out = [predictor1.predict(s) for s in X_test]
        outpath1 = outpath + 'own_predictions_' + sufix
        outpath2 = outpath + 'other1_predictions_' + sufix
        outpath3 = outpath + 'other2_predictions_' + sufix

        save_obj(out1, outpath1) 
        save_obj(out2, outpath2)
        save_obj(out3, outpath3)
    
    def main(self, data, preddata1, preddata2, outpath, lr = 5e-5, epochs =3): 
        self.MODEL_NAME='distilbert-base-uncased'
        for i in range(1,11): 
            self.run_BERT_model(data, preddata1, preddata2, i, outpath, lr, epochs)


# In[27]:


# ## USAGE


# orig_data = load_obj('XXX/Results/perfect_annotations_psytar')

# basic_extr =  load_obj('XXX/Results/imperfect_annotations_concept_basic_psytar')

# simplify_extr = load_obj('XXX/Results/imperfect_annotations_concept_simplify_psytar')


# In[28]:


# outpath = '.'

# data = basic_extr
# preddata1 = simplify_extr
# preddata2 = orig_data

# ConceptNorm().main(data, preddata1, preddata2, outpath)


# In[ ]:




