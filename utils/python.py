import re
origtext = "Here is Banana."
origtext = origtext.lower()

alist = []
words = re.findall('[a-z]+', origtext)
for word in words:
    length = len(word)
    for i in range(length):
        for j in range(i,length):
            if word[i:j + 1] not in alist:
                alist.append(word[i:j + 1]) 
alist.sort()

result_list = []
for s in alist:
	count = origtext.count(s)
	result_list.append({
		"str": s,
		"count": count
		})
result_list = sorted(result_list, key=lambda d: d['count'], reverse=True) 

result_str = ""
for item in result_list:
	result_str += str(item["count"]) + ":" + item["str"] + "\n"
print(result_str)