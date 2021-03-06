# choose_phonemes.py
#
# requires `phoible-phonemes.tsv` from https://github.com/phoible/dev/releases/tag/v2014
# to be placed in `..\data\`

import csv
import matplotlib.pyplot as plt
import pickle

MODIFIERS = {'ː', 'ˑ', 'ʷ', 'ʲ', 'ˠ', 'ˤ', 'ˀ'} #accents that are more important on their own than in combo with other sounds
ACCENTS = {'̪', '̞', '̟', '̝', '̙', '̘', '̈', '̠', '͉', '̻', '̺', '͇', '̯', '͓', '˔'} #accents that my data source abuses and that mean nothing to me

COMBOS = {('a','ɑ','ɐ'), ('e','ɛ'), ('o','ɔ'),
		('i','ɪ'), ('u','ʊ','ɯ'), ('j','i'), ('w','u'),
		('ʃ','ɕ','ʂ'), ('ʒ','ʑ','ʐ'), ('dʒ','dʑ','ɖʐ'), ('tʃ','tɕ','ʈʂ'),
		('ʈʂ','ʂ','tʃ','ʃ'), ('ɖʐ','ʐ','dʒ','ʒ'), ('s','z'),
		('r','ɾ','ɽ','ɻ','ʁ','ʀ','ɹ'), ('l','ɭ','ɾ','ɽ','ɺ'),
		('h','ħ','χ','x', 'ɦ'), ('ʕ','ʁ','ɣ'), ('f','ɸ'), ('v','β','ʋ'),
		('kʰ','k'), ('tʰ','t'), ('pʰ','p'),
		('k','ɡ','ʰ'), ('t','d','ʰ'), ('p','b','ʰ'),
		('ɡ','ɣ','ʰ'), ('d','ð','ʰ'), ('b','β','ʰ')}

# OLTILIP = {'/pʰ/', '/b/', '/tʰ/', '/d/', '[ts]', '/tʃ/', '/dʒ/', '/kʰ/', '/ɡ/', '/f/', '/v/', '[s]', '[z]', '/ʃ/', '/ʒ/', '[x]', '[h]',
# 			'[m]', '[n]', '/r/', '[l]', '[j]', '/w/', '/i/', '/u/', '/e/', '/o/', '/a/'} # Esperanto
# OLTILIP = {'/pʰ/', '/b/', '/tʰ/', '/d/', '/tʃ/', '/dʒ/', '/kʰ/', '/ɡ/', '/f/', '/s/', '/ʃ/', '/h/',
# 			'[m]', '[n]', '[ŋ]', '/r/', '[l]', '/j/', '/ʋ/', '/i/', '/u/', '/e/', '/o/', '/a/'} # all 24 common phonemes
# OLTILIP = {'/pʰ/', '/b/', '/tʰ/', '/d/', '/kʰ/', '/ɡ/', '/ʈʂ/', '/f/', '/s/', '/ʃ/', '/h/',
# 			'[m]', '[n]', '/l/', '/j/', '/ʋ/', '/i/', '/u/', '/e/', '/o/', '/a/'} # 20 more common phonemes (sin /r/ y /ŋ/)
OLTILIP = {'/p/', '/t/', '/k/', '/ʈʂ/', '/f/', '/s/', '/h/', '[m]', '[n]', '/w/', '/l/', '/j/',
			'/u/', '/i/', '/o/', '/a/', '/e/'} # only the 17 that half of people can say


with open('..\\data\\ethnologue.pkl', 'rb') as f:
	POPULATIONS = pickle.load(f)

