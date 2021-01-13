import requests
import re
from PIL import Image
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
                atk=0, atk_op=1, life=0, life_op=1, type_='', skill='', 
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
                    atk=0, atk_op=1, life=0, life_op=1, type_='', skill='', 
                    include_token='', card_text='', lang=3):
    init_link = link_format(name, format_, clan, cost, card_set, char_type, rarity, atk, atk_op, 
                            life, life_op, type_, skill, include_token, card_text, lang)
    content = requests.get(init_link).text
    soup = BeautifulSoup(content, 'html.parser')
    last = soup.find(class_='bl-pagination-item is-last')
    if last == None:
        return 0
    else:
        return int(re.search('card_offset=(\d*)', last.contents[0].get('href')).group(1))//12
    
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
        card['title'] = card['title'][2:-2]
    
    skills = soup.find_all(class_='card-content-skill')
    card['skill0'] = skills[0].get_text('\n')
    if len(card['skill0']) > 0:
        card['skill0'] = card['skill0'][2:-2]
    
    descs = soup.find_all(class_='card-content-description')
    card['desc0'] = descs[0].get_text('\n')
    if len(card['desc0']) > 0:
        card['desc0'] = card['desc0'][2:-2]
    
    if cid//1000%10 == 1:
        atks = soup.find_all(class_='el-card-status is-atk')
        card['atk0'] = int(atks[0].get_text())
        card['atk1'] = int(atks[1].get_text())
        lifes = soup.find_all(class_='el-card-status is-life')
        card['life0'] = int(lifes[0].get_text())
        card['life1'] = int(lifes[1].get_text())
        card['skill1'] = skills[1].get_text('\n')
        if len(card['skill1']) > 0:
            card['skill1'] = card['skill1'][2:-2]
        card['desc1'] = descs[1].get_text('\n')
        if len(card['desc1']) > 0:
            card['desc1'] = card['desc1'][2:-2]
    
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

if __name__ == '__main__':
    print(get_last_offset(name='b'))
    # for i in range(8):
    #     print(get_card_data(118141010,i))