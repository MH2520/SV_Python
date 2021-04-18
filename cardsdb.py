import sqlite3
import util
import requests
import re
import argparse
from altart_dict import alt2std, std2alt
from search_dict import svportal_packs, alt_packs

cid_pattern = re.compile('<a href="/card/(.*?)" class="el-card-visual-content">', re.S)
title_pattern = re.compile('<p class="el-card-visual-name">(.*?)</p>', re.S)

evo_text = [['進化前', '進化後'],
            ['Unevolved', 'Evolved'],
            ['진화전', '진화후'],
            ['進化前', '進化後'],
            ['Avant évolution', 'Après évolution'],
            ['Pre-evoluzione', 'Post-evoluzione'],
            ['Grundform', 'Entwickelt'],
            ['Pre-evolución', 'Post-evolución']]

class_text = [['ニュートラル', 'エルフ', 'ロイヤル', 'ウィッチ', 'ドラゴン', 
               'ネクロマンサー', 'ヴァンパイア', 'ビショップ', 'ネメシス'],
              ['Neutral', 'Forestcraft', 'Swordcraft', 'Runecraft', 
               'Dragoncraft', 'Shadowcraft', 'Bloodcraft', 'Havencraft', 
               'Portalcraft'],
              ['중립', '엘프', '로얄', '위치', '드래곤', '네크로맨서', 
               '뱀파이어', '비숍', '네메시스'],
              ['中立', '精靈', '皇家護衛', '巫師', '龍族', '死靈法師', '吸血鬼', 
               '主教', '復仇者'],
              ['Neutres', 'Sylvestres', 'Royaux', 'Ésotériques', 'Draconiques', 
               'Nécromanciers', 'Vampiriques', 'Ecclésiastiques', 'Dimensionnels'],
              ['Neutrale', 'Silvani', 'Legioni Reali', 'Esoterici', 'Draconici', 
               'Necromanti', 'Sanguinari', 'Chierici', 'Dimensionali'],
              ['Neutral', 'Waldgeister', 'Königsarmee', 'Magi', 'Drachenblut', 
               'Nekromanten', 'Sanguine', 'Klerisei', 'Machinae'],
              ['Neutral', 'Forestal', 'Imperial', 'Rúnico', 'Dracónico', 
               'Nigromante', 'Vampírico', 'Clerical', 'Dimensional']]

rar_text = [['ブロンズ', 'シルバー', 'ゴールド', 'レジェンド'],
            ['Bronze', 'Silver', 'Gold', 'Legendary'],
            ['브론즈', '실버', '골드', '레전드'],
            ['青銅', '白銀', '黃金', '傳說'],
            ['Bronze', 'Argent', 'Or', 'Légendaire'],
            ['Bronzo', 'Argento', 'Dorata', 'Leggendaria'],
            ['Bronze', 'Silber', 'Gold', 'Legendär'],
            ['Bronce', 'Plata', 'Oro', 'Legendaria']]

type_text = [['フォロワー', 'アミュレット', 'アミュレット', 'スペル'],
             ['Follower', 'Amulet', 'Amulet', 'Spell'],
             ['추종자', '마법진', '마법진', '주문'],
             ['從者', '護符', '護符', '法術'],
             ['Combattants', 'Amulettes', 'Amulettes', 'Sorts'],
             ['Difensori', 'Amuleti', 'Amuleti', 'Magie'],
             ['Vasallen', 'Amulette', 'Amulette', 'Zaubersprüche'],
             ['Combatientes', 'Amuletos', 'Amuletos', 'Hechizos']]

rel_text = ['関連カード', 'Related Cards', '관련 카드', '相關卡片', 
            'Cartes liées', 'Carte Relazionate', 'Verwandte Karten', 
            'Cartas Relacionadas']

promo_text = ['プライズ', 'Promo', '한정', '永久卡', 'Spécial', 
              'Premio', 'Preis', 'Premio']

token_text = ['トークン', 'Token', '토큰', '特殊卡', 'Carte jeton', 
              'Carta Token', 'Token', 'Cartas Token']

