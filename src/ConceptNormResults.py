#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pickle 
import pandas as pd
from sklearn.metrics import accuracy_score
import numpy as np
from gensim.models import KeyedVectors

def load_obj(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f, encoding='latin1')
    

def save_obj(obj, name):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


# In[12]:


class ConceptNormEval(): 
    
    def __init__(self): 
        pass
    
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
                    if c == 'CONCEPT_LESS' or c == 'No code': 
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
                        if c == 'CONCEPT_LESS' or c == 'No code': 
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
                    if c == 'CONCEPT_LESS' or c == 'No code': 
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
    
    def classic_eval(self, true, pred): 
        true2 = []
        pred2 = []
        for a,b in zip(true, pred): 
            if a == 'CONCEPT_LESS' or a== 'No code': 
                pass
            else: 
                true2.append(a)
                pred2.append(b)
        acc = accuracy_score(true2, pred2)
        return acc
    
    def unclassic_eval(self, testdf, origtestdf, pred): 
        y0 = [j for j in origtestdf.cui_code if j != 'CONCEPT_LESS']
        
        y = [j for j in y0 if j != 'No code']

        total = len(y)
        c= 0 
        testdf = testdf.reset_index()
        df = pd.concat([testdf, pd.Series(pred, name = 'pred')], axis=1)
        for a,b in zip(origtestdf.cui_code, origtestdf.id): ##iterate over true entities
            if a == 'CONCEPT_LESS' or a == 'No code':
                pass 
            else:
                found = df[df.id == b]
                l = list(found.pred)
                if a in l: 
                    c += 1
                else: 
                    pass
        acc = c/total
        return acc
    
    def approx_distance_from_correct(self, true, pred): 
        sims =[]
        for a,b in zip(true, pred): 
            if a != b:
                a2 = 'SNOMEDCT_' + str(a)
                b2 = 'SNOMEDCT_' + str(b)

                try: 
                    m = self.model.similarity(a2, b2)
                    sims.append(m)
                except: 
                    pass
    #         sims.append(m)

        return np.mean(sims)
    
    def get_concept_norm_results(self, data, origdata, predpath, predictionsname): ##per model per case
        allacc1 = []
        allacc2 = []
        approx = []
        approx = []
        for i in range(1,11):
    #         fd = folddict[i]
            traindf, testdf, devdf, classnames = self.reformat_for_bert(data, i)
            traindf1, testdf1, devdf1, classnames1 = self.reformat_for_bert(orig_data, i)

            predpath2 = predpath + predictionsname + '_fold' + str(i)

            pred = load_obj(predpath2)
            acc1 = self.classic_eval(testdf.cui_code, pred)
            allacc1.append(acc1)
            acc2 = self.unclassic_eval(testdf, testdf1, pred)
            allacc2.append(acc2)

            a1 = self.approx_distance_from_correct(testdf.cui_code, pred)
            approx.append(a1)

        print('The mean accuracy is: ')
        print(np.mean(allacc1))
        print("The percentage of target entities found: ")
        print(np.mean(allacc2))
        print('The mean cosine similarity of incorrect entities to targets: ')
        print(np.mean(approx))

    def main (self, modelpath, predpath, origdata, basic_extr, simplify_extr): 
        self.model = KeyedVectors.load_word2vec_format(modelpath, binary = True)
        print('Perfect model on perfect data')
        self.get_concept_norm_results(origdata, origdata, predpath, 'PerfectAnno/own_predictions')
        print('\n')
        
        print("Perfect model on imperfect BIOHD data")
        self.get_concept_norm_results(basic_extr, origdata, predpath, 'PerfectAnno/other1_predictions')
        print('\n')

        print("Perfect model on imperfect BIOHD data")
        self.get_concept_norm_results(simplify_extr, origdata, predpath, 'PerfectAnno/other2_predictions')
        

        


# In[13]:


# ##get data 

# orig_data = load_obj('XXX/Results/perfect_annotations_cadec')

# basic_extr =  load_obj('XXX/Results/imperfect_annotations_concept_basic')

# simplify_extr = load_obj('XXX/Results/imperfect_annotations_concept_simplify')


# In[14]:


# modelpath = 'XXX/Stored_data/mednorm_raw_10n_40l_5w_64dim.bin'


# In[15]:


##first the model trained on perfect data
# predpath = 'C:\\Users\\dirksonar\\Documents\\Data\\Project4_entityextract\\Results\\ConceptNorm\\'

# ConceptNormEval().main(modelpath, predpath, orig_data, basic_extr, simplify_extr)


# In[ ]:





# In[ ]:




