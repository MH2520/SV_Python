import requests
import re
import image
from bs4 import BeautifulSoup

cy_base64 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
lang_list = ('ja', 'en', 'ko', 'zh-tw', 'fr', 'it', 'de', 'es')
link = 'https://shadowverse-portal.com/cards?card_name={}&format={}{}&atk={}&atk_operator={}&life={}&life_operator={}&type={}&skill={}&include_token={}&card_text={}&lang={}&card_offset={}'
img_link = 'https://shadowverse-portal.com/image/card/phase2/common/C/C_{}.png'

# Formats the link for searching cards on shadowverse-portal.com
#  1. name:      card name
#  2. format_:   format that the card is in, 1 = rotation, 3 = unlimited
#  3. clan:      list of classes to include, 0-8 = neutral, forest, sword, rune, dragon, shadow, blood, haven, portal
#  4. cost:      list of costs to include, acceptable range is integers from 0 to 10 (inclusive), 
#                10 denoting cards with cost >= 10
#  5. card_set:  5-digit integers indicating card sets to include, 
#                see svportal_dict in search_dict.py for full explanation
#  6. char_type: card type, 1 = follower, 2 = spell, 3 = amulet
#  7. rarity:    rarity of card, 1-4 = bronze, silver, gold, legendary
#  8. atk:       base value of attack to compare with
#  9. atk_op:    1 denotes attack of card >= atk; 2 denotes <=; 3 denotes ==
#                spells and amulets will only be included when atk=0 and atk_op=1
# 10. life:      base value of life to compare with
# 11. life_op:   similar to atk_op
# 12. type_:     type of card, see type_dict in search_dict.py for full explanation
# 13. skill:     keyword included in card, see skill_list in search_dict.py for full explanation
# 14. include_token: whether to include token in search, 1 = include
# 15. card_text: text in card skills
# 16. lang:      language of the website, see lang_list for list of languages
# 17. offset:    offset of search, starts at 0 (or empty string) and 
#                increases by 12 for each page (as each page contains at most 12 cards)
def link_format(name='', format_=1, clan=[], cost=[], card_set=[], char_type=[], rarity=[], 
                atk=0, atk_op=1, life=0, life_op=1, type_=0, skill='', 
                include_token='', card_text='', lang=3, offset=''):
    extra_str = ''
    for i in clan:
        extra_str += '&clan%5B%5D={}'.format(i)
    for i in cost:
        extra_str += '&cost%5B%5D={}'.format(i)
    for i in char_type:
        extra_str += '&char_type%5B%5D={}'.format(i)
    for i in rarity:
        extra_str += '&rarity%5B%5D={}'.format(i)
    for i in card_set:
        extra_str += '&card_set%5B%5D={}'.format(i)
    return link.format(name, format_, extra_str, atk, atk_op, life, life_op, type_, 
                       skill, include_token, card_text, lang_list[lang], offset)

# Finds the offset number divided by 12 of the last page of a particular search
# See the documenation for link_format for explanations of parameters
def get_last_offset(name='', format_=1, clan=[], cost=[], card_set=[], char_type=[], rarity=[], 
                    atk=0, atk_op=1, life=0, life_op=1, type_=0, skill='', 
                    include_token='', card_text='', lang=3):
    init_link = link_format(name, format_, clan, cost, card_set, char_type, rarity, atk, atk_op, 
                            life, life_op, type_, skill, include_token, card_text, lang)
    content = requests.get(init_link).text
    soup = BeautifulSoup(content, 'html.parser')
    last = soup.find(class_='bl-pagination-item is-last')
    if last == None: # <= 3 pages
        items = soup.find_all(class_='bl-pagination-item')
        if len(items)==0:
            return 0
        else:
            return len(items)//2-2
    else:
        return int(re.search(r'card_offset=(\d*)', last.contents[0].get('href')).group(1))//12
    
# converts card ID to 5-character code
def cy_encode(cid):
    code = ""
    for i in range(5):
        code = cy_base64[cid % 64] + code 
        cid >>= 6
    return code

# converts 5-character code to card ID
def cy_decode(code):
    cid = 0
    cid += cy_base64.find(code[0])
    for i in range(4):
        cid <<= 6
        cid += cy_base64.find(code[i+1])
    return cid