# List of cards with cost > 10
high_cost_list = {
    109441010: 11,
    118641030: 11,
    116141010: 12,
    111541030: 12,
    113541010: 12,
    115341010: 15,
    714341010: 15,
    900344020: 15,
    119441020: 17,
    116341020: 18,
    110341010: 20,
    711341010: 20,
    101334020: 20}

# Starts the connection with the database and returns the connection and a cursor
# Create the table cards if it doesn't exist
# Explanation of columns:
#  1. CID:    int;  card ID, the 9-digit ID that specifies a card
#  2. lang:   int;  language, 0-7 = ja, en, ko, zh-tw, fr, it, de, es
#  3. num:    int;  digits 7, 8 of CID distinguishing cards with the same first 6 digits
#  4. type:   int;  digit 6 of CID, 1-4 = follower, amulet, countdown amulet, spell
#  5. rarity: int;  digit 5 of CID, 1-4 = bronze, silver, gold, legendary
#  6. class:  int;  digit 4 of CID, 0-8 = neutral, forest, sword, rune, 
#                   dragon, shadow, blood, haven, portal
#  7. pack:   int;  first 3 digits of CID showing the card pack of the card, 
#                   see cardsdb_dict in search_dict.py for full explanation
#  8. title:  text; name of the card
#  9. cost:   int;  original cost of the card
# 10. skill0: text; skill of the card before evo
# 11. desc0:  text; flavor text before evo
# 12. atk0:   int;  attack of the card before evo (follower only)
# 13. atk1:   int;  attack of the card after evo (follower only)
# 14. life0:  int;  life of the card before evo (follower only)
# 15. life1:  int;  life of the card after evo (follower only)
# 16. skill1: text; skill of the card after evo (follower only)
# 17. desc1:  text; flavor text after evo (follower only)
# 18. trait:  text; trait of the card
# 19. cv:     text; voice actor of the card, only shown in ja and zh-tw version
# 20. rels:   text; list of CIDs of cards related to the card
def init():
    conn = sqlite3.connect('cards.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('create table if not exists cards(cid integer, lang integer, \
              num integer, type integer, rarity integer, class integer, \
              pack integer, title text, cost integer, skill0 text, desc0 text, \
              atk0 integer, atk1 integer, life0 integer, life1 integer, \
              skill1 text, desc1 text, trait text, cv text, rels text)')
    return (conn, c)

# Removes duplicate rows, i.e. rows with the same card ID and language
def remove_dupe(cursor):
    cursor.execute('DELETE FROM cards WHERE rowid NOT IN \
                   (SELECT MIN(rowid) FROM cards GROUP BY cid, lang)')

# Deprecated, use search(cursor, lang, form=3) instead
def print_all(cursor, keys=('cid', 'title')):
    for row in cursor.execute('select * from cards'):
        if len(keys) == 0:
            keys = row.keys()
        output = ''
        for key in keys:
            if key in row.keys():
                output += str(row[key]) + ', '
        print(output[:-2])

# Updates rows that have the same card ID and language as data
# If there is no such row, insert a new row with the data
def update(cursor, data, cost):
    if data['type'] == 1: # this card is a follower
        atk0, atk1, life0, life1, skill1, desc1 = \
        data['atk0'], data['atk1'], data['life0'], \
        data['life1'], data['skill1'], data['desc1']
    else:
        atk0, atk1, life0, life1, skill1, desc1 = -1, -1, -1, -1, '', ''
    # Only ja and zh-tw have name of cv
    if data['lang'] == 0 or data['lang'] == 3:
        cv = data['info'][5]
    else:
        cv = ''
    rels = str(data['rels'])[1:-1]
    if len(cursor.execute('select * from cards where cid=? and lang=?', 
                          (data['cid'], data['lang'])).fetchall()) != 0:
        cursor.execute('update cards set (num, type, rarity, class, pack, \
            title, cost, skill0, desc0, atk0, atk1, life0, life1, skill1, \
            desc1, trait, cv, rels) = (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) \
            where cid=? and lang=?', 
            (data['num'], data['type'], data['rarity'], data['class'], data['pack'], 
             data['title'], cost, data['skill0'], data['desc0'], atk0, atk1, life0, life1, 
             skill1, desc1, data['info'][0], cv, rels, data['cid'], data['lang']))
        return 0
    else: # No such row exists, so insert a new row with the data
        cursor.execute("insert into cards VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                       (data['cid'], data['lang'], data['num'], data['type'], 
                        data['rarity'], data['class'], data['pack'], data['title'], 
                        cost, data['skill0'], data['desc0'], atk0, atk1, 
                        life0, life1, skill1, desc1, data['info'][0], cv, rels))
        return 1

