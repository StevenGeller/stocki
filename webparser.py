__author__ = 'Steven Geller'

from bs4 import BeautifulSoup
import urllib2

def get_quote(isin):

    try:
        url = "https://www.consorsbank.de/euroWebDe/-?$part=financeinfosHome.Desks.stocks.Desks.snapshot.Desks.snapshotoverview&id_name=ISIN&id=" + isin + "&$euroWeb.em.msg=min"
        html = urllib2.urlopen(url)
        soup = BeautifulSoup(html)
        try:
            for tag in soup.find_all('strong', attrs={'class': 'price price-minus'}):
                price = float(str(tag.text).replace(',', '.'))
        except Exception:
            pass

        return price
    except Exception:
        return None

print get_quote("US0378331005")



