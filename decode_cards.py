import base64

cards = open('cardmaster\card_master_1')
stats = {}
c1 = cards.readline()
c2 = cards.readline()
# while c != '':
#     if c in stats:
#         stats[c] += 1
#     else:
#         stats[c] = 1
#     c = cards.read(1)
# print(stats)
s1 = base64.b64decode(c1)
s2 = base64.b64decode(c2)
s3 = []
for i in range(65536):
    x = s2[i]
    s3.append(x)
    if x in stats:
        stats[x] += 1
    else:
        stats[x] = 1
#print(s3)
print(max(stats.values()))
print(min(stats.values()))
decoded = open('decoded.txt', 'wb')
decoded.write(s2)
cards.close()
decoded.close()