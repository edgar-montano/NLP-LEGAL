##############
# phrase extraction tool
# caches results using pickle, then creates dictionary and counts word frequency
################

import nltk
import sys
import os
import os.path
import pickle #caching mechanism

# def picke_isEmpty(fn):
#     try:
#         fileobj = open(fn,"wb")
#         return picke.load(fileobj)
#     except EOFError:
#         return None
#     except IOError,e:
#         return None

def main():
    if(len(sys.argv) != 2):
        print("Usage: phrase_extraction.py <file_name>")
        exit()
    fn = sys.argv[1] # set filename
    grammar = r"""
        NBAR:
            {<NN.*|JJ|VBN>*<NN.*>}  # Nouns and Adjectives, terminated with Nouns

        NP:
            {<NBAR>}
            {<NBAR><IN><NBAR>}  # Above, connected with in/of/etc...
    """
    chunker = nltk.RegexpParser(grammar)

    cached = fn+".pickle" #checked version phrase extraction
    #if a cached version exists we dont have to iterate and extract, just load array

    if(os.path.isfile(cached) ):
        array_phrases = pickle.load(open(cached,"r")) #load the array list
        # array_phrases = pickle.load(open(cached,"r")) #load the array list

    #if the file doesnt exist we have to
    else:
        speech = open(fn)
        array_phrases = []

        for line in speech:

        	tagged = nltk.pos_tag(nltk.word_tokenize(line.decode('utf-8')))
        	tree = chunker.parse(tagged)

        	for element in tree:

        		if type(element) is nltk.tree.Tree and element.label() == 'NP':
        			phrase = ""
        			for subelement in element:
        				for token in subelement:
        					phrase += token[0] + " "
        			phrase = phrase[:-1].encode('utf-8')
        			#print phrase

        			array_phrases.append(phrase)

        #dump array phrases into cached file
        fileobj = open(cached,"wb")
        pickle.dump(array_phrases,fileobj)


    # print(array_phrases)
    #print array_phrases
    dict = {};
    #memset dictionary to 0
    for i in range(len(array_phrases)):
        key = array_phrases[i].replace(" ","_") #key friendly
        if key in dict:
            dict[key.lower()] += 1 #if phrase exist, increment counter
        else:
            dict[key.lower()] = 1 #if phrase doesnt exist, init counter

    print(dict)


if __name__ == '__main__':
    main()
