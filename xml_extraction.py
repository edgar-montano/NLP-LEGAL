import sys
import urllib2
import json
import xmltodict
import nltk


month_to_str = {
	"01" : "January",
	"02" : "Feburary",
	"03" : "March",
	"04" : "April",
	"05" : "May",
	"06" : "June",
	"07" : "July",
	"08" : "August",
	"09" : "September",
	"10" : "October",
	"11" : "November",
	"12" : "December"
}

class Bill(object):
	def __init__(self,url,data):
		self.data = data

		self.url = url


		
		# Title
		self.title = data['bill']['metadata']['dublinCore']['dc:title'].split(": ")[1]


		# Date
		raw_date = data['bill']['metadata']['dublinCore']['dc:date']
		if raw_date:
			date_info = raw_date.split('-')
			self.year = date_info[0]
			self.month = month_to_str[date_info[1]]
			self.day = date_info[2]
		else:
			self.month = "Idiot"
			self.day = "coughed"
			self.year = "it up"


		# Sponsors/Cosponsors
		spo_info = data['bill']['form']['action']['action-desc']

		self.sponsor_name = spo_info['sponsor']['#text']
		

		self.cosponsors = []
		if spo_info.get('cosponsor'):

			cospon = spo_info['cosponsor']

			if type(cospon) is list:

				for co in cospon:

					cosponsor_name = co['#text']

					self.cosponsors.append(cosponsor_name)

			else:

				cosponsor_name = cospon['#text']

				self.cosponsors.append(cosponsor_name)

		# Section

		self.headers = []


		section_array = data['bill']['legis-body']['section']

		if type(section_array) is list:


			for section in section_array:

				if not section.get('header'):
					continue


				header = section['header']


				if type(header) is unicode:
					temp_header = header
				else:
					if header.get('act-name'):
						temp_header = header['act-name']
					else:
						temp_header = header['#text']

				self.headers.append(temp_header)
		elif  section_array.get('header'):


			header = section_array['header']

			if type(header) is unicode:
				temp_header = header


			else:
				temp_header = header['#text']

			self.headers.append(temp_header)







	def __str__(self):

		output = self.title + "\n"
		output += "Date: %s %s, %s\n\n" % (self.month,self.day,self.year)


		output += "Sponsor: %s\n" % self.sponsor_name
		output += "Cosponsor(s):\n"

		if len(self.cosponsors) == 0:
			output += "\t((NONE))\n"
		else:
			for co in self.cosponsors:
				output += "\t%s\n" % co


		output += "\nSection(s):\n"

		for head in self.excluded_headers():
			output += "\t%s\n" % head



		return output.encode('utf-8')

	def excluded_headers(self):

		adjusted_headers = []

		title_exclusions = [
			"Short title",
			"Definitions",
			"table of contents",
			"Findings",
			"Definition",
			"Report",
			"Statement of policy",
			"Purposes",
			"Gao report"

		]


		for head in self.headers:

			exclude = False
			for exclusions in title_exclusions:
				if head == exclusions:
					exclude = True
					break

				if exclusions in head:
					exclude = True
					break

			if not exclude:
				adjusted_headers.append(head)

		return adjusted_headers

	def keywords(self):
		keywords = self.title + " "
		
		for head in self.excluded_headers():
			keywords += head + " "
		
		tokens = nltk.word_tokenize(keywords)

		return tokens

def seperation():
	print "------------------------------------------------------------------------------------------------------------------------------------------"



start = 2000

threshold = 50

bills_array = []
for i in range(threshold):

	hr_number = start + i

	url = 'https://www.congress.gov/114/bills/hr%s/BILLS-114hr%sih.xml' % (hr_number,hr_number)
	print url

	try:
		file = urllib2.urlopen(url)
	except urllib2.HTTPError:
		print "404"
		continue

	data = file.read()
	file.close()


	data = xmltodict.parse(data)

	if data['bill'].get('metadata'):

		bills_array.append(Bill(url,data)) 


seperation()

for bill in bills_array:

	print bill
	print bill.url
	print bill.keywords()
	seperation()





