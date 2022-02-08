import random

#create an empty dictionary
d = {}

key = 0

#open dictionary file and store it in 'dic'
with open('dictionaries/nouns.rtf',encoding="utf8", errors='ignore') as dic:
    #read every line and give it a number
    for line in dic:
        #.rstrip() removes all kinds of whitespace by default. To specify to strip the \n, you have to put it inside the function
        ##STRIPING \N >>>>>>https://stackoverflow.com/questions/275018/how-can-i-remove-a-trailing-newline
        value = line.replace('\\', '')
        key += 1
        d[key] = value
    #print(d)

#PYTHON'S RANDOM MODULE >>>>> https://www.w3schools.com/python/module_random.asp


#select a random number in the range of the dictionary (and store it in a variable)
rand = random.randrange(1, len(d) + 1)

print(rand)
#get the word with that number (and store it in a variable)
word = d[rand]

#print(word)


