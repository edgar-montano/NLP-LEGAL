import nltk
import sys
import os

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


    speech = open(fn)
    array_phrases = []

    for line in speech:

    	tagged = nltk.pos_tag(nltk.word_tokenize(line))
    	tree = chunker.parse(tagged)

    	for element in tree:

    		if type(element) is nltk.tree.Tree and element.label() == 'NP':
    			phrase = ""
    			for subelement in element:
    				for token in subelement:
    					phrase += token[0] + " "
    			phrase = phrase[:-1].encode('utf-8')
    			#print phrase
    			if phrase not in array_phrases:
    				array_phrases.append(phrase)



    print array_phrases


if __name__ == '__main__':
    main()
