__author__ = 'steven'

import urllib2
import urllib
import cookielib

login_url = 'https://www.flatex.de/kunden-login.html'
acc_pwd = {'login':'Log In','email':'123456789','password':'asdfgh'}
cj = cookielib.CookieJar() ## add cookies
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [('User-agent','Mozilla/5.0 \
                    (compatible; MSIE 6.0; Windows NT 5.1)')]
data = urllib.urlencode(acc_pwd)
try:
    opener.open(login_url,data,10)
    print data
    print 'log in - success!'
except:
    print 'log in - times out!', login_url
#go('https://www.flatex.de/kunden-login.html')

#fv("1", "uname_app", "dsfs")
#fv("1", "password_app", "sdfsd")

#submit('0')
