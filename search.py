from key_figures import figures
from spell import main
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import sqlite3
import re
import time
import math
import os
import json
import pprint

import numpy as np
import nltk
nltk.download('punkt')
nltk.download('stopwords')


docs = {}
result = {}
con = sqlite3.connect('inforet.db')
con.isolation_level = None
cur = con.cursor()


def process_doc(docname=None, query=None):
    if docname:
        data_path = 'dataset'
        f = open(os.path.join(data_path, docname), 'r')
        content = json.loads(f.read())['text']
        unicode = re.compile(r"[^\U00000000-\U0000007F]")
        content = unicode.sub(" ", content)

    if query:
        content = query

    clean = re.compile(r'[\-#"():+,.*/$%&]')
    delim = re.compile(r'\W+')
    newline = re.compile(r'\n+')
    content = re.sub(newline, " ", content)
    content = clean.sub(" ", content)
    content = re.sub("'", "", content)
    content = content.lower()
    # pre_data = pre_process(content)
    # print(pre_data)
    if docname:
        tokens = delim.split(content)[:-1]
    if query:
        tokens = delim.split(content)
    tokens = pre_process(tokens)
    return tokens


def pre_process(tokens):
    stop_words = set(stopwords.words('english'))
    stop_words.remove('of')
    # print(stop_words)
    new_tokens = []
    for token in tokens:
        if token not in stop_words:
            new_tokens.append(token)
    return new_tokens


def get_term_id(term):
    q_word_id = '''SELECT TERMID FROM TERMSTABLE WHERE TERM="{}"'''.format(term)
    try:
        cur.execute(q_word_id)
        row = cur.fetchone()
        return row[0]
    except:
        pass


def commonElements(docs_list):
    common = set(docs_list[0])
    for l in docs_list:
        common = common.intersection(set(l))
    return common


def calc_tf(words, docs):
    tf = {}
    for word in words:
        tf[word] = {}
        for doc in docs:
            # print(doc, word)
            q = '''SELECT P.TERMCOUNT FROM POSITIONALINDEX AS P WHERE P.TERMID={} AND P.DOCID={}'''.format(
                get_term_id(word), doc)
            try:
                cur.execute(q)
                row = cur.fetchone()
                tf[word][doc] = row[0]
            except:
                tf[word][doc] = 0
            # print(row[0])
    return tf


def calc_idf(N, words):
    idf = {}
    for word in words:
        # print(word)
        q = '''SELECT DOCCOUNT FROM TERMSTABLE WHERE TERMID={}'''.format(
            get_term_id(word))
        cur.execute(q)
        row = cur.fetchone()
        idf[word] = round(math.log(N / row[0], 10), 3)
    return idf


def calc_tfidf(N, words, docs):
    tf = calc_tf(words, docs)
    idf = calc_idf(N, words)
    tfidf = {}
    for i in words:
        tfidf[i] = {}
        for doc in docs:
            tfidf[i][doc] = tf[i][doc] * idf[i]
    return tfidf


def get_doc(name):
    f = open('dataset/{}'.format(name), 'r')
    data = json.loads(f.read())
    f.close()
    return data