with open('..\\data\\phoible.tsv', 'r', encoding='utf-8') as f:
	reader = csv.reader(f, delimiter=',')
	header = None
	data_sets = {}
	inventories = {}
	language_names = {}
	for row in reader:
		data_idx, lang_code, lang_name, phoneme, clazz = row[0], row[2], row[3], row[6], row[9]

		if header is None:
			header = row
			continue
		if lang_code not in inventories:
			data_sets[lang_code] = data_idx
			inventories[lang_code] = set()
			language_names[lang_code] = lang_name
		if data_sets[lang_code] == data_idx: #only use the first instance of each language
			for mod in MODIFIERS: #pull out some uncommon modifiers
				if mod in phoneme:
					phoneme = phoneme.replace(mod,'')
					inventories[lang_code].add('{}[{}]:'.format(clazz[0].upper(), mod))
			for accent in ACCENTS: #pull out some useless accents, but don't make note of them
				phoneme = phoneme.replace(accent, '') #go away!
			if clazz == 'tone': #with tones, the number matters more than the exact value
				for num_tones in range(10,-1,-1):
					if str(num_tones)+'T: ' in inventories[lang_code] or num_tones <= 0: #count tones
						inventories[lang_code].add(str(num_tones+1)+'T: ')
						break
			inventories[lang_code].add('['+phoneme+']:')

			for allophone_set in COMBOS:
				if phoneme in allophone_set:
					inventories[lang_code].add('/'+allophone_set[0]+'/:')
				elif 'ʰ' in allophone_set and 'ʰ' in phoneme and phoneme.replace('ʰ','') in allophone_set:
					inventories[lang_code].add('/'+allophone_set[0]+'/:')

for lang_code, inventory in inventories.items(): #get useful information about stop distinctions
	if '[k]:' in inventory and '[ɡ]:' in inventory: 	inventory.add('[VP]:') #voiced/voiceless plosive distinction
	if '[k]:' in inventory and '[kʰ]:' in inventory: 	inventory.add('[AP]:') #aspirated/unaspirated plosive distinction
	if '[ɡ]:' in inventory and '[kʰ]:' in inventory: 	inventory.add('[XP]:') #voiceless aspirated/voiced unasp
	if '[VP]:' in inventory or '[XP]:' in inventory:  	inventory.add('/VP/:')
	if '[AP]:' in inventory or '[XP]:' in inventory:  	inventory.add('/AP/:')

phonemes = {}
total_pop = 0
for lang_code, inventory in inventories.items():
	population = POPULATIONS.get(lang_code, (0,0))[1]
	for phoneme in inventory:
		phonemes[phoneme] = phonemes.get(phoneme,0) + population
	total_pop += population
	print(population)

num_who_must_learn = [0]*(len(OLTILIP)+1) #find the number of humans who must learn _x_ new phonemes to speak Djastiz
avg_num_to_learn = 0
specific_needs = {}
for lang_code, inventory in inventories.items():
	population = POPULATIONS.get(lang_code, (0,0))[1]
	num_to_learn = 0
	for phoneme in OLTILIP:
		if phoneme+':' not in inventory:
			num_to_learn += 1
			if population:
				specific_needs[lang_code] = specific_needs.get(lang_code, []) + [phoneme]
	num_who_must_learn[num_to_learn] += population
	avg_num_to_learn += num_to_learn*population/total_pop

for i, num in enumerate(num_who_must_learn):
	if num == 0:
		break
	elif i == 0:
		print('{:.2%} of humans can pronounce Oltilip words natively.'.format(num/total_pop))
	else:
		print('{:.2%} of humans must learn {} new phonem{} to pronounce Oltilip words.'.format(num/total_pop, i, 'es' if i>1 else 'e'))
print('The average human must learn {:.2f}/{} phonemes to pronounce Oltilip words.'.format(avg_num_to_learn, len(OLTILIP)))

print()

for lang_code, missing_phns in sorted(specific_needs.items(), key=lambda it:POPULATIONS[it[0]][1], reverse=True)[:10]:
	phn_list = ", ".join(missing_phns[:-1])+", or "+missing_phns[-1] if len(missing_phns)>1 else missing_phns[0]
	print("{} ({}) doesn't have {}".format(language_names[lang_code], lang_code, phn_list))

print()

for phoneme in sorted(phonemes.keys(), key=lambda p:-phonemes[p]):
	print("{}\t{:.2f}%".format(phoneme, 100*phonemes[phoneme]/total_pop))

plt.pie(num_who_must_learn, labels=["Native"]+["{} phn.".format(i) for i in range(1,len(OLTILIP)+1)], startangle=-90)
plt.axis('equal')
plt.show()
