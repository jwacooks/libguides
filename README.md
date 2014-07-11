libguides
===
The files in this project are used to harvest metadata from the BU Libraries' Research Guides developed and maintained on a WordPress web site to load to Ex Libris Primo to enable the guides to be discovered in that platform. 

The primary file is the ipython notebook:

* Harvest_Library_Research_Guide_Metadata.ipynb

A markdown version of the file was created using nbconvert:

* Harvest_Library_Research_Guide_Metadata.md

The input file for the Harvest is a file exported from WordPress in an RSS format. Two examples are provided:

* bulibraries.wordpress.2014-05-30.xml
* bulibraries.wordpress.2014-07-08.xml

The output file ('guides.xml') is the file that is ingested into Primo via a standard harvest pipe.

Jack Ammerman

