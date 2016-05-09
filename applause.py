import sys
import os
import math
import nltk
import re
import pickle


#looks for applause to denote for key words
#test data
#research paper

def main():
    if(len(sys.argv)==1):
        print("[USAGE]: python applause.py <filename> (buffsize)")
        print("\t note buffsize is optional")
        print("[Example]: python applause.py trascripts/trump/1-24-06...iowa_freed_speech.txt")

    if(len(sys.argv)==3):
        buffmax = int(sys.argv[2])
    else:
        buffmax = 100

    currbuff = 0
    buff = []
    picke_file_iteration = 0 #determines extension of  pickle file

    with open(sys.argv[1],'r') as fn:

        lines = fn.readlines()
        for line in lines:

            words = nltk.word_tokenize(line.decode('utf-8').lower())
            for word in words:
                #reset the buffer
                if(currbuff == buffmax):
                    currbuff = 0
                    buff = []

                buff.append(word)
                currbuff += 1

                #print("word="+word)
            ##print(word+"==")
                if(word == 'laughter' or word == 'applause'  or word == 'cheers'):
                    fn = sys.argv[1]+str(picke_file_iteration)+".pickle"
                    picke_file_iteration += 1
                    print("printing buffer\n--------------\n")
                    with open(fn, 'wb') as handle:
                        pickle.dump(buff, handle)
                    print(buff)
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
