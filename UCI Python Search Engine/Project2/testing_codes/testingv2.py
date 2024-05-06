import cbor
from lxml import html
from urllib.parse import urlparse, urljoin
import hashlib
import os



url = "http://www.ics.uci.edu/"
#change this base_dir if doesn't work on your end
base_dir = r"C:\Users\manhd\Desktop\CS 121\Homework\CS121-Project-2-Web-Crawler\src\spacetime_crawler_data"
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
    exit(0) 
str_content: str = byte_content.decode()
html_content = html.fromstring(str_content)

text_content = html_content.text_content()

print(text_content)
exit(0)

# changed the links so that it only contains links
# that belongs to the href and is not empty
# though there are still href=" " with an empty space
links = [link for element, attr, link, position in html_content.iterlinks() if link.Strip() != ""]


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
#for _, _, link, _ in links:
n=0
for link in links:
    print(f'{n}: {link}')
    parsed_url = urlparse(link)
    # Removed the mailto, "//" logic:
    # mailto and any links with a scheme parsed by urlparse will be 
    # added to the link untouched.
    # links starts with "//" are only pdf files contained in a src, not href
    # so they aren't included in this version. Whether or not if pdfs should be included
    # is questionable, since they aren't websites?
    if parsed_url.scheme != "":
        n += 1
        print(f'{n}: {link}')
        continue
    if link.startswith('//') :
        link = parsed_base_url.scheme + link
    elif link.startswith('/'):
        link = urljoin(base_url, link)
    elif link.startswith("www."):
        link = "https://" + link
    else:
        link = base_url + '/' + link
    print(f'{n}: {link}')
    n += 1