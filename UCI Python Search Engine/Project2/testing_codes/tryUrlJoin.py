from urllib.parse import urljoin
import posixpath

current_url = "https://ics.uci.edu/faculty/about/"


jpg = "//www.sd.ga.ee/bin/img/photos/faculty/joshug4.jpg"
double_dot = "../employment/index.php"
htag = "#"
one_slash = "/area/highlights/"
no_slash = "./highlights/index.php"
www = "//www.ics.uci.edu"
print(urljoin("https:", www))

all = [jpg,double_dot,htag,one_slash,no_slash,www]
for i in all:
    print(urljoin(current_url, i))