# query: search item
# N: number of documents in the databse
#
def search_query(sq=None):

    if not sq:
        query = input("Enter Query: ")
    else:
        query = sq

    start_time = time.time()
    processed_input = process_doc(query=query)
    # processed_input = [main(correct) for correct in processed_input]

    postings = {}
    docs_list = []
    # print(processed_input)
    for word in processed_input:
        pquery = '''SELECT * FROM POSITIONALINDEX WHERE TERMID={}'''.format(
            get_term_id(word))
        s = cur.execute(pquery)

        posting = [i for i in s]
        d = []
        for p in posting:
            pd = p[1]
            d.append(pd)
        docs_list.append(d)
        postings[word] = posting
    # print(docs_list)
    if docs_list:
        common_docs = commonElements(docs_list)
        if not common_docs:
            common_docs = []
            for i in docs_list:
                common_docs.extend(i)
        # print(common_docs)
    else:
        print('No Matching Results!')
        exit()

    for doc in common_docs:
        q = '''SELECT DOCTITLE FROM DOCTABLE WHERE DOCID={}'''.format(doc)
        try:
            cur.execute(q)
            row = cur.fetchone()
            docs[doc] = row[0]
        except:
            continue
    # print(docs)

    q = '''SELECT COUNT(*) FROM DOCTABLE'''
    cur.execute(q)
    row = cur.fetchone()
    N = row[0]

    # tf(i, d) = termcount from postingstable where i=word and d=docid
    # idf N/doccount
    tfidf = calc_tfidf(N, processed_input, common_docs)
    # print(tfidf)
    query_vector = []
    doc_vector = {}
    query_vector = {}
    similarity = {}
    # print(docs)
    for docid, docname in docs.items():
        # try:
        # get a sorted, clean doc
        text = process_doc(docname)
        processed_doc = set(sorted(text))
        doc_tfidf = calc_tfidf(N, processed_doc, [docid])

        set_words = sorted(list(set(processed_input).union(processed_doc)))
        query_vector[docid] = []
        doc_vector[docid] = []

        for w in set_words:
            if w in processed_input:
                # print(docid, query_vector[docid])
                # print(docid, tfidf[w][docid])
                query_vector[docid].append(tfidf[w][docid])
            else:
                query_vector[docid].append(0)
            if w in processed_doc:
                doc_vector[docid].append(doc_tfidf[w][docid])
            else:
                doc_vector[docid].append(0)

        query_norm = np.linalg.norm(query_vector[docid])
        doc_norm = np.linalg.norm(doc_vector[docid])
        cosine_similarity = np.sum(np.multiply(
            query_vector[docid], doc_vector[docid])) / (query_norm * doc_norm)
        similarity[docid] = cosine_similarity
        # except:
        # continue

    result = dict(sorted(similarity.items(), key=lambda t: t[1], reverse=True))
    print('results retrieved in ', time.time() - start_time, ' secs')
    print(result)
    if sq == None:
        pretty_print_results(result)
    return result


def pretty_print_results(result):
    for d in result:
        print(d)
        q = '''SELECT DOCTITLE FROM DOCTABLE WHERE DOCID={}'''.format(d)
        cur.execute(q)
        row = cur.fetchone()[0]
        data = get_doc(row)
        print('DocID: ', row)
        print('Title: ', data['title'])
        print('URL: ', data['url'])
        print('=================================================================')


def search_tag():
    tag = input("Enter Tag: ")
    q = '''SELECT DOCIDS FROM TAGSTABLE WHERE TAG="{}"'''.format(tag)
    cur.execute(q)
    row = cur.fetchone()[0]
    docs = row.split(", ")
    pretty_print_results(docs)
    return docs


def fetch(did=None):
    if not did:
        docID = input("Enter docid to retrieve: ")
    else:
        docID = did
    data_path = 'dataset'
    file = json.loads(open(os.path.join(data_path, docID)).read())
    q = ''' SELECT DOCID FROM DOCTABLE WHERE DOCTITLE="{}"'''.format(docID)
    cur.execute(q)
    row = cur.fetchone()[0]

    print(f"DocID: {docID} Title: {file['title']}")
    print(f"URL: {file['url']}\n")
    kf = figures(file['text'])
    print(f"Key Figures:\n\n")
    for k in kf:
        print(k[0], end=' -- ')
    print(f"\n\nDoc Excerpt:\n\n {file['text']}")
    rec_docs = dict()
    for item in kf[:5]:
        try:
            docs = search_query(item[0])
        except:
            continue
        # print(docs)
        for doc, score in docs.items():
            if (doc not in rec_docs) and (doc != row):
                if score > 0:
                    rec_docs[doc] = score
            elif doc != row:
                if score > rec_docs[doc]:
                    rec_docs[doc] = score
    
    rec_docs = dict(sorted(rec_docs.items(), key=lambda x:x[1], reverse=True))
    print(f"Similar Docs:\n\n")
    print(rec_docs)
    pretty_print_results(rec_docs)