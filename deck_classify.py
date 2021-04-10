import util
from deck_classify_dict import rot_deck, unl_deck
from altart_dict import alt2std

classes = ['精灵', '皇室', '法师', '龙族', '死灵', '吸血鬼', '主教', '复仇者']

# Counts the number of each card and checks legality of the deck
# Standardizes all alt-art cards in the deck
# Input: hash of a deck, which can be obtained by util.get_hash
# Output: class number and a dictionary mapping card id to the number of copies in deck
def count_cards(hs):
    bd = util.hash_breakdown(hs)
    if len(bd) != 42:
        return (0, 'Illegal Deck')
    cl = bd[1]
    cnt = {}
    for i in range(2, len(bd)):
        if bd[i]//100000%10 != cl and bd[i]//100000%10 != 0:
            return (0, 'Illegal Deck')
        cid = bd[i]
        if bd[i] in alt2std:
            cid = alt2std[bd[i]]
        if cid not in cnt:
            cnt[cid] = 1
        else:
            cnt[cid] += 1
    return (cl, cnt)

def classify(mode, cl, cnt):
    if mode == 0: # rotation
        for (deck, criterion) in rot_deck:
            if cl != criterion[0]:
                continue
            for i in range((len(criterion)-1)/3):
                cid = criterion[3*i+1]
                op = criterion[3*i+2]
                num = criterion[3*i+3]
                if op == 0: # >=
                    if cid not in cnt or cnt[cid] < num:
                        continue
                elif op == 1: # <=
                    if cid in cnt and cnt[cid] > num:
                        continue
            return deck
    else # unlimited
        for (deck, criterion) in unl_deck:
            if cl != criterion[0]:
                continue
            for i in range((len(criterion)-1)/3):
                cid = criterion[3*i+1]
                op = criterion[3*i+2]
                num = criterion[3*i+3]
                if op == 0: # >=
                    if cid not in cnt or cnt[cid] < num:
                        continue
                elif op == 1: # <=
                    if cid in cnt and cnt[cid] > num:
                        continue
            return deck
    return '其它' + classes[cl-1]

if __name__ == '__main__':
    print('0')