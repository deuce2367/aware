
-- ############################################################################
-- ############################################################################
--                         DISKLOAD TRIGGERS
-- ############################################################################
-- ############################################################################

--
-- Round-Robin Triggers
--

DROP TRIGGER IF EXISTS diskload_insert;
DELIMITER $$
CREATE TRIGGER  diskload_insert
BEFORE INSERT ON diskload
FOR EACH ROW
BEGIN
  select table_rows into @rows from table_info where table_name = 'diskload';
  IF NEW.id = 0 THEN
    INSERT into diskload_rrd_key VALUES(0);
    select LAST_INSERT_ID() % @rows + 1 into @rrd_key;
    DELETE FROM diskload_rrd_key;
    SET NEW.id = @rrd_key;
  END IF;
END;
$$
DELIMITER ;


DROP TRIGGER IF EXISTS diskload_daily_insert;
DELIMITER $$
CREATE TRIGGER  diskload_daily_insert
BEFORE INSERT ON diskload_daily
FOR EACH ROW
BEGIN
  select table_rows into @rows from table_info where table_name = 'diskload_daily';
  IF NEW.id = 0 THEN
    INSERT into diskload_daily_rrd_key VALUES(0);
    select LAST_INSERT_ID() % @rows + 1 into @rrd_key;
    DELETE FROM diskload_daily_rrd_key;
    SET NEW.id = @rrd_key;
  END IF;
END;
$$
DELIMITER ;


DROP TRIGGER IF EXISTS diskload_weekly_insert;
DELIMITER $$
CREATE TRIGGER  diskload_weekly_insert
BEFORE INSERT ON diskload_weekly
FOR EACH ROW
BEGIN
  select table_rows into @rows from table_info where table_name = 'diskload_weekly';
  IF NEW.id = 0 THEN
    INSERT into diskload_weekly_rrd_key VALUES(0);
    select LAST_INSERT_ID() % @rows + 1 into @rrd_key;
    DELETE FROM diskload_weekly_rrd_key;
    SET NEW.id = @rrd_key;
  END IF;
END;
$$
DELIMITER ;


DROP TRIGGER IF EXISTS diskload_monthly_insert;
DELIMITER $$
CREATE TRIGGER  diskload_monthly_insert
BEFORE INSERT ON diskload_monthly
FOR EACH ROW
BEGIN
  select table_rows into @rows from table_info where table_name = 'diskload_monthly';
  IF NEW.id = 0 THEN
    INSERT into diskload_monthly_rrd_key VALUES(0);
    select LAST_INSERT_ID() % @rows + 1 into @rrd_key;
    DELETE FROM diskload_monthly_rrd_key;
    SET NEW.id = @rrd_key;
  END IF;
END;
$$
DELIMITER ;


--
-- Consolidation Triggers
--

DROP TRIGGER IF EXISTS diskload_consolidator;
DELIMITER $$
CREATE TRIGGER  diskload_consolidator
AFTER INSERT ON diskload
FOR EACH ROW
BEGIN
  select window_size into @window from table_info where table_name = 'diskload_daily';
  set @windowID = 0;
  select from_unixtime(unix_timestamp(NEW.updated) - unix_timestamp(NEW.updated) % (@window * 60)) into @windowStart;
  select from_unixtime(unix_timestamp(NEW.updated) + @window*60 - (unix_timestamp(NEW.updated) % (@window * 60))) into @windowStop;
  select id from diskload_daily where hostid = NEW.hostid and updated = @windowStop and device = NEW.device into @windowID;

  select avg(svctime), avg(utilization), avg(bi), avg(bo) from diskload where hostid = NEW.hostid and device = NEW.device
	and updated >= @windowStart and updated <= @windowStop into @SVCTIME, @UTIL, @RX, @TX;

  replace delayed into diskload_daily (id, hostid, device, updated, svctime, utilization, bo, bi) 
    values (@windowID, NEW.hostid, NEW.device, @windowStop, @SVCTIME, @UTIL, @TX, @RX);

END;
$$
DELIMITER ;


DROP TRIGGER IF EXISTS diskload_daily_consolidator;
DELIMITER $$
CREATE TRIGGER  diskload_daily_consolidator
AFTER INSERT ON diskload_daily
FOR EACH ROW
BEGIN
  select window_size into @window from table_info where table_name = 'diskload_weekly';
  set @windowID = 0;
  select from_unixtime(unix_timestamp(NEW.updated) - unix_timestamp(NEW.updated) % (@window * 60)) into @windowStart;
  select from_unixtime(unix_timestamp(NEW.updated) + @window*60 - (unix_timestamp(NEW.updated) % (@window * 60))) into @windowStop;
  select id from diskload_weekly where hostid = NEW.hostid and updated = @windowStop and device = NEW.device into @windowID;

  select avg(svctime), avg(utilization), avg(bi), avg(bo) from diskload_daily where hostid = NEW.hostid and device = NEW.device
	and updated >= @windowStart and updated <= @windowStop into @SVCTIME, @UTIL, @RX, @TX;

  replace delayed into diskload_weekly (id, hostid, device, updated, svctime, utilization, bo, bi) 
    values (@windowID, NEW.hostid, NEW.device, @windowStop, @SVCTIME, @UTIL, @TX, @RX);

END;
$$
DELIMITER ;


DROP TRIGGER IF EXISTS diskload_weekly_consolidator;
DELIMITER $$
CREATE TRIGGER  diskload_weekly_consolidator
AFTER INSERT ON diskload_weekly
FOR EACH ROW
BEGIN
  select window_size into @window from table_info where table_name = 'diskload_monthly';
  set @windowID = 0;
  select from_unixtime(unix_timestamp(NEW.updated) - unix_timestamp(NEW.updated) % (@window * 60)) into @windowStart;
  select from_unixtime(unix_timestamp(NEW.updated) + @window*60 - (unix_timestamp(NEW.updated) % (@window * 60))) into @windowStop;
  select id from diskload_monthly where hostid = NEW.hostid and updated = @windowStop and device = NEW.device into @windowID;

  select avg(svctime), avg(utilization), avg(bi), avg(bo) from diskload_weekly where hostid = NEW.hostid and device = NEW.device
	and updated >= @windowStart and updated <= @windowStop into @SVCTIME, @UTIL, @RX, @TX;

  replace delayed into diskload_monthly (id, hostid, device, updated, svctime, utilization, bo, bi) 
    values (@windowID, NEW.hostid, NEW.device, @windowStop, @SVCTIME, @UTIL, @TX, @RX);

END;
$$
DELIMITER ;
