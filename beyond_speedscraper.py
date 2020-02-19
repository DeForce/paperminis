import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import asyncio
import concurrent.futures
import json
import codecs
import browser_cookie3
import functools


async def speedcrawl(a_pages):
    data = []
    for l_page in range(1, a_pages + 1):
        data.append({'page': l_page})

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(a_pages, 100)) as executor:
        async_loop = asyncio.get_event_loop()
        futures = [
            async_loop.run_in_executor(
                executor,
                functools.partial(
                    requests.get,
                    'https://www.dndbeyond.com/monsters',
                    d_page,
                    cookies=cj
                )
            )
            for d_page in data
        ]
        for response in await asyncio.gather(*futures):
            pass
    return [f.result() for f in futures]


class Monster:
    name = None
    source = None
    type = None
    size = None
    alignment = None
    cr = None
    image = None


# Beyond hates automation at the moment, and there is no API available yet, so you need to be careful.
# They may block your account
cj = browser_cookie3.chrome(domain_name='www.dndbeyond.com')

ua = UserAgent()
header = {'User-Agent': str(ua.chrome)}
url = 'https://www.dndbeyond.com/monsters'
htmlContent = requests.get(url, headers=header, cookies=cj)
soup = BeautifulSoup(htmlContent.text, "html.parser")

uldiv = soup.find_all("a", class_="b-pagination-item")
pages = int(uldiv[-1].text)

print('{} pages found.'.format(pages))

loop = asyncio.get_event_loop()
result = loop.run_until_complete(speedcrawl(pages))

monster_type_url_dict = {'aberration': 'https://i.imgur.com/qI39ipJ.jpg',
                         'beast': 'https://i.imgur.com/GrjN1HL.jpg',
                         'celestial': 'https://i.imgur.com/EHaX5Pz.jpg',
                         'construct': 'https://i.imgur.com/me0a3la.jpg',
                         'dragon': 'https://i.imgur.com/92iC5ga.jpg',
                         'elemental': 'https://i.imgur.com/egeiuFf.jpg',
                         'fey': 'https://i.imgur.com/hhSXx7Y.jpg',
                         'fiend': 'https://i.imgur.com/OWTsHDl.jpg',
                         'giant': 'https://i.imgur.com/lh3eZGN.jpg',
                         'humanoid': 'https://i.imgur.com/ZSH9ikY.jpg',
                         'monstrosity': 'https://i.imgur.com/5iY8KhJ.jpg',
                         'ooze': 'https://i.imgur.com/WDHbliU.jpg',
                         'plant': 'https://i.imgur.com/FqEpGiQ.jpg',
                         'undead': 'https://i.imgur.com/MwdXPAX.jpg'}

monsters = {}
for page in result:
    soup = BeautifulSoup(page.text, "html.parser")
    infos = soup.find_all('div', class_='info')
    # css_links = [link["href"] for link in soup.findAll("link") if "stylesheet" in link.get("rel", [])]

    for info in infos:
        monster = Monster()

        divs = info.find_all('div')
        for d in divs:
            c = d.get('class')
            if 'monster-icon' in c:
                a = d.find('a')
                if a is None:
                    creature_type = d.find('div').get('class')[1]
                    img_url = monster_type_url_dict[creature_type]
                else:
                    img_url = a.get('href')
                monster.image = img_url
            elif 'monster-challenge' in c:
                cr = d.find('span').text
                monster.cr = cr
            elif 'monster-name' in c:
                name = d.find('a').text
                monster.name = name

                source = d.find('span', class_="source").text
                monster.source = source
            elif 'monster-type' in c:
                monster_type = d.find('span').text
                monster.type = monster_type
            elif 'monster-size' in c:
                size = d.find('span').text
                monster.size = size
            elif 'monster-alignment' in c:
                alignment = d.find('span').text
                monster.alignment = alignment

        monsters[monster.name] = {
            'name': monster.name,
            'source': monster.source,
            'creature_type': monster.type,
            'creature_size': monster.size,
            'alignment': monster.alignment,
            'CR': monster.cr,
            'img_url': monster.image
        }

with open('monsters.json', 'wb') as f:
    json.dump(monsters, codecs.getwriter('utf-8')(f), ensure_ascii=False, indent=4, sort_keys=True)
