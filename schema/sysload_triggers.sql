-- ############################################################################
-- ############################################################################
--                         SYSLOAD TABLES / TRIGGERS
-- ############################################################################
-- ############################################################################

DROP TRIGGER IF EXISTS sysload_insert;
DELIMITER $$
CREATE TRIGGER  sysload_insert
BEFORE INSERT ON sysload
FOR EACH ROW
BEGIN
  SET @rows = 5000000;
  IF NEW.id = 0 THEN
    INSERT into sysload_rrd_key VALUES(0);
	select LAST_INSERT_ID() % @rows into @rrd_key;
    DELETE FROM sysload_rrd_key;
    SET NEW.id = @rrd_key;
  END IF;
END;
$$
DELIMITER ;


DROP TRIGGER IF EXISTS sysload_daily_insert;
DELIMITER $$
CREATE TRIGGER  sysload_daily_insert
BEFORE INSERT ON sysload_daily
FOR EACH ROW
BEGIN
  SET @rows = 5000000;
  IF NEW.id = 0 THEN
    INSERT into sysload_daily_rrd_key VALUES(0);
	select LAST_INSERT_ID() % @rows into @rrd_key;
    DELETE FROM sysload_daily_rrd_key;
    SET NEW.id = @rrd_key;
  END IF;
END;
$$
DELIMITER ;


DROP TRIGGER IF EXISTS sysload_weekly_insert;
DELIMITER $$
CREATE TRIGGER  sysload_weekly_insert
BEFORE INSERT ON sysload_weekly
FOR EACH ROW
BEGIN
  SET @rows = 5000000;
  IF NEW.id = 0 THEN
    INSERT into sysload_weekly_rrd_key VALUES(0);
	select LAST_INSERT_ID() % @rows into @rrd_key;
    DELETE FROM sysload_weekly_rrd_key;
    SET NEW.id = @rrd_key;
  END IF;
END;
$$
DELIMITER ;


DROP TRIGGER IF EXISTS sysload_monthly_insert;
DELIMITER $$
CREATE TRIGGER  sysload_monthly_insert
BEFORE INSERT ON sysload_monthly
FOR EACH ROW
BEGIN
  SET @rows = 5000000;
  IF NEW.id = 0 THEN
    INSERT into sysload_monthly_rrd_key VALUES(0);
	select LAST_INSERT_ID() % @rows into @rrd_key;
    DELETE FROM sysload_monthly_rrd_key;
    SET NEW.id = @rrd_key;
  END IF;
END;
$$
DELIMITER ;


--
-- Consolidation Triggers
--

DROP TRIGGER IF EXISTS sysload_consolidator;
DELIMITER $$
CREATE TRIGGER  sysload_consolidator
AFTER INSERT ON sysload
FOR EACH ROW
BEGIN
  set @window = 5;
  set @windowID = 0;
  select from_unixtime(unix_timestamp(NEW.updated) - unix_timestamp(NEW.updated) % (@window * 60)) into @windowStart;
  select from_unixtime(unix_timestamp(NEW.updated) + @window*60 - (unix_timestamp(NEW.updated) % (@window * 60))) into @windowStop;
  select id from sysload_daily where hostid = NEW.hostid and updated = @windowStop into @windowID;

  select avg(avg), avg(procs), avg(bi), avg(bo), avg(tx), avg(rx), avg(user), avg(system), avg(iowait), avg(irq), 
    avg(softirq), avg(idle), avg(nice) from sysload where hostid = NEW.hostid and updated >= @windowStart and updated <= @windowStop 
    into @AVG, @PROCS, @BI, @BO, @TX, @RX, @USR, @SYS, @IOWAIT, @IRQ, @SIRQ, @IDLE, @NICE;

  replace delayed into sysload_daily (id, hostid, updated, avg, procs, bi, bo, tx, rx, user, system, iowait, irq, softirq, idle, nice)
    values (@windowID, NEW.hostid, @windowStop, @AVG, @PROCS, @BI, @BO, @TX, @RX, @USR, @SYS, @IOWAIT, @IRQ, @SIRQ, @IDLE, @NICE);

END;
$$
DELIMITER ;


DROP TRIGGER IF EXISTS sysload_daily_consolidator;
DELIMITER $$
CREATE TRIGGER  sysload_daily_consolidator
AFTER INSERT ON sysload_daily
FOR EACH ROW
BEGIN
  set @window = 30;
  set @windowID = 0;
  select from_unixtime(unix_timestamp(NEW.updated) - unix_timestamp(NEW.updated) % (@window * 60)) into @windowStart;
  select from_unixtime(unix_timestamp(NEW.updated) + @window*60 - (unix_timestamp(NEW.updated) % (@window * 60))) into @windowStop;
  select id from sysload_weekly where hostid = NEW.hostid and updated = @windowStop into @windowID;

  select avg(avg), avg(procs), avg(bi), avg(bo), avg(tx), avg(rx), avg(user), avg(system), avg(iowait), avg(irq), 
    avg(softirq), avg(idle), avg(nice) from sysload_daily where hostid = NEW.hostid and updated >= @windowStart and updated <= @windowStop 
    into @AVG, @PROCS, @BI, @BO, @TX, @RX, @USR, @SYS, @IOWAIT, @IRQ, @SIRQ, @IDLE, @NICE;

  replace delayed into sysload_weekly (id, hostid, updated, avg, procs, bi, bo, tx, rx, user, system, iowait, irq, softirq, idle, nice)
    values (@windowID, NEW.hostid, @windowStop, @AVG, @PROCS, @BI, @BO, @TX, @RX, @USR, @SYS, @IOWAIT, @IRQ, @SIRQ, @IDLE, @NICE);

END;
$$
DELIMITER ;


DROP TRIGGER IF EXISTS sysload_weekly_consolidator;
DELIMITER $$
CREATE TRIGGER  sysload_weekly_consolidator
AFTER INSERT ON sysload_weekly
FOR EACH ROW
BEGIN
  set @window = 120;
  set @windowID = 0;
  select from_unixtime(unix_timestamp(NEW.updated) - unix_timestamp(NEW.updated) % (@window * 60)) into @windowStart;
  select from_unixtime(unix_timestamp(NEW.updated) + @window*60 - (unix_timestamp(NEW.updated) % (@window * 60))) into @windowStop;
  select id from sysload_monthly where hostid = NEW.hostid and updated = @windowStop into @windowID;

  select avg(avg), avg(procs), avg(bi), avg(bo), avg(tx), avg(rx), avg(user), avg(system), avg(iowait), avg(irq), 
    avg(softirq), avg(idle), avg(nice) from sysload_weekly where hostid = NEW.hostid and updated >= @windowStart and updated <= @windowStop 
    into @AVG, @PROCS, @BI, @BO, @TX, @RX, @USR, @SYS, @IOWAIT, @IRQ, @SIRQ, @IDLE, @NICE;

  replace delayed into sysload_monthly (id, hostid, updated, avg, procs, bi, bo, tx, rx, user, system, iowait, irq, softirq, idle, nice)
    values (@windowID, NEW.hostid, @windowStop, @AVG, @PROCS, @BI, @BO, @TX, @RX, @USR, @SYS, @IOWAIT, @IRQ, @SIRQ, @IDLE, @NICE);

END;
$$
DELIMITER ;
