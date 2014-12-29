-- ############################################################################
-- ############################################################################
--                         SENSOR TABLES / TRIGGERS
-- ############################################################################
-- ############################################################################

--
-- Table structure for table sensor
--

DROP TABLE IF EXISTS sensor;
CREATE TABLE sensor (
  id int unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  hostid smallint NOT NULL default '0',
  units varchar(16) NOT NULL,
  label varchar(128) NOT NULL,
  updated datetime NOT NULL default '0000-00-00 00:00:00',
  UNIQUE KEY  (hostid, label)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ROW_FORMAT=fixed;

--
-- Table structure for table sensor_reading 
--

DROP TABLE IF EXISTS sensor_reading;
CREATE TABLE sensor_reading (
  id int unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  hostid smallint NOT NULL default '0',
  updated datetime NOT NULL default '0000-00-00 00:00:00',
  sensor_id int unsigned NOT NULL,
  reading float NOT NULL default '0',
  UNIQUE KEY  (updated,hostid, sensor_id)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ROW_FORMAT=fixed;


DROP TABLE IF EXISTS sensor_reading_rrd_key;
CREATE TABLE sensor_reading_rrd_key (
  rrd_counter BIGINT unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY
);
insert into sensor_reading_rrd_key values(0);


--
-- Table structure for table sensor_reading_daily
--

DROP TABLE IF EXISTS sensor_reading_daily;
CREATE TABLE sensor_reading_daily (
  id int(10) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  hostid smallint(6) NOT NULL default '0',
  updated datetime NOT NULL default '0000-00-00 00:00:00',
  sensor_id int unsigned NOT NULL,
  reading float NOT NULL default '0',
  UNIQUE KEY  (updated,hostid, sensor_id)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ROW_FORMAT=fixed;


DROP TABLE IF EXISTS sensor_reading_daily_rrd_key;
CREATE TABLE sensor_reading_daily_rrd_key (
  rrd_counter BIGINT unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY
);
insert into sensor_reading_daily_rrd_key values(0);


--
-- Table structure for table sensor_reading_weekly
--

DROP TABLE IF EXISTS sensor_reading_weekly;
CREATE TABLE sensor_reading_weekly (
  id int(10) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  hostid smallint(6) NOT NULL default '0',
  updated datetime NOT NULL default '0000-00-00 00:00:00',
  sensor_id int unsigned NOT NULL,
  reading float NOT NULL default '0',
  UNIQUE KEY  (updated,hostid, sensor_id)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ROW_FORMAT=fixed;


DROP TABLE IF EXISTS sensor_reading_weekly_rrd_key;
CREATE TABLE sensor_reading_weekly_rrd_key (
  rrd_counter BIGINT unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY
);
insert into sensor_reading_weekly_rrd_key values(0);


--
-- Table structure for table sensor_reading_monthly
--

DROP TABLE IF EXISTS sensor_reading_monthly;
CREATE TABLE sensor_reading_monthly (
  id int(10) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  hostid smallint(6) NOT NULL default '0',
  updated datetime NOT NULL default '0000-00-00 00:00:00',
  sensor_id int unsigned NOT NULL,
  reading float NOT NULL default '0',
  UNIQUE KEY  (updated,hostid, sensor_id)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ROW_FORMAT=fixed;


DROP TABLE IF EXISTS sensor_reading_monthly_rrd_key;
CREATE TABLE sensor_reading_monthly_rrd_key (
  rrd_counter BIGINT unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY
);
insert into sensor_reading_monthly_rrd_key values(0);
