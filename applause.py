import sys
import os
import math
import nltk
import re


#looks for applause to denote for key words
#test data
#research paper

def main():
    if(len(sys.argv)==1):
        print("[USAGE]: python applause.py <filename> (buffsize)")
        print("\t note buffsize is optional")
        print("[Example]: python applause.py trascripts/trump/1-24-06...iowa_freed_speech.txt")

    if(sys.argv[2]):
        buffmax = int(sys.argv[2])
    else:
        buffmax = 50

    currbuff = 0
    buff = []

    with open(sys.argv[1],'r') as fn:

        lines = fn.readlines()
        for line in lines:

            words = nltk.word_tokenize(line.decode('utf-8').lower())
            for word in words:
                if(currbuff != buffmax):
                    buff.append(word)

                #print("word="+word)
            ##print(word+"==")
                if(word == 'laughter' or word == 'applause'  or word == 'cheers'):
                    print(buffer)
                    #print("phrase="+word)

        #print(lines[0].split(" "))
        # count = 0
        # for token in tokens:
        #     print(token)

            # if count == 30:
            #     exit()
            # count += 1

    # return ""


if __name__ == '__main__':
    main()
