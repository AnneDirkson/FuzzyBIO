#!/usr/bin/env python
# coding: utf-8

# This script will transform the messy ADR data into BIOHD format

# In[12]:


import pandas as pd
import pickle


# In[20]:


from ExtractEntitiesforEval import EntityExtractor


# In[14]:


import pickle
import pandas as pd 

def save_obj(obj, name):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f, encoding='latin1')

    


# In[28]:


class Fuzzify(): 
    
    def __init__(self): 
        pass
    
    def fuzzify(self, ent_ranges, tgs, words, tagtype):
        nw_tags= []
        for ix, a1 in enumerate(ent_ranges):
            a = [i for i in a1 if i != []]
            b = tgs.iloc[ix]
            c = words.iloc[ix]
            btag = 'B-' + tagtype
            itag = 'I-' + tagtype
            if list(set(b)) == ['O']:
                nw_tags.append(b)
            else: 
                temp= []
                entnum = 0 
                for num, word in enumerate(c): 
                    try: 
                        ent = a[entnum]
                    except: 
                        ent = a[-1]
                    if ent == []: 
                        entnum +=1
                        try: 
                            ent = a[entnum]
                        except: 
                            ent= a[-1]

                    try: 
                        s= min(ent)
                        e= max(ent)
                    except ValueError: 
                        entnum +=1
                        ent = a[entnum]

                        s= min(ent)
                        e= max(ent)

                    if num > e: 
                        entnum +=1 
                        try: 
                            ent = a[entnum]
                        except: 
                            ent = a[-1]
                        if ent == []: 
                            entnum +=1
                            try: 
                                ent = a[entnum]
                            except: 
                                ent = a[-1]
                        try: 
                            s= min(ent)
                            e= max(ent)
                        except ValueError: 

                            entnum +=1
                            try: 
                                ent = a[entnum]
                            except: 
                                ent = a[-1]
                            s= min(ent)
                            e= max(ent)


                    if s <= num <= e: 
                        if num == s: 
                            temp.append(btag)
                        else: 
                            temp.append(itag)
                    else: 
                        temp.append('O')

                    if num == e: 
                        entnum +=1 
                nw_tags.append(temp)
        return nw_tags
    
    def main (self, data, tagtype):
        ##data must be aggregated
        data_agg = data.groupby('sent_id').agg(list)
        data_agg = data_agg.reset_index()
        all_adr, all_tgs, all_ix, ent_ranges = EntityExtractor().main(data_agg.word, data_agg.tag, tagtype =  tagtype)
        nwertags = self.fuzzify(ent_ranges, data_agg.tag, data_agg.word, tagtype)
        ##save new data 

        words = []
        tgs = []
        ids = []

        for a,b,c in zip(data_agg.sent_id, data_agg.word, nwertags): 
            for b2,c2 in zip(b,c): 
                ids.append(a)
                words.append(b2)
                tgs.append(c2)
        df = pd.concat([pd.Series(ids, name = 'sent_id'), pd.Series(words, name = 'word'), pd.Series(tgs, name = 'tag')], axis=1)
        return df


# In[29]:


# ##Usage

# data = load_obj('XXXX/NER_Corpus_ADR_nw_withID')
# data_agg = data.groupby('sent_id').agg(list)
# data_agg = data_agg.reset_index()
        
# df= Fuzzify().main(data, tagtype = 'ADR')


# In[30]:


# df.tail()


# In[ ]:




