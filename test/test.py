import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

feedsarray=[]

feedsarray.clear()
feedsfile = open(BASE_DIR + "/feedtimes.txt", "r")
for i,x in enumerate(feedsfile):
    try:
        feedsarray[i] = x
    except:
        feedsarray.append(x)

for c,y in enumerate(feedsarray):
    if(y != '\n' and y != ''):
        print("Feed " + str(c+1) + ": " + str(y))
