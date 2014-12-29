
-- ############################################################################
-- ############################################################################
--                         DISKLOAD TABLES
-- ############################################################################
-- ############################################################################


--
-- Table structure for table diskload
--

DROP TABLE IF EXISTS diskload;
CREATE TABLE diskload (
  id int(10) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  hostid smallint(6) NOT NULL default '0',
  device char(32) NOT NULL default '',
  updated datetime NOT NULL default '0000-00-00 00:00:00',
  svctime double default NULL,
  utilization tinyint(3) unsigned NOT NULL default '0',
  bi int(10) unsigned default NULL,
  bo int(10) unsigned default NULL,
  UNIQUE KEY  (updated,hostid,device),
  KEY diskload_search (hostid,updated,device)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ROW_FORMAT=fixed;


DROP TABLE IF EXISTS diskload_rrd_key;
CREATE TABLE diskload_rrd_key (
  rrd_counter BIGINT unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY
);
insert into diskload_rrd_key values(0);


--
-- Table structure for table diskload_daily
--

DROP TABLE IF EXISTS diskload_daily;
CREATE TABLE diskload_daily (
  id int(10) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  hostid smallint(6) NOT NULL default '0',
  device char(32) NOT NULL default '',
  updated datetime NOT NULL default '0000-00-00 00:00:00',
  svctime double default NULL,
  utilization tinyint(3) unsigned NOT NULL default '0',
  bi int(10) unsigned default NULL,
  bo int(10) unsigned default NULL,
  UNIQUE KEY  (updated,hostid,device),
  KEY diskload_search (hostid,updated,device)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ROW_FORMAT=fixed;


DROP TABLE IF EXISTS diskload_daily_rrd_key;
CREATE TABLE diskload_daily_rrd_key (
  rrd_counter BIGINT unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY
);
insert into diskload_daily_rrd_key values(0);


--
-- Table structure for table diskload_weekly
--

DROP TABLE IF EXISTS diskload_weekly;
CREATE TABLE diskload_weekly (
  id int(10) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  hostid smallint(6) NOT NULL default '0',
  device char(32) NOT NULL default '',
  updated datetime NOT NULL default '0000-00-00 00:00:00',
  svctime double default NULL,
  utilization tinyint(3) unsigned NOT NULL default '0',
  bi int(10) unsigned default NULL,
  bo int(10) unsigned default NULL,
  UNIQUE KEY  (updated,hostid,device),
  KEY diskload_search (hostid,updated,device)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ROW_FORMAT=fixed;


DROP TABLE IF EXISTS diskload_weekly_rrd_key;
CREATE TABLE diskload_weekly_rrd_key (
  rrd_counter BIGINT unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY
);
insert into diskload_weekly_rrd_key values(0);


--
-- Table structure for table diskload_monthly
--

DROP TABLE IF EXISTS diskload_monthly;
CREATE TABLE diskload_monthly (
  id int(10) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  hostid smallint(6) NOT NULL default '0',
  device char(32) NOT NULL default '',
  updated datetime NOT NULL default '0000-00-00 00:00:00',
  svctime double default NULL,
  utilization tinyint(3) unsigned NOT NULL default '0',
  bi int(10) unsigned default NULL,
  bo int(10) unsigned default NULL,
  UNIQUE KEY  (updated,hostid,device),
  KEY diskload_search (hostid,updated,device)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ROW_FORMAT=fixed;


DROP TABLE IF EXISTS diskload_monthly_rrd_key;
CREATE TABLE diskload_monthly_rrd_key (
  rrd_counter BIGINT unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY
);
insert into diskload_monthly_rrd_key values(0);
