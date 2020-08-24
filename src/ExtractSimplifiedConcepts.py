#!/usr/bin/env python
# coding: utf-8

# In[1]:


## this script extracts the simplified concepts (with only B and I) and automatically annotates them with SNOMED CT CUI codes and names (multiple if provided.)


# In[4]:


import pickle 

def load_obj(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f, encoding='latin1')
    

def save_obj(obj, name):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
        
import pandas as pd
import re
from collections import defaultdict
import unidecode


# In[5]:


from ExtractEntitiesforEval import EntityExtractor


# In[41]:


class AnnotateImperfect(): 
    def __init__(self): 
        self.WORD = '[A-Za-z0-9]+'
        self.ONLYHYPHEN = '[-]+'
        self.punclst = ["_", "%", '+', "&", "<", ">", ")","(", "[", "]", ".", ",", "/", ";", ":" ,"!", "?", '"', "$","'", '#', '-', "|", "~", "=", "`", "*"]
    
    def reformat_for_bert (self, data, folddict): 
        x = folddict['dev']
        y = folddict['train']
        z = folddict['test']


        dev_df = data[data.sent_id.isin(x)]
        train_df = data[data.sent_id.isin(y)]
        test_df = data[data.sent_id.isin(z)]

        nwtrain_df = pd.concat([train_df, dev_df], axis=0)

        test = test_df.groupby(test_df.sent_id).agg(list)
        X_test1 = [' '.join(w) for w in test.word]
        X_test2 = list(test.word)
        y_test = list(test.tag)
        test = test.reset_index()
        testids = list(test.sent_id)
        return X_test1, X_test2, y_test, testids 
    
    
    ##remove punctuation from both 

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

            tempa = a
            if go ==1: 
                for i in self.punclst:
    #                 print(i)
                    if i in tempa: 
                        a2 = tempa.split(i)
    #                     print(a2)
                        a1a = [i for i in a2 if i != '']
                        a1b = " ".join(a1a)
                        tempa = a1b
    #                     print(tempa)
                a3 = []
                for j in a2: 
                    j2 = j.split(' ')
                    [a3.append(x) for x in j2]

    #             a3 = a2.split(' ')
                for x in a3: 
                    if x != '':
                        out.append(x)
                        out2.append([])

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
    
    
    def looseI_toB (self, tgs, tagtype):
        itag = 'I-' + tagtype
        nwtgs = tgs ##initialize 
        change = 0
        for num, t in enumerate(tgs): 
            if t.endswith (itag) and tgs[num-1] == 'O':
                t2 = t.replace('I', 'B')
                nwtgs[num] == t2
        return nwtgs
        
    def get_entity_results(self, data, folddict, predpath, tagtype= 'ADR'): 
        out = {}
        predtxt = {}
        enttag_pred = {}
        all_ents= []

        for num in folddict: 
            foldout = {}
            fd = folddict[num]
            X_test1, X_test2, y_test, testids = self.reformat_for_bert(data, fd)

            predpath2 = predpath + 'predictions_fold' + str(num) + '0.01'
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

    #         nwpredlbls2 = [link_up_loose_I(r) for r in nwpredlbls]

            nwpredlbls2 = [self.looseI_toB(r, tagtype) for r in nwpredlbls]
            all_adr, all_tgs, all_ix, ent_ranges =EntityExtractor().main(nwpred2, nwpredlbls2)

            for a,b, c in zip(nwpred2, testids, nwpredlbls2): 
                predtxt[b] =a
                enttag_pred[b] = c

            for a,b,c in zip(all_adr, testids, ent_ranges):

                ##remove [] from c 
                c2 = [i for i in c if i != []]

                a2 = []
                for i, j in zip(a,c2): 
                    a2.append(tuple([i,j]))

                foldout[b] = a2
                all_ents.append(a)


            out[num] = foldout
        return out, all_ents, predtxt, enttag_pred
    
    def extract_true_entrange(self, sent, c): #c is conceptdict entry
        char_dict = defaultdict(list)
        ent_tags= []
        entrange = {}
        extra_con = {}

        for con in c: 
            if con[1] != None and con[1] != con[0]: 
                extra_con[con[0]] = con[1]    

        for con in c: 
            if len(con) > 11:
                for i in range(con[-4], con[-3]+1): ##second set 
                    char_dict[i].append(con[0:8])
                for i in range(con[-2], con[-1]+1): 
                    char_dict[i].append(con[0:8])
            else: 
                for i in range(con[-2], con[-1]+1): 
                    char_dict[i].append(con[0:8])
        sent2 = []
        t = []
        for num, char in enumerate(sent): 

            if char == ' ' or char in self.punclst: 

                if sent[num-1] == " " or sent[num-1] in self.punclst: 

                    pass
                else:

                    t2 = "".join(t)
                    sent2.append(t2)
                    t = []
                    ent_tags.append(w)
            else: 
                t.append(char)
            try: 
                w = char_dict[num]

            except KeyError: 
                w = 0

        if sent[-1] in self.punclst or sent[-1] == ' ': 
            pass
        else:
            ent_tags.append(w)

        one, two = self.remove_punc_ytest(sent2, ent_tags)

        if (len(one) == len(two)) == False: 
            print('Problematic')


        for num, j in enumerate(two): 
            if j != []: ##something there
                j2 = j            
                entrange[num] = j2

        return entrange, one
        
    
    def collect_cui_for_extracted_con(self, concept_dict, txt_dict, found_ent_all, pred_txt): 
        found_ent_annotated = {}
        for i in found_ent_all.keys():
