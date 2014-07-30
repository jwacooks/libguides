#!/usr/local/bin/python2.7

##
## lawguides.py
## written by Jack Ammerman
## date:  7/30/2014
## CC BY license
##
## This harvests the library research guides authored by librarians from Boston University Law Library
## These guides are written and maintained on the LibGuides platform.
##


## Import the required libraries
import urllib2
from pymarc import Field, Record
from BeautifulSoup import BeautifulSoup
import cgi
import gzip
import tarfile
import os

## remove existing LawGuides.xml and LawGuides.xml.tar.gz
os.chdir('/home/primo/libguides')
os.remove('/home/primo/libguides/LawGuides.xml')
os.remove('/home/primo/libguides/LawGuides.xml.tar.gz')

## setup a variable for excaping HTML chars
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

## read the A-Z list and create  a list of guides to parse
page = urllib2.urlopen('http://lawlibraryguides.bu.edu/browse.php')
rpage = page.read()
soup =  BeautifulSoup(rpage)
a_list = soup.fetch('a', {'class' : 'pdisplay_name'})
href_list = []
for href in a_list:
    href_list.append('http://lawlibraryguides.bu.edu' + href['href'])


## open the xml file and write the header
f = open('/home/primo/libguides/LawGuides.xml', 'wb')
f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
f.write('<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">\n')
f.write('<responseDate>2014-07-17T21:02:57Z</responseDate>\n')
f.write('    <request verb="ListRecords" metadataPrefix="oai_dc" >http://lawlibraryguides.bu.edu/</request>\n')
f.write('<ListRecords>\n')

## write each record
i = 0

while i < len(href_list):
    page = urllib2.urlopen(href_list[i])
    rpage = page.read()
    parsed_html =  BeautifulSoup(rpage)
    metaList = parsed_html.fetch('meta')
    x = 11

    while x < 22:
        if x == 11:
            title = metaList[11]['content']
            title = title[:-1]
            title = title[:title.rfind('.')]
    	    title = title[11:]
            title += ' (Research Guide)'
        elif x == 12:
            creator = metaList[12]['content']
        elif x == 13:
            subject = metaList[13]['content']
            if subject[0:4] == 'Home':
                subject = subject[5:]
            if subject[-9:] == 'LibGuides':
                subject = subject[0:-9]
        elif x == 14:
            description = metaList[14]['content']
            if description[0:9] == 'LibGuides':
                description = description[11:]
            if description.rfind('Home.') > 0:
                description = description[:description.rfind('Home.')]
        elif x == 15:
            publisher =  metaList[15]['content']
            if publisher.rfind('Library Library') > 0:
                publisher = publisher[:publisher.rfind('Library')]

        elif x == 16:
            rights = metaList[16]['content']
        elif x == 17:
            #language = metaList[17]['content']
            language = 'English'
        elif x == 18:
            #print 'identifier: ', metaList[18]['content']
            identifier = 'lawlib:' + str(i)
        elif x == 19:
            created_date = metaList[19]['content']
        elif x == 20:
            updated_date = metaList[20]['content']
        else:
            url = href_list[i]
        x += 1
    id = 'LawGuide-' + str(i)
    f.write('<record>\n')
    f.write('<header>\n')
    f.write('<identifier>')
    f.write(id)
    f.write('</identifier>\n')
    f.write('<datestamp>2009-09-19T06:00:13Z</datestamp>\n')
    f.write('</header>\n')
    f.write('<metadata>\n')
    f.write('<oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:doc="http://www.lyncode.com/xoai" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:dc="http://purl.org/dc/elements/1.1/" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd">\n')
    ## write title
    f.write('<dc:title>')
    f.write(html_escape(title.encode('utf-8')))
    f.write('</dc:title>\n')
    ## write creator
    f.write('<dc:creator>')
    f.write(html_escape(creator.encode('utf-8')))
    f.write('</dc:creator>\n')
    ## write subject
    f.write('<dc:subject>')
    f.write(html_escape(subject.encode('utf-8')))
    f.write('</dc:subject>\n')   
    f.write('<dc:subject>')
    f.write('research guide')
    f.write('</dc:subject>\n') 
    ## write description
    f.write('<dc:description>')
    f.write(html_escape(description.encode('utf-8')))
    f.write('</dc:description>\n')
    ## write publisher
    f.write('<dc:publisher>')
    f.write(html_escape(publisher.encode('utf-8')))
    f.write('</dc:publisher>\n')
    ## write rights
    f.write('<dc:rights>')
    f.write(html_escape(rights.encode('utf-8')))
    f.write('</dc:rights>\n')
    ## write language
    f.write('<dc:language>')
    f.write(html_escape(language.encode('utf-8')))
    f.write('</dc:language>\n')
    ## write date
    f.write('<dc:date>')
    f.write(html_escape(updated_date.encode('utf-8')))
    f.write('</dc:date>\n')
    f.write('<dc:identifier>')
    f.write(url)
    f.write('</dc:identifier>\n')
    f.write('<dc:type>')
    f.write('guide')
    f.write('</dc:type>\n') 
    f.write('</oai_dc:dc>\n</metadata>\n</record>\n')

    i += 1
f.write('</ListRecords>\n')
f.write('</OAI-PMH>\n')
f.close()

## write the xml file as a gzipped file
#f_in = open('LawGuildes.xml','rb')
#f_out = gzip.open('LawGuides.xml.gz', 'wb')
#f_out.writelines(f_in)
#f_out.close()
#f_in.close()

tar = tarfile.open('/home/primo/libguides/LawGuides.xml.tar.gz' , 'w:gz')
tar.add('LawGuides.xml')
tar.close()

## We're done

