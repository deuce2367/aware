
-- ############################################################################
-- ############################################################################
--                         NETLOAD TRIGGERS
-- ############################################################################
-- ############################################################################


-- 
-- Round-Robin Triggers
--

DROP TRIGGER IF EXISTS netload_insert;
DELIMITER $$
CREATE TRIGGER  netload_insert
BEFORE INSERT ON netload
FOR EACH ROW
BEGIN
  select table_rows into @rows from table_info where table_name = 'netload';
  IF NEW.id = 0 THEN
    INSERT into netload_rrd_key VALUES(0);
    select LAST_INSERT_ID() % @rows + 1 into @rrd_key;
    DELETE FROM netload_rrd_key;
    SET NEW.id = @rrd_key;
  END IF;
END;
$$
DELIMITER ;


DROP TRIGGER IF EXISTS netload_daily_insert;
DELIMITER $$
CREATE TRIGGER  netload_daily_insert
BEFORE INSERT ON netload_daily
FOR EACH ROW
BEGIN
  select table_rows into @rows from table_info where table_name = 'netload_daily';
  IF NEW.id = 0 THEN
    INSERT into netload_daily_rrd_key VALUES(0);
    select LAST_INSERT_ID() % @rows + 1 into @rrd_key;
    DELETE FROM netload_daily_rrd_key;
    SET NEW.id = @rrd_key;
  END IF;
END;
$$
DELIMITER ;


DROP TRIGGER IF EXISTS netload_weekly_insert;
DELIMITER $$
CREATE TRIGGER  netload_weekly_insert
BEFORE INSERT ON netload_weekly
FOR EACH ROW
BEGIN
  select table_rows into @rows from table_info where table_name = 'netload_weekly';
  IF NEW.id = 0 THEN
    INSERT into netload_weekly_rrd_key VALUES(0);
    select LAST_INSERT_ID() % @rows + 1 into @rrd_key;
    DELETE FROM netload_weekly_rrd_key;
    SET NEW.id = @rrd_key;
  END IF;
END;
$$
DELIMITER ;


DROP TRIGGER IF EXISTS netload_monthly_insert;
DELIMITER $$
CREATE TRIGGER  netload_monthly_insert
BEFORE INSERT ON netload_monthly
FOR EACH ROW
BEGIN
  select table_rows into @rows from table_info where table_name = 'netload_monthly';
  IF NEW.id = 0 THEN
    INSERT into netload_monthly_rrd_key VALUES(0);
    select LAST_INSERT_ID() % @rows + 1 into @rrd_key;
    DELETE FROM netload_monthly_rrd_key;
    SET NEW.id = @rrd_key;
  END IF;
END;
$$
DELIMITER ;


-- 
-- Consolidation Triggers
--

DROP TRIGGER IF EXISTS netload_consolidator;
DELIMITER $$
CREATE TRIGGER  netload_consolidator
AFTER INSERT ON netload
FOR EACH ROW
BEGIN
  select window_size into @window from table_info where table_name = 'netload_daily';
  set @windowID = 0;
  select from_unixtime(unix_timestamp(NEW.updated) - unix_timestamp(NEW.updated) % (@window * 60)) into @windowStart;
  select from_unixtime(unix_timestamp(NEW.updated) + @window*60 - (unix_timestamp(NEW.updated) % (@window * 60))) into @windowStop;
  select id from netload_daily where hostid = NEW.hostid and updated = @windowStop and device = NEW.device into @windowID;

  select avg(rx), avg(tx) from netload where hostid = NEW.hostid and device = NEW.device and vlan = NEW.vlan 
	and updated >= @windowStart and updated <= @windowStop into @RX, @TX;

  replace delayed into netload_daily (id, hostid, device, vlan, updated, tx, rx) values (@windowID, NEW.hostid, NEW.device, NEW.vlan, @windowStop, @TX, @RX);

END;
$$
DELIMITER ;


DROP TRIGGER IF EXISTS netload_daily_consolidator;
DELIMITER $$
CREATE TRIGGER  netload_daily_consolidator
AFTER INSERT ON netload_daily
FOR EACH ROW
BEGIN
  select window_size into @window from table_info where table_name = 'netload_weekly';
  set @windowID = 0;
  select from_unixtime(unix_timestamp(NEW.updated) - unix_timestamp(NEW.updated) % (@window * 60)) into @windowStart;
  select from_unixtime(unix_timestamp(NEW.updated) + @window*60 - (unix_timestamp(NEW.updated) % (@window * 60))) into @windowStop;
  select id from netload_weekly where hostid = NEW.hostid and updated = @windowStop and device = NEW.device into @windowID;

  select avg(rx), avg(tx) from netload_daily where hostid = NEW.hostid and device = NEW.device and vlan = NEW.vlan 
	and updated >= @windowStart and updated <= @windowStop into @RX, @TX;

  replace delayed into netload_weekly (id, hostid, device, vlan, updated, tx, rx) values (@windowID, NEW.hostid, NEW.device, NEW.vlan, @windowStop, @TX, @RX);

END;
$$
DELIMITER ;


DROP TRIGGER IF EXISTS netload_weekly_consolidator;
DELIMITER $$
CREATE TRIGGER  netload_weekly_consolidator
AFTER INSERT ON netload_weekly
FOR EACH ROW
BEGIN
  select window_size into @window from table_info where table_name = 'netload_monthly';
  set @windowID = 0;
  select from_unixtime(unix_timestamp(NEW.updated) - unix_timestamp(NEW.updated) % (@window * 60)) into @windowStart;
  select from_unixtime(unix_timestamp(NEW.updated) + @window*60 - (unix_timestamp(NEW.updated) % (@window * 60))) into @windowStop;
  select id from netload_monthly where hostid = NEW.hostid and updated = @windowStop and device = NEW.device into @windowID;

  select avg(rx), avg(tx) from netload_weekly where hostid = NEW.hostid and device = NEW.device and vlan = NEW.vlan 
	and updated >= @windowStart and updated <= @windowStop into @RX, @TX;

  replace delayed into netload_monthly (id, hostid, device, vlan, updated, tx, rx) values (@windowID, NEW.hostid, NEW.device, NEW.vlan, @windowStop, @TX, @RX);

END;
$$
DELIMITER ;
