import sqlite3
import util
import requests
import re
from altart_dict import alt2std

cid_pattern = re.compile('<a href="/card/(.*?)" class="el-card-visual-content">', re.S)

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
#  3. num:    int;  digits 7 and 8 of CID distinguishing cards with the same first 6 digits
#  4. type:   int;  digit 6 of CID, 1 = follower, 2 = amulet, 3 = countdown amulet, 4 = spell
#  5. rarity: int;  digit 5 of CID, 1 = bronze, 2 = silver, 3 = gold, 4 = legendary
#  6. class:  int;  digit 4 of CID, 0-8 = neutral, forest, sword, rune, dragon, shadow, blood, haven, portal
#  7. pack:   int;  first 3 digits of CID showing the pack to which the card belongs, 
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
    cursor.execute('DELETE FROM cards WHERE rowid NOT IN (SELECT MIN(rowid) FROM cards GROUP BY cid, lang)')

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
                       title, cost, skill0, desc0, atk0, atk1, life0, life1, \
                       skill1, desc1, trait, cv, rels) = (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) \
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

def list_high_cost():
    off = util.get_last_offset(format_=3, include_token=1, cost=(10,))
    for i in range(off+1):
        content = requests.get(util.link_format(format_=3, include_token=1, offset=12*i, cost=(10,))).text
        results = re.findall(cid_pattern, content)
        print('Page {}'.format(i))
        for cid in results:
            print(cid)

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
    for row in cursor.execute('select * from cards WHERE (rowid NOT IN (SELECT MIN(rowid) FROM cards where pack<900 GROUP BY title) or pack>=700) and pack<900 and lang=3'):
        rels = []
        for rel in row['rels'].split(', '):
            rel = int(rel)
            if rel < 700000000 and (row['cid'] == 705314010 or rel != 100314010) and rel != 102743010:
                rels.append(rel)
        print('{}, {}, {}'.format(row['cid'], row['title'], rels[0]))
        file.write('{}: {},\n'.format(row['cid'], rels[0]))
    file.write('}')
    file.close()

def check_alt_art(cursor):
    from altart_dict import alt2std
    for (alt, std) in alt2std.items():
        alt_name = cursor.execute('select * from cards where cid=? and lang=3', [alt]).fetchone()
        std_name = cursor.execute('select * from cards where cid=? and lang=3', [std]).fetchone()
        print('{}: {}; {}: {}'.format(alt, alt_name['title'], std, std_name['title']))

def search(cursor, lang=3, search_keys = [], search_items = [], keys=['title'], simp=0):
    for row in cursor.execute('select * from cards where atk0>0 and atk0<2 and lang=?', [lang]):
        if len(keys) == 0:
            keys = row.keys()
        output = ''
        for key in keys:
            if key in row.keys():
                if simp == 0:
                    output += str(row[key]) + ', '
                else:
                    output += key + ': ' + str(row[key]) + '\n'
        print(output[:-2])

if __name__ == '__main__':
    (conn, cursor) = init()
    # for row in cursor.execute('select * from cards where cid=? and lang=?', [900344080,3]):
    #     keys = row.keys()
    #     output = ''
    #     for key in keys:
    #         if key in row.keys():
    #             output += key + ': ' + str(row[key]) + '\n'
    #     print(output[:-2])
    # for row in cursor.execute('select * from cards where lang=3 and cv like ?', ('%檜山修之%',)):
        # output = ''
        # for key in ('title',):
            # output += str(row[key]) + ', '
        # print(output[:-2])
    # for i in range(8):
        # for row in cursor.execute('select count(*) from cards where lang = ?', (i,)):
            # print('lang {}, cards num {}'.format(i, row['count(*)']))
        # online_update_all(conn, cursor, lang=i)
    list_alt_art(cursor)
    check_alt_art(cursor)
    # search(cursor)
    conn.close()