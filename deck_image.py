import requests
import urllib3

def download_deck(name, num, link):
    name = name.replace('/','')
    name = name.replace('|','')
    filename = '{}_{}.png'.format(name, num)
    
    urllib3.disable_warnings()
    session = requests.Session()
    session.headers.clear()
    result = session.post('https://shadowverse-portal.com/image/1?lang=zh-tw', headers={'Referer': link}, verify=False)
    if result.status_code == 200:
        open(filename, 'wb').write(result.content)
        print(filename + ' downloaded.')
    else:
        print(result.text)

def batch_download_deck(names, nums, links, lang1='en', lang2='zh-tw'):
    if len(names) != len(nums) or len(names) != len(links):
        print('Lengths of lists don\'t match.')
        return
    
    urllib3.disable_warnings()
    session = requests.Session()
    session.headers.clear()
    
    for i in range(len(names)):
        names[i] = names[i].replace('/','')
        names[i] = names[i].replace('|','')
        filename = '{}_{}.png'.format(names[i], nums[i])
        result = session.post('https://shadowverse-portal.com/image/1?lang=zh-tw', headers={'Referer': links[i]}, verify=False)
        if result.status_code == 200:
            open(filename, 'wb').write(result.content)
            print(filename + ' downloaded.')
        else:
            print(result.text)

if __name__ == '__main__':
    names = ['Alice', 'Bob', 'Catherine', 'Dave', 'Eve', 'Federick']
    nums = [1, 2, 3, 4, 5, 6]
    links = ['https://shadowverse-portal.com/deck/1.4.6qXGi.6qXGi.73iyC.73iyC.73iyC.6y7rA.6y7rA.6y7rA.6y4gM.6y4gM.6y4gM.6y9Yi.6y9Yi.6_up2.6_up2.6_up2.5_38w.5_38w.5_38w.6_-QQ.6_-QQ.6_-QQ.73m7A.73m7A.73m7A.6uNs6.6uNs6.6uNs6.7007y.7007y.7007y.73qGy.73qGy.73qGy.6yAHQ.6yAHQ.6yAHQ.6yB-y.6yB-y.6yB-y?lang=en', \
             'https://shadowverse-portal.com/deck/1.7.74sBY.74sBY.72Icy.72Icy.72Icy.6zDvY.6zDvY.74sBi.74sBi.74sBi.74x42.74x42.74x42.60COa.60COa.6vUfC.6vUfC.6vUfC.719NS.719NS.719NS.6zJWw.6zJWw.6zJWw.6rg_I.6rg_I.6rg_I.6-UTo.6-UTo.6-UTo.719Nc.719Nc.719Nc.74swQ.6vX5I.6vX5I.6vX5I.74zWS.74zWS.74zWS?lang=en', \
             'https://shadowverse-portal.com/deck/1.8.71TeA.71TeA.71TeA.6zemS.6zemS.71QTC.71QTC.71QTC.75Lwo.75Lwo.75Lwo.6zd2w.6zd2w.6zd2w.6s2wi.6s2wi.6s2wi.6vt3s.6vt3s.6vt3s.6zcK2.6zcK2.6zcK2.6zcKC.6zcKC.6zcKC.6-UTy.6-UTy.6-UTy.75JUY.75JUY.75JUY.6zhxQ.6zhxQ.6zhxQ.71VLY.71VLY.71VLY.71Xo6.71Xo6?lang=en', \
             'https://shadowverse-portal.com/deck/1.4.6qVZA.6qVZA.6qVZA.6oxSw.6oxSw.6oxSw.6qSOM.6qSOM.6qSOM.73nqY.73nqY.73nqY.5_38w.5_38w.5_38w.6qUqS.6qUqS.6qUqS.6qZiy.6qZiy.6qZiy.6-UTo.6-UTo.6-UTo.6wdui.6wdui.6wdui.73iyM.73iyM.73iyM.6ssBy.6qZj6.6qZj6.6qZj6.7007o.7007o.7007o.73qGo.73qGo.73qGo?lang=en', \
             'https://shadowverse-portal.com/deck/1.5.6qtEy.6qtEy.6qtEy.6ufgQ.6ufgQ.6ufgQ.6qy7c.6qy7c.6qy7c.6yXz2.6yXz2.6yXz2.6yaPI.6yaPI.6yaPI.70HyQ.70HyQ.70HyQ.6owk2.6owk2.6owk2.6yXzC.6yXzC.6yXzC.6ujqC.70HDY.70HDY.70HDY.748Xg.748Xg.748Xg.6-UTo.6-UTo.6-UTo.74ChS.74ChS.74ChS.6qtEo.6qtEo.6qtEo?lang=en', \
             'https://shadowverse-portal.com/deck/1.8.75H2I.75H2I.75H2I.6vovw.6vovw.6vovw.75Lwo.75Lwo.75Lwo.75FKw.75FKw.75FKw.72Icy.72Icy.72Icy.6s2wi.6s2wi.6s65g.6s65g.6s65g.6wbSI.6wbSI.6wbSI.6vqdS.6vqdS.71Xno.71Xno.71Xno.6vr6Y.6vr6Y.6vr6Y.71Xny.71Xny.71Xny.6-UTo.6-UTo.6-UTo.6vvVy.6vvVy.6vvVy?lang=en']
    batch_download_deck(names, nums, links)
    # link1 = "https://docs.google.com/spreadsheets/u/2/d/e/2PACX-1vTpaQ65MlzO9nn-I6gaK4UqtF7_VbvbNeyEQAbWZ9DkR9oZOrUuSWy54gWSTTmwyhnhufshSsbePqaN/pubhtml?gid=0&single=true"
    # link2 = "https://docs.google.com/spreadsheets/u/2/d/e/2PACX-1vTpaQ65MlzO9nn-I6gaK4UqtF7_VbvbNeyEQAbWZ9DkR9oZOrUuSWy54gWSTTmwyhnhufshSsbePqaN/pubhtml?gid=1060989176&single=true"
    
    # content = requests.get(link1).text
    # pattern = re.compile('<td class="s\d">([^<>]*?)</td><td class="s\d softmerge"><div class="softmerge-inner" style="width: 97px; left: -1px;"><a target="_blank" rel="noreferrer" href=".*?">(.*?)</a></div></td><td class="s\d softmerge"><div class="softmerge-inner" style="width: 97px; left: -1px;"><a target="_blank" rel="noreferrer" href=".*?">(.*?)</a></div></td><td class="s\d softmerge"><div class="softmerge-inner" style="width: 97px; left: -1px;"><a target="_blank" rel="noreferrer" href=".*?">(.*?)</a></div></td>', re.S)
    # results = re.findall(pattern, content)
    # for result in results:
    #     for i in range(3):
    #         download_deck(result[0], i+11, result[i+1])
    
    # content = requests.get(link2).text
    # results = re.findall(pattern, content)
    # for result in results:
    #     for i in range(3):
    #         download_deck(result[0], i+21, result[i+1])