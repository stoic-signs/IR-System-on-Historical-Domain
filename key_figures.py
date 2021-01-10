from pprint import pprint
import time
import spacy
# from spacy import displacy
# from collections import Counter
import en_core_web_sm
nlp = en_core_web_sm.load()

precedence = ['NORP', 'PERSON', 'ORG']
order = {key: i for i, key in enumerate(precedence)}


def figures(text):
    # start = time.time()
    doc = nlp(text)
    # print(f"Time taken: {time.time()-start} sec")
    kf = set((X.text, X.label_)
             for X in doc.ents if X.label_ == "PERSON" or X.label_ == "ORG" or X.label_ == "NORP")
    return list(sorted(kf, key=lambda x: order[x[1]]))


# spacy_ner(ex3)


ex = "The Ariostazo (Spanish: El Ariostazo) occurred on August 25, 1939, and was a brief revolt of the Tacna artillery regiment, led by General Ariosto Herrera, in what turned out to be a non-violent attempt against the government of Chilean President Pedro Aguirre Cerda.\n\nBackground\nPedro Aguirre Cerda was elected and assumed as president on December 25, 1938, as the candidate of the Popular Front. He had narrowly defeated conservative candidate Gustavo Ross in the presidential elections of 1938. General Ariosto Herrera, the commander of the Army Division stationed in Santiago, was a supporter of former president Carlos Ib\u00e1\u00f1ez del Campo and very much influenced by the fascist ideas he had absorbed while a military attach\u00e9 in Italy during the 1930s. He was also very much opposed to the Popular Front.\nOn May 21, 1939, as General Herrera was arriving to the Presidential Palace for a ceremony, he saw a red flag hanging from one of the balconies and in a sudden impulse grabbed it and tore it down. The \"flag incident\" was picked up as an insult to the new government and a formal inquiry was instituted in order to remove him from his command. He was eventually forced into retirement, and immediately started to conspire to bring down the government.\n\nEvents\nOn August 25, 1939, General Herrera together with General Carlos Ib\u00e1\u00f1ez del Campo arrived to the Tacna Regiment in Santiago, with the intention of insurrecting it and forcing the resignation of President Aguirre Cerda.  Nonetheless, the commander of said Regiment, Colonel Luco, had been previously notified of the intentions of the plotters and proceeded to arrest General Herrera as soon as he arrived and to prevent the entry to General Ib\u00e1\u00f1ez. In view of the arrest of their leader, the rest of the military units involved decided to back down. Due to these events 36 officers that were participants in the plot were subsequently purged from the army.\n\nSee also\nSeguro Obrero massacre\nList of Chilean coups d'\u00e9tat\nHistory of Chile\nOperation Bolivar\n\n\n== Footnotes and reference"
# spacy_ner(ex)
figures(ex)
