import requests
import re
from bs4 import BeautifulSoup
from deck_image import batch_download_deck

link = 'https://sv.j-cg.com/compe/view/tour/'
svportal_link = 'https://shadowverse-portal.com/deck/'

def get_player_data(tour):
    tourlink = link + str(tour)
    content = requests.get(tourlink).text
    soup = BeautifulSoup(content, 'html.parser')
    
    round1 = soup.find(class_="round round1")
    player16 = round1.find_all(class_='tour_match left') + round1.find_all(class_='tour_match right')
    round2 = soup.find(class_="round round2")
    player8 = round2.find_all(class_='tour_match left') + round2.find_all(class_='tour_match right')
    round3 = soup.find(class_="round round3")
    player4 = round3.find_all(class_='tour_match left') + round3.find_all(class_='tour_match right')
    round4 = soup.find(class_="round round4")
    player2 = round4.find_all(class_='tour_match left') + round4.find_all(class_='tour_match right')
    player1 = round4.find_all(class_='tour_match right winner') + round4.find_all(class_='tour_match left winner')
    
    for i in range(len(player1)):
        player1[i] = player1[i].find(class_='name_abbr').text
    for i in range(len(player2)):
        player2[i] = player2[i].find(class_='name_abbr').text
    for i in range(len(player4)):
        player4[i] = player4[i].find(class_='name_abbr').text
    for i in range(len(player8)):
        player8[i] = player8[i].find(class_='name_abbr').text
    for i in range(len(player16)):
        player16[i] = player16[i].find(class_='name_abbr').text
    
    names = []
    nums = []
    decks = []
    matches = round1.find_all(class_='match')
    for i in range(len(matches)):
        matches[i] = re.search('href=\'(.*)\'', matches[i].get('onclick')).group(1)
        match_content = requests.get(matches[i]).text
        match_soup = BeautifulSoup(match_content, 'html.parser')
        teams = match_soup.find_all(class_='team')
        for team in teams:
            name = team.find(class_='link-nodeco link-black hover-blue').text
            svplinks = team.find_all(target='_svp')
            num = 1
            for svplink in svplinks:
                href = str(svplink.get('href'))
                if href.find('deckbuilder') != -1:
                    if href.find('&lang=') != -1:
                        hashcode = re.search('hash=(.*)&lang=', href).group(1)
                    else:
                        hashcode = re.search('hash=(.*)', href).group(1)
                else:
                    if href.find('\?lang=') != -1:
                        hashcode = re.search('deck/(.*)\?lang=', href).group(1)
                    else:
                        hashcode = re.search('deck/(.*)', href).group(1)
                decklink = svportal_link + hashcode + '?lang=zh-tw'
                names.append(name)
                nums.append(num)
                decks.append(decklink)
                num += 1
                
    batch_download_deck(names, nums, decks, lang1='zh-tw', lang2='zh-tw')
    # print(names, nums, decks)
    # print(player1, player2, player4, player8, player16)
#     return (names, nums, decks, player1, player2, player4, player8, player16)

# def format_report(decklists, player1, player2, player4, player8, player16):
#     report = '[quote][头图][/quote]\n[简要解析]\n[collapse=接下来的JCG日程]\n[jcg日程图片]\n[/collapse]\n[excel表格图片]\n'
#     report += '\n[color=orange][size=120%][b]冠军[/b][/size][/color]\n'
#     for player in player1:
#         report += '[u]{}[/u]\n{}\n[deck1图片]\n{}\n[deck2图片]\n'.format(player, deck1, deck2)

if __name__ == '__main__':
    get_player_data(2566)