import sys
import json

md5 = open(sys.argv[1], 'r')

arr = []

for line in md5:
	parts = line.split()
	dic = {'file': parts[1], 'md5': parts[0]}
	arr.append(dic)

print json.dumps(arr)
