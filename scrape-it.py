from __future__ import print_function, unicode_literals
import argparse
from six.moves import urllib
from glob import glob
import re

import requests
from bs4 import BeautifulSoup
from internetarchive import get_item


def iter_pdfs():
    u = 'http://darwin-online.org.uk/converted/pdf/'
    soup = get_soup(u)
    for a in soup.find_all('a'):
        href = a['href']
        if not href.endswith('.pdf'):
            continue
        yield 'http://darwin-online.org.uk/converted/pdf/' + href


def get_soup(url, params=None):
    params = params if params else dict()
    r = requests.get(url, params=params)
    return BeautifulSoup(r.content, 'html.parser')


def get_item_md(pdf_id):
    u = 'http://darwin-online.org.uk/content/record'
    p = dict(itemID=pdf_id)
    soup = get_soup(u, p)
    table = soup.find_all('tr')
    md = dict(
        collection='darwin-online',
        contributor='Darwin Online',
        mediatype='texts',
        language='eng',
    )

    if '.' in pdf_id:
        md['volume'] = pdf_id.split('.')[-1].lstrip('0')
    desc = None
    for tr in table:
        k, v = [x.get_text().strip(':\n\t').lower() for x in tr.find_all('span')]
        if k == 'identifier':
            continue
        elif k == 'date':
            date = v.split('-')[0]
            try:
                re.match(r'^\d{4}$', date).group()
            except AttributeError:
                date = None
            if date:
                md[k] = date
        elif 'reference' in k:
            if desc:
                desc + '\n\n{0}'.format(v)
            else:
                desc = v
        elif 'title' in k:
            md['title'] = v.encode('utf-8')
        else:
            md[k.replace(' ', '-')] = v.encode('utf-8')
    if desc:
        md['description'] = desc.encode('utf-8')
    return md


def get_title(pdf_file):
    title = ' '.join(urllib.parse.unquote(pdf_file).split('_')[1:-1])
    if '.' in title:
        title = title.split('.')[0]
    return title.encode('ISO-8859-1').decode('utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Darwin Online Archiver.')
    parser.add_argument('--pdf-urls', dest='pdf_urls', action='store_true',
                        help='Print PDF URLs to stdout.')

    args = parser.parse_args()

    if args.pdf_urls:
        for pdf in iter_pdfs():
            print(urllib.parse.unquote(pdf.encode('utf-8')))

    else:
        for pdf_file in glob('*.pdf'):
            pdf_file = pdf_file.split('/')[-1].replace(' ', '-')
            identifier = 'darwin-online_{0}'.format(pdf_file.rstrip('.pdf'))
            pdf_id = pdf_file.split('_')[-1].rstrip('.pdf')
            md = get_item_md(pdf_id)
            title = get_title(pdf_file)
            md['title'] = get_title(pdf_file)
            item = get_item(identifier)

            # Upload.
            print('{0}:'.format(item.identifier))
            item.upload(pdf_file,
                        metadata=md,
                        delete=True,
                        retries=30,
                        checksum=True,
                        verbose=True)
