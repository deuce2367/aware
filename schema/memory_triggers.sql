-- ############################################################################
-- ############################################################################
--                         MEMORY TABLES / TRIGGERS
-- ############################################################################
-- ############################################################################


--
-- Round-Robin Triggers
--

DROP TRIGGER IF EXISTS memory_insert;
DELIMITER $$
CREATE TRIGGER  memory_insert
BEFORE INSERT ON memory
FOR EACH ROW
BEGIN
  select table_rows into @rows from table_info where table_name = 'memory';
  IF NEW.id = 0 THEN
    INSERT into memory_rrd_key VALUES(0);
    select LAST_INSERT_ID() % @rows + 1 into @rrd_key;
    DELETE FROM memory_rrd_key;
    SET NEW.id = @rrd_key;
  END IF;
END;
$$
DELIMITER ;


DROP TRIGGER IF EXISTS memory_daily_insert;
DELIMITER $$
CREATE TRIGGER  memory_daily_insert
BEFORE INSERT ON memory_daily
FOR EACH ROW
BEGIN
  select table_rows into @rows from table_info where table_name = 'memory_daily';
  IF NEW.id = 0 THEN
    INSERT into memory_daily_rrd_key VALUES(0);
    select LAST_INSERT_ID() % @rows + 1 into @rrd_key;
    DELETE FROM memory_daily_rrd_key;
    SET NEW.id = @rrd_key;
  END IF;
END;
$$
DELIMITER ;


DROP TRIGGER IF EXISTS memory_weekly_insert;
DELIMITER $$
CREATE TRIGGER  memory_weekly_insert
BEFORE INSERT ON memory_weekly
FOR EACH ROW
BEGIN
  select table_rows into @rows from table_info where table_name = 'memory_weekly';
  IF NEW.id = 0 THEN
    INSERT into memory_weekly_rrd_key VALUES(0);
    select LAST_INSERT_ID() % @rows + 1 into @rrd_key;
    DELETE FROM memory_weekly_rrd_key;
    SET NEW.id = @rrd_key;
  END IF;
END;
$$
DELIMITER ;


DROP TRIGGER IF EXISTS memory_monthly_insert;
DELIMITER $$
CREATE TRIGGER  memory_monthly_insert
BEFORE INSERT ON memory_monthly
FOR EACH ROW
BEGIN
  select table_rows into @rows from table_info where table_name = 'memory_monthly';
  IF NEW.id = 0 THEN
    INSERT into memory_monthly_rrd_key VALUES(0);
    select LAST_INSERT_ID() % @rows + 1 into @rrd_key;
    DELETE FROM memory_monthly_rrd_key;
    SET NEW.id = @rrd_key;
  END IF;
END;
$$
DELIMITER ;


--
-- Consolidation Triggers
--

DROP TRIGGER IF EXISTS memory_consolidator;
DELIMITER $$
CREATE TRIGGER  memory_consolidator
AFTER INSERT ON memory
FOR EACH ROW
BEGIN
  select window_size into @window from table_info where table_name = 'memory_daily';
  set @windowID = 0;
  select from_unixtime(unix_timestamp(NEW.updated) - unix_timestamp(NEW.updated) % (@window * 60)) into @windowStart;
  select from_unixtime(unix_timestamp(NEW.updated) + @window*60 - (unix_timestamp(NEW.updated) % (@window * 60))) into @windowStop;
  select id from memory_daily where hostid = NEW.hostid and updated = @windowStop into @windowID;

  select avg(used), avg(free), avg(cached), avg(buffers), avg(usedSwap), avg(freeSwap), avg(shmseg), 
    avg(shmsize), avg(shmsem), avg(committed_as) from memory where hostid = NEW.hostid and updated >= @windowStart and updated <= @windowStop 
    into @USED, @FREE, @CACHED, @BUFS, @USWP, @FSWP, @SHMSEG, @SHMSIZ, @SHMSEM, @CAS;

  replace delayed into memory_daily (id, hostid, updated, used, free, cached, buffers, usedSwap, freeSwap, shmseg, shmsize, shmsem, committed_as)
    values (@windowID, NEW.hostid, @windowStop, @USED, @FREE, @CACHED, @BUFS, @USWP, @FSWP, @SHMSEG, @SHMSIZ, @SHMSEM, @CAS);

END;
$$
DELIMITER ;


DROP TRIGGER IF EXISTS memory_daily_consolidator;
DELIMITER $$
CREATE TRIGGER  memory_daily_consolidator
AFTER INSERT ON memory_daily
FOR EACH ROW
BEGIN
  select window_size into @window from table_info where table_name = 'memory_weekly';
  set @windowID = 0;
  select from_unixtime(unix_timestamp(NEW.updated) - unix_timestamp(NEW.updated) % (@window * 60)) into @windowStart;
  select from_unixtime(unix_timestamp(NEW.updated) + @window*60 - (unix_timestamp(NEW.updated) % (@window * 60))) into @windowStop;
  select id from memory_weekly where hostid = NEW.hostid and updated = @windowStop into @windowID;

  select avg(used), avg(free), avg(cached), avg(buffers), avg(usedSwap), avg(freeSwap), avg(shmseg), 
    avg(shmsize), avg(shmsem), avg(committed_as) from memory_daily 
    where hostid = NEW.hostid and updated >= @windowStart and updated <= @windowStop 
    into @USED, @FREE, @CACHED, @BUFS, @USWP, @FSWP, @SHMSEG, @SHMSIZ, @SHMSEM, @CAS;

  replace delayed into memory_weekly (id, hostid, updated, used, free, cached, buffers, usedSwap, freeSwap, shmseg, shmsize, shmsem, committed_as)
    values (@windowID, NEW.hostid, @windowStop, @USED, @FREE, @CACHED, @BUFS, @USWP, @FSWP, @SHMSEG, @SHMSIZ, @SHMSEM, @CAS);

END;
$$
DELIMITER ;


DROP TRIGGER IF EXISTS memory_weekly_consolidator;
DELIMITER $$
CREATE TRIGGER  memory_weekly_consolidator
AFTER INSERT ON memory_weekly
FOR EACH ROW
BEGIN
  select window_size into @window from table_info where table_name = 'memory_monthly';
  set @windowID = 0;
  select from_unixtime(unix_timestamp(NEW.updated) - unix_timestamp(NEW.updated) % (@window * 60)) into @windowStart;
  select from_unixtime(unix_timestamp(NEW.updated) + @window*60 - (unix_timestamp(NEW.updated) % (@window * 60))) into @windowStop;
  select id from memory_monthly where hostid = NEW.hostid and updated = @windowStop into @windowID;

  select avg(used), avg(free), avg(cached), avg(buffers), avg(usedSwap), avg(freeSwap), avg(shmseg), 
    avg(shmsize), avg(shmsem), avg(committed_as) from memory_weekly 
    where hostid = NEW.hostid and updated >= @windowStart and updated <= @windowStop 
    into @USED, @FREE, @CACHED, @BUFS, @USWP, @FSWP, @SHMSEG, @SHMSIZ, @SHMSEM, @CAS;

  replace delayed into memory_monthly (id, hostid, updated, used, free, cached, buffers, usedSwap, freeSwap, shmseg, shmsize, shmsem, committed_as)
    values (@windowID, NEW.hostid, @windowStop, @USED, @FREE, @CACHED, @BUFS, @USWP, @FSWP, @SHMSEG, @SHMSIZ, @SHMSEM, @CAS);

END;
$$
DELIMITER ;
