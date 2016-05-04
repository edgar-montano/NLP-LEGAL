import sys
import urllib2
import json
import xmltodict
import nltk
import math

from multiprocessing import Pool, TimeoutError


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


phrase_exclusion = [

	"Condition",
	"Plan",
	"Accuracy",
	"Project",
	"Clarification",
	"Rule",
	"Effect",
	"Act",
	"Development",
	"Implementation",
	"Authorization",
	"Use",
	"Status",
	"Mission",
	"Report",
	"Study",
	"Date",
	"Body",
	"Audit",
	"Sense",
	"Requirement",
	"Member",
	"Change",
	"United States",
	"Amendment",
	"Department",
	"Expansion",
	"Record",
	"Establishment",
	"Repeal"

]

mass_PE = []
for pe in phrase_exclusion:
	mass_PE.append(pe)
	mass_PE.append(pe.lower())
	mass_PE.append(pe + "s")
	mass_PE.append(pe.lower() + "s")




class Representative(object):
	def __init__(self,data):
		self.data = data
		self.name = self.data['#text']
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

	def aggregate_phrases(self):
		aggro_phrases = []
		for (_,bill) in self.bill_hash.iteritems():
			phrases = bill.get_phrases()
			for p in phrases:
				if p not in aggro_phrases:
					aggro_phrases.append(p)

		return aggro_phrases

	def get_grade(self,keyword):
		
		(grade,_) = self.get_relevant_bills(keyword)

		return grade

	def get_relevant_bills(self,keyword):
		aggro_grade = 0
		bill_array = []
		for (_,bill) in self.bill_hash.iteritems():
			bill_grade = bill.get_grade(keyword)
			if bill_grade != "N/A":
				print bill_grade
				bill_array.append(bill)
				aggro_grade += bill_grade

		return (aggro_grade,bill_array)


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

		# print spo_info


		self.sponsor = spo_info['sponsor']	
		

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

		self.adjusted_headers = []
		self.phrases = []

		self.grades = {}





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

		if self.adjusted_headers:
			return self.adjusted_headers

		self.adjusted_headers = []

		title_exclusions = [
			"short title",
			"definitions",
			"table of contents",
			"findings",
			"definition",
			"report",
			"statement of policy",
			"purposes",
			"gao report",
			"gao study",
			"staff"

		]


		for head in self.headers:

			exclude = False
			for exclusions in title_exclusions:
				temp_head = head.lower()
				if temp_head == exclusions:
					exclude = True
					break

				if exclusions in temp_head:
					exclude = True
					break

			if not exclude:
				self.adjusted_headers.append(head)

		return self.adjusted_headers

	def keywords(self):
		keywords = self.title + " "
		
		for head in self.excluded_headers():
			keywords += head + " "
		
		tokens = nltk.word_tokenize(keywords)

		return tokens

	def set_sponsor(self):

		temp_spo = [self.sponsor] + self.cosponsors

		for spo in temp_spo:

			name = spo['#text']

			global USRepre_hash
			if not USRepre_hash.get(name):
				USRepre_hash[name] = Representative(spo)
			USRepre_hash[name].add_bill(self)

	def get_phrases(self):

		if self.phrases:
			return self.phrases


		grammar = r"""
		    NBAR:
		        {<NN.*|JJ|VBN>*<NN.*>}  # Nouns and Adjectives, terminated with Nouns
		        
		    NP:
		        {<NBAR>}
		        {<NBAR><IN><NBAR>}  # Above, connected with in/of/etc...
		"""
		chunker = nltk.RegexpParser(grammar)


		
		for header in self.titles_and_exHeaders():

			tagged = nltk.pos_tag(nltk.word_tokenize(header))
			tree = chunker.parse(tagged)		

			for element in tree:
				
				if type(element) is nltk.tree.Tree and element.label() == 'NP':
					phrase = ""
					for subelement in element:
						for token in subelement:
							phrase += token[0] + " "
					phrase = phrase[:-1].encode('utf-8')
					if phrase not in mass_PE:
						self.phrases.append(phrase)


		return self.phrases

	def titles_and_exHeaders(self):

		headers_titles = self.excluded_headers()	
		headers_titles.insert(0,self.title)
		return headers_titles

	def get_grade(self,keyword):



		if self.grades.get(keyword):
			return self.grades[keyword]



		base_words = [
			'fund',
			'require',
			'support',
			'train',
			'expand'

		]

		plus_words = [
			'increas',
			'establish',
			'preserv',
			'addition',
			'eas', # ease


		]

		minus_words = [
			'remov',
			'decreas', #decrease
			'enforc', # enforce
			'stop',
			'penalt', # Penalty
			'reduc', # reduction
			'subtraction',
			'demot',

		]

		base_score = 1
		plusMinus_score = 0

		on_topic = False

		for phrase in self.titles_and_exHeaders():
			mod_phrase = phrase.lower()

			if keyword in mod_phrase:
				on_topic = True
				base_score += 1

			for base in base_words:
				if base in mod_phrase:
					base_score +=1


			for plus in plus_words:
				if plus in mod_phrase:
					plusMinus_score += 1

			for minus in minus_words:
				if minus in mod_phrase:
					plusMinus_score -= 1




		if not on_topic:
			aggregate_score = "N/A"
		elif plusMinus_score >= 0:
			aggregate_score = plusMinus_score + base_score
		else:
			aggregate_score = plusMinus_score - base_score

		self.grades[keyword] = aggregate_score


		return self.grades[keyword]

		

def seperation():
	print "------------------------------------------------------------------------------------------------------------------------------------------"


bills_array = []
congress_number = 114

start = 1600
start = 2538
threshold = 100

# ----------------------------------------------------------- Senate -------------------------------------------------------------------


print "Senate"

for i in range(threshold):
	s_number = start + i
	url = 'https://www.congress.gov/%s/bills/s%s/BILLS-%ss%sis.xml' %(congress_number,s_number,congress_number,s_number)
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

		bills_array.append(Bill(s_number,url,data)) 




seperation()

# ----------------------------------------------------------- House of Representatives ------------------------------------------------


# print "House of Representatives"


# start = 2000
# start = 3449

# threshold = 1

# for i in range(threshold):

# 	hr_number = start + i

# 	url = 'https://www.congress.gov/%s/bills/hr%s/BILLS-%shr%sih.xml' % (congress_number,hr_number,congress_number,hr_number)
# 	print url

# 	try:
# 		file = urllib2.urlopen(url)
# 	except urllib2.HTTPError:
# 		print "404"
# 		continue


# 	data = file.read()
# 	file.close()


# 	data = xmltodict.parse(data)

# 	if data['bill'].get('metadata'):

# 		bills_array.append(Bill(hr_number,url,data)) 


# --------------------------------------------------------------------------------------------------------------------------------------------


seperation()

set_repr_hash(bills_array)

for bill in bills_array:

	print bill
	print bill.url
	print bill.get_phrases()
	print bill.get_grade('immigration')
	seperation()



# seperation()


# for (name,represent) in USRepre_hash.iteritems():
# 	print name
# 	print represent.aggregate_phrases()
# 	seperation()




names_of_interest = [
	"Mr. Sanders",
	"Ms. Pelosi",
	"Mr. Ryan",
	"Ms. Clark",
	"Mr. Cruz"
]

for name in names_of_interest:
	print name
	if USRepre_hash.get(name):
		print USRepre_hash[name].get_grade('immigration')
	else:
		print "NOT PRESENT"





