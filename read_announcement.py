import requests
import re
import argparse
from bs4 import BeautifulSoup
from langconv import Converter

link = 'https://shadowverse.com/cht/news/'

def read_announcement(n=0):
    content = requests.get(link).text
    soup = BeautifulSoup(content, 'html.parser')
    ann_link = soup.find_all(class_='title-link')[n].get('href')
    ann_num = re.search('=(\d*)', ann_link).group(1)
    ann = requests.get(link + ann_link)
    ann.encoding = 'utf-8'
    ann = ann.text
    ann_soup = BeautifulSoup(ann, 'html.parser')
    ann_title = translate(ann_soup.find(class_='news-detail-head').get_text())
    ann_body = ann_soup.find(class_='body')
    imgs = ann_body.find_all('img')
    img_links = ['https://shadowverse.com/' + img.get('src') for img in imgs]
    ann_text = translate(ann_body.get_text())
    return(ann_num, link + ann_link, img_links, ann_title, ann_text)

def translate(text):
    return Converter('zh-hans').convert(text)

def download_ann_img(ann_num, img_links):
    i = 0
    for img_link in img_links:
        i += 1
        r = requests.get(img_link, stream=True)
        print(r.status_code) # 返回状态码
        if r.status_code == 200:
            open('{}.{}.png'.format(ann_num, i), 'wb').write(r.content)

def ann_format(ann_title, ann_text, ann_link):
    titles = re.findall('(■.*?)\n', ann_text, re.S)
    titles = list(dict.fromkeys(titles))
    for title in titles:
        ann_text = ann_text.replace(title, '[h][color=red][size=110%]'+title[1:]+'[/size][/color][/h]')
    titles = re.findall('(▼.*?)\n', ann_text, re.S)
    titles = list(dict.fromkeys(titles))
    for title in titles:
        ann_text = ann_text.replace(title, '[h][color=blue]'+title[1:]+'[/color][/h]')
    times = re.findall('\n([^\n]*?月[^\n]*?日[^\n]*?～[^\n]*?)\n', ann_text, re.S)
    times = list(dict.fromkeys(times))
    for time in times:
        ann_text = ann_text.replace(time, '[b]'+time+'[/b]')
    ann_text = ann_title + ann_text + '\n\n' + ann_link
    return ann_text

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Downloads and formats announcements from Shadowverse')
    parser.add_argument('-n','--num',nargs='+',default=0,help='Selects the announcement to download')
    args = parser.parse_args()
    for i in args.num:
        (ann_num, ann_link, img_links, ann_title, ann_text) = read_announcement(int(i))
        ann_text = ann_format(ann_title, ann_text, ann_link)
        print(ann_text)