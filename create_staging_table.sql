CREATE TABLE stage_table (
	RDF$STC_sub  VARCHAR(4000) not null,
	RDF$STC_pred VARCHAR(4000) not null,
	RDF$STC_obj VARCHAR(4000) not null
);

EXECUTE SEM_APIS.CREATE_SEM_NETWORK('rdf_tblspace');
CREATE TABLE worldcup_rdf_data (id NUMBER, triple SDO_RDF_TRIPLE_S);
EXEC SEM_APIS.CREATE_SEM_MODEL('worldcup', 'worldcup_rdf_data', 'triple');
GRANT SELECT ON stage_table TO MDSYS;
GRANT insert ON worldcup_rdf_data TO MDSYS;
exec sem_apis.bulk_load_from_staging_table('worldcup', 'marketbasket', 'stage_table', flags => 'PARSE');

SELECT w.triple.GET_PROPERTY() FROM worldcup_rdf_data w;

CREATE INDEX worldcup_sub_idx ON worldcup_rdf_data (triple.GET_SUBJECT());
CREATE INDEX worldcup_prop_idx ON worldcup_rdf_data (triple.GET_PROPERTY());
CREATE INDEX worldcup_obj_idx ON worldcup_rdf_data (TO_CHAR(triple.GET_OBJECT()));

// Find every one who scored

SELECT m
  FROM TABLE(SEM_MATCH(
    '(?m action:scores player:GOAL)',
    SEM_Models('worldcup'),
    null,
    SEM_ALIASES(
    	SEM_ALIAS('action','http://oracleworldcup.com/actions/'), 
    	SEM_ALIAS('player', 'http://oracleworldcup.com/players/')),
    null));
    
