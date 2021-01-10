import sqlite3, re, time, math, os, json
import numpy as np
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


def read_exclude_cats(filename='exclude_cats.txt'):
    with open(filename) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    return content

def process_doc(docname):
    data_path = 'dataset'
    f = open(os.path.join(data_path, docname), 'r')
    content = json.loads(f.read())['text']
    unicode = re.compile(r"[^\U00000000-\U0000007F]")
    content = unicode.sub(" ", content)
    clean = re.compile(r'[\-#"():+,.*/$%&]')
    delim = re.compile(r'\W+')
    newline = re.compile(r'\n+')
    content = re.sub(newline, " ", content)
    content = clean.sub(" ", content)
    content = re.sub("'", "", content)
    content = content.lower()
    # pre_data = pre_process(content)
    # print(pre_data)
    tokens = delim.split(content)[1:-1]
    tokens = pre_process(tokens)
    return len(tokens)


def pre_process(tokens):
    stop_words = set(stopwords.words('english'))
    stop_words.remove('of')
    # print(stop_words)
    new_tokens = []
    for token in tokens:
        if token not in stop_words:
            new_tokens.append(token)
    return new_tokens



con = sqlite3.connect('inforet.db')
con.isolation_level = None
cur = con.cursor()

data_path = 'dataset'
doc_files = sorted(os.listdir(data_path))

index_path = 'index'
test_file = sorted(os.listdir(index_path))[0]
test_file = os.path.join(index_path, test_file)

f = open(test_file, 'r')
data = json.loads(f.read())
f.close()

EXCULDE = read_exclude_cats()

start_time = time.time()
count = 1
for doc in doc_files[:10]:
    N = process_doc(doc)
    q = '''INSERT INTO DOCTABLE(DOCID, DOCTITLE, WORDCOUNT) VALUES({}, "{}", {})'''.format(count, doc, N)
    cur.execute(q)
    print('doc insereted ', doc)

    doc_tags = json.loads(open(os.path.join(data_path, doc), 'r').read())['tags']
    tags = [tag[9:] for tag in doc_tags if tag not in EXCULDE]
    for tag in tags:
        t = '''SELECT 1 FROM TAGSTABLE WHERE TAG="{}"'''.format(tag)
        try:
            out = cur.execute(t)
        except:
            continue
        out = [o for o in out]
        if out:
            #update
            t1 = '''SELECT DOCIDS FROM TAGSTABLE WHERE TAG="{}"'''.format(tag)
            cur.execute(t1)
            current_docs = cur.fetchone()[0]
            new_docs = current_docs + ', ' + str(count)
            cur.execute('''UPDATE TAGSTABLE
                            SET DOCIDS = "{}"
                            WHERE TAG="{}"'''.format(new_docs, tag)
                        )
            print('tag updated ', tag)
        else:
            #insert
            cur.execute(
                ''' INSERT INTO TAGSTABLE(TAG, DOCIDS) VALUES("{}", "{}")'''.format(tag, str(count))
            )            
            print('tag inserted ', tag)

    count += 1

count = 1
for key, values in data.items():
    q = '''INSERT INTO TERMSTABLE(TERMID, TERM, DOCCOUNT) VALUES({}, "{}", {})'''.format(count, key, len(values))
    cur.execute(q)
    print('key {} inserted'.format(key))
    doc_str = ''
    for sk, sv in values.items():
        doc_str = ', '.join(map(str, sv))
        p = '''INSERT INTO POSITIONALINDEX(TERMID, DOCID, POSITIONS, TERMCOUNT) VALUES({}, {}, "{}", {})'''.format(count, sk, doc_str,len(sv))
        cur.execute(p)
        # print('doc {} inserted'.format(sk))
    count += 1


print('\nTime taken to build the database: ',time.time() - start_time)