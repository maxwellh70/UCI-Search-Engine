from lxml import html
import nltk
import os
from nltk.tokenize import RegexpTokenizer

current = os.getcwd()
root_path = "WEBPAGES_RAW"
new_root = os.path.join(current, root_path)
"""
def getHTML(path):
    root = os.path.join(path, "")
    print(sorted([x[0] for _, x in zip(range(10),os.walk(root))]))

getHTML(new_root)
print("")
print(new_root)
print('')
for count, file in zip(range(4), os.listdir(new_root)):
    d = os.path.join(new_root, file)
    if os.path.isdir(d):
        print(d)

html_1 = os.path.join(new_root, "0\\0")
page = html.parse(html_1)
html_content = html.tostring(page)
print(html_content)
'''
for ct, filename in zip(range(4),os.listdir(html_1)):
    if ct == 0:
        print(filename)
        file_path  = os.path.join(html_1, filename)
        print(f'hehehehe\t{file_path}')
        page = html.parse(file_path )
        html_content = html.tostring(page)
        print(html_content)
''' 
# Get the human readable text content, drop the script and style tags and comments

#print(html_content)       
"""
with open("testCode\\test.txt") as file:
    page = file.read()
    tokenizer = RegexpTokenizer(r'\w+')
    print(tokenizer.tokenize(page))