import os
import re
import sys
import time
import math
import json
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from collections import OrderedDict
lemmatizer = WordNetLemmatizer()


class InvertedIndex:
    def __init__(self, start: int, end: int, index_no: int, path=None) -> None:
        self.index = {}
        self.start = start
        self.end = end
        self.index_no = index_no
        self.common_words = stopwords.words('english')
        self.common_words.remove('of')
        self.path = os.path.join(os.getcwd(), 'dataset')
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
            if tokens[i] not in self.common_words:
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
        f = open('output.txt', 'w')
        for key, value in sorted(self.index.items(), key=lambda x: x[0]):
            # print(key, end='       ')
            f.write("{} ({}) ==> {{".format(key, len(value)))
            for nestkey, nestvalue in value.items():
                f.write(f"{nestkey} = {len(nestvalue)}, ")
            f.write("}\n")
            # print('\n')
        f.close()

    def main(self):
        i = self.index_no
        while i <= self.index_no + (self.end - self.start) // 1000:
            self.index = {}
            start = i * 1000 + 1
            end = start + 999 if (start + 999) <= self.end else self.end
            start_time = time.time()
            self.readFiles(start, end)
            idx = open(f'index/index_{i}.txt', 'w')
            idx.write(json.dumps(dict(sorted(self.index.items(), key=lambda t: t[0]))))
            idx.close()
            end_time = time.time()
            print("time taken to create sorted index:", end_time - start_time)
            i += 1
        # self.make_it_pretty_ffs()
        # print(self.index)


if __name__ == '__main__':
    start = 1
    end = 10
    index_no = 0
    path = None
    invidx = InvertedIndex(start, end, index_no, path)
    invidx.main()
