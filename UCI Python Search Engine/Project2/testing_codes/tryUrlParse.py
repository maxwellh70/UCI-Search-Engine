from urllib.parse import urlparse

"""
Types of hrefs and how to manage:
starts with "/": use the base domain and concatnate the href to the base
have a scheme after parse: pass directly into list

"""
mailto = "mailto:sangeetha.aj@uci.edu"
questionmark = "?letter_i"
ics_uci_edi = "https://www.ics.uci.edu/"
ftp = "ftp://ftp.ics.uci.edu"
jpg = "//www.ics.uci.edu/bin/img/photos/faculty/joshug4.jpg"
double_dot = "../employment/index.php"
htag = "#"
one_slash = "/faculty/highlights/"
no_slash = "highlights/index.php"
www = "//www.ics.uci.edu"
all = [mailto,questionmark,ics_uci_edi,ftp, \
    jpg, double_dot, htag, one_slash, no_slash, \
        www]

for test_url in all:
    parsed = urlparse(test_url)
    print(parsed)
    print(f'scheme:\t\t"{parsed.scheme}"\nnetloc:\t\t"{parsed.netloc}"\nhostname:\t"{parsed.hostname}"\npath:\t\t"{parsed.path}"')
