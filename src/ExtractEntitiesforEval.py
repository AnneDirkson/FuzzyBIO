#!/usr/bin/env python
# coding: utf-8

# This script extracts the mentions based on NER predictions. It links discontinuous entities together according to the following rules: 
# 
# step 1: First entity parts are linked by attaching all I tags to previous B, HI to previous HB and DI to previous DB. (this already solves non-overlapping discontinuous entities). 
# 
# step 2: If the entity part starts with HB, check 4 tags to the left and 4 to the right for entity parts starting with DB. 
# - If there are only two, join the head entity to each non-head entity to form 2 entities
# - If there are more than two, use the sentence endings to determine if they fall in the same sentence. If this still results in more than 4 non-head entity parts, use only those on either the left or right side of the head entity based on which is within shortest distance to the head entity. 
# 

# In[8]:


from collections import defaultdict


# In[170]:


class EntityExtractor(): 
    
    def __init__(self): 
        pass
    
    ### use methods to extract concepts and add to df

    def extract_adr_words(self, sent, tags, tagtype = 'ADR'):
        adr_tags = []
        adr_words = []
        ent_range = []
        dist = defaultdict(list)
        tempwords = []
        temprange = []
        temptags = [] 

        for num, a in enumerate(tags): 
            try: 
                word = sent[num]
            except IndexError: 
                print('Tags and sent are not equal')
                print(len(s))
                print(len(t))
            if word == '.': 
                dist['sent_end'].append(num)
            else: 
                if a.endswith(tagtype): 
                    if a.startswith('B') or a.startswith('DB') or a.startswith('HB'): 
                        if len(temptags) != 0: 
                            adr_tags.append(temptags)
                            adr_words.append(tempwords)
                            ent_range.append(temprange)


                        tempwords= []
                        temptags = []
                        temprange = []

                        tempwords.append(word)
                        temptags.append(a)
                        temprange.append(num)

                        dist['start_ent'].append(num)

                        dist['end_ent'].append(num)

                    elif a.startswith('I') or a.startswith('DI'): 
                        tempwords.append(word)
                        temprange.append(num)
                        temptags.append(a)

                        try: 
                            dist['end_ent'][-1] == num
                        except IndexError: 
                            break

                    elif a.startswith('HI'): ##can have DB in between 
                        t1 = 'HB-' + tagtype
                        t2 = 'HI-' + tagtype
                        if tags[num-1] != t1: ##it is loose and could be sandwiched (or it just a second HI)

                            if tags[num-1] == t2: ##it is OK
                                tempwords.append(word)
                                temptags.append(a)
                                temprange.append(num)
                                try: 
                                    dist['end_ent'][-1] == num
                                except IndexError: 
                                    break
                            else: ##it is sandwiched - start new entity - previous is not HB-ADR or HI-ADR

                                if len(temptags) != 0: 
                                    adr_tags.append(temptags)
                                    adr_words.append(tempwords)
                                    ent_range.append(temprange)

                                tempwords= []
                                temptags = []
                                temprange = []

                                tempwords.append(word)
                                temptags.append(a)
                                temprange.append(num)
                                dist['start_ent'].append(num) 
                                dist['end_ent'].append(num)

                        else: 
                            tempwords.append(word)
                            temptags.append(a)
                            temprange.append(num)
                            dist['end_ent'][-1] == num
                else: 
                    pass
        adr_words.append(tempwords)
        adr_tags.append(temptags)
        ent_range.append(temprange)
        if num not in dist['sent_end']: 
            dist['sent_end'].append(num)

        return adr_tags, adr_words, dist, ent_range
    
    def sent_end_inbetween(self, start1, end1, start2, end2, sent_ends): 
        p = 0
        for num, end in enumerate(sent_ends): 
    #         print(end)
            if num == 0 : 
                q = 0 
            else: 
                q = sent_ends[num-1]
            if q < start1 < end and q < end2 < end: 
                p = 1
                return True

            elif q < start2 < end and q < end1 < end: 
                p = 1
                return True

        if p== 0: 
            return False
       
    def overlap_correction(self,adrlst, tagslst, ixlst, ent_range, s, tagtype = 'ADR'): 
        flat = [i for j in tagslst for i in j]
        
        t1 = 'HB-' + tagtype
        t2 = 'HI-' + tagtype
        t3 = 'DB-' + tagtype
        
        if t1 in flat: 
            nwadrlst =  [[] for _ in range(len(adrlst))]
            nwtagslst = [[] for _ in range(len(adrlst))]
            
            nwentrange =  [[] for _ in range(len(adrlst))]

            nwixlst = defaultdict(list)
            nwixlst['start_ent'] = [[]] * len(adrlst)
            nwixlst['end_ent'] =[[]] * len(adrlst)
            nwixlst['sent_end'] = ixlst['sent_end'] ##does not change

            for num, i in enumerate(tagslst): 
                y = adrlst[num]
                w = ent_range[num]

                start = ixlst['start_ent'][num]
                try: 
                    end = ixlst['end_ent'][num]
                except: 
                    print(ixlst)
                    print(adrlst)

                if i[0] == t1 or i[0] == t2: 

                    cnt = 0
                    to_change = []
                    for x in [-1, -2, -3,-4]: ##check 4 to left 
                        try: 

                            if num+x >= 0: 

                                if tagslst[num+x][0] != t3: 
                                    break

                                else:

                                    cnt +=1 
                                    to_change.append(num+x)
                        except IndexError: 
                            pass
    
                    for x in [1,2,3,4]: ##try right side
                        try: 
                            if tagslst[num+x][0] != t3:
                                break
                            else: 
                                cnt +=1 
                                to_change.append(num+x)
                        except IndexError: 
                            pass

                    if 1 < cnt < 3: ##good

                        for z in to_change: 


                            nwadrlst[z].extend(y)
                            nwtagslst[z].extend(i)
                            nwentrange[z].extend(w)

                        ##possibly change start or end
                            if start < ixlst['start_ent'][z]: ##start entity earlier
                                nwixlst['start_ent'][z] = start
                            elif end > ixlst['end_ent'][z]: ## end later
                                nwixlst['end_ent'][z] = end

                    else: ##use the sentence endings if more than 3