#             print(i)

            tempanno= defaultdict(list)
            found_ent = found_ent_all[i]
            k= found_ent.keys()

            for ky in k: 
#                 print(ky)
                sent = txt_dict[ky]
                try: 
                    c= concept_dict[ky]

                    ent_range, out_sent = self.extract_true_entrange(sent, c)

                    w = pred_txt[ky]
     
                    for f in found_ent[ky]: ##iterate through entities found

                        temp = []
                        f2 = list(f)
                        f3 = f2
                        for b in f2[1]: ##the range of words found
                            try: 
                                q = ent_range[b]
                                temp.append(q)
                            except: 
                                pass
                        if len(temp) == 0: 
                            temp.append([0])


                        t = [i for j in temp for i in j]

                        t2 = list(set(t))

                        f3.append(t2)

                        tempanno[ky].append(tuple(f3))

                except KeyError: 
   
                    for f in found_ent[ky]: ## add 0 to every one
                        f2 = list(f)
                        f2.append(0)
                        f3 = tuple(f2)

                        tempanno[ky].append(f3)
            found_ent_annotated[i] = tempanno  
        return found_ent_annotated
    
    def some_stats(self, out):
        l = []
        c1 = 0
        c2 = 0
        for i in out.keys(): 
            o = out[i]
            for ky in o.keys(): 
                o2 = o[ky]
                for i in o2: 
                    x = i[2]
                    if x == 0: 
                        l.append(0)
                    else: 
                        try:
                            l.append(len(x))
                            if len(x) == 1: 
                                c1 += 1
                            else: 
                                c2 +=1
                        except TypeError: 
                            print(x)
        total = len(l)
        c3 = c1 + c2
        print('Percentage with at least one concept: ' + str(c3/total))
        print('Percentage with more than one concept: ' + str(c2/total))
                    
    
    ##Reformat original data in same way 

    def reformat_orig_data (self, concept_dict, found_ent_all): 
        out = {}
        for i in found_ent_all.keys():
#             print(i)
            tempanno= defaultdict(list)
            found_ent = found_ent_all[i]
            k= found_ent.keys()

            for ky in k:
                try: 
                    c = concept_dict[ky]
                    if c == []: 
                        pass
                    else: 
                        for f in c:
                            f2 = list(f)
                            t = []
                            t.append(f2[8])
                            t.append([])
                            q = []
                            q.append(tuple(f2[0:8]))

                            t.append(q)
                            tempanno[ky].append(tuple(t))
                except: 
                    pass
            out[i] = tempanno

        return out


    def main(self, data, data_sim, folddict, conceptdict, txtdict, preds_folder1, preds_folder2, tagtype = 'ADR'): 
        data.columns = ['sent_id', 'word', 'tag']
        data_sim.columns = ['sent_id', 'word', 'tag']
        
        ent_basic, allents_basic, predtxt_basic, predlbl_basic = self.get_entity_results(datac, folddict, preds_folder1, tagtype) 
        ##simplified 
        ent_basic2, all_ents_basic2, predtxt_basic2, predlbl_basic2  = self.get_entity_results(data_sim, folddict, preds_folder2, tagtype) 
        
        f = self.collect_cui_for_extracted_con(conceptdict, txtdict, ent_basic, predtxt_basic)
        f2 = self.collect_cui_for_extracted_con(conceptdict, txtdict, ent_basic2, predtxt_basic2)
        
        print('For BIOHD annotations: ')
        self.some_stats(f)
        print('For FuzzyBIO annotations: ')
        self.some_stats(f2)
        
        f3 = self.reformat_orig_data(conceptdict, ent_basic)
        
        return f, f2, f3


# In[42]:


##TO DO 

#automatically make a text dict.


# In[43]:


##usage 

# datac = load_obj('xxxx/cadec_data_redone_ner')
# datac2 = load_obj('xxxx/cadec_data_noBIOHD')
# folddictc = load_obj('xxx/folddict_cadec')
# txt_dict= load_obj('xxx/cadec_textdict')
# concept_dict = load_obj('xxx/cadec_conceptdict_snomed')

# predfolder1 = 'xx/BERT_models/BERTbasic_cadec/' 
# predfolder2 = 'xxx/BERT_models/BERTbasic_cadec_simple/' 


# In[44]:


# f, f2, f3 = AnnotateImperfect().main(datac, datac2, folddictc, concept_dict, txt_dict, predfolder1, predfolder2, tagtype = 'ADR')


# In[ ]:




