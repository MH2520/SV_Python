import util
import requests
import re

cid_pattern = re.compile('<a href="/card/(.*?)" class="el-card-visual-content">', re.S)

if __name__ == '__main__':
    off = util.get_last_offset(format_=3, include_token=1, card_set=[10019, 70020, 70021])
    for i in range(off+1):
        content = requests.get(util.link_format(format_=3, include_token=1, card_set=[10019, 70020, 70021], offset=12*i)).text
        results = re.findall(cid_pattern, content)
        for cid in results:
            util.download_img_and_compress(cid)
    util.download_img_and_compress("714441020")
    util.download_img_and_compress("714341010")
    util.download_img_and_compress("714641010")