import openpyxl
import deck_image

if __name__ == '__main__':
    sheet = openpyxl.load_workbook('decklist.xlsx')['Sheet1']
    names = []
    nums = []
    links = []
    for i in range(8):
        for j in range(3):
            names.append('4_'+sheet.cell(i+1, 1).value)
            nums.append(j+1)
            links.append(sheet.cell(i+1, j+2).value)
    deck_image.batch_download_deck(names, nums, links)