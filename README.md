Graph Analysis
==============================

Datasets and example code for Lesson 6 in Oracle Academy's Data Science Bootcamp. The datasets and code here cover 4 topics: 

1. Scraping the 2010 World Cup website to create a passing graph
2. Python code which uses NetworkX and D3 to construct, analyze and annotate the passing graph
3. SQL code for using the passing graph as RDF with Oracle Spatial and Graph
4. Gremlin queries and a graphml file for using the passing graph with Rexter

Scraping code and data are in **raw_scrape.py**.  The resulting dataset is in **worldcup_passes.json**.

Python code for analysis is in **contruct_graph.py**.  Outputs from this are in **rdf_staging_table.nt**, **worldcup.graphml** and **javascript/force/world_cup_graph.json**.

SQL queries and SQL*Loader control information are in **create_staging_table.sql** and **load_staging_data.ctl**

Gremlin queries are in **gremlin_queries.txt**.