def get_card_data(cid, lang=3):
    if lang < 0 or lang > 7:
        return
    content = requests.get('https://shadowverse-portal.com/card/' + str(cid) + '?lang=' + lang_list[lang]).text
    soup = BeautifulSoup(content, 'html.parser')
    if soup.find(class_='el-heading-error') != None:
        return
    card = {'cid':cid,'lang':lang}
    cd = cid//10
    card['num'] = cd%100
    cd //= 100
    card['type'] = cd%10
    cd //= 10
    card['rarity'] = cd%10
    cd //= 10
    card['class'] = cd%10
    cd //= 10
    card['pack'] = cd
    card['title'] = soup.find(class_='card-main-title').get_text()
    
    if len(card['title']) > 0:
        card['title'] = card['title'].strip('\r\n')
        if lang == 0:
            card['title'] = re.sub(r'\(.*?\)', '', card['title'])
    
    skills = soup.find_all(class_='card-content-skill')
    card['skill0'] = skills[0].get_text('\n')
    if len(card['skill0']) > 0:
        card['skill0'] = card['skill0'].strip('\r\n')
    
    descs = soup.find_all(class_='card-content-description')
    card['desc0'] = descs[0].get_text('\n')
    if len(card['desc0']) > 0:
        card['desc0'] = card['desc0'].strip('\r\n')
    
    if card['type'] == 1:
        atks = soup.find_all(class_='el-card-status is-atk')
        lifes = soup.find_all(class_='el-card-status is-life')
        if len(atks) == 1: # Without un-evolved form
            card['atk0'] = 0
            card['atk1'] = int(atks[0].get_text())
            card['life0'] = 0
            card['life1'] = int(lifes[0].get_text())
            card['skill0'] = ''
            card['skill1'] = skills[0].get_text('\n')
            card['desc0'] = ''
            card['desc1'] = descs[0].get_text('\n')
        else:
            card['atk0'] = int(atks[0].get_text())
            card['atk1'] = int(atks[1].get_text())
            card['life0'] = int(lifes[0].get_text())
            card['life1'] = int(lifes[1].get_text())
            card['skill1'] = skills[1].get_text('\n')
            card['desc1'] = descs[1].get_text('\n')
        if len(card['skill1']) > 0:
            card['skill1'] = card['skill1'].strip('\r\n')
        if len(card['desc1']) > 0:
            card['desc1'] = card['desc1'].strip('\r\n')
    
    information = [text for text in soup.find(class_='card-info').stripped_strings]
    if lang == 0 or lang == 3:
        if len(information) == 15:
            info = [information[2],information[4],information[6],information[8],information[10],information[12],information[14]]
        else:
            info = [information[2],information[4],information[6],information[8],' '.join(information[10:13]),information[14],information[16]]
    else:
        if len(information) == 13:
            info = [information[2],information[4],information[6],information[8],information[10],information[12]]
        else:
            info = [information[2],information[4],information[6],information[8],' '.join(information[10:13]),information[14]]
    card['info'] = info
    
    relatives = soup.find_all(class_='el-card-detail')
    rels = []
    for relative in relatives:
        rels.append(int(relative.get('href')[-9:]))
    card['rels'] = rels
    return card

def download_img(img_url, cid):
    r = requests.get(img_url, stream=True)
    print(r.status_code)
    if r.status_code == 200:
        open('{}.png'.format(cid), 'wb').write(r.content)
        print(cid+" downloaded")
    del r

def download_img_and_compress(cid, size=(199,259)):
    download_img(img_link.format(cid), cid)
    img = Image.open(cid+'.png')
    img.thumbnail(size,Image.ANTIALIAS)
    img.save('small_{}.png'.format(cid),'png')

def get_hash(link):
    if link.find('deckbuilder') >= 0:
        if link.find('lang=') == -1:
            link = link + '&lang=zh-tw'
        return re.search('hash=(.*?)&lang=', link).group(1)
    elif link.find('deck/') >= 0:
        if link.find('lang=') == -1:
            link = link + '?lang=zh-tw'
        return re.search('deck/(.*?)\?lang=', link).group(1)
    else:
        return 'Not a valid deck link'
    
def hash_breakdown(hs):
    s = hs.split('.')
    b = [int(s[0]), int(s[1])]
    for i in range(2, len(s)):
        b.append(cy_decode(s[i]))
    return b

def link_from_hash(hs, lang=3):
    return 'https://shadowverse-portal.com/deck/{}?lang={}'.format(hs, lang_list[lang])

if __name__ == '__main__':
    # link1 = 'https://shadowverse-portal.com/deckbuilder/create/6?hash=3.6.6v3oc.72BIC.72GAY.72Icy.761tS.764Ji.6-Ntw.6v1MC.6v6Ei.6yrV2.gYEAw.6wgKo.72GAi.75_R2.6v8gy.74b5y.78L5A.72GvQ.6v8go.70myy.74Yfi.78MoY.78Moi.6-S1i.767Ug.gYGdA.6-UTo.6yypo.74TnM.78PEo.70kWY.74b5o.74b5o.74b5o.6-N92.6v8h6.74TnC.766lo.6yyq6.74b66'
    # link2 = 'https://shadowverse-portal.com/deck/3.5.745Mi.745Mi.745Mi.77xxo.77xxo.77xxo.72BIC.72BIC.72BIC.761tS.761tS.761tS.745Ms.745Ms.745Ms.77vW0.77vW0.77vW0.7Bm4y.7Bm4y.6yTpQ.6yTpQ.72DkI.72DkI.72DkI.745MY.745MY.745MY.77vVi.77vVi.77vVi.747oy.747oy.747oy.748Xg.748Xg.748Xg.747oo.747oo.747oo?lang=en'
    # print(link_from_hash(get_hash(link1)))
    # print(hash_breakdown(get_hash(link2)))
    for i in range(8):
        print(get_card_data(100721020,i))