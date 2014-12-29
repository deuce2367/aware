--
--
-- Table structure for table table_info
--

DROP TABLE IF EXISTS table_info;
CREATE TABLE table_info (
  table_name    varchar(64) NOT NULL,
  table_rows    int(10) unsigned NOT NULL default '5000000',
  window_size   int(10) unsigned NOT NULL default '0',
  PRIMARY KEY (table_name)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

LOCK TABLES table_info WRITE;
INSERT INTO table_info VALUES ('diskload', 10000000, 0),('diskload_daily', 10000000,5),('diskload_weekly',10000000,30),('diskload_monthly',10000000,180);
INSERT INTO table_info VALUES ('memory', 10000000, 0),('memory_daily', 10000000,5),('memory_weekly',10000000,30),('memory_monthly',10000000,180);
INSERT INTO table_info VALUES ('netload', 10000000, 0),('netload_daily', 10000000,5),('netload_weekly',10000000,30),('netload_monthly',10000000,180);
INSERT INTO table_info VALUES ('sensor_reading', 10000000, 0),('sensor_reading_daily', 10000000,5),('sensor_reading_weekly',10000000,30),('sensor_reading_monthly',10000000,180);
INSERT INTO table_info VALUES ('sysload', 10000000, 0),('sysload_daily', 10000000,5),('sysload_weekly',10000000,30),('sysload_monthly',10000000,180);
UNLOCK TABLES;
