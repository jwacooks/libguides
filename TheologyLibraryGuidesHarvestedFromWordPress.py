
# coding: utf-8

## Theology Library Guides Harvested From WordPress

# The flow of this script is to execute a search for all the guides that are in the Libraries' web site. At BU, this is done by executing a search for "inurl:www.bu.edu/library/guide". The results are placed into a list of URLs for pages that will be harvested. Other libraries will need to determine how to generate that list of URLs, generally using a search engine.
# 
# Once the list of URLs is generated, we iterate through the load each page and use BeautifulSoup to parse and extract fields from the page. The values from the selected fields are written to disk as an xml file in the standard OAI_PMH format. This can then be ingested by Primo using an OAI_PMH pipe.

# In[1]:

#!/usr/local/bin/python2.7  

##
## Variables:
##
## search_url contains the initial search string. In this case we
## are searching for all of the guides published by the BU Libraries
## on the Libraries' web site:  * inurl:www.bu.edu/library/guide/
search_url = 'http://www.bu.edu/phpbin/search/?t=default&dir=1&maps=1&q=inurl%3Awww.bu.edu%2Fsthlibrary%2Flibrary-research-guides%2F'
##
## results_url contains the results of the initial search. To this string
## we will append the total number of results parsed from the initial
## results page.
results_url = 'http://www.bu.edu/phpbin/search/index.php?q=inurl:www.bu.edu/sthlibrary/library-research-guides/&start=0&col=default_collection&site=&t=default&sort=&dir=1&maps=1&num='
##
## If test is True, print the values ; If test is False, write to file
test = True

## Import the required libraries
import urllib2
from pymarc import Field, Record
from BeautifulSoup import BeautifulSoup
import cgi
import gzip
import tarfile
import time
import os
reload(sys)  
sys.setdefaultencoding('utf8')
import codecs


#os.chdir('/home/primo/libguides')

# setup a variable for excaping HTML chars
html_escape_table = {
                     "&": "&amp;",
                     '"': "&quot;",
                     "'": "&apos;",
                     ">": "&gt;",
                     "<": "&lt;",
                     }
## define a function that will escape strings of text for use in xml
def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text) 

#if not test:
## open the xml file and write the header
##f = open('/home/primo/libguides/TheoGuides.xml', 'wb')
f = open('TheoGuides.xml', 'wb')
f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
f.write('<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">\n')
f.write('<responseDate>2014-07-09T21:02:57Z</responseDate>\n')
f.write('    <request verb="ListRecords" metadataPrefix="oai_dc" >http://www.bu.edu/library/guides</request>\n')
f.write('<ListRecords>\n')



## read the results list to get the number of results
page = urllib2.urlopen(search_url)
rpage = page.read()
soup =  BeautifulSoup(rpage)
num_hits = soup.fetch('span', {'class' : 'hits'})
num_hits = num_hits[0].text
num_hits = int(num_hits[num_hits.rfind('y')+1:])
print num_hits
## Get the full list of guides
results_url += str(num_hits)
page = urllib2.urlopen(results_url)
rpage = page.read()
soup =  BeautifulSoup(rpage)
## grab all of the 'a' tags
a_list = soup.fetch('a')
##a_list = soup.find_all('a')
#a_list = soup("a")
href_dict = {}
href_list = []
for a in a_list:
    if a['href'][:4] == 'http':
        href_dict[a['href']] = 'url'
href_list = list(href_dict.keys())

