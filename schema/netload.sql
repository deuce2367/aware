
-- ############################################################################
-- ############################################################################
--                         NETLOAD TABLES
-- ############################################################################
-- ############################################################################

--
-- Table structure for table netload
--

DROP TABLE IF EXISTS netload;
CREATE TABLE netload (
  id           int(10) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  hostid       smallint(6) NOT NULL default '0',
  device       char(8) NOT NULL default '',
  vlan         smallint unsigned NOT NULL default 0,
  updated      datetime NOT NULL default '0000-00-00 00:00:00',
  tx int(10)   unsigned default NULL,
  rx int(10)   unsigned default NULL,
  UNIQUE KEY (updated,hostid,device,vlan),
  KEY netload_search (hostid,updated,device,vlan)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ROW_FORMAT=fixed;


DROP TABLE IF EXISTS netload_rrd_key;
CREATE TABLE netload_rrd_key (
  rrd_counter BIGINT unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY
);
insert into netload_rrd_key values(0);

--
-- Table structure for table netload_daily
--

DROP TABLE IF EXISTS netload_daily;
CREATE TABLE netload_daily (
  id           int(10) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  hostid       smallint(6) NOT NULL default '0',
  device       char(8) NOT NULL default '',
  vlan         smallint unsigned NOT NULL default 0,
  updated      datetime NOT NULL default '0000-00-00 00:00:00',
  tx int(10)   unsigned default NULL,
  rx int(10)   unsigned default NULL,
  UNIQUE KEY (updated,hostid,device,vlan),
  KEY netload_daily_search (hostid,updated,device,vlan)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ROW_FORMAT=fixed;


DROP TABLE IF EXISTS netload_daily_rrd_key;
CREATE TABLE netload_daily_rrd_key (
  rrd_counter BIGINT unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY
);
insert into netload_daily_rrd_key values(0);


--
-- Table structure for table netload_weekly
--

DROP TABLE IF EXISTS netload_weekly;
CREATE TABLE netload_weekly (
  id           int(10) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  hostid       smallint(6) NOT NULL default '0',
  device       char(8) NOT NULL default '',
  vlan         smallint unsigned NOT NULL default 0,
  updated      datetime NOT NULL default '0000-00-00 00:00:00',
  tx int(10)   unsigned default NULL,
  rx int(10)   unsigned default NULL,
  UNIQUE KEY (updated,hostid,device,vlan),
  KEY netload_weekly_search (hostid,updated,device,vlan)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ROW_FORMAT=fixed;


DROP TABLE IF EXISTS netload_weekly_rrd_key;
CREATE TABLE netload_weekly_rrd_key (
  rrd_counter BIGINT unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY
);
insert into netload_weekly_rrd_key values(0);


--
-- Table structure for table netload_monthly
--

DROP TABLE IF EXISTS netload_monthly;
CREATE TABLE netload_monthly (
  id           int(10) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  hostid       smallint(6) NOT NULL default '0',
  device       char(8) NOT NULL default '',
  vlan         smallint unsigned NOT NULL default 0,
  updated      datetime NOT NULL default '0000-00-00 00:00:00',
  tx int(10)   unsigned default NULL,
  rx int(10)   unsigned default NULL,
  UNIQUE KEY (updated,hostid,device,vlan),
  KEY netload_monthly_search (hostid,updated,device,vlan)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ROW_FORMAT=fixed;

DROP TABLE IF EXISTS netload_monthly_rrd_key;
CREATE TABLE netload_monthly_rrd_key (
  rrd_counter BIGINT unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY
);
insert into netload_monthly_rrd_key values(0);
