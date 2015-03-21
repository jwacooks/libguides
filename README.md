Harvesting library guides from WordPress to ingest into Primo
===
The files in this project are used to harvest metadata from the BU Libraries' Research Guides developed and maintained on a WordPress web site to load to Ex Libris Primo to enable the guides to be discovered in that platform. 

The project began with the assumption that the assumption that the guides would be harvested once per semester. The scripts to do this were developed using ipython notebook:

* Harvest_Library_Research_Guide_Metadata.ipynb

A markdown version of the file was created using nbconvert:

* Harvest_Library_Research_Guide_Metadata.md

The input file for the Harvest can be a file exported from WordPress in an RSS format. Two examples are provided:

* bulibraries.wordpress.2014-05-30.xml
* bulibraries.wordpress.2014-07-08.xml

The output file ('guides.xml') is the file that is ingested into Primo via a standard (oai) harvest pipe.

After initial testing, we determined that it would be more desireable to harvest the guides on a daily basis. The export of the file from WordPress could not be automated, so we developed  scripts to harvest all of the metadata directly from the WordPress web pages. U harvests library subject guides from four different sites. Two are WordPress sites Mugar and Theology. The Medical Library maintains its guides on a php driven web site . The Law Library maintains its guides on the SpringShare LibGuides platform. The python scripts for harvesting from each was developed using iPython notebook. The files were explorted as standard python (*.py) files to be run scheduled by a cron job.

* mugar_libguides.ipynb
* LawLibraryLibGuldes.ipynb		
* theology_research_guides.ipynb
* Medical Research Guides.ipynb

The ipython notebook files (*.ipynb) are reasonably well documented and are the basis for the python files ( *.py ) that we currently use.

These four python scripts are run daily on a cron job. The output from each is an xml file that is harvested using a standard Primo harvest pipe. The normalization rules are the same rules we use to harvest Dublin Core records from our DSpace repository.

Screen shots of the data source definition and harvest pipe definition are included in this directory.

* libguides_harvest_pipe_definition.png
* libguides_data_source_definition.png



Jack Ammerman
July 30, 2014

****

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.