def translate(cursor, title, lang1=1, lang2=3, exact=0):
    if exact == 0:
        title1 = '%'+title+'%'
    else:
        title1 = title
    trans_results = \
    cursor.execute('select * from cards where cid in \
                   (select cid from cards where title like ? and lang=?) and lang=?', 
                   (title1, lang1, lang2)).fetchall()
    if len(trans_results) == 0:
        return [title]
    else:
        trans_list = []
        for t in trans_results:
            trans_list.append(t['title'])
        return trans_list

# Lists all cards with cost >= 10 from shadowverse-portal
# Allows us to update high_cost_list more easily
def online_list_high_cost():
    off = util.get_last_offset(format_=3, include_token=1, cost=(10,))
    for i in range(off+1):
        content = requests.get(util.link_format(format_=3, include_token=1, offset=12*i, cost=(10,))).text
        cids = re.findall(cid_pattern, content)
        titles = re.findall(title_pattern, content)
        print('Page {}'.format(i))
        if len(cids) != len(titles):
            print('Length error')
        for i in range(len(cids)):
            print('{}, {}'.format(cids[i], titles[i]))

# Updates a single card (defaultly for all languages)
# Useful when you only need to updates a few cards (for example after a card nerf/buff)
def online_update(conn, cursor, cid, cost, lang=range(8)):
    for l in lang:
        for t in range(10):
            try:
                data = util.get_card_data(cid, lang=l)
                break
            except:
                print('{} exception on trial {}'.format(cid, t))
        print('{} downloaded'.format(cid))
        update(cursor, data, cost)
        conn.commit()

def online_update_all(conn, cursor, lang=3, card_set = []):
    num = 0
    for cost in range(11):
        off = util.get_last_offset(format_=3, include_token=1, cost=(cost,), card_set=card_set)
        for i in range(off+1):
            for s in range(10):
                try:
                    content = requests.get(util.link_format(format_=3, include_token=1, card_set=card_set, offset=12*i, cost=(cost,))).text
                    break
                except:
                    print('Cost {}, Page {}, exception on trial {}'.format(cost, i, s))
            results = re.findall(cid_pattern, content)
            print('Cost {}, Page {}, lang {}'.format(cost, i, lang))
            for cid in results:
                for t in range(10):
                    try:
                        data = util.get_card_data(int(cid),lang=lang)
                        break
                    except:
                        print('{} exception on trial {}'.format(cid, t))
                print('{} downloaded'.format(cid))
                if cost<10 or int(cid) not in high_cost_list:
                    num += update(cursor, data, cost)
                else:
                    num += update(cursor, data, high_cost_list[int(cid)])
            conn.commit()
    print("Added {} cards".format(num))

def list_alt_art(cursor):
    file = open('altart_dict.py', 'w')
    file.write('alt2std = {\n')
    stdict = {}
    for row in cursor.execute('select * from cards WHERE (rowid NOT IN (SELECT MIN(rowid) FROM cards where pack<900 GROUP BY title) or pack>=700) and pack<900 and lang=3').fetchall():
        rels = []
        for rel in row['rels'].split(', '):
            rel = int(rel)
            if rel < 700000000 and (row['cid'] == 705314010 or rel != 100314010) and rel != 102743010:
                rels.append(rel)
        print('{}, {}, {}'.format(row['cid'], row['title'], rels[0]))
        if rels[0] not in stdict:
            stdict[rels[0]] = [row['cid']]
        else:
            stdict[rels[0]].append(row['cid'])
        file.write('{}: {},\n'.format(row['cid'], rels[0]))
    file.write('}\n')
    file.write('std2alt = {\n')
    for (std, alts) in stdict.items():
        file.write('{}: {},\n'.format(std, str(alts)))
    file.write('}')
    file.close()

