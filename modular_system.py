import sys
import os
import nltk
import re


def main():
    with open("modular.config","r") as fn:
        lines = fn.readlines()
        for line in lines:
            print("Executing line: "+line)
            os.system(line)


if __name__=='__main__':
    main()