#                         print('Using sentence endings')
                        cnt = 0
                        orig_change = to_change
                        to_change = []
                        for x in [-1, -2, -3,-4]: ##check 4 to left 
                            try: 

                                if num+x >= 0: 
   
                                    if tagslst[num+x][0] != t3: 
                                        break

                                    else:

                                        start2 = ixlst['start_ent'][num+x]
                                        end2 = ixlst['end_ent'][num+x]
                                        if self.sent_end_inbetween(start, end, start2, end2, ixlst['sent_end']): ##fulfills both conditions
                                            cnt +=1 
                                            to_change.append(num+x)
                            except IndexError: 
                                pass
   
                        for x in [1,2,3,4]: ##try right side
                            try: 
                                if tagslst[num+x][0] != t3:
                                    break
                                else: 

                                    start2 = ixlst['start_ent'][num+x]
                                    end2 = ixlst['end_ent'][num+x]
                                    if self.sent_end_inbetween(start, end, start2, end2, ixlst['sent_end']): ##fulfills both conditions
                                        cnt +=1 
                                        to_change.append(num+x)
                            except IndexError: 
                                pass

                        if 1 < cnt < 5: ##good

                            for z in to_change: 


                                nwadrlst[z].extend(y)
                                nwtagslst[z].extend(i)
                                nwentrange[z].extend(w)

                            ##possibly change start or end
                                if start < ixlst['start_ent'][z]: ##start entity earlier
                                    nwixlst['start_ent'][z] = start
                                elif end > ixlst['end_ent'][z]: ## end later
                                    nwixlst['end_ent'][z] = end
                        elif cnt < 2: 
                            for z in orig_change: 
                                nwadrlst[z].extend(y)
                                nwtagslst[z].extend(i)
                                nwentrange[z].extend(w)

                            ##possibly change start or end
                                if start < ixlst['start_ent'][z]: ##start entity earlier
                                    nwixlst['start_ent'][z] = start
                                elif end > ixlst['end_ent'][z]: ## end later
                                    nwixlst['end_ent'][z] = end

                        else: ##only use one side with shortest distance
                            
            
                            dist_left = (ixlst['start_ent'][num]) - (ixlst['end_ent'][num-1])
            
                            dist_right = (ixlst['start_ent'][num+1]) - (ixlst['end_ent'][num])
                            
                
                            if dist_left < dist_right: ##smaller dist wins
                                print('Left wins')
                                to_change2 = [i for i in to_change if i < num]
                            
                            else: 
                                to_change2 = [i for i in to_change if i > num]
                                
                            for z in to_change2: 


                                nwadrlst[z].extend(y)
                                nwtagslst[z].extend(i)
                                nwentrange[z].extend(w)

                            ##possibly change start or end
                                if start < ixlst['start_ent'][z]: ##start entity earlier
                                    nwixlst['start_ent'][z] = start
                                elif end > ixlst['end_ent'][z]: ## end later
                                    nwixlst['end_ent'][z] = end

                elif i[0] == t2: ##loose end
                    print('Happening')
                    if 1 < cnt < 5: ##good
                        for z in to_change: 

                            nwentrange[z].extend(w)
                            nwadrlst[z].extend(y)
                            nwtagslst[z].extend(i)

                        ##possibly change start or end
                            if start < ixlst['start_ent'][z]: ##start entity earlier
                                nwixlst['start_ent'][z] = start
                            elif end > ixlst['end_ent'][z]: ## end later
                                nwixlst['end_ent'][z] = end

                elif i[0] == t3:  

                    try: 
                        if nwixlst['start_ent'][num] > 0 :  ## start entity already taken
                            pass
                        else: 
                            nwixlst['start_ent'][num] = start
                    except TypeError: 
                        nwixlst['start_ent'][num] = start

                    nwixlst['end_ent'][num]=end

                    nwadrlst[num].extend(y)
                    nwtagslst[num].extend(i)
                    nwentrange[num].extend(w)

                else: 
                    nwentrange[num].extend(w)
                    nwtagslst[num]= i
                    nwadrlst[num] = y
                    nwixlst['end_ent'][num]=end
                    nwixlst['start_ent'][num]=start

            return nwadrlst, nwtagslst, nwixlst, nwentrange           
        else: 
            return adrlst, tagslst, ixlst, ent_range
                
        
    def main(self, nwermsgs, nwtags3, tagtype ='ADR'): 
        all_adr = []
        all_tgs = []
        all_ix = []
        all_ent_ranges= []

        for s,t in zip(nwermsgs, nwtags3): 

            outtgs, outwords, ix, ent_range = self.extract_adr_words(s,t, tagtype = tagtype) 

            outwords2, outtgs2, ix2, ent_range2 = self.overlap_correction(outwords, outtgs, ix, ent_range, s, tagtype = tagtype)

            outwords3 = [i for i in outwords2 if i != []]
            outtgs3 = [i for i in outtgs2 if i != []]

            all_adr.append(outwords3)
            all_tgs.append(outtgs3)
            all_ix.append(ix2)
            all_ent_ranges.append(ent_range2)
        return all_adr, all_tgs, all_ix, all_ent_ranges
  