def check_alt_art(cursor):
    for (alt, std) in alt2std.items():
        alt_name = cursor.execute('select * from cards where cid=? and lang=3', [alt]).fetchone()
        std_name = cursor.execute('select * from cards where cid=? and lang=3', [std]).fetchone()
        print('{}: {}; {}: {}'.format(alt, alt_name['title'], std, std_name['title']))

# Prints the data of a card
# Input: row: row data obtained from sqlite
#   form: format of output
#       0 = simple, only print cid and title (default)
#       1 = cid, title and skills
#       2 = cid, title, class, rarity, type, cost, atk, life, skill, trait, rels
#       3 = all information about the card
def print_card(cursor, row, form):
    lang = row['lang']
    if form == 0:
        output = '{}, {}'.format(row['cid'], row['title'])
    
    elif form == 1:
        output = '{}, {}\n{}'.format(row['cid'], row['title'], row['skill0'])
        if row['skill1'] != '':
            output += '\n{}'.format(row['skill1'])
        output += '\n'
    
    elif form == 2:
        output = '{} {} '.format(row['cid'], row['title'])
        output += '{} {} {} {} Cost {}\n'.format(class_text[lang][row['class']], rar_text[lang][row['rarity']-1], type_text[lang][row['type']-1], row['trait'], row['cost'])
        if row['type'] == 1:
            output += '{} {}/{}\n'.format(evo_text[lang][0], row['atk0'], row['life0'])
            output += '{}\n'.format(row['skill0'])
            output += '{} {}/{}\n'.format(evo_text[lang][1], row['atk1'], row['life1'])
            output += '{}\n'.format(row['skill1'])
        else:
            output += '{}\n'.format(row['skill0'])
        if row['rels'] != '':
            output += rel_text[lang] + '\n'
            for rel in row['rels'].split(', '):
                rel_name = cursor.execute('select * from cards where cid=? and lang=?', [rel, lang]).fetchone()
                output += '{} {}; '.format(rel, rel_name['title'])
            output = output[:-2] + '\n'
    
    elif form == 3:
        output = '{} {} '.format(row['cid'], row['title'])
        if row['pack'] < 700:
            output += '{} '.format(svportal_packs[lang][str(row['pack']+10000-100)])
        elif row['pack'] < 900:
            if type(alt_packs[row['pack']][0]) == int:
                output += promo_text[lang] + ' '
            else:
                output += '{} '.format(svportal_packs[lang][str(alt2std[row['cid']]//1000000+10000-100)])
        else:
            output += token_text[lang] + ' '
        output += '{} {} {} {} Cost {}\n'.format(class_text[lang][row['class']], rar_text[lang][row['rarity']-1], type_text[lang][row['type']-1], row['trait'], row['cost'])
        if row['type'] == 1:
            output += '{} {}/{}\n'.format(evo_text[lang][0], row['atk0'], row['life0'])
            output += '{}\n'.format(row['skill0'])
            output += '{}\n\n'.format(row['desc0'])
            output += '{} {}/{}\n'.format(evo_text[lang][1], row['atk1'], row['life1'])
            output += '{}\n'.format(row['skill1'])
            output += '{}\n'.format(row['desc1'])
        else:
            output += '{}\n'.format(row['skill0'])
            output += '{}\n'.format(row['desc0'])
        if lang == 0 or lang == 3:
            output += '\nCV: {}\n'.format(row['cv'])
        if row['rels'] != '':
            output += '\n' + rel_text[lang] + '\n'
            for rel in row['rels'].split(', '):
                rel_name = cursor.execute('select * from cards where cid=? and lang=?', [rel, lang]).fetchone()
                output += '{} {}; '.format(rel, rel_name['title'])
            output = output[:-2] + '\n'
    print(output)

# Searches for cards using criterions from the input
# Input: lang: language, 0-7 = ja, en, ko, zh-tw, fr, it, de, es
#   int_keys: integer search keys: cid, cost, pack, class, rarity, type,
#       must be in format [('cid', [list of cids to search]), ...]
#   txt_keys: text search keys: title, skill, desc, cv, trait, 
#       format similar to above
#   atk, life: in format (operation, baseline), operation is 0-2 = >=, ==, <=, 
#       operation defaulting to 0, baseline defaulting to -1
#   alt, token: include alt-art or token, defaulting to True and False resp.
#   token only works correctly when you are searching for all tokens in a pack
#   form: format of output, see print_card
def search(cursor, lang=3, int_keys=[], txt_keys=[], atk=(0, -1), life=(0, -1), alt=True, token=False, form=0):
    command = 'select * from cards where lang=?'
    pack_cmd =  ''
    search_keys = [lang]
    pack_keys = []
    
    for (key, items) in int_keys:
        if key not in ('cid', 'cost', 'pack', 'class', 'rarity', 'type'):
            continue
        if len(items) > 0 and key != 'pack':
            command = command + ' and ('
            for item in items:
                command = command + '{}=? or '.format(key)
                search_keys.append(item)
            command = command[:-4] + ')'
        elif len(items) > 0 and key == 'pack':
            pack_cmd = pack_cmd + ' and ('
            for item in items:
                pack_cmd = pack_cmd + '{}=? or '.format(key)
            pack_keys = items
            pack_cmd = pack_cmd[:-4] + ')'
    
    for (key, items) in txt_keys:
        if key not in ('title', 'skill', 'desc', 'cv', 'trait'):
            continue
        for item in items:
            if key == 'skill' or key == 'desc':
                command = command + ' and ({}0 like ? or {}1 like ?)'.format(key, key)
                search_keys.append('%'+item+'%', '%'+item+'%')
            else:
                command = command + ' and {} like ?'.format(key)
                search_keys.append('%'+item+'%')
    
    if atk[0] == 0:
        command = command + ' and atk0 >= ?'
    elif atk[0] == 1:
        command = command + ' and atk0 = ?'
    elif atk[0] == 2:
        command = command + ' and atk0 <= ?'
    if life[0] == 0:
        command = command + ' and life0 >= ?'
    elif life[0] == 1:
        command = command + ' and life0 = ?'
    elif life[0] == 2:
        command = command + ' and life0 <= ?'
    search_keys.append(atk[1])
    search_keys.append(life[1])
    
    token_cmd = command
    token_keys = search_keys
    command = command + pack_cmd
    search_keys = search_keys + pack_keys
    
    altoken = []
    if not token:
        command = command + ' and pack < 900'
    
    for row in cursor.execute(command, search_keys).fetchall():
        std = row['cid']
        if std in alt2std:
            std = alt2std[std]
        if alt and std in std2alt:
            for c in std2alt[std]:
                if c > 700000000 and len(pack_keys) > 0 and c != row['cid']:
                    altoken.append(c)
        if token and len(row['rels']) > 0:
            for rel in row['rels'].split(', '):
                rel = int(rel)
                if rel != std and (std not in std2alt or rel not in std2alt[std]):
                    altoken.append(rel)
        print_card(cursor, row, form)
    
    if len(altoken) > 0:
        token_cmd = token_cmd + ' and ('
        for i in altoken:
            token_cmd = token_cmd + 'cid=? or '
            token_keys.append(i)
        token_cmd = token_cmd[:-4] + ')'
        for row in cursor.execute(token_cmd, token_keys).fetchall():
            print_card(cursor, row, form)

if __name__ == '__main__':
    # TODO: finish command line arguments
    parser = argparse.ArgumentParser(description='Manage an offline card database of Shadowverse')
    parser.add_argument('-s', '--search', help='Search for cards')
    parser.add_argument('-alt', help='List all alt-art cards')
    parser.add_argument('-hi', help='List all cards with cost >=10')
    parser.add_argument('-u', help='Update a single card')
    parser.add_argument('-uall', help='Update all cards')
    parser.add_argument('-t', help='Translate the title of a card')
    args = parser.parse_args()
    (conn, cursor) = init()
    
    # for i in range(8):
        # for row in cursor.execute('select count(*) from cards where lang = ?', (i,)):
            # print('lang {}, cards num {}'.format(i, row['count(*)']))
        # online_update_all(conn, cursor, lang=i)
    # list_alt_art(cursor)
    # check_alt_art(cursor)
    # online_list_high_cost()
    search(cursor, int_keys=[('pack', [704])], alt=False, token=True, form=3)
    conn.close()