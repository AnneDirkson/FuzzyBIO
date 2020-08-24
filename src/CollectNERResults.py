#!/usr/bin/env python
# coding: utf-8

# In[4]:


import pickle 

def load_obj(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f, encoding='latin1')
    

def save_obj(obj, name):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
        
import pandas as pd


# In[5]:


import unidecode
from sklearn.metrics import f1_score, recall_score, precision_score
from collections import defaultdict
import numpy as np
import re
from ExtractEntitiesforEval import EntityExtractor
from collections import defaultdict


# In[15]:


class NER_results(): 
    
    def __init__(self): 
        self.WORD = '[A-Za-z0-9]+'
        self.ONLYHYPHEN = '[-]+'
        self.punclst = ["\n", "'", "(", '#', '-', "_", "%", '+', "&", "<", ">", ")", "[", "]", "*", "~"]
    
    def reformat_for_bert (self,data, folddict):
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
    

    def remove_punc_ypred(self, inp):
        out = []
        for sent in inp:
            tempsent = []
            for w in sent:
                if re.fullmatch(self.WORD, w[0]) != None: 
                    if re.fullmatch(self.ONLYHYPHEN, w[0]) != None: 
                        pass
                    else:
                        tempsent.append(w)
                else: 
                    pass
            out.append(tempsent)
        return out

    def remove_punc_ytest(self, words, lbls):
        out = []
        out2 = []

        for a,b in zip(words, lbls): 
            unaccented_a = unidecode.unidecode(a)
    #         print(a)
            go = 0
            for i in a: 
                if i in self.punclst: 
                    go = 1

            if go ==1: 
                for i in self.punclst:
                    a2 = a.split(i)
                    if b.startswith("B") or b.startswith('DB') or b.startswith('HB'):
                        out2.append(b)
                        b2 = b.replace("B", "I")
                        for x in range(0, len(a2)-1): 
                            out2.append(b2)
                    else: 
                        for x in a2: 
                            out2.append(b)

                    for x in a2: 
                        out.append(x)

            else:
                if re.fullmatch(self.WORD, unaccented_a) != None: 
                    if re.fullmatch(self.ONLYHYPHEN, unaccented_a) != None: 
                        pass
                    else:
        #             print(a) 
                        out.append(unaccented_a)
                        out2.append(b)
                else: 
                    pass
        return out, out2
        
    def align_pred_test(self, pred, predlbls, test, testlbls, origtest): 
        nwtestlbls = []

        for a,b, c,d,e in zip(pred, predlbls, test, testlbls, origtest): 
            if len(a) == len(c): 
                nwtestlbls.append(d)
            else: 
                temp = []
                n = 0

                for w1,w2,l in zip(a,c,d):

                    temp.append(l)

                nwtestlbls.append(temp)
#                 if len(temp) != len(b): 
#                     print(a)
#                     print(c)
#                     print(e)
#                     print('\n')
        return nwtestlbls
    
    def get_BERT_results(self, data, folddict, predpath): 
        out = defaultdict(list)
        out2 = defaultdict(list)

        lbls = list(set(data.tag))
        metric_lbls= [i for i in lbls if i != 'O']

        for i in folddict: 
            fd = folddict[i]
            X_test1, X_test2, y_test = self.reformat_for_bert(data, fd)

            predpath2 = predpath + 'predictions_fold' + str(i) + '0.01'
    #         + '0.01'
            pred = load_obj(predpath2)
            nwpred = self.remove_punc_ypred(pred)
    #         nwpred = pred
            nwpred2 = []
            for i in nwpred: 
                t= []
                t = [j[0] for j in i]
                nwpred2.append(t)

            nwpredlbls = []
            for i in nwpred: 
                t= []
                t = [j[1] for j in i]
                nwpredlbls.append(t)


            nwtrueX = []
            nwtrueY = []
            for a,b in zip(X_test2, y_test): 
                c,d = self.remove_punc_ytest(a,b)

                nwtrueX.append(c)
                nwtrueY.append(d)
            nwtrueY2 = self.align_pred_test(nwpred2, nwpredlbls, nwtrueX, nwtrueY, X_test2)


            trueflat = [i for j in nwtrueY2 for i in j]
            predflat = [i for j in nwpredlbls for i in j]

            trueflat2 = []
            for i in trueflat: 
                if i.endswith('ADR'): 
                    trueflat2.append('ADR')
                else: 
                    trueflat2.append('O')

            predflat2 = []
            for i in predflat: 
                if i.endswith('ADR'): 
                    predflat2.append('ADR')
                else: 
                    predflat2.append('O')


            f = f1_score(y_true= trueflat, y_pred= predflat, average = 'micro', labels = metric_lbls)
            r = recall_score(y_true= trueflat, y_pred= predflat, average = 'micro', labels = metric_lbls)
            p = precision_score(y_true= trueflat, y_pred= predflat, average = 'micro', labels = metric_lbls)

            out['F1'].append(f)
            out['Recall'].append(r)
            out['Precision'].append(p)

            f2 = f1_score(y_true= trueflat2, y_pred= predflat2,  pos_label = 'ADR')
            r2 = recall_score(y_true= trueflat2, y_pred= predflat2,  pos_label = 'ADR')
            p2 = precision_score(y_true= trueflat2, y_pred= predflat2,  pos_label = 'ADR')

            out2['F1'].append(f2)
            out2['Recall'].append(r2)
            out2['Precision'].append(p2)

        print("The average F1 score is: ")
        print(np.mean(out['F1'])) 
        print("The average recall is: ")
        print(np.mean(out['Recall'])) 
        print("The average precision is: ")
        print(np.mean(out['Precision'])) 

        print('If we forget about BIOHD: ')
        print("The average F1 score is: ")
        print(np.mean(out2['F1'])) 
        print("The average recall is: ")
        print(np.mean(out2['Recall'])) 
        print("The average precision is: ")
        print(np.mean(out2['Precision'])) 


        return out, out2
    
    ## inexact evaluation entity level


    def get_inexact_entity_evaluation(self,data, folddict, foldnum, predpath): 

        cor_ent= 0 
        part_ent= 0 
        missed_ent = 0
        len_missed = []
        len_cor = []
        len_part = []
        perc_part= []


        fd = folddict[foldnum]
        X_test1, X_test2, y_test = self.reformat_for_bert(data, fd)

        predpath2 = predpath + 'predictions_fold' + str(foldnum) + '0.01'
    #         + '0.01'
        pred = load_obj(predpath2)
        nwpred = self.remove_punc_ypred(pred)
        nwpred2 = []
        for i in nwpred: 
            t= []
            t = [j[0] for j in i]
            nwpred2.append(t)

        nwpredlbls = []
        for i in nwpred: 
            t= []
            t = [j[1] for j in i]
            nwpredlbls.append(t)


        nwtrueX = []
        nwtrueY = []
        for a,b in zip(X_test2, y_test): 
            c,d = self.remove_punc_ytest(a,b)
            nwtrueX.append(c)
            nwtrueY.append(d)
        nwtrueY2 = self.align_pred_test(nwpred2, nwpredlbls, nwtrueX, nwtrueY, X_test2)

        all_adr, all_tgs, all_ix, ent_ranges =EntityExtractor().main(nwtrueX, nwtrueY2)


        for a,b,c in zip(ent_ranges, nwtrueY, nwpredlbls): 
            if a == [[]]: ##no entities
                pass
            for ent in a:

                if ent == []: 
                    pass #no entities or empty entity due to overlap correction
                else:
    #                 print(ent)

                    len_ent = len(ent)
    #                 print(len_ent)
    #                     print(range(i,j))
                    p = 0 
                    for nums in ent: 
    #                     print(ent)
    #                     print(c[nums])
                        if c[nums] != 'O': 
                            p += 1

                    if p == len_ent: 
                        cor_ent += 1
                        len_cor.append(len_ent)
                    elif p > 0: 
                        part_ent += 1
                        len_part.append(len_ent)
                        perc_part.append(p/len_ent)

                    else:
                        missed_ent += 1
                        len_missed.append(len_ent)

        return missed_ent, len_missed, cor_ent, len_cor, part_ent, len_part, perc_part

    def run_inexact(self, data, modelpath, folddict): 
        for i in range(1,11): 
            missed_ent_all = []
            len_missed_all = []
            len_cor_all = []
            cor_ent_all = []
            part_ent_all = []
            len_part_ent_all= []
            perc_part_all = []

            missed_ent, len_missed, cor_ent, len_cor, part_ent, len_part, perc_part = self.get_inexact_entity_evaluation(data, folddict, i, modelpath)
            total_ent = missed_ent + cor_ent + part_ent

            perc_part_all.append(np.mean(perc_part))
            missed_ent_all.append(missed_ent/total_ent)
            part_ent_all.append(part_ent/total_ent)
            cor_ent_all.append(cor_ent/total_ent)

            len_missed_all.append(np.mean(len_missed))
            len_cor_all.append(np.mean(len_cor))
            len_part_ent_all.append(np.mean(len_part))

        print('Number of missed ent is ' + str(np.mean(missed_ent_all)))
        print('Their average length is  ' + str(np.mean(len_missed_all)))

        print('Number of correct ent is ' + str(np.mean(cor_ent_all)))
        print('Their average length is  ' + str(np.mean(len_cor_all)))

        print('Number of partially correct ent is ' + str(np.mean(part_ent_all)))
        print('Their average length is  ' + str(np.mean(len_part_ent_all)))

        print('The caught percentage is on average ' + str(np.mean(perc_part_all)))
    
    def main(self, data, folddict, predfolder1, predfolder2): 
        print('The model based on BIOHD data: ')
        o,o2 = self.get_BERT_results (data, folddict, predfolder1)
        self.run_inexact(data, predfolder1, folddict)
        
        
        print('The model based on FuzzyBIO data: ')
        o,o2 = self.get_BERT_results (data, folddict, predfolder2)
        self.run_inexact(data, predfolder2, folddict)


# In[20]:


# ##USAGE -- all evaluation is done on the BIOHD tagged data

# datac = load_obj('XXX/cadec_data_redone_ner')
# # datac2 = load_obj('xxx/cadec_data_noBIOHD')
# folddictc = load_obj('xxx/folddict_cadec')
# predfolder1 = 'xxx/BERTbasic_cadec/'
# predfolder2 = 'xxx/BERTbasic_cadec_anno/'

# datac.columns= ['sent_id', 'word', 'tag']


# In[21]:


# NER_results().main(datac, folddictc, predfolder1, predfolder2)


# In[ ]:




