
# Creating records for the BU Libraries Research Guides to be ingested into Primo

This code could be used to harvest other WordPress web pages.

## If we haven't done so already, install feedparser

 sudo pip install feedparser

## Import libraries: feedparser and pymarc


    import feedparser
    from pymarc import Record, Field
    import urllib2
    from BeautifulSoup import BeautifulSoup
    import cgi
    
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

#Display xml files that can be used to import metadata from Wordpress
From WordPress, we are able to export the research guides. The export is in an
RSS format that can be parsed by feedparser


    ls *.xml

    bulibraries.wordpress.2014-05-30.xml  bulibraries.wordpress.2014-07-08.xml  guides.xml


use feedparser to load the file


    d = feedparser.parse(r'bulibraries.wordpress.2014-07-08.xml')

## Parse the feed and write it out to a file in OAI-PMH format to be loaded into Primo

We are going to open an output file ('guides.xml') and iterate through d to grab
the fields for each record that we will write to a file. The output file is
formatted as an OAI-PMH file that can be ingested into Primo.
Note that there are a few fields that aren't included in the RSS feed. These are
SEO fields for description and keywords. In the code below you will see that
each guide is briefly loaded and the meta fields pulled from the guide to obtain
these additional fields.


    ## open the xml file and write the header
    f = open('guides.xml', 'wb')
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">\n')
    f.write('<responseDate>2014-07-09T21:02:57Z</responseDate>\n')
    f.write('    <request verb="ListRecords" metadataPrefix="oai_dc" >http://www.bu.edu/library/guides</request>\n')
    f.write('<ListRecords>\n')
    
    ## write each record
    i = 0
    while i < len(d.entries):
        if d.entries[i].wp_status == 'publish':
            f.write('<record>\n')
            f.write('<header>\n')
            f.write('<identifier>\n')
            #id = d.entries[i].id
            id = 'libguide:' + str(i)
            f.write(html_escape(id))
            f.write('</identifier>\n')
            f.write('<datestamp>2009-09-19T06:00:13Z</datestamp>\n')
            f.write('</header>\n')
            f.write('<metadata>\n')
            f.write('<oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:doc="http://www.lyncode.com/xoai" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:dc="http://purl.org/dc/elements/1.1/" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd">\n')
            
            if d.entries[i].has_key('tags'):
                tags = d.entries[i].tags
                authors = []
                subjects = []
                for tag in tags:
                    if tag['scheme'] == 'profile_tax':
                        authors.append(tag['term'])                
                    if tag['scheme'] == 'subject':
                        subjects.append(tag['term'])
            if d.entries[i].has_key('title'):
                title = d.entries[i].title
                f.write('<dc:title>')
                f.write(html_escape(title.encode('utf-8')))
                f.write('</dc:title>\n')
            else:
                # each record in Primo has to have a title, so we provide a default title
                title = 'untitled'
                f.write('<dc:title>')
                f.write(html_escape(title.encode('utf-8')))
                f.write('</dc:title>\n')            
            if len(authors) > 0 :
                for author in authors:
                    f.write('<dc:creator>')
                    f.write(html_escape(author.encode('utf-8')))
                    f.write('</dc:creator>\n')   
            if len(subjects) > 0:
                for subject in subjects:
                    f.write('<dc:subject>')
                    f.write(html_escape(subject.encode('utf-8')))
                    f.write('</dc:subject>\n')  
            if d.entries[i].has_key('link'):    
                f.write('<dc:identifier>')
                f.write(d.entries[i].link)
                f.write('</dc:identifier>\n')             
            if d.entries[i].has_key('published'):
                f.write('<dc:date>')
                f.write(d.entries[i].published)
                f.write('</dc:date>') 
            if d.entries[i].has_key('summary\n'):
                f.write('<dc:abstract>')
                f.write(html_escape(d.entries[i].summary.encode('utf-8')))
                f.write('</dc:abstract>\n') 
            if d.entries[i].has_key('wp_post_type'):
                f.write('<dc:type>')
                f.write(d.entries[i].wp_post_type)
                f.write('</dc:type>\n') 
            f.write('<dc:subject>')
            f.write('research guide')
            f.write('</dc:subject>\n')  
    ## 
    ## The SEO fields aren't included in the RSS feed from WordPress, so we us the link field from the RSS record for each guide
    ## to open load each research guide. We then use BeautifulSoup to grab the "meta" fields from the page. These are parsed
    ## in order to grab the description and keyword fields from the page.
    ##
            page = urllib2.urlopen(d.entries[i].link)
            rpage = page.read()
            parsed_html =  BeautifulSoup(rpage)
            metaList = parsed_html.fetch('meta')
            for l in metaList:
                meta = l.attrs
                meta_desc = ''
                meta_keywords = ''
                if len(meta) == 2:
                    if meta[0][1] == 'description':
                        meta_desc = meta[1][1]
                        #print 'meta_desc: ' , meta_desc
                        f.write('<dc:description>')
                        f.write(html_escape(meta_desc.encode('utf-8')))
                        f.write('</dc:description>\n') 
                    if meta[0][1] == 'keywords':
                        meta_keywords = meta[1][1]
                        #print 'meta_key:  ', meta_keywords  
                        f.write('<dc:subject>')
                        f.write(html_escape(meta_keywords.encode('utf-8')))
                        f.write('</dc:subject>\n') 
            f.write('</oai_dc:dc>\n</metadata>\n</record>\n')
            print 'Record: ', i
            i += 1
        else:
            i += 1
            print 'Record: ', i
            continue
    f.write('</ListRecords>\n')
    f.write('</OAI-PMH>\n')
    f.close()

    Record:  1
    Record:  2
    Record:  3
    Record:  4
    Record:  5
    Record:  6
    Record:  7
    Record:  8
    Record:  9
    Record:  10
    Record:  11
    Record:  12
    Record:  13
    Record:  14
    Record:  15
    Record:  16
    Record:  17
    Record:  18
    Record:  19
    Record:  20
    Record:  21
    Record:  22
    Record:  23
    Record:  24
    Record:  25
    Record:  26
    Record:  27
    Record:  28
    Record:  29
    Record:  30
    Record:  31
    Record:  32
    Record:  33
    Record:  34
    Record:  35
    Record:  36
    Record:  37
    Record:  38
    Record:  39
    Record:  40
    Record:  41
    Record:  42
    Record:  43
    Record:  44
    Record:  45
    Record:  46
    Record:  47
    Record:  48
    Record:  49
    Record:  50
    Record:  51
    Record:  52
    Record:  53
    Record:  54
    Record:  55
    Record:  56
    Record:  57
    Record:  58
    Record:  59
    Record:  60
    Record:  61
    Record:  62
    Record:  63
    Record:  64
    Record:  65
    Record:  66
    Record:  67
    Record:  68
    Record:  69
    Record:  70
    Record:  71
    Record:  72
    Record:  73
    Record:  74
    Record:  75
    Record:  76
    Record:  77
    Record:  78
    Record:  79
    Record:  80
    Record:  81
    Record:  82
    Record:  83
    Record:  84
    Record:  85
    Record:  86
    Record:  87
    Record:  88
    Record:  89
    Record:  90
    Record:  91
    Record:  92
    Record:  93
    Record:  94
    Record:  95
    Record:  96
    Record:  97
    Record:  98
    Record:  99
    Record:  100
    Record:  101
    Record:  102
    Record:  103
    Record:  104
    Record:  105
    Record:  106
    Record:  107
    Record:  108
    Record:  109
    Record:  110
    Record:  111
    Record:  112
    Record:  113
    Record:  114
    Record:  115
    Record:  116
    Record:  117
    Record:  118
    Record:  119
    Record:  120
    Record:  121
    Record:  122
    Record:  123
    Record:  124
    Record:  125
    Record:  126
    Record:  127
    Record:  128
    Record:  129
    Record:  130
    Record:  131
    Record:  132
    Record:  133
    Record:  134
    Record:  135
    Record:  136
    Record:  137
    Record:  138
    Record:  139
    Record:  140
    Record:  141
    Record:  142
    Record:  143
    Record:  144
    Record:  145
    Record:  146
    Record:  147
    Record:  148
    Record:  149
    Record:  150
    Record:  151
    Record:  152
    Record:  153
    Record:  154
    Record:  155
    Record:  156
    Record:  157
    Record:  158
    Record:  159
    Record:  160
    Record:  161
    Record:  162
    Record:  163
    Record:  164
    Record:  165
    Record:  166
    Record:  167
    Record:  168
    Record:  169
    Record:  170
    Record:  171
    Record:  172
    Record:  173
    Record:  174
    Record:  175
    Record:  176
    Record:  177
    Record:  178
    Record:  179
    Record:  180
    Record:  181
    Record:  182
    Record:  183
    Record:  184
    Record:  185
    Record:  186
    Record:  187
    Record:  188
    Record:  189
    Record:  190
    Record:  191
    Record:  192
    Record:  193
    Record:  194
    Record:  195
    Record:  196
    Record:  197
    Record:  198
    Record:  199
    Record:  200
    Record:  201
    Record:  202
    Record:  203
    Record:  204
    Record:  205
    Record:  206
    Record:  207
    Record:  208
    Record:  209
    Record:  210
    Record:  211
    Record:  212
    Record:  213
    Record:  214
    Record:  215
    Record:  216
    Record:  217
    Record:  218
    Record:  219
    Record:  220
    Record:  221
    Record:  222
    Record:  223
    Record:  224
    Record:  225
    Record:  226
    Record:  227
    Record:  228
    Record:  229
    Record:  230
    Record:  231
    Record:  232
    Record:  233
    Record:  234
    Record:  235
    Record:  236
    Record:  237
    Record:  238
    Record:  239
    Record:  240
    Record:  241
    Record:  242
    Record:  243
    Record:  244
    Record:  245
    Record:  246
    Record:  247
    Record:  248
    Record:  249
    Record:  250
    Record:  251
    Record:  252
    Record:  253
    Record:  254
    Record:  255
    Record:  256
    Record:  257
    Record:  258
    Record:  259
    Record:  260
    Record:  261
    Record:  262
    Record:  263
    Record:  264
    Record:  265
    Record:  266
    Record:  267
    Record:  268
    Record:  269
    Record:  270
    Record:  271
    Record:  272
    Record:  273
    Record:  274
    Record:  275
    Record:  276
    Record:  277
    Record:  278
    Record:  279
    Record:  280
    Record:  281
    Record:  282
    Record:  283
    Record:  284
    Record:  285
    Record:  286
    Record:  287
    Record:  288
    Record:  289
    Record:  290
    Record:  291
    Record:  292
    Record:  293
    Record:  294
    Record:  295
    Record:  296
    Record:  297
    Record:  298
    Record:  299
    Record:  300
    Record:  301
    Record:  302
    Record:  303
    Record:  304
    Record:  305
    Record:  306
    Record:  307
    Record:  308
    Record:  309
    Record:  310
    Record:  311
    Record:  312
    Record:  313
    Record:  314
    Record:  315
    Record:  316
    Record:  317
    Record:  318
    Record:  319
    Record:  320
    Record:  321
    Record:  322
    Record:  323
    Record:  324
    Record:  325
    Record:  326
    Record:  327
    Record:  328
    Record:  329
    Record:  330
    Record:  331
    Record:  332
    Record:  333
    Record:  334
    Record:  335
    Record:  336
    Record:  337
    Record:  338
    Record:  339
    Record:  340
    Record:  340
    Record:  341
    Record:  342
    Record:  343
    Record:  344
    Record:  345
    Record:  346
    Record:  347
    Record:  348
    Record:  349
    Record:  350
    Record:  351
    Record:  352
    Record:  353
    Record:  354
    Record:  355
    Record:  356
    Record:  357
    Record:  359
    Record:  360
    Record:  360
    Record:  361
    Record:  362
    Record:  363
    Record:  364
    Record:  365
    Record:  366
    Record:  367
    Record:  368
    Record:  369
    Record:  370
    Record:  371
    Record:  372
    Record:  373
    Record:  374
    Record:  375
    Record:  376
    Record:  377
    Record:  378
    Record:  379
    Record:  380
    Record:  381
    Record:  382
    Record:  383
    Record:  384
    Record:  385
    Record:  386
    Record:  387
    Record:  388
    Record:  389
    Record:  390
    Record:  391
    Record:  392
    Record:  393
    Record:  394
    Record:  395
    Record:  396
    Record:  397
    Record:  398
    Record:  399
    Record:  400
    Record:  401
    Record:  402
    Record:  403
    Record:  404
    Record:  405
    Record:  406
    Record:  407
    Record:  408
    Record:  409
    Record:  410
    Record:  411
    Record:  412
    Record:  413
    Record:  414
    Record:  415
    Record:  416
    Record:  417
    Record:  418
    Record:  419
    Record:  420
    Record:  421
    Record:  422
    Record:  423
    Record:  424
    Record:  425
    Record:  426
    Record:  427
    Record:  428
    Record:  429
    Record:  430
    Record:  431
    Record: 

