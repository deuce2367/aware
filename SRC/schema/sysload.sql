-- ############################################################################
-- ############################################################################
--                         SYSLOAD TABLES / TRIGGERS
-- ############################################################################
-- ############################################################################

--
-- Table structure for table sysload
--

DROP TABLE IF EXISTS sysload;
CREATE TABLE sysload (
  id int(10) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  hostid smallint(6) NOT NULL default '0',
  updated datetime NOT NULL default '0000-00-00 00:00:00',
  avg tinyint(3) NOT NULL default '0',
  procs smallint(4) NOT NULL default '0',
  bi int(10) unsigned default NULL,
  bo int(10) unsigned default NULL,
  tx int(10) unsigned default NULL,
  rx int(10) unsigned default NULL,
  user tinyint(3) unsigned default NULL,
  system tinyint(3) unsigned default NULL,
  iowait tinyint(3) unsigned default NULL,
  irq tinyint(3) unsigned default NULL,
  softirq tinyint(3) unsigned default NULL,
  idle tinyint(3) unsigned default NULL,
  nice tinyint(3) unsigned default NULL,
  UNIQUE KEY  (updated,hostid)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ROW_FORMAT=fixed;


DROP TABLE IF EXISTS sysload_rrd_key;
CREATE TABLE sysload_rrd_key (
  rrd_counter BIGINT unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY
);
insert into sysload_rrd_key values(0);


--
-- Table structure for table sysload_daily
--

DROP TABLE IF EXISTS sysload_daily;
CREATE TABLE sysload_daily (
  id int(10) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  hostid smallint(6) NOT NULL default '0',
  updated datetime NOT NULL default '0000-00-00 00:00:00',
  avg tinyint(3) NOT NULL default '0',
  procs smallint(4) NOT NULL default '0',
  bi int(10) unsigned default NULL,
  bo int(10) unsigned default NULL,
  tx int(10) unsigned default NULL,
  rx int(10) unsigned default NULL,
  user tinyint(3) unsigned default NULL,
  system tinyint(3) unsigned default NULL,
  iowait tinyint(3) unsigned default NULL,
  irq tinyint(3) unsigned default NULL,
  softirq tinyint(3) unsigned default NULL,
  idle tinyint(3) unsigned default NULL,
  nice tinyint(3) unsigned default NULL,
  UNIQUE KEY  (updated,hostid)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ROW_FORMAT=fixed;


DROP TABLE IF EXISTS sysload_daily_rrd_key;
CREATE TABLE sysload_daily_rrd_key (
  rrd_counter BIGINT unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY
);
insert into sysload_daily_rrd_key values(0);


--
-- Table structure for table sysload_weekly
--

DROP TABLE IF EXISTS sysload_weekly;
CREATE TABLE sysload_weekly (
  id int(10) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  hostid smallint(6) NOT NULL default '0',
  updated datetime NOT NULL default '0000-00-00 00:00:00',
  avg tinyint(3) NOT NULL default '0',
  procs smallint(4) NOT NULL default '0',
  bi int(10) unsigned default NULL,
  bo int(10) unsigned default NULL,
  tx int(10) unsigned default NULL,
  rx int(10) unsigned default NULL,
  user tinyint(3) unsigned default NULL,
  system tinyint(3) unsigned default NULL,
  iowait tinyint(3) unsigned default NULL,
  irq tinyint(3) unsigned default NULL,
  softirq tinyint(3) unsigned default NULL,
  idle tinyint(3) unsigned default NULL,
  nice tinyint(3) unsigned default NULL,
  UNIQUE KEY  (updated,hostid)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ROW_FORMAT=fixed;


DROP TABLE IF EXISTS sysload_weekly_rrd_key;
CREATE TABLE sysload_weekly_rrd_key (
  rrd_counter BIGINT unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY
);
insert into sysload_weekly_rrd_key values(0);


--
-- Table structure for table sysload_monthly
--

DROP TABLE IF EXISTS sysload_monthly;
CREATE TABLE sysload_monthly (
  id int(10) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  hostid smallint(6) NOT NULL default '0',
  updated datetime NOT NULL default '0000-00-00 00:00:00',
  avg tinyint(3) NOT NULL default '0',
  procs smallint(4) NOT NULL default '0',
  bi int(10) unsigned default NULL,
  bo int(10) unsigned default NULL,
  tx int(10) unsigned default NULL,
  rx int(10) unsigned default NULL,
  user tinyint(3) unsigned default NULL,
  system tinyint(3) unsigned default NULL,
  iowait tinyint(3) unsigned default NULL,
  irq tinyint(3) unsigned default NULL,
  softirq tinyint(3) unsigned default NULL,
  idle tinyint(3) unsigned default NULL,
  nice tinyint(3) unsigned default NULL,
  UNIQUE KEY  (updated,hostid)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ROW_FORMAT=fixed;


DROP TABLE IF EXISTS sysload_monthly_rrd_key;
CREATE TABLE sysload_monthly_rrd_key (
  rrd_counter BIGINT unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY
);
insert into sysload_monthly_rrd_key values(0);
