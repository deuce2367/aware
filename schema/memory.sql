-- ############################################################################
-- ############################################################################
--                         MEMORY TABLES / TRIGGERS
-- ############################################################################
-- ############################################################################

--
-- Table structure for table memory
-- 

DROP TABLE IF EXISTS memory;
CREATE TABLE memory (
  id int(10) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  hostid smallint(6) NOT NULL default '0',
  updated datetime NOT NULL default '0000-00-00 00:00:00',
  used mediumint(5) unsigned default NULL,
  free mediumint(5) unsigned default NULL,
  cached mediumint(5) unsigned default NULL,
  buffers mediumint(5) unsigned default NULL,
  usedSwap mediumint(5) unsigned default NULL,
  freeSwap mediumint(5) unsigned default NULL,
  shmseg smallint(5) unsigned default '0',
  shmsize int(10) unsigned default '0',
  shmsem smallint(5) unsigned default '0',
  committed_as int(10) unsigned default '0',
  UNIQUE KEY  (updated,hostid)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ROW_FORMAT=fixed;


DROP TABLE IF EXISTS memory_rrd_key;
CREATE TABLE memory_rrd_key (
  rrd_counter BIGINT unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY
);
insert into memory_rrd_key values(0);


--
-- Table structure for table memory_daily
--

DROP TABLE IF EXISTS memory_daily;
CREATE TABLE memory_daily (
  id int(10) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  hostid smallint(6) NOT NULL default '0',
  updated datetime NOT NULL default '0000-00-00 00:00:00',
  used mediumint(5) unsigned default NULL,
  free mediumint(5) unsigned default NULL,
  cached mediumint(5) unsigned default NULL,
  buffers mediumint(5) unsigned default NULL,
  usedSwap mediumint(5) unsigned default NULL,
  freeSwap mediumint(5) unsigned default NULL,
  shmseg smallint(5) unsigned default '0',
  shmsize int(10) unsigned default '0',
  shmsem smallint(5) unsigned default '0',
  committed_as int(10) unsigned default '0',
  UNIQUE KEY  (updated,hostid)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ROW_FORMAT=fixed;


DROP TABLE IF EXISTS memory_daily_rrd_key;
CREATE TABLE memory_daily_rrd_key (
  rrd_counter BIGINT unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY
);
insert into memory_daily_rrd_key values(0);


--
-- Table structure for memory_weekly
--

DROP TABLE IF EXISTS memory_weekly;
CREATE TABLE memory_weekly (
  id int(10) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  hostid smallint(6) NOT NULL default '0',
  updated datetime NOT NULL default '0000-00-00 00:00:00',
  used mediumint(5) unsigned default NULL,
  free mediumint(5) unsigned default NULL,
  cached mediumint(5) unsigned default NULL,
  buffers mediumint(5) unsigned default NULL,
  usedSwap mediumint(5) unsigned default NULL,
  freeSwap mediumint(5) unsigned default NULL,
  shmseg smallint(5) unsigned default '0',
  shmsize int(10) unsigned default '0',
  shmsem smallint(5) unsigned default '0',
  committed_as int(10) unsigned default '0',
  UNIQUE KEY  (updated,hostid)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ROW_FORMAT=fixed;


DROP TABLE IF EXISTS memory_weekly_rrd_key;
CREATE TABLE memory_weekly_rrd_key (
  rrd_counter BIGINT unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY
);
insert into memory_weekly_rrd_key values(0);


--
-- Table structure for memory_monthly
--

DROP TABLE IF EXISTS memory_monthly;
CREATE TABLE memory_monthly (
  id int(10) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  hostid smallint(6) NOT NULL default '0',
  updated datetime NOT NULL default '0000-00-00 00:00:00',
  used mediumint(5) unsigned default NULL,
  free mediumint(5) unsigned default NULL,
  cached mediumint(5) unsigned default NULL,
  buffers mediumint(5) unsigned default NULL,
  usedSwap mediumint(5) unsigned default NULL,
  freeSwap mediumint(5) unsigned default NULL,
  shmseg smallint(5) unsigned default '0',
  shmsize int(10) unsigned default '0',
  shmsem smallint(5) unsigned default '0',
  committed_as int(10) unsigned default '0',
  UNIQUE KEY  (updated,hostid)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ROW_FORMAT=fixed;


DROP TABLE IF EXISTS memory_monthly_rrd_key;
CREATE TABLE memory_monthly_rrd_key (
  rrd_counter BIGINT unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY
);
insert into memory_monthly_rrd_key values(0);
