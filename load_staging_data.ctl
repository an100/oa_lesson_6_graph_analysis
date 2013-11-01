LOAD DATA
  INFILE './rdf_staging_table.nt'
  INTO TABLE stage_table
  FIELDS TERMINATED BY " "
  (RDF$STC_sub, RDF$STC_pred, RDF$STC_obj)
  

