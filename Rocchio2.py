#!/usr/bin/env python

"""The simplest TF-IDF library imaginable.

Add your documents as two-element lists `[docname,
[list_of_words_in_the_document]]` with `addDocument(docname, list_of_words)`.
Get a list of all the `[docname, similarity_score]` pairs relative to a
document by calling `similarities([list_of_words])`.

See the README for a usage example.

"""

import sys
import os
import numpy as np
import math
class TfIdf:
    def __init__(self):
        self.weighted = False
        self.a = 0.7
        self.b = 0.3
        self.PRMax = 100
        self.PR = 0
        self.new_score_dic={}
        self.doc_vec = {} # doc : vec
        self.documents = {} #doc : list of words
        self.corpus_dict = {} # word : times
        self.sims = {} # q : (doc , value)
    def add_document(self, doc_name, list_of_words):
        # building a dictionary : {doc:{字:字數}}
        doc_dict = {} # building a dic : {字:字數}
        for w in list_of_words: # list_of_words list 中的每個字
            doc_dict[w] = doc_dict.get(w, 0.) + 1.0 # 定義字典中w 字的數字為 : key為 w的value +1.0 , 若找不到則以0 + 1.0 存為value
            self.corpus_dict[w] = self.corpus_dict.get(w, 0.0) + 1.0 #corpus為全部document一起共用的字典
        
        # normalizing the dictionary (got Term frequency)
        length = float(len(list_of_words))
        for k in doc_dict:
            doc_dict[k] = 1 + doc_dict[k] / length

        # add the normalized document to the corpus  (TF)
        self.documents[doc_name]= doc_dict #{doc:{字:TF}}
    def similarities(self, list_of_words, queryName):
        """Returns a list of all the [docname, similarity_score] pairs relative to a
list of words.

        """

        # building the query dictionary
        query_dict = {}
        for w in list_of_words:
            query_dict[w] = query_dict.get(w, 0.0) + 1.0

        # normalizing the query
        length = float(len(list_of_words))
        for k in query_dict:
            query_dict[k] = 1+ query_dict[k] / length #got TF

        # computing the list of similarities
        scoreDic = {}
        for doc in self.documents:
            #每一篇文件要做的事情
            #1. 讀出名字跟dic
            #2. 比對是否存在該字,有的話計算tfidf 沒有則0 ,存在list中
            #3. 把list 轉換為array之後進行dot product
            #4. 最後把結果化為 sim:{q1:{D1:值,D2:值},q2:{...},q3{...}}
            docTFIDF = []
            qTFIDF=[]
            lengthDoc=0
            lengthQuery=0
            score = 0
            #1 得到該document的字典
            dicTemp = self.documents[doc]
            
            #2. 依字典中次序選字，當作向量的順序！
            for w in self.corpus_dict:
                if w in dicTemp: #then compute TF * IDF
                    docTFIDF.append(dicTemp[w]*math.log10((2265/self.corpus_dict[w])))
                    lengthDoc = lengthDoc+ ( dicTemp[w]*math.log10((2265/self.corpus_dict[w])) )**2
                else : #then add 0 
                    docTFIDF.append(0)
                
                if w in query_dict: #compute IDF of query (use the parameter of documents)
                    qTFIDF.append(query_dict[w]*math.log10((2265/self.corpus_dict[w])))
                    lengthQuery = lengthQuery + (query_dict[w]*math.log10((2265/self.corpus_dict[w])))**2
                else:
                    qTFIDF.append(0)
            
            lengthDoc = lengthDoc**0.5 # length of a vector :　(sum of elements**2)**0.5
            lengthQuery = lengthQuery**0.5
            #3. compute dot product and normalize to get cos!
            arrayQuery = np.array(qTFIDF)
            arrayDoc = np.array(docTFIDF)
            self.doc_vec[doc]=arrayDoc # save the vec of doc
            score = arrayQuery.dot(arrayDoc)/(lengthDoc * lengthQuery)
            scoreDic[doc]=score
        
        #4.    
        self.sims[queryName] = sorted(scoreDic.items(), key=lambda item:item[1], reverse = True)
        #做排序    
        new_query=[]
        doc_vector = []
        #5 query expand 
        for doc in self.sims[queryName]:
            if self.PR <self.PRMax:
                if self.PR==0:
                    doc_vector = doc[self.PR]
                    self.PR++1
                else:
                    doc_vector = doc_vector + doc[self.PR]
        new_query = self.a * arrayQuery + self.b*(doc_vector/self.PRMax) # get new query
        # do new dot product
        for doc in self.doc_vect:
            new_score = new_query.dot(self.doc_vect[doc])/(lengthDoc * lengthQuery)
            self.new_score_dic[doc]= new_score 
        