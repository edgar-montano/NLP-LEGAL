import urllib
import urllib2
import requests
import sys


def main():
    if(len(sys.argv)>3):
        print("USAGE: python download_test_data.py <threshold> <range_counter>")
        print("Default usage will set threshold to 50, range_counter will be set to 2000")
        threshold = 50
        range_counter = 2000
    elif(len(sys.argv) == 3):
        threshold = int(sys.argv[1])
        range_counter = int(sys.argv[2])
    else:
        threshold = 50
        range_counter = 2000

    for i in range(range_counter,range_counter+threshold):
        url = 'https://www.congress.gov/114/bills/hr%s/BILLS-114hr%sih.xml' % (i,i)
        fn = "HR_"+str(i)+".xml"

        #print "downloading with urllib"
        urllib.urlretrieve(url, fn)

        # print "downloading with urllib2"
        f = urllib2.urlopen(url)
        data = f.read()
        with open(fn, "wb") as code:
            code.write(data)


if __name__ == "__main__":
    main()
