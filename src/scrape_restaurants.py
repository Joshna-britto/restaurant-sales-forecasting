"""Conservative scraper for public pages; respect terms, robots.txt and rate limits."""
import argparse, csv, json, time
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import requests
from bs4 import BeautifulSoup
from src.config import ROOT, OUTPUTS
UA='StudentResearchBot/1.0 (academic project; contact: add-your-email-before-use)'
def allowed(url):
    p=urlparse(url); robots=f'{p.scheme}://{p.netloc}/robots.txt'; rp=RobotFileParser(robots)
    try: rp.read(); return rp.can_fetch(UA,url)
    except Exception: return False
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--urls',default=str(ROOT/'data/raw/scrape_urls.txt')); args=ap.parse_args()
    urls=[x.strip() for x in Path(args.urls).read_text().splitlines() if x.strip() and not x.strip().startswith('#')]
    OUTPUTS.mkdir(exist_ok=True); restaurants=[]; items=[]
    for url in urls:
        if not allowed(url): print('Skipped (robots disallow or robots unavailable):',url); continue
        try:
            r=requests.get(url,headers={'User-Agent':UA},timeout=15); r.raise_for_status()
            soup=BeautifulSoup(r.text,'html.parser')
            for node in soup.select('script[type="application/ld+json"]'):
                try: data=json.loads(node.string or node.get_text())
                except Exception: continue
                stack=data if isinstance(data,list) else [data]
                for obj in stack:
                    if not isinstance(obj,dict): continue
                    typ=obj.get('@type',[]); typ=[typ] if isinstance(typ,str) else typ
                    if any('Restaurant' in t for t in typ): restaurants.append({'source_url':url,'name':obj.get('name'),'servesCuisine':obj.get('servesCuisine'),'priceRange':obj.get('priceRange'),'ratingValue':(obj.get('aggregateRating') or {}).get('ratingValue') if isinstance(obj.get('aggregateRating'),dict) else None})
                    menu=obj.get('hasMenu',[]); menu=menu if isinstance(menu,list) else [menu]
                    for m in menu:
                        if isinstance(m,dict):
                            for mi in m.get('hasMenuSection',[]) or []:
                                for dish in mi.get('hasMenuItem',[]) or []: items.append({'source_url':url,'restaurant':obj.get('name'),'section':mi.get('name'),'item':dish.get('name'),'description':dish.get('description')})
            print('Processed:',url)
        except Exception as e: print('Failed:',url,type(e).__name__,e)
        time.sleep(2)
    for name,rows in [('web_scraped_restaurants.csv',restaurants),('web_scraped_menu_items.csv',items)]:
        if rows:
            with open(OUTPUTS/name,'w',newline='',encoding='utf-8') as f:
                w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(f'Extracted {len(restaurants)} restaurant records and {len(items)} menu items. Empty results are possible.')
if __name__=='__main__': main()