##
counter = 1
for href in href_list:
    time.sleep(1)
    try:
        page = urllib2.urlopen(href)
    except:
        continue
    rpage = page.read()
    info = page.info()
    date = info['date']
    date = date[5:-12]
    soup =  BeautifulSoup(rpage)
    ## get the title
    try:
        title = soup.title.contents[0]
    except:
        continue
    title = title[:-41]
    title = title[:-56]

    ## author
    author = ''
    authors = soup.findAll('div', {'class' : 'widget bu-library-profiles-widget guide_authors'})
    if len(authors) > 0 :
        authors = authors[0]
        authors_list = authors.fetch('h3')
        for a in authors_list:
            if len(author) > 0:
                author += '; '
        author += a.a.contents[0]
    ## subjects
    subs = ''
    subjects = soup.findAll('div', {'class' : 'widget bu-library-subjects-widget'})
    if len(subjects) > 0:
        subs_ul = subjects[0].ul
        subs_ul.findAll('li')
        for li in subs_ul.findAll('li'):
            if len(subs) > 0:
                subs += ';  '
            subs += li.a.contents[0]
    url = href

        
    metaList = soup.fetch('meta')
    meta_desc = ''
    description = ''
    meta_keywords = ''
    for l in metaList:
        meta = l.attrs

        meta_rights = 'Copyright (c) 2014 Boston University'

        if len(meta) == 2:
            if meta[0][1] == 'description':
                #print 'DESCRIPTION'
                #print meta[1][1]
                meta_desc = meta[1][1]
                description = meta[1][1]
                #print description
                #print 'meta_desc:  ', meta_desc  
            if meta[0][1] == 'keywords':
                meta_keywords = meta[1][1]
                #print 'meta_key:  ', meta_keywords  
            #if meta[0][1] == 'copyright':
             #   meta_rights = meta[1][1]
                #print 'meta_rights:  ', meta_rights
    id = 'Theo-' + str(counter)
    counter += 1
    #if not test:
    f.write('<record>\n')
    f.write('<header>\n')
    f.write('<identifier>')
    f.write(id)
    f.write('</identifier>\n')
    f.write('<datestamp>2009-09-19T06:00:13Z</datestamp>\n')
    f.write('</header>\n')
    f.write('<metadata>\n')
    f.write('<oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:doc="http://www.lyncode.com/xoai" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:dc="http://purl.org/dc/elements/1.1/" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd">\n')
    f.write('<dc:title>')
    f.write(html_escape(title.encode('utf-8')))
    f.write('</dc:title>\n')
    f.write('<dc:type>')
    f.write('guide')
    f.write('</dc:type>\n')
    if len(author) > 0:
        f.write('<dc:creator>')
        f.write(html_escape(author.encode('utf-8')))
        f.write('</dc:creator>\n')  
    if len(subs) > 0:
        f.write('<dc:subject>')
        f.write(html_escape(subs.encode('utf-8')))
        f.write('</dc:subject>\n')
    f.write('<dc:identifier>')
    f.write(url)
    f.write('</dc:identifier>\n') 
#        f.write('<dc:date>')
#        f.write(date)
#        f.write('</dc:date>') 
    f.write('<dc:subject>')
    f.write('research guide')
    f.write('</dc:subject>\n')
    if len(meta_desc) > 0:
        f.write('<dc:description>')
        f.write(html_escape(meta_desc.encode('utf-8')))
        f.write('</dc:description>\n') 
    if len(meta_keywords) > 0:
        f.write('<dc:subject>')
        f.write(html_escape(meta_keywords.encode('utf-8')))
        f.write('</dc:subject>\n') 
    f.write('</oai_dc:dc>\n</metadata>\n</record>\n')

    if  test:
        # lets see what we have
        print 'record: ', str(counter)
        print 'title: ', title
        print 'author: ', author
        print 'subject: ', subs
        print 'keywords:', meta_keywords
        print 'description: ', meta_desc
        print 'link: ', url
        print 'rights: ', meta_rights
        print 'date: ', date
        print ' '
        
#if not test:
f.write('</ListRecords>\n')
f.write('</OAI-PMH>\n')
f.close()

#tar = tarfile.open('/home/primo/libguides/TheoGuides.xml.tar.gz' , 'w:gz')
tar = tarfile.open('TheoGuides.xml.tar.gz' , 'w:gz')
tar.add('TheoGuides.xml')
tar.close()

## We're done


# In[ ]:



