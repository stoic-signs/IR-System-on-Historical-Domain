
import os
import re
import sys
import time
import math
import json
import nltk
from threading import Thread
from queue import Queue
import logging
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from collections import OrderedDict
lemmatizer = WordNetLemmatizer()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

common_words = stopwords.words('english')
common_words.remove('of')


class InvertedIndex:
    def __init__(self, path=None) -> None:
        self.index = {}
        # self.start = start
        # self.end = end
        # self.index_no = index_no
        self.path = os.path.join(os.getcwd(), 'dataset/json_files')
        if path:
            self.path = path

    def nltk_tag_to_wordnet_tag(self, nltk_tag):
        if nltk_tag.startswith('J'):
            return wordnet.ADJ
        elif nltk_tag.startswith('V'):
            return wordnet.VERB
        elif nltk_tag.startswith('N'):
            return wordnet.NOUN
        elif nltk_tag.startswith('R'):
            return wordnet.ADV
        else:
            return None

    def lemmatize_tokens(self, tokens):
        # tokenize the sentence and find the POS tag for each token
        tags = []
        for word in tokens:
            tags.append(nltk.pos_tag(nltk.word_tokenize(word))[0][1])
        for i in range(len(tags)):
            tags[i] = self.nltk_tag_to_wordnet_tag(tags[i])
        # tuple of (token, wordnet_tag)
        lemm_tokens = []
        for i in range(len(tokens)):
            if tags[i] is None:
                # if there is no available tag, append the token as is
                lemm_tokens.append(tokens[i])
            else:
                # else use the tag to lemmatize the token
                lemm_tokens.append(lemmatizer.lemmatize(tokens[i], tags[i]))
        return lemm_tokens

    def tokenize_add_index(self, s: str, file_num: str) -> None:
        unicode = re.compile(r"[^\U00000000-\U0000007F]")
        s = unicode.sub(" ", s)
        clean = re.compile(r'[#"():+*/$%&_]')
        delim = re.compile(r'\W+')
        newline = re.compile(r'\\n+')
        s = re.sub(newline, " ", s)
        s = clean.sub(" ", s)
        s = re.sub("'", "", s)
        s = s.lower()
        tokens = delim.split(s)[1:-1]
        # print(token)
        N = len(tokens)
        # tokens = self.lemmatize_tokens(tokens)
        # print(new_tokens[:10])
        for i in range(N):
            if tokens[i] not in common_words:
                if tokens[i] not in self.index:
                    self.index[tokens[i]] = {}
                    self.index[tokens[i]][file_num] = []
                elif file_num not in self.index[tokens[i]]:
                    self.index[tokens[i]][file_num] = []
                self.index[tokens[i]][file_num].append(i)

    def file_name(self, num: int):
        name = "0" * (5 - int(math.log10(num))) + str(num)
        return name

    def readFiles(self, start: int, end: int,  dir=None) -> None:
        for i in range(start, end + 1):
            f_name = self.file_name(i)
            if os.path.isfile(os.path.join(self.path, f_name)):
                f = json.load(open(os.path.join(self.path, f_name),
                                   'r'))
                text = f['text']
                # print(f)
                self.tokenize_add_index(text, f_name)

    def make_it_pretty_ffs(self) -> None:
        f = open('output.txt', 'w+')
        for key, value in sorted(self.index.items(), key=lambda x: x[0]):
            # print(key, end='       ')
            f.write("{} ({}) ==> {{".format(key, len(value)))
            for nestkey, nestvalue in value.items():
                f.write(f"{nestkey} = {len(nestvalue)}, ")
            f.write("}\n")
            # print('\n')
        f.close()

    def create_index_batch(self, start, end, index_no):
        self.index = {}
        start_time = time.time()
        self.readFiles(start, end)
        idx = open(f'index/index_{index_no}.txt', 'a+')
        for key, value in sorted(self.index.items(), key=lambda x: x[0]):
            idx.write("{} : {}\n".format(key, value))
        end_time = time.time()
        print("time taken to create sorted index:", end_time - start_time)
        print(f"SUCCESS: Index {index_no}")
        idx.close()


class Indexer(Thread):

    def __init__(self, queue, invidx):
        Thread.__init__(self)
        self.queue = queue
        self.invidx = invidx

    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            start, end, index = self.queue.get()
            try:
                self.invidx.create_index_batch(start, end, index)
            finally:
                self.queue.task_done()


def main(start, end, index_no):
    ts = time.time()
    i = index_no
    # invidx = InvertedIndex(start, end, index_no)
    queue = Queue()
    while i <= index_no + (end - start) // 1000:
        start_iter = i * 1000 + 1
        end_iter = start_iter + 999 if (start_iter + 999) <= end else end
        logger.info(f'Queueing files {start_iter} to {end_iter}')
        queue.put((start_iter, end_iter, i))
        i += 1
    print(queue.queue)
    for x in range(8):
        worker = Indexer(queue, InvertedIndex())
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()
    queue.join()
    logging.info('Took %s', time.time() - ts)
    # self.make_it_pretty_ffs()
    # print(self.index)


if __name__ == '__main__':
    start = 1
    end = 10000
    index_no = 0
    path = None
    # start = int(sys.argv[1])
    # end = int(sys.argv[2])
    # path = None
    # if len(sys.argv) > 3:
    #     path = sys.argv[3]
    main(start, end, index_no)
