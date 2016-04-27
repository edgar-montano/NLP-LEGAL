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

class Representative(object):
	def __init__(self,data):
		self.data = data

		self.bill_hash = {}


	def add_bill(self,bill):
		hr_number = bill.hr_number
		if not self.bill_hash.get(hr_number):
			self.bill_hash[hr_number] = bill

	def __str__(self):
		output = self.data['#text'] + "\n"

		for (hr_number,bill) in self.bill_hash.iteritems():
			# print bill
			output += "\t" + str(hr_number) + "\n"

		return output.encode('utf-8')

def set_repr_hash(bills_array):
	for bill in bills_array:
		bill.set_sponsor()




USRepre_hash = {}

class Bill(object):
	def __init__(self,hr_number,url,data):
		self.data = data

		self.hr_number = hr_number
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


		self.sponsor = spo_info['sponsor']


		# self.sponsor_name = spo_info['sponsor']['#text']
		

		self.cosponsors = []
		if spo_info.get('cosponsor'):


			cospon = spo_info['cosponsor']

			if type(cospon) is list:
				for co in cospon:
					self.cosponsors.append(co)
			else:
				self.cosponsors.append(cospon)

		
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





	def get_sponsor_name(self):
		return self.sponsor['#text']

	def get_cosponsors_str(self):
		co_array = []
		if len(self.cosponsors) == 0:
			co_array.append("((NONE))")
		else:
			for co in self.cosponsors:
				co_array.append(co['#text'])

		return co_array
				

	def __str__(self):

		output = self.title + "\n"
		output += "Date: %s %s, %s\n\n" % (self.month,self.day,self.year)

		output += "Sponsor: %s\n" % self.get_sponsor_name()
		output += "Cosponsor(s):\n"


		for cospon in self.get_cosponsors_str():
			output += "\t%s\n" % cospon


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

	def set_sponsor(self):

		temp_spo = [self.sponsor] + self.cosponsors

		for spo in temp_spo:
			name_id = spo['@name-id']

			global USRepre_hash
			if not USRepre_hash.get(name_id):
				USRepre_hash[name_id] = Representative(spo)
			USRepre_hash[name_id].add_bill(self)




		

def seperation():
	print "------------------------------------------------------------------------------------------------------------------------------------------"





start = 2000

threshold = 100

bills_array = []
for i in range(threshold):

	hr_number = start + i

	url = 'https://www.congress.gov/114/bills/hr%s/BILLS-114hr%sih.xml' % (hr_number,hr_number)
	print url

	# Edgar Fix it
	try:
		file = urllib2.urlopen(url)
	except urllib2.HTTPError:
		print "404"
		continue

	data = file.read()
	file.close()


	data = xmltodict.parse(data)

	if data['bill'].get('metadata'):

		bills_array.append(Bill(hr_number,url,data)) 


seperation()

set_repr_hash(bills_array)

for bill in bills_array:

	print bill
	print bill.url
	print bill.keywords()
	seperation()

seperation()

for (represent_id,represent) in USRepre_hash.iteritems():
	print represent_id
	print represent
	seperation()

 



