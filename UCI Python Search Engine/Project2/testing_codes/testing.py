import cbor
from lxml import html
from urllib.parse import urlparse
import hashlib
import os



url = "http://www.ics.uci.edu/faculty"
#change this base_dir if doesn't work on your end
base_dir = "..\\CS121-Project-2-Web-Crawler-1\\spacetime_crawler_data"
pd = urlparse(url)
if pd.path:
    path = pd.path[:-1] if pd.path[-1] == "/" else pd.path
else:
    path = ""
url = pd.netloc + path + (("?" + pd.query) if pd.query else "")

try:
    hashed_link = hashlib.sha224(url).hexdigest()
except (UnicodeEncodeError, TypeError):
    try:
        hashed_link = hashlib.sha224(url.encode("utf-8")).hexdigest()
    except UnicodeEncodeError:
        hashed_link = str(hash(url))
print(os.path.join(base_dir, hashed_link))
if os.path.exists(os.path.join(base_dir, hashed_link)):
    file_name = os.path.join(base_dir, hashed_link)

data_dict = cbor.load(open(file_name, "rb"))
def get_content_type(data):
    if b'http_headers' not in data: return None

    hlist = data_dict[b"http_headers"][b'value']
    for header in hlist:
        if header[b'k'][b'value'] == b'Content-Type':
            return str(header[b'v'][b'value'])
    return None





url_data = {
    "url": url,
    "content": data_dict[b'raw_content'][b'value'] if b'raw_content' in data_dict and b'value' in data_dict[b'raw_content'] else "",
    "http_code": int(data_dict[b"http_code"][b'value']),
    "content_type": get_content_type(data_dict),
    "size": os.stat(file_name).st_size,
    "is_redirected": data_dict[b'is_redirected'][b'value'] if b'is_redirected' in data_dict and b'value' in data_dict[b'is_redirected'] else False,
    "final_url": data_dict[b'final_url'][b'value'] if b'final_url' in data_dict and b'value' in data_dict[b'final_url'] else None
}
print('url:', url_data['url'])
print('final_url:', url_data['final_url'])
print('is_redirected:',url_data['is_redirected'])
outputLinks = []
byte_content: bytes = url_data['content']
if byte_content is None:
    ...
str_content: str = byte_content.decode()
html_content = html.fromstring(str_content)
links = html_content.iterlinks()
# Check if the url is redirected
if url_data['is_redirected']:
    base_url = url_data['final_url']
else:
    base_url = url_data['url']
# Find the first index of the '/' in the base url
# Strip the last / if there is one
if base_url[-1] == '/':
    base_url = base_url[:-1]
parsed_base_url = urlparse(base_url)
base_domain_network_location = parsed_base_url.scheme + '://' + parsed_base_url.netloc
for _, _, link, _ in links:
    print(f'1: {link}')
    if link.startswith('/') or not link.startswith('http'):
        if link.startswith('//') or \
           link.startswith("mailto:") or \
           link.startswith("www."):
            pass
        elif link.startswith('/'):
            link = base_domain_network_location + link
        else:
            link = base_url + '/' + link
    print(f'2: {link}')
    #assert link.startswith('http')