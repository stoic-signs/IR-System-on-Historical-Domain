import sqlite3


class SpellChecker:
    def __init__(self, word, keys, num, W=1):
        self.word = word
        self.W=W
        self.candidates = []
        self.dictionary = keys
        self.N = num
        self.suggestions = []
    
    def priorOfWord(self, word):
        """
        Language Model Probability
        """
        return self.dictionary[word]/self.N
    
    def likelihoodOfWord(self):
        """
        Channel Model Probability
        """
        return 1/len(self.candidates)
    
    def probabilityOfWord(self, word):
        """
        Noisy Channel Probability
        """
        return self.likelihoodOfWord() * self.priorOfWord(word)
    
    def wordInDict(self, word_list):
        """
        Remove the words from a list that are not in the Dictionary
        """
        for word in word_list:
            if word in self.dictionary:
                yield word
    
    def splitKgrams(self, word):
        """
        Split the word in kgrams for k=1->len(word)
        """
        return [(word[:i], word[i:]) for i in range(len(self.word))]

    def deleteMethod(self, kgrams):
        """
        Generate all candidates that occur after deleting a character
        """
        return [x + y[1:] for x,y in kgrams if y]
    
    def transposeMethod(self, kgrams):
        """
        Generate all candidates that occur after transposing 2 consequent characters
        """
        return [x + y[1] + y[0] + y[2:] for x, y in kgrams if len(y)>1]
    
    def substituteMethod(self, kgrams, alpha):
        """
        Generate all candidates that occur after replacing a charactor with one from the alphabet set
        """
        return [x + c + y[1:] for x, y in kgrams if y for c in alpha]
    
    def insertMethod(self, kgrams, alpha):
        """
        Generate all candidates that occur after inserting a charactor from the alphabet set
        """
        return [x + c + y for x, y in kgrams for c in alpha]
    
    def get_1editWords(self, word):
        """
        Generate all candidates at edit distance 1
        """
        alpha = 'abcdefghijklmnopqrstuvwxyz'
        edited_words = []
        kgrams = self.splitKgrams(word)
        edited_words.extend(self.deleteMethod(kgrams))
        edited_words.extend(self.transposeMethod(kgrams))
        edited_words.extend(self.substituteMethod(kgrams, alpha))
        edited_words.extend(self.insertMethod(kgrams, alpha))
        return edited_words
    
    def get_2editWords(self):
        """
        Generate all candidates at edit distance 2
        This is done by finding candidates for candidates at edit distance 1
        """
        edit2_candidates = [y for x in self.get_1editWords(self.word) for y in self.get_1editWords(word=x)]
        return list(set(edit2_candidates))
    
    def getCandidates(self):
        """
        Finalize the list of candidates by the decided priority (edit distance 1 > edit distance 2)
        """
        self.candidates = list(self.wordInDict(self.get_1editWords(self.word))) or \
                            list(self.wordInDict(self.get_2editWords())) or [self.word]
    
   
    def runSpellCorrector(self):
        """
        Starting point for the spell checker
        Extracts words, generated candidates and returns W number of suggestions
        """
        # self.extractWordIntoDict()
        self.getCandidates()
        if len(self.candidates)>self.W:
            self.suggestions = sorted(self.candidates, key=lambda x: self.probabilityOfWord(x), reverse=True)[:self.W]
        else:
            self.suggestions = sorted(self.candidates, key=lambda x: self.probabilityOfWord(x), reverse=True)



def main(wrong_word):
    conn = sqlite3.connect('inforet.db')
    
    #get list of all keys and their count in dict
    final_dict = {}
    words = list(conn.execute('''SELECT TERMID, TERM FROM TERMSTABLE'''))
    for w in words:
        q = "SELECT SUM(TERMCOUNT) FROM POSITIONALINDEX WHERE TERMID=%d" % w[0]
        count = list(conn.execute(q))[0]
        final_dict[w[1]]=count[0]
    num = list(conn.execute('''SELECT SUM(WORDCOUNT) FROM DOCTABLE'''))[0][0]
    # print(final_dict, num)

    if wrong_word in final_dict.keys():
        return wrong_word

    # wrong = 'one'
    checker = SpellChecker(
        word=wrong_word,
        keys=final_dict,
        num=num
        )
    checker.runSpellCorrector()
    return checker.suggestions[0]



# con = sqlite3.connect('inforet.db')
# con.isolation_level = None
# cur = con.cursor()

# r = cur.execute(''' SELECT TAG FROM TAGSTABLE ''')
# print([r1 for r1 in r])
# # w = input()
# # x = main(w)
# # print(x)