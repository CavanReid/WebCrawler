import re
import requests
import csv
import sys

def crawl(target, limit_flag=False, limit=10):  # Explore website from domain provided until all links exhausted

    sitemap = []

    target_domain = target

    to_visit = set()
    visited = set()

    to_visit.add('https://' + target_domain + '/')

    cc = 0

    while len(to_visit) > 0 and cc < limit:
        if limit_flag == "True":
            cc += 1
        target_url = to_visit.pop()
        out_links = set()

        session = requests.Session()
        r = session.get(target_url)
        p_hyperlinks = re.compile('(?<=href=")[^\s]*(?=")')  # href = "LINK"
        p_title = re.compile('(?<=<title>)[^<]*(?=</title>)')  # <title>TITLE</title>
        hyperlinks = set(p_hyperlinks.findall(r.text))
        title = p_title.findall(r.text)

        if len(hyperlinks) == 0:
            hyperlinks = ''  # Clean up output csv slightly
        if len(title) == 0:
            title = ''
        else:
            title = title[0]
        sitemap.append({'url': r.url, 'title': title, 'out_links': hyperlinks})

        p2 = re.compile('http(s)?://(www\.)?' + target_domain + '.*')  # http(s)://(www.)DOMAIN(...)
        p3 = re.compile('/[^/].*')  # /URL
        for elem in hyperlinks:
            m = re.search(";", elem)  # avoid getting stuck on GET
            if m is not None:
                elem = elem[:m.start()]
            if p2.match(elem):
                out_links.add(elem)
            elif p3.match(elem):
                out_links.add('https://' + target_domain + elem)  # http://DOMAIN/URL

        visited.add(target_url)  # Note page visited
        to_visit = to_visit.union(out_links.difference(visited))  # Don't visit page more than once
        print(target_url + ' - visited')

    return sitemap


def write_to_csv(sitemap, t_domain):  # Once domain is fully explored. Write sitemap to csv

    with open(t_domain+'_sitemap.csv', 'w', newline='') as csv_file:
        fieldnames = ['url', 'title', 'out_links']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sitemap)

    return None
	

def main(args):
	if len(args) == 4:
		out = crawl(args[1], args[2], int(args[3]))  # args[1] = domain, args[2] = flag, args[3] = limit
	elif len(args) == 3:
		out = crawl(args[1], args[2])
	elif len(args) == 2:
		out = crawl(args[1])
	else:
		print("Error, no url provided")
		exit()  
	write_to_csv(out, args[1])
	
	return None
	
main(sys.argv) 