#Use the code below for testing


    i = 0
    while i < len(d.entries):
        if d.entries[i].wp_status == 'publish':
    #        i += 1
    #        continue
    #    else:
            print ' '
            print 'Record: ' , str(i)
            if d.entries[i].has_key('tags'):
                tags = d.entries[i].tags
                authors = []
                subjects = []
                for tag in tags:
                    if tag['scheme'] == 'profile_tax':
                        authors.append(tag['term'])                
                    if tag['scheme'] == 'subject':
                        subjects.append(tag['term'])
            if d.entries[i].has_key('title'):
                print 'title:  ', d.entries[i].title
            if len(authors) > 0 :
                for author in authors:
                    print 'author: ', author
            if len(subjects) > 0:
                for subject in subjects:
                    print 'subject: ', subject
            if d.entries[i].has_key('link'):    
                print 'link:   ', d.entries[i].link
    #        if d.entries[i].has_key('id'):    
    #            print 'link:   ', d.entries[i].id
            if d.entries[i].has_key('published'):
                print 'published: ', d.entries[i].published
            if d.entries[i].has_key('summary'):
                print 'summary: ', d.entries[i].summary
            if d.entries[i].has_key('author_detail'):
                print 'email: ', d.entries[i].author_detail['name'],'@bu.edu'
            #if d.entries[i].has_key('status'):
            print 'status: ', d.entries[i].wp_status
            if d.entries[i].has_key('wp_postmeta'):
                print 'postmeta: ', d.entries[i].wp_postmeta
            if d.entries[i].has_key('wp_post_type'):
                print 'postType: ', d.entries[i].wp_post_type
            if d.entries[i].has_key('excerpt_encoded'):
                print 'excerpt: ', d.entries[i].excerpt_encoded
            page = urllib2.urlopen(d.entries[i].link)
            rpage = page.read()
            parsed_html =  BeautifulSoup(rpage)
            metaList = parsed_html.fetch('meta')
            for l in metaList:
                meta = l.attrs
                meta_desc = ''
                meta_keywords = ''
                if len(meta) == 2:
                    if meta[0][1] == 'description':
                        meta_desc = meta[1][1]
                        print 'meta_desc: ' , meta_desc
                    if meta[0][1] == 'keywords':
                        meta_keywords = meta[1][1]
                        print 'meta_key:  ', meta_keywords  
    #        print 'meta_desc: ' , meta_desc
    #        print 'meta_key:  ', meta_keywords
            print ' '
            i += 1
        else:
            i += 1
            continue

     
    Record:  340
    title:   WR150: Russian Literature Sources
    author:  Diane D’Almeida
    subject:  Literature &amp; Language
    link:    http://www.bu.edu/library/guide/wr150russian/
    published:  Mon, 16 May 2011 21:45:49 +0000
    summary:  
    email:  dalmeida @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  341
    title:   African Newspapers in Print
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/newsresources/currentevents/
    published:  Mon, 16 May 2011 21:45:57 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  342
    title:   Background Sources on Current Events in Africa
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/newsresources/background/
    published:  Mon, 16 May 2011 21:45:57 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  343
    title:   African News Resources
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/newsresources/
    published:  Mon, 16 May 2011 21:45:57 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  344
    title:   African Newspapers on Microfilm
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/newsresources/microfilm/
    published:  Mon, 16 May 2011 21:45:58 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  345
    title:   African Newspapers Online
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/newsresources/onlinenewspapers/
    published:  Mon, 16 May 2011 21:45:58 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  346
    title:   Newspaper Articles on Nelson Mandela's Release
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/newsresources/currentevents/mandela/
    published:  Mon, 16 May 2011 21:45:58 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  347
    title:   Primary Sources and Archival Collections: Lesotho - Libya
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/collections_index/collections_l/
    published:  Mon, 16 May 2011 21:45:58 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  348
    title:   Primary Sources and Archival Collections: Egypt - Ethiopia
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/collections_index/collections_e/
    published:  Mon, 16 May 2011 21:45:58 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  349
    title:   Primary Sources and Archival Collections: Djibouti
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/collections_index/collections_d/
    published:  Mon, 16 May 2011 21:45:58 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  350
    title:   Primary Sources and Archival Collections: Gabon - Guinea-Bissau
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/collections_index/collections_g/
    published:  Mon, 16 May 2011 21:45:58 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  351
    title:   Primary Sources and Archival Collections: Kenya
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/collections_index/collections_k/
    published:  Mon, 16 May 2011 21:45:58 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  352
    title:   Primary Sources and Archival Collections: Madagascar-Mozambique
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/collections_index/collections_m/
    published:  Mon, 16 May 2011 21:45:58 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  353
    title:   Primary Sources and Archival Collections: Namibia, Niger, Nigeria
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/collections_index/collections_n/
    published:  Mon, 16 May 2011 21:45:58 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  354
    title:   Primary Sources and Archival Collections: Rwanda
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/collections_index/collections_r/
    published:  Mon, 16 May 2011 21:45:58 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  355
    title:   Primary Sources and Archival Collections: Senegal - Swaziland
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/collections_index/collections_s/
    published:  Mon, 16 May 2011 21:45:59 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  356
    title:   Primary Sources and Archival Collections: Algeria - Angola
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/collections_index/collections_a/
    published:  Mon, 16 May 2011 21:45:59 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  357
    title:   Primary Sources and Archival Collections: Benin - Botswana
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/collections_index/collections_b/
    published:  Mon, 16 May 2011 21:45:59 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  360
    title:   Primary Sources and Archival Collections: Cameroon - Cote d'Ivoire
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/collections_index/collections_c/
    published:  Mon, 16 May 2011 21:45:59 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  361
    title:   Primary Sources and Archival Collections: Tanzania - Tunisia
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/collections_index/collections_t/
    published:  Mon, 16 May 2011 21:45:59 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  362
    title:   Primary Sources and Archival Collections: Uganda
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/collections_index/collections_u/
    published:  Mon, 16 May 2011 21:45:59 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  363
    title:   Primary Sources and Archival Collections: Zambia and Zimbabwe
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/collections_index/collections_z/
    published:  Mon, 16 May 2011 21:45:59 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  364
    title:   Primary Sources and Archival Collections: African Regions
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/collections_index/collections_regions/
    published:  Mon, 16 May 2011 21:45:59 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
    meta_desc:  Primary sources for study of African regions.
    meta_key:   African Studies, Primary documents, microfilm
     
     
    Record:  365
    title:   Primary Sources in the ASL
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/collections_index/collections_various/
    published:  Mon, 16 May 2011 21:45:59 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  366
    title:   Primary Resources and Archival Collections on Africa: Index Page
    author:  Beth Restrick
    subject:  African Studies
    subject:  Area &amp; Cultural Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/collections_index/
    published:  Mon, 16 May 2011 21:45:59 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  367
    title:   Primary Resources and Archival Collections: Index of Finding Guides
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/guide_index/
    published:  Mon, 16 May 2011 21:45:59 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  368
    title:   Primary Resources and Archival Collections Held Internationally and in the U.S.
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/guide_index/collections_other/
    published:  Mon, 16 May 2011 21:45:59 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  369
    title:   Primary Resources and Archival Collections: Algeria - Zimbabwe
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/guide_index/collection_countries/
    published:  Mon, 16 May 2011 21:45:59 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  370
    title:   Primary Resources and Archival Collections Held in Africa
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/guide_index/collections_in_africa/
    published:  Mon, 16 May 2011 21:45:59 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  371
    title:   HI588: Women, Power and Culture in Africa
    author:  Beth Restrick
    subject:  African Studies
    subject:  Anthropology
    subject:  History
    subject:  Women's Studies
    link:    http://www.bu.edu/library/guide/hi588/
    published:  Mon, 16 May 2011 21:45:59 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  372
    title:   ID 116: Africa Today
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/id116/
    published:  Mon, 16 May 2011 21:45:59 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  373
    title:   Primary Resources and Archival Collections: Missions
    author:  Beth Restrick
    author:  David Westley
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/guide_index/collections_missions/
    published:  Mon, 16 May 2011 21:46:00 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  374
    title:   Primary Resources and Archival Collections: General Guides
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/guide_index/collections_general/
    published:  Mon, 16 May 2011 21:46:00 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  375
    title:   Primary Resources about Africa: Research Strategies
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanprimaryarchives/
    published:  Mon, 16 May 2011 21:46:00 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  376
    title:   Zulu Language Resources
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/zulu/
    published:  Mon, 16 May 2011 21:46:00 +0000
    summary:  
    email:  brestric @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  377
    title:   Swahili Publishing Terms
    author:  David Westley
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/swahiliterms/
    published:  Mon, 16 May 2011 21:46:00 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  378
    title:   Guide to Using Web Resources for the Study of Africa
    author:  Beth Restrick
    author:  David Westley
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africa-webresources/
    published:  Mon, 16 May 2011 21:46:01 +0000
    summary:  
    email:  brestric @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  379
    title:   Researching Africa: Problems, Initiatives, Resources
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/researchingafrica/
    published:  Mon, 16 May 2011 21:46:01 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  380
    title:   Africa: Getting Started with Research
    author:  Beth Restrick
    author:  David Westley
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africaresearch/
    published:  Mon, 16 May 2011 21:46:01 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  381
    title:   Exploring the Culture and Arts of Africa: A Survey of the Literature
    author:  Beth Restrick
    author:  David Westley
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanculture/
    published:  Mon, 16 May 2011 21:46:01 +0000
    summary:  
    email:  brestric @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  382
    title:   Human Rights and Refugees in Africa
    author:  David Westley
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/humanrights/
    published:  Mon, 16 May 2011 21:46:01 +0000
    summary:  
    email:  brestric @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  383
    title:   Women's Issues in Africa: Finding Information on the Web
    author:  Beth Restrick
    author:  David Westley
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanwomen/
    published:  Mon, 16 May 2011 21:46:01 +0000
    summary:  
    email:  brestric @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  384
    title:   Research Guide: Peoples and Cultures of Africa
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africanpeoples/
    published:  Mon, 16 May 2011 21:46:01 +0000
    summary:  
    email:  shirleyl @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  385
    title:   Web Resources for the Peoples and Cultures of Africa
    author:  Beth Restrick
    subject:  African Studies
    link:    http://www.bu.edu/library/guide/africa-2/
    published:  Mon, 16 May 2011 21:46:01 +0000
    summary:  
    email:  brestric @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  386
    title:   American Art
    subject:  American Studies
    subject:  Area &amp; Cultural Studies
    subject:  Arts
    subject:  Arts &amp; Humanities
    subject:  Images
    link:    http://www.bu.edu/library/guide/americanart/
    published:  Mon, 16 May 2011 21:46:10 +0000
    summary:  
    email:  rthomas @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  387
    title:   Abortion
    author:  J. Christina Smith
    subject:  Health
    subject:  Law &amp; Ethics
    subject:  Politics and Public Policy
    subject:  Women's Studies
    link:    http://www.bu.edu/library/guide/abortion/
    published:  Mon, 16 May 2011 21:46:10 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  388
    title:   Classical Studies
    subject:  Archaeology
    subject:  Area &amp; Cultural Studies
    subject:  Arts
    subject:  Arts &amp; Humanities
    subject:  History
    subject:  Literature &amp; Language
    subject:  Middle East
    link:    http://www.bu.edu/library/guide/classics/
    published:  Mon, 16 May 2011 21:46:11 +0000
    summary:  
    email:  rthomas @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  389
    title:   Patent and Trademark Searching
    author:  Paula Carey
    subject:  Business &amp; Management
    subject:  Engineering
    subject:  Science &amp; Engineering
    link:    http://www.bu.edu/library/guide/patents/
    published:  Mon, 16 May 2011 21:46:11 +0000
    summary:  
    email:  pac @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  390
    title:   Modern and Contemporary Art
    author:  Ruth Thomas
    subject:  Arts
    subject:  Arts &amp; Humanities
    subject:  History
    link:    http://www.bu.edu/library/guide/20thart/
    published:  Mon, 16 May 2011 21:46:11 +0000
    summary:  
    email:  rthomas @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  391
    title:   Hispanic American Studies
    author:  J. Christina Smith
    subject:  American Studies
    subject:  Area &amp; Cultural Studies
    subject:  Psychology and Sociology
    link:    http://www.bu.edu/library/guide/hispanic-american-studies/
    published:  Mon, 16 May 2011 21:46:11 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  392
    title:   Clothing, Fashion & Appearance
    author:  J. Christina Smith
    subject:  Anthropology
    subject:  Area &amp; Cultural Studies
    subject:  Arts &amp; Humanities
    subject:  Psychology and Sociology
    link:    http://www.bu.edu/library/guide/clothing/
    published:  Mon, 16 May 2011 21:46:11 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  393
    title:   Standards
    author:  Paula Carey
    subject:  Engineering
    subject:  Interdisciplinary Sciences
    subject:  Science &amp; Engineering
    link:    http://www.bu.edu/library/guide/standards/
    published:  Mon, 16 May 2011 21:46:12 +0000
    summary:  
    email:  pac @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  394
    title:   Social Work
    author:  Meredith Kirkpatrick
    subject:  Psychology and Sociology
    link:    http://www.bu.edu/library/guide/socwork/
    published:  Mon, 16 May 2011 21:46:12 +0000
    summary:  
    email:  meredith @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  395
    title:   Criminology & Criminal Justice
    author:  J. Christina Smith
    subject:  Law &amp; Ethics
    subject:  Psychology and Sociology
    link:    http://www.bu.edu/library/guide/criminology-criminaljustice/
    published:  Mon, 16 May 2011 21:46:12 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  396
    title:   Juvenile Justice
    author:  J. Christina Smith
    subject:  Law &amp; Ethics
    subject:  Psychology and Sociology
    link:    http://www.bu.edu/library/guide/juvenilejustice/
    published:  Mon, 16 May 2011 21:46:12 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  397
    title:   Gastronomy
    author:  J. Christina Smith
    subject:  Anthropology
    subject:  Gastronomy
    link:    http://www.bu.edu/library/guide/gastronomy/
    published:  Mon, 16 May 2011 21:46:12 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  398
    title:   African American Studies
    author:  J. Christina Smith
    subject:  African Studies
    subject:  American Studies
    subject:  Area &amp; Cultural Studies
    subject:  Psychology and Sociology
    link:    http://www.bu.edu/library/guide/african-american-studies/
    published:  Mon, 16 May 2011 21:46:12 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  399
    title:   Asian American Studies
    author:  J. Christina Smith
    subject:  American Studies
    subject:  Area &amp; Cultural Studies
    subject:  Asian Studies
    subject:  Psychology and Sociology
    link:    http://www.bu.edu/library/guide/asian-american-studies/
    published:  Mon, 16 May 2011 21:46:13 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  400
    title:   Japanese Art and Architecture
    subject:  Arts
    subject:  Asian Studies
    subject:  History
    link:    http://www.bu.edu/library/guide/japanart/
    published:  Mon, 16 May 2011 21:46:13 +0000
    summary:  
    email:  rthomas @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  401
    title:   LGBTQIA and Gender Identity Studies
    author:  J. Christina Smith
    subject:  Law &amp; Ethics
    subject:  Psychology and Sociology
    link:    http://www.bu.edu/library/guide/lgbtgenderstudies/
    published:  Mon, 16 May 2011 21:46:13 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  402
    title:   Bioethics
    author:  Lisa Philpotts
    subject:  Health
    subject:  Law &amp; Ethics
    subject:  Life Sciences
    link:    http://www.bu.edu/library/guide/bioethics/
    published:  Mon, 16 May 2011 21:46:13 +0000
    summary:  
    email:  philpo @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  403
    title:   Stem Cell Research
    author:  Lisa Philpotts
    subject:  Health
    subject:  Life Sciences
    link:    http://www.bu.edu/library/guide/stemcell/
    published:  Mon, 16 May 2011 21:46:13 +0000
    summary:  
    email:  philpo @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  404
    title:   Oral History & Family History
    author:  J. Christina Smith
    subject:  American Studies
    subject:  History
    link:    http://www.bu.edu/library/guide/oralhistory/
    published:  Mon, 16 May 2011 21:46:13 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  405
    title:   Smoking and Tobacco
    author:  J. Christina Smith
    subject:  Health
    subject:  Politics and Public Policy
    subject:  Psychology and Sociology
    link:    http://www.bu.edu/library/guide/smokingandtobacco/
    published:  Mon, 16 May 2011 21:46:14 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  406
    title:   Biomedical Engineering
    author:  Paula Carey
    subject:  Engineering
    link:    http://www.bu.edu/library/guide/biomed/
    published:  Mon, 16 May 2011 21:46:15 +0000
    summary:  
    email:  pac @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  407
    title:   Chemistry
    author:  J.D. Kotula
    subject:  Physical Sciences
    link:    http://www.bu.edu/library/guide/chemrg/
    published:  Mon, 16 May 2011 21:46:15 +0000
    summary:  
    email:  jdkotula @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  408
    title:   Computer Science
    author:  J.D. Kotula
    subject:  Mathematics, Computer Science and Statistics
    link:    http://www.bu.edu/library/guide/csrg/
    published:  Mon, 16 May 2011 21:46:15 +0000
    summary:  
    email:  jdkotula @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  409
    title:   Electrical & Computer Engineering
    author:  Paula Carey
    subject:  Engineering
    link:    http://www.bu.edu/library/guide/ece/
    published:  Mon, 16 May 2011 21:46:15 +0000
    summary:  
    email:  pac @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  410
    title:   Ecology
    author:  Jenna Ryan
    subject:  Life Sciences
    link:    http://www.bu.edu/library/guide/ecologyguide/
    published:  Mon, 16 May 2011 21:46:15 +0000
    summary:  
    email:  jennary @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  411
    title:   Massachusetts Geology
    author:  Jenna Ryan
    subject:  Physical Sciences
    subject:  Urban Studies
    link:    http://www.bu.edu/library/guide/gmassrg/
    published:  Mon, 16 May 2011 21:46:15 +0000
    summary:  
    email:  jennary @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  412
    title:   Mathematics
    author:  Paula Carey
    subject:  Mathematics, Computer Science and Statistics
    link:    http://www.bu.edu/library/guide/mathrg/
    published:  Mon, 16 May 2011 21:46:16 +0000
    summary:  
    email:  pac @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  413
    title:   Marine Biology
    author:  Jenna Ryan
    subject:  Life Sciences
    link:    http://www.bu.edu/library/guide/marinebioguide/
    published:  Mon, 16 May 2011 21:46:16 +0000
    summary:  
    email:  jennary @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  414
    title:   Mathematical Statistics
    author:  Paula Carey
    subject:  Mathematics, Computer Science and Statistics
    link:    http://www.bu.edu/library/guide/mathstats/
    published:  Mon, 16 May 2011 21:46:16 +0000
    summary:  
    email:  pac @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  415
    title:   Mechanical Engineering
    author:  Paula Carey
    subject:  Engineering
    link:    http://www.bu.edu/library/guide/mech/
    published:  Mon, 16 May 2011 21:46:16 +0000
    summary:  
    email:  pac @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  416
    title:   Nanotechnology
    author:  Paula Carey
    subject:  Engineering
    subject:  Interdisciplinary Sciences
    link:    http://www.bu.edu/library/guide/nanotech/
    published:  Mon, 16 May 2011 21:46:16 +0000
    summary:  
    email:  pac @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  417
    title:   Nonlinear Science
    author:  Paula Carey
    subject:  Engineering
    subject:  Interdisciplinary Sciences
    link:    http://www.bu.edu/library/guide/nonlinear/
    published:  Mon, 16 May 2011 21:46:16 +0000
    summary:  
    email:  pac @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  418
    title:   Photonics
    author:  Paula Carey
    subject:  Engineering
    subject:  Interdisciplinary Sciences
    subject:  Science &amp; Engineering
    link:    http://www.bu.edu/library/guide/photon/
    published:  Mon, 16 May 2011 21:46:17 +0000
    summary:  
    email:  pac @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  419
    title:   Physics
    author:  Mary Foppiani
    subject:  Physical Sciences
    link:    http://www.bu.edu/library/guide/phyguide/
    published:  Mon, 16 May 2011 21:46:17 +0000
    summary:  
    email:  foppiani @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  420
    title:   Women's Studies
    author:  J. Christina Smith
    subject:  Women's Studies
    link:    http://www.bu.edu/library/guide/womens-studies/
    published:  Mon, 16 May 2011 21:46:17 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  421
    title:   Animal Rights
    author:  Meredith Kirkpatrick
    subject:  Law &amp; Ethics
    link:    http://www.bu.edu/library/guide/animalrights/
    published:  Mon, 16 May 2011 21:46:17 +0000
    summary:  
    email:  meredith @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  422
    title:   Women in the United States in the 19th Century
    author:  J. Christina Smith
    subject:  American Studies
    subject:  History
    subject:  Women's Studies
    link:    http://www.bu.edu/library/guide/women19thcenturyus/
    published:  Mon, 16 May 2011 21:46:17 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  423
    title:   United States History
    author:  Donald Altschiller
    subject:  History
    link:    http://www.bu.edu/library/guide/americanhistory/
    published:  Mon, 16 May 2011 21:46:17 +0000
    summary:  
    email:  donaltsc @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  424
    title:   Women in Developing Countries
    author:  J. Christina Smith
    subject:  Women's Studies
    link:    http://www.bu.edu/library/guide/women-in-developing-countries/
    published:  Mon, 16 May 2011 21:46:17 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  425
    title:   Drug Abuse
    author:  J. Christina Smith
    subject:  Health
    subject:  Law &amp; Ethics
    subject:  Politics and Public Policy
    subject:  Psychology and Sociology
    link:    http://www.bu.edu/library/guide/drugabuse/
    published:  Mon, 16 May 2011 21:46:17 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  426
    title:   Philosophy
    author:  J. Christina Smith
    subject:  Religion and Philosophy
    link:    http://www.bu.edu/library/guide/philosophy/
    published:  Mon, 16 May 2011 21:46:18 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  427
    title:   Alcoholism
    author:  J. Christina Smith
    subject:  Health
    subject:  Psychology and Sociology
    link:    http://www.bu.edu/library/guide/alcoholism/
    published:  Mon, 16 May 2011 21:46:18 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  428
    title:   Art History
    subject:  American Studies
    subject:  Archaeology
    subject:  Arts
    subject:  Arts &amp; Humanities
    subject:  Asian Studies
    subject:  History
    subject:  Images
    subject:  Middle East
    subject:  Urban Studies
    link:    http://www.bu.edu/library/guide/arthistory/
    published:  Mon, 16 May 2011 21:46:18 +0000
    summary:  
    email:  rthomas @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  429
    title:   Plant Biology
    author:  Jenna Ryan
    subject:  Life Sciences
    link:    http://www.bu.edu/library/guide/plantbio/
    published:  Mon, 16 May 2011 21:46:18 +0000
    summary:  
    email:  jennary @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  430
    title:   German Language and Literature - in the Library and on the Web
    author:  Diane D’Almeida
    subject:  Arts &amp; Humanities
    subject:  Literature &amp; Language
    link:    http://www.bu.edu/library/guide/german/
    published:  Mon, 16 May 2011 21:46:18 +0000
    summary:  
    email:  dalmeida @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  431
    title:   Anthropology
    author:  J. Christina Smith
    subject:  African Studies
    subject:  Anthropology
    link:    http://www.bu.edu/library/guide/anthropology/
    published:  Mon, 16 May 2011 21:46:18 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  432
    title:   Death Studies
    author:  J. Christina Smith
    subject:  Psychology and Sociology
    link:    http://www.bu.edu/library/guide/deathstudies/
    published:  Mon, 16 May 2011 21:46:19 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  433
    title:   Italian Language and Literature - in the Library and on the Web
    author:  Diane D’Almeida
    subject:  Arts &amp; Humanities
    subject:  Literature &amp; Language
    link:    http://www.bu.edu/library/guide/italian/
    published:  Mon, 16 May 2011 21:46:19 +0000
    summary:  
    email:  dalmeida @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  434
    title:   American Architecture
    author:  Ruth Thomas
    subject:  American Studies
    subject:  Archaeology
    subject:  Arts
    subject:  History
    subject:  Images
    subject:  Urban Studies
    link:    http://www.bu.edu/library/guide/americanarchitecture/
    published:  Mon, 16 May 2011 21:46:19 +0000
    summary:  
    email:  rthomas @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  435
    title:   American Studies
    author:  Ruth Thomas
    subject:  American Studies
    subject:  Archaeology
    subject:  Arts
    subject:  Arts &amp; Humanities
    subject:  History
    subject:  Literature &amp; Language
    subject:  Women's Studies
    link:    http://www.bu.edu/library/guide/americanstudies/
    published:  Mon, 16 May 2011 21:46:19 +0000
    summary:  
    email:  rthomas @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  436
    title:   Guns and Gun Control
    author:  J. Christina Smith
    subject:  Law &amp; Ethics
    subject:  Politics and Public Policy
    subject:  Psychology and Sociology
    link:    http://www.bu.edu/library/guide/guns-and-gun-control/
    published:  Mon, 16 May 2011 21:46:19 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  437
    title:   Islamic Art and Architecture
    author:  Ruth Thomas
    subject:  African Studies
    subject:  Archaeology
    subject:  Area &amp; Cultural Studies
    subject:  Arts
    subject:  Arts &amp; Humanities
    subject:  History
    subject:  Literature &amp; Language
    subject:  Middle East
    subject:  Religion and Philosophy
    link:    http://www.bu.edu/library/guide/islamicart/
    published:  Mon, 16 May 2011 21:46:19 +0000
    summary:  
    email:  rthomas @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  438
    title:   Archaeology
    author:  Ruth Thomas
    subject:  African Studies
    subject:  American Studies
    subject:  Anthropology
    subject:  Archaeology
    subject:  Arts
    subject:  History
    subject:  Middle East
    link:    http://www.bu.edu/library/guide/archaeology/
    published:  Mon, 16 May 2011 21:46:19 +0000
    summary:  
    email:  rthomas @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  439
    title:   Citing Your Sources: CSE (Council of Science Editors) Style
    author:  Paula Carey
    subject:  Interdisciplinary Sciences
    subject:  Science &amp; Engineering
    link:    http://www.bu.edu/library/guide/csestyle/
    published:  Mon, 16 May 2011 21:46:19 +0000
    summary:  
    email:  pac @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  440
    title:   Astronomy & Astrophysics
    author:  Mary Foppiani
    subject:  Physical Sciences
    link:    http://www.bu.edu/library/guide/astro/
    published:  Mon, 16 May 2011 21:46:19 +0000
    summary:  
    email:  foppiani @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  441
    title:   Spanish and Latin American Language and Literature - in the Library and on the Web
    author:  Diane D’Almeida
    subject:  Arts &amp; Humanities
    subject:  Literature &amp; Language
    link:    http://www.bu.edu/library/guide/spanish/
    published:  Mon, 16 May 2011 21:46:20 +0000
    summary:  
    email:  dalmeida @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  442
    title:   Sociology
    author:  J. Christina Smith
    subject:  Psychology and Sociology
    link:    http://www.bu.edu/library/guide/sociology/
    published:  Mon, 16 May 2011 21:46:20 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  443
    title:   Seismology
    author:  Jenna Ryan
    subject:  Physical Sciences
    subject:  Science &amp; Engineering
    link:    http://www.bu.edu/library/guide/seismology/
    published:  Mon, 16 May 2011 21:46:20 +0000
    summary:  
    email:  jennary @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  444
    title:   Architecture
    author:  Ruth Thomas
    subject:  American Studies
    subject:  Arts
    subject:  History
    link:    http://www.bu.edu/library/guide/architecture/
    published:  Mon, 16 May 2011 21:46:20 +0000
    summary:  
    email:  rthomas @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  445
    title:   Literature
    author:  Diane D’Almeida
    subject:  Literature &amp; Language
    link:    http://www.bu.edu/library/guide/liternet/
    published:  Mon, 16 May 2011 21:46:20 +0000
    summary:  
    email:  dalmeida @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  446
    title:   Linguistics
    author:  Diane D’Almeida
    subject:  Literature &amp; Language
    link:    http://www.bu.edu/library/guide/ling/
    published:  Mon, 16 May 2011 21:46:20 +0000
    summary:  
    email:  dalmeida @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  447
    title:   Psychology
    author:  Meredith Kirkpatrick
    subject:  Psychology and Sociology
    link:    http://www.bu.edu/library/guide/psych/
    published:  Mon, 16 May 2011 21:46:21 +0000
    summary:  
    email:  meredith @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  448
    title:   Population Studies
    author:  J. Christina Smith
    subject:  Psychology and Sociology
    subject:  Urban Studies
    link:    http://www.bu.edu/library/guide/populationstudies/
    published:  Mon, 16 May 2011 21:46:21 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  449
    title:   Photography
    author:  Ruth Thomas
    subject:  Arts
    subject:  Communications
    subject:  History
    subject:  Literature &amp; Language
    subject:  Women's Studies
    link:    http://www.bu.edu/library/guide/phot/
    published:  Mon, 16 May 2011 21:46:21 +0000
    summary:  
    email:  rthomas @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  450
    title:   Folklore & Fairy Tales
    author:  J. Christina Smith
    subject:  Anthropology
    subject:  Literature &amp; Language
    link:    http://www.bu.edu/library/guide/folklore/
    published:  Mon, 16 May 2011 21:46:21 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  451
    title:   Biography
    author:  J. Christina Smith
    subject:  Area &amp; Cultural Studies
    subject:  Arts &amp; Humanities
    subject:  Social Science
    link:    http://www.bu.edu/library/guide/biography/
    published:  Mon, 16 May 2011 21:46:21 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  452
    title:   Book Reviews
    author:  Donald Altschiller
    subject:  Area &amp; Cultural Studies
    subject:  Arts &amp; Humanities
    subject:  Social Science
    link:    http://www.bu.edu/library/guide/bookreviews/
    published:  Mon, 16 May 2011 21:46:22 +0000
    summary:  
    email:  donaltsc @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  453
    title:   French Language and Literature - in the Library and on the Web
    author:  Diane D’Almeida
    subject:  Arts &amp; Humanities
    subject:  Literature &amp; Language
    link:    http://www.bu.edu/library/guide/french/
    published:  Mon, 16 May 2011 21:46:22 +0000
    summary:  
    email:  dalmeida @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  454
    title:   Ethnic Studies
    author:  J. Christina Smith
    subject:  American Studies
    subject:  Psychology and Sociology
    link:    http://www.bu.edu/library/guide/ethnicstudies/
    published:  Mon, 16 May 2011 21:46:22 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  455
    title:   
    author:  Jenna Ryan
    subject:  Life Sciences
    link:    http://www.bu.edu/library/guide/zoo/
    published:  Mon, 16 May 2011 21:46:22 +0000
    summary:  
    email:  jennary @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  456
    title:   Citing Your Sources
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/citeys/
    published:  Mon, 16 May 2011 21:46:22 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  457
    title:   Middle Eastern Americans
    author:  J. Christina Smith
    subject:  American Studies
    subject:  Area &amp; Cultural Studies
    subject:  Psychology and Sociology
    link:    http://www.bu.edu/library/guide/middle-eastern-americans/
    published:  Mon, 16 May 2011 21:46:22 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  458
    title:   Capital Punishment
    author:  J. Christina Smith
    subject:  Law &amp; Ethics
    subject:  Politics and Public Policy
    subject:  Psychology and Sociology
    link:    http://www.bu.edu/library/guide/capitalpunishment/
    published:  Mon, 16 May 2011 21:46:22 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  459
    title:   Boston: Newspapers and Media
    subject:  Urban Studies
    link:    http://www.bu.edu/library/guide/boston/newspaperlink/
    published:  Mon, 16 May 2011 21:46:22 +0000
    summary:  
    email:  donaltsc @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  460
    title:   Cities & Urbanization
    author:  J. Christina Smith
    subject:  Psychology and Sociology
    subject:  Urban Studies
    link:    http://www.bu.edu/library/guide/citiesurbanization/
    published:  Mon, 16 May 2011 21:46:23 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  461
    title:   Native American Studies
    author:  J. Christina Smith
    subject:  American Studies
    subject:  Anthropology
    subject:  Archaeology
    subject:  Area &amp; Cultural Studies
    link:    http://www.bu.edu/library/guide/nativeamericanstudies/
    published:  Mon, 16 May 2011 21:46:23 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  462
    title:   Family Studies
    author:  J. Christina Smith
    subject:  Psychology and Sociology
    link:    http://www.bu.edu/library/guide/familystudies/
    published:  Mon, 16 May 2011 21:46:23 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  463
    title:   Images, Illustrations, Reproductions
    author:  Ruth Thomas
    subject:  Arts
    subject:  Communications
    subject:  History
    subject:  Images
    subject:  Law &amp; Ethics
    subject:  Literature &amp; Language
    subject:  Religion and Philosophy
    subject:  Women's Studies
    link:    http://www.bu.edu/library/guide/findimages/illustrations/
    published:  Mon, 16 May 2011 21:46:23 +0000
    summary:  
    email:  rthomas @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  464
    title:   Environmental Science
    author:  Jenna Ryan
    subject:  Interdisciplinary Sciences
    subject:  Life Sciences
    subject:  Science &amp; Engineering
    link:    http://www.bu.edu/library/guide/esguide/
    published:  Mon, 16 May 2011 21:46:24 +0000
    summary:  
    email:  pac @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  465
    title:   Journalism
    author:  Diane D’Almeida
    subject:  Communications
    subject:  Law &amp; Ethics
    link:    http://www.bu.edu/library/guide/journalism/
    published:  Mon, 16 May 2011 21:46:24 +0000
    summary:  
    email:  dalmeida @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  466
    title:   African Art and Archaeology
    author:  Ruth Thomas
    subject:  African Studies
    subject:  Archaeology
    subject:  Arts
    subject:  History
    link:    http://www.bu.edu/library/guide/africanart/
    published:  Mon, 16 May 2011 21:46:24 +0000
    summary:  
    email:  rthomas @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  467
    title:   About the Research Process
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/guidetoresearch/
    published:  Mon, 16 May 2011 21:46:24 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  468
    title:   International Relations
    author:  Susan Wishinsky
    subject:  International Relations
    subject:  Politics and Public Policy
    link:    http://www.bu.edu/library/guide/ir/
    published:  Mon, 16 May 2011 21:46:24 +0000
    summary:  
    email:  susanw @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  469
    title:   Film and Television
    author:  Diane D’Almeida
    subject:  American Studies
    subject:  Arts
    subject:  Communications
    subject:  Film
    link:    http://www.bu.edu/library/guide/film/
    published:  Mon, 16 May 2011 21:46:25 +0000
    summary:  
    email:  dalmeida @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  470
    title:   Human Relations Area Files (HRAF): Africa
    author:  J. Christina Smith
    link:    http://www.bu.edu/library/guide/hraf/hraf-africa/
    published:  Mon, 16 May 2011 21:46:25 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  471
    title:   Human Relations Area Files (HRAF): Asia
    author:  J. Christina Smith
    link:    http://www.bu.edu/library/guide/hraf/hraf-asia/
    published:  Mon, 16 May 2011 21:46:25 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  472
    title:   Human Relations Area Files (HRAF): Europe
    author:  J. Christina Smith
    link:    http://www.bu.edu/library/guide/hraf/hraf-europe/
    published:  Mon, 16 May 2011 21:46:25 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  473
    title:   Human Relations Area Files (HRAF)
    author:  J. Christina Smith
    subject:  Anthropology
    subject:  Area &amp; Cultural Studies
    subject:  Human Relations Area Files
    link:    http://www.bu.edu/library/guide/hraf/
    published:  Mon, 16 May 2011 21:46:26 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  474
    title:   Arab and Islamic Studies - in the Library and on the Web
    author:  Diane D’Almeida
    subject:  Middle East
    subject:  Religion and Philosophy
    link:    http://www.bu.edu/library/guide/arabstudies/
    published:  Mon, 16 May 2011 21:46:26 +0000
    summary:  
    email:  dalmeida @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  475
    title:   Gerontology
    author:  Meredith Kirkpatrick
    subject:  Psychology and Sociology
    link:    http://www.bu.edu/library/guide/geron/
    published:  Mon, 16 May 2011 21:46:26 +0000
    summary:  
    email:  meredith @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  476
    title:   Human Relations Area Files (HRAF): Middle East
    author:  J. Christina Smith
    link:    http://www.bu.edu/library/guide/hraf/hraf-mideast/
    published:  Mon, 16 May 2011 21:46:26 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  477
    title:   Human Relations Area Files (HRAF): North America
    author:  J. Christina Smith
    link:    http://www.bu.edu/library/guide/hraf/hraf-northamerica/
    published:  Mon, 16 May 2011 21:46:26 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  478
    title:   Human Relations Area Files (HRAF): Oceania
    author:  J. Christina Smith
    link:    http://www.bu.edu/library/guide/hraf/hraf-oceania/
    published:  Mon, 16 May 2011 21:46:26 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  479
    title:   Open Access
    author:  Meredith Kirkpatrick
    subject:  Area &amp; Cultural Studies
    subject:  Arts &amp; Humanities
    subject:  Science &amp; Engineering
    subject:  Social Science
    link:    http://www.bu.edu/library/guide/openaccess/
    published:  Mon, 16 May 2011 21:46:27 +0000
    summary:  
    email:  meredith @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  480
    title:   Human Relations Area Files (HRAF): Russia
    author:  J. Christina Smith
    link:    http://www.bu.edu/library/guide/hraf/hraf-russia/
    published:  Mon, 16 May 2011 21:46:27 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  481
    title:   Human Relations Area Files (HRAF): South America
    author:  J. Christina Smith
    link:    http://www.bu.edu/library/guide/hraf/hraf-southamerica/
    published:  Mon, 16 May 2011 21:46:27 +0000
    summary:  
    email:  jchris @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  482
    title:   eBooks
    author:  Meredith Kirkpatrick
    link:    http://www.bu.edu/library/guide/ebooks/
    published:  Mon, 16 May 2011 21:46:27 +0000
    summary:  
    email:  meredith @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  483
    title:   Primary Sources
    author:  Meredith Kirkpatrick
    subject:  Area &amp; Cultural Studies
    subject:  Arts &amp; Humanities
    subject:  Social Science
    link:    http://www.bu.edu/library/guide/primarysources/
    published:  Mon, 16 May 2011 21:46:27 +0000
    summary:  
    email:  meredith @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  484
    title:   Dance
    author:  Holly Mockovak
    author:  Sarah Hunter
    subject:  Arts
    subject:  Music
    link:    http://www.bu.edu/library/guide/dance/
    published:  Mon, 16 May 2011 21:46:27 +0000
    summary:  
    email:  mockovak @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  485
    title:   Museums and Museum Studies
    author:  Ruth Thomas
    subject:  Arts
    subject:  Arts &amp; Humanities
    subject:  History
    link:    http://www.bu.edu/library/guide/museumstudies/
    published:  Mon, 16 May 2011 21:46:28 +0000
    summary:  
    email:  rthomas @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
    meta_key:   museums professional organizations,museums biography,museums exhibitions,museums careers,collectors and collecting
     
     
    Record:  486
    title:   Music Therapy
    author:  Meredith Kirkpatrick
    subject:  Music
    subject:  Psychology and Sociology
    link:    http://www.bu.edu/library/guide/musictherapy/
    published:  Mon, 16 May 2011 21:46:28 +0000
    summary:  
    email:  meredith @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  487
    title:   Cited References: How Do I Find Who Cited an Article or Book?
    author:  Meredith Kirkpatrick
    link:    http://www.bu.edu/library/guide/citedreferences/
    published:  Mon, 16 May 2011 21:46:28 +0000
    summary:  
    email:  meredith @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  488
    title:   Human Rights
    author:  Susan Wishinsky
    subject:  International Relations
    subject:  Law &amp; Ethics
    subject:  Politics and Public Policy
    link:    http://www.bu.edu/library/guide/hr/
    published:  Mon, 16 May 2011 22:46:29 +0000
    summary:  
    email:  susanw @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  489
    title:   Think Tanks, NGOs and IGOs: IR
    author:  Susan Wishinsky
    subject:  International Relations
    subject:  Politics and Public Policy
    link:    http://www.bu.edu/library/guide/ir/io/
    published:  Mon, 16 May 2011 22:46:29 +0000
    summary:  
    email:  susanw @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  490
    title:   Terrorism: IR
    author:  Susan Wishinsky
    subject:  International Relations
    subject:  Politics and Public Policy
    link:    http://www.bu.edu/library/guide/ir/ter/
    published:  Mon, 16 May 2011 22:46:30 +0000
    summary:  
    email:  susanw @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  491
    title:   Treaties
    author:  Susan Wishinsky
    subject:  International Relations
    subject:  Politics and Public Policy
    link:    http://www.bu.edu/library/guide/ir/treaties/
    published:  Mon, 16 May 2011 22:46:30 +0000
    summary:  
    email:  susanw @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  492
    title:   Arab Women Writers
    author:  Diane D’Almeida
    subject:  Arts
    subject:  Literature &amp; Language
    subject:  Middle East
    subject:  Women's Studies
    link:    http://www.bu.edu/library/guide/caww/
    published:  Mon, 16 May 2011 22:46:34 +0000
    summary:  
    email:  dalmeida @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  493
    title:   Boston and Its Neighborhoods
    author:  Donald Altschiller
    author:  Ruth Thomas
    subject:  American Studies
    subject:  Archaeology
    subject:  Area &amp; Cultural Studies
    subject:  Arts
    subject:  Arts &amp; Humanities
    subject:  Boston
    subject:  Business &amp; Management
    subject:  Film
    subject:  History
    subject:  Images
    subject:  Literature &amp; Language
    subject:  Politics and Public Policy
    subject:  Social Science
    subject:  Urban Studies
    link:    http://www.bu.edu/library/guide/boston/
    published:  Mon, 16 May 2011 21:46:35 +0000
    summary:  
    email:  rthomas @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  494
    title:   Books on Boston: A Selection
    author:  Ruth Thomas
    link:    http://www.bu.edu/library/guide/boston/books/
    published:  Mon, 16 May 2011 21:46:35 +0000
    summary:  
    email:  rthomas @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  495
    title:   Boston: Images
    author:  Ruth Thomas
    subject:  Arts
    subject:  Arts &amp; Humanities
    subject:  Images
    link:    http://www.bu.edu/library/guide/boston/images/
    published:  Mon, 16 May 2011 21:46:35 +0000
    summary:  
    email:  rthomas @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  496
    title:   Television Programs set in Boston
    author:  Donald Altschiller
    link:    http://www.bu.edu/library/guide/boston/boston-settings/tv/
    published:  Mon, 16 May 2011 21:46:35 +0000
    summary:  
    email:  donaltsc @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  497
    title:   Music lyrics with a Boston theme
    author:  Donald Altschiller
    link:    http://www.bu.edu/library/guide/boston/boston-settings/music/
    published:  Mon, 16 May 2011 21:46:36 +0000
    summary:  
    email:  donaltsc @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  498
    title:   "Banned in Boston": selected sources.
    author:  Ruth Thomas
    subject:  American Studies
    subject:  History
    subject:  Literature &amp; Language
    link:    http://www.bu.edu/library/guide/boston/banned/
    published:  Mon, 16 May 2011 21:46:36 +0000
    summary:  
    email:  rthomas @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  499
    title:   Movies with Boston Sets and Scenes
    author:  Ruth Thomas
    link:    http://www.bu.edu/library/guide/boston/boston-settings/moviessetin/
    published:  Mon, 16 May 2011 21:46:36 +0000
    summary:  
    email:  rthomas @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  500
    title:   Boston: Works Progress Administration: FAP, FMP, FTP, FWP, PWAP
    author:  Ruth Thomas
    link:    http://www.bu.edu/library/guide/boston/wpa/
    published:  Mon, 16 May 2011 21:46:36 +0000
    summary:  
    email:  rthomas @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  501
    title:   Boston: Parks, Land, Harbor Use and Natural History
    link:    http://www.bu.edu/library/guide/boston/parks/
    published:  Mon, 16 May 2011 21:46:36 +0000
    summary:  
    email:  rthomas @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  502
    title:   Boston: Green Design, Sustainability, Transportation
    link:    http://www.bu.edu/library/guide/boston/greendesign/
    published:  Mon, 16 May 2011 21:46:36 +0000
    summary:  
    email:  rthomas @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  503
    title:   Guide for Writers of Theses & Dissertations
    author:  Brendan McDermott
    link:    http://www.bu.edu/library/guide/theses/
    published:  Mon, 16 May 2011 21:46:36 +0000
    summary:  
    email:  brendan @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  504
    title:   Adult and Continuing Education
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/adulted/
    published:  Mon, 16 May 2011 21:46:37 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  505
    title:   Higher Education
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/highered/
    published:  Mon, 16 May 2011 21:46:37 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  506
    title:   Educational Leadership
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/admin/
    published:  Mon, 16 May 2011 21:46:37 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  507
    title:   Child Development and Early Childhood Education
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/child/
    published:  Mon, 16 May 2011 21:46:37 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  508
    title:   Educational Technology
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/techno/
    published:  Mon, 16 May 2011 21:46:37 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  509
    title:   Character Education
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/charedu/
    published:  Mon, 16 May 2011 21:46:38 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  510
    title:   Educational and Psychological Tests and Measures
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/edutests/
    published:  Mon, 16 May 2011 21:46:38 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  511
    title:   Deaf Studies
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/deaf/
    published:  Mon, 16 May 2011 21:46:38 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  512
    title:   School Counseling and Psychology
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/counsel/
    published:  Mon, 16 May 2011 21:46:38 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  513
    title:   Curriculum
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/curriculum/
    published:  Mon, 16 May 2011 21:46:38 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  514
    title:   Distance Education
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/disted/
    published:  Mon, 16 May 2011 21:46:39 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  515
    title:   Educational Law
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/edulaw/
    published:  Mon, 16 May 2011 21:46:39 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  516
    title:   Funding Resources
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/funding/
    published:  Mon, 16 May 2011 21:46:39 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  517
    title:   Special Education
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/specedu/
    published:  Mon, 16 May 2011 21:46:39 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  518
    title:   Philosophy of Education
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/philed/
    published:  Mon, 16 May 2011 21:46:39 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  519
    title:   Teaching
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/teaching/
    published:  Mon, 16 May 2011 21:46:40 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  520
    title:   Physical Education, Health and Coaching
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/sports/
    published:  Mon, 16 May 2011 21:46:40 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  521
    title:   Educational Research
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/eduresearch/
    published:  Mon, 16 May 2011 21:46:40 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  522
    title:   Literacy and Reading
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/literacy/
    published:  Mon, 16 May 2011 21:46:40 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  523
    title:   International Education
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/international/
    published:  Mon, 16 May 2011 21:46:40 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  524
    title:   Language Learning and Linguistics
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/langlearning/
    published:  Mon, 16 May 2011 21:46:40 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  525
    title:   Achievement Gap
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/gap/
    published:  Mon, 16 May 2011 21:46:41 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  526
    title:   Children's and Young Adult Literature
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/childlit/
    published:  Mon, 16 May 2011 21:46:41 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  527
    title:   Resources For Teachers
    author:  Dan Benedetti
    link:    http://www.bu.edu/library/guide/teachers/
    published:  Mon, 16 May 2011 21:46:43 +0000
    summary:  
    email:  benededa @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  528
    title:   Business Ethics and Corporate Social Responsibility
    author:  Arlyne Jackson
    subject:  Management
    link:    http://www.bu.edu/library/guide/busethics/
    published:  Mon, 16 May 2011 21:46:44 +0000
    summary:  
    email:  ajac @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  529
    title:   Business Dictionaries & Encyclopedias
    link:    http://www.bu.edu/library/guide/online-facts-data/busdict/
    published:  Mon, 16 May 2011 21:46:44 +0000
    summary:  
    email:  fhasan @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  530
    title:   eCommerce & Internet Marketing
    author:  Terry Crystal
    subject:  Marketing
    link:    http://www.bu.edu/library/guide/marketing1/internet/
    published:  Mon, 16 May 2011 21:46:45 +0000
    summary:  
    email:  tcrystal @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  531
    title:   Human Resources Management and Organizational Behavior
    author:  Arlyne Jackson
    subject:  Management
    link:    http://www.bu.edu/library/guide/human/
    published:  Mon, 16 May 2011 21:46:45 +0000
    summary:  
    email:  ajac @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  532
    title:   Citing Business Sources
    author:  Kathleen Berger
    subject:  Management
    link:    http://www.bu.edu/library/guide/citation/
    published:  Mon, 16 May 2011 21:46:45 +0000
    summary:  
    email:  bergerkm @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  533
    title:   Investing
    author:  Farha Hasan
    subject:  Accounting &amp; Finance
    link:    http://www.bu.edu/library/guide/invest/
    published:  Mon, 16 May 2011 21:46:46 +0000
    summary:  
    email:  fhasan @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  534
    title:   Company Annual and Financial Reports
    author:  Arlyne Jackson
    subject:  Companies
    link:    http://www.bu.edu/library/guide/tenkay/
    published:  Mon, 16 May 2011 21:46:46 +0000
    summary:  
    email:  ajac @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  535
    title:   Financing Business Ventures
    author:  Arlyne Jackson
    subject:  Entrepreneurship
    link:    http://www.bu.edu/library/guide/financing/
    published:  Mon, 16 May 2011 21:46:46 +0000
    summary:  
    email:  ajac @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  536
    title:   Energy
    author:  Terry Crystal
    subject:  Industry
    link:    http://www.bu.edu/library/guide/energy/
    published:  Mon, 16 May 2011 21:46:47 +0000
    summary:  
    email:  tcrystal @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  537
    title:   Social Entrepreneurship
    author:  Arlyne Jackson
    subject:  Entrepreneurship
    link:    http://www.bu.edu/library/guide/socialent/
    published:  Mon, 16 May 2011 21:46:47 +0000
    summary:  
    email:  ajac @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  538
    title:   Accounting and Auditing
    author:  Arlyne Jackson
    subject:  Accounting &amp; Finance
    link:    http://www.bu.edu/library/guide/accounting/
    published:  Mon, 16 May 2011 21:46:48 +0000
    summary:  
    email:  ajac @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  539
    title:   Entrepreneurship and New Ventures
    author:  Arlyne Jackson
    subject:  Entrepreneurship
    link:    http://www.bu.edu/library/guide/entre2/
    published:  Mon, 16 May 2011 21:46:48 +0000
    summary:  
    email:  ajac @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  540
    title:   Resources on Sustainability Issues
    author:  Farha Hasan
    subject:  Management
    link:    http://www.bu.edu/library/guide/sustainability/
    published:  Mon, 16 May 2011 21:46:48 +0000
    summary:  
    email:  fhasan @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  541
    title:   Bloomberg Essentials Online Training Program
    author:  Kathleen Berger
    link:    http://www.bu.edu/library/guide/bloombergtutorial/bloombergessentials/
    published:  Mon, 16 May 2011 21:46:49 +0000
    summary:  
    email:  fhasan @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  542
    title:   Resources For Analyst Reports
    author:  Farha Hasan
    subject:  Accounting &amp; Finance
    link:    http://www.bu.edu/library/guide/analystreports/
    published:  Mon, 16 May 2011 21:46:49 +0000
    summary:  
    email:  fhasan @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  543
    title:   Academics
    link:    http://www.bu.edu/library/guide/online-facts-data/academics/
    published:  Mon, 16 May 2011 21:46:52 +0000
    summary:  
    email:  bergerkm @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  544
    title:   Job Search
    author:  Terry Crystal
    subject:  Careers
    link:    http://www.bu.edu/library/guide/career/books-2/
    published:  Mon, 16 May 2011 21:46:56 +0000
    summary:  
    email:  tcrystal @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  545
    title:   Career: Health Sector Management
    author:  Terry Crystal
    subject:  Careers
    link:    http://www.bu.edu/library/guide/career/health-management/
    published:  Mon, 16 May 2011 21:46:56 +0000
    summary:  
    email:  tcrystal @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  546
    title:   Career: Consulting
    author:  Terry Crystal
    subject:  Careers
    link:    http://www.bu.edu/library/guide/career/consulting/
    published:  Mon, 16 May 2011 21:46:56 +0000
    summary:  
    email:  tcrystal @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  547
    title:   Career: Entrepreneurship
    author:  Terry Crystal
    subject:  Careers
    link:    http://www.bu.edu/library/guide/career/entrepreneurship/
    published:  Mon, 16 May 2011 21:46:57 +0000
    summary:  
    email:  tcrystal @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  548
    title:   Career: Finance & Investing
    author:  Terry Crystal
    subject:  Careers
    link:    http://www.bu.edu/library/guide/career/finance/
    published:  Mon, 16 May 2011 21:46:57 +0000
    summary:  
    email:  tcrystal @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  549
    title:   Career: Marketing
    author:  Terry Crystal
    subject:  Careers
    link:    http://www.bu.edu/library/guide/career/career-marketing/
    published:  Mon, 16 May 2011 21:46:57 +0000
    summary:  
    email:  tcrystal @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  550
    title:   Career: Nonprofits & Public Sector
    author:  Terry Crystal
    subject:  Careers
    link:    http://www.bu.edu/library/guide/career/nonprofit/
    published:  Mon, 16 May 2011 21:46:57 +0000
    summary:  
    email:  tcrystal @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  551
    title:   Career: Information Technology
    author:  Terry Crystal
    subject:  Careers
    link:    http://www.bu.edu/library/guide/career/it/
    published:  Mon, 16 May 2011 21:46:58 +0000
    summary:  
    email:  tcrystal @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     
     
    Record:  552
    title:   Career: How To Analyze Your Industry
    author:  Terry Crystal
    subject:  Careers
    link:    http://www.bu.edu/library/guide/career/industry-analysis/
    published:  Mon, 16 May 2011 21:46:58 +0000
    summary:  
    email:  tcrystal @bu.edu
    status:  publish
    postmeta:  
    postType:  guide
    excerpt:  
     


    
