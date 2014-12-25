
-- ############################################################################
-- ############################################################################
--                             AWARE CORE TABLES 
-- ############################################################################
-- ############################################################################

--
--
-- Table structure for table aware 
--

DROP TABLE IF EXISTS aware;
CREATE TABLE aware (
  updated              timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  major                smallint unsigned NOT NULL,
  minor                smallint unsigned NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


--
--
-- Table structure for table alert
--

DROP TABLE IF EXISTS alert;
CREATE TABLE alert (
  hostid               smallint(6) NOT NULL default '0',
  type                 varchar(20) NOT NULL default '',
  display              tinyint(4) NOT NULL default '1',
  message              varchar(100) default NULL,
  updated              datetime NOT NULL default '0000-00-00 00:00:00',
  PRIMARY KEY (hostid,type,updated),
  KEY alert_idx (updated,hostid),
  KEY alert_idx_type (type,updated),
  KEY alert_message (message)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


--
-- Table structure for table daemon
--

DROP TABLE IF EXISTS daemon;
CREATE TABLE daemon (
  hostid               smallint(5) unsigned NOT NULL default '0',
  updated              datetime NOT NULL default '0000-00-00 00:00:00',
  name                 varchar(30) NOT NULL default '',
  status               varchar(200) default NULL,
  version              varchar(30) default NULL,
  PRIMARY KEY  (hostid,name)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table daemon_tasking
--

DROP TABLE IF EXISTS daemon_tasking;
CREATE TABLE daemon_tasking (
  daemon               varchar(30) default NULL,
  status               varchar(15) default NULL,
  description          varchar(100) default NULL,
  id                   smallint(6) NOT NULL auto_increment,
  frequency            smallint(6) default NULL,
  PRIMARY KEY  (id)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


--
-- Table structure for table nic
--

DROP TABLE IF EXISTS nic;
CREATE TABLE nic (
  hostid               smallint(6) NOT NULL default 0,
  updated              timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  device               varchar(8) NOT NULL default '',
  vlan                 smallint unsigned NOT NULL default 0,
  macaddr              varchar(17) default NULL,
  ipaddr               varchar(15) default NULL,
  netmask              varchar(15) default NULL,
  primary key (hostid, device, vlan)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;



--
-- Table structure for table filesystem
--

DROP TABLE IF EXISTS filesystem;
CREATE TABLE filesystem (
  hostid               smallint(6) NOT NULL default '0',
  updated              timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  pct                  tinyint(4) default NULL,
  mount                varchar(20) default '',
  free                 mediumint(9) default NULL,
  type                 varchar(8) default NULL,
  ifree                int(11) default NULL,
  ipct                 tinyint(4) default NULL,
  device               varchar(32) NOT NULL default '',
  partition            tinyint(4) unsigned NOT NULL default '1',
  svctime              double default NULL,
  PRIMARY KEY  (hostid,device,partition)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


--
-- Table structure for table node
--

DROP TABLE IF EXISTS node;
CREATE TABLE node (
  hostname varchar(50) default NULL,
  hostid varchar(50) default NULL,
  ipaddr varchar(15) default NULL,
  arch varchar(8) default NULL,
  macaddr varchar(17) default NULL,
  os varchar(50) default NULL,
  procs smallint(5) default NULL,
  uptime int(11) default NULL,
  updated datetime default NULL,
  idx smallint(5) default NULL,
  ilomac varchar(17) default NULL,
  iloaddr varchar(15) default NULL,
  password varchar(10) default NULL,
  port varchar(255) default NULL,
  rack varchar(32) not null default '',
  iloport varchar(10) default NULL,
  online tinyint(4) default NULL,
  status varchar(10) default NULL,
  sysload tinyint(4) default NULL,
  temperature tinyint(4) default NULL,
  maxdisk varchar(32) default NULL,
  alert int(11) unsigned default '0',
  memory smallint(6) default NULL,
  id smallint(6) NOT NULL auto_increment,
  ping mediumint(8) unsigned default '0',
  poll mediumint(8) unsigned default '0',
  description text,
  notes text,
  numcpu tinyint(3) unsigned default NULL,
  cpu_type varchar(50) default NULL,
  profile_id smallint(5) unsigned default NULL,
  bytesIn int(11) unsigned default NULL,
  bytesOut int(11) unsigned default NULL,
  tx int(11) unsigned default NULL,
  rx int(11) unsigned default NULL,
  maxpart tinyint(3) unsigned default NULL,
  PRIMARY KEY  (id),
  KEY node_hostid (hostid),
  KEY node_hostname (hostname)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table process
--

DROP TABLE IF EXISTS process;
CREATE TABLE process (
  hostid smallint(5) unsigned NOT NULL default '0',
  pid smallint(5) unsigned NOT NULL default '0',
  ppid smallint(5) unsigned NOT NULL default '0',
  user char(15) NOT NULL default '',
  cpu tinyint(3) unsigned NOT NULL default '0',
  mem tinyint(3) unsigned NOT NULL default '0',
  nice tinyint(3) unsigned NOT NULL default '0',
  prio tinyint(3) unsigned NOT NULL default '0',
  rsz int(10) unsigned NOT NULL default '0',
  vsz int(10) unsigned NOT NULL default '0',
  sz int(10) unsigned NOT NULL default '0',
  stime char(15) NOT NULL default '',
  etime char(15) NOT NULL default '',
  cmd char(100) NOT NULL default '',
  args char(255) NOT NULL default '',
  PRIMARY KEY  (hostid,pid)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table profile
--

DROP TABLE IF EXISTS profile;
CREATE TABLE profile (
  id smallint(5) unsigned NOT NULL auto_increment,
  name varchar(30) default NULL,
  description varchar(255) default NULL,
  PRIMARY KEY  (id)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table settings
--

DROP TABLE IF EXISTS settings;
CREATE TABLE settings (
  label varchar(20) default NULL,
  value varchar(20) default NULL,
  id smallint(6) NOT NULL auto_increment,
  description varchar(100) default NULL,
  PRIMARY KEY  (id),
  UNIQUE KEY label (label)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


--
-- Table structure for table thresholds
--

DROP TABLE IF EXISTS thresholds;
CREATE TABLE thresholds (
  profile_id smallint(5) unsigned NOT NULL default '0',
  maxmem smallint(5) unsigned default '75',
  maxdisk smallint(5) unsigned default '85',
  maxload smallint(5) unsigned default '97',
  maxtemp smallint(5) unsigned default '61',
  missedpings smallint(5) unsigned default '1',
  maxprocs smallint(5) unsigned default '500',
  maxreport smallint(5) unsigned default '300',
  missedpolls smallint(5) unsigned default '1',
  maxinodes smallint(5) unsigned default '85',
  PRIMARY KEY  (profile_id)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table uptime
--

DROP TABLE IF EXISTS uptime;
CREATE TABLE uptime (
  hostid      smallint(6) NOT NULL default '0',
  booted      datetime NOT NULL default '0000-00-00 00:00:00',
  updated     datetime NOT NULL default '0000-00-00 00:00:00',
  uptime      double unsigned NOT NULL default '0',
  PRIMARY KEY  (booted,hostid)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;





