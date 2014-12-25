-- ############################################################################
-- ############################################################################
--                         SENSOR TRIGGERS
-- ############################################################################
-- ############################################################################


--
-- Round-Robin Triggers
--

DROP TRIGGER IF EXISTS sensor_reading_insert;
DELIMITER $$
CREATE TRIGGER  sensor_reading_insert
BEFORE INSERT ON sensor_reading
FOR EACH ROW
BEGIN
  SET @rows = 5000000;
  IF NEW.id = 0 THEN
    INSERT into sensor_reading_rrd_key VALUES(0);
    select LAST_INSERT_ID() % @rows into @rrd_key;
    DELETE FROM sensor_reading_rrd_key;
    SET NEW.id = @rrd_key;
  END IF;
END;
$$
DELIMITER ;


DROP TRIGGER IF EXISTS sensor_reading_daily_insert;
DELIMITER $$
CREATE TRIGGER  sensor_reading_daily_insert
BEFORE INSERT ON sensor_reading_daily
FOR EACH ROW
BEGIN
  SET @rows = 5000000;
  IF NEW.id = 0 THEN
    INSERT into sensor_reading_daily_rrd_key VALUES(0);
    select LAST_INSERT_ID() % @rows into @rrd_key;
    DELETE FROM sensor_reading_daily_rrd_key;
    SET NEW.id = @rrd_key;
  END IF;
END;
$$
DELIMITER ;


DROP TRIGGER IF EXISTS sensor_reading_weekly_insert;
DELIMITER $$
CREATE TRIGGER  sensor_reading_weekly_insert
BEFORE INSERT ON sensor_reading_weekly
FOR EACH ROW
BEGIN
  SET @rows = 5000000;
  IF NEW.id = 0 THEN
    INSERT into sensor_reading_weekly_rrd_key VALUES(0);
    select LAST_INSERT_ID() % @rows into @rrd_key;
    DELETE FROM sensor_reading_weekly_rrd_key;
    SET NEW.id = @rrd_key;
  END IF;
END;
$$
DELIMITER ;


DROP TRIGGER IF EXISTS sensor_reading_monthly_insert;
DELIMITER $$
CREATE TRIGGER  sensor_reading_monthly_insert
BEFORE INSERT ON sensor_reading_monthly
FOR EACH ROW
BEGIN
  SET @rows = 5000000;
  IF NEW.id = 0 THEN
    INSERT into sensor_reading_monthly_rrd_key VALUES(0);
    select LAST_INSERT_ID() % @rows into @rrd_key;
    DELETE FROM sensor_reading_monthly_rrd_key;
    SET NEW.id = @rrd_key;
  END IF;
END;
$$
DELIMITER ;


--
-- Consolidation Triggers
--

DROP TRIGGER IF EXISTS sensor_reading_consolidator;
DELIMITER $$
CREATE TRIGGER  sensor_reading_consolidator
AFTER INSERT ON sensor_reading
FOR EACH ROW
BEGIN
  set @window = 5;
  set @windowID = 0;
  select from_unixtime(unix_timestamp(NEW.updated) - unix_timestamp(NEW.updated) % (@window * 60)) into @windowStart;
  select from_unixtime(unix_timestamp(NEW.updated) + @window*60 - (unix_timestamp(NEW.updated) % (@window * 60))) into @windowStop;
  select id from sensor_reading_daily where hostid = NEW.hostid and updated = @windowStop and sensor_id = NEW.sensor_id into @windowID;

  select avg(reading) from sensor_reading where hostid = NEW.hostid and sensor_id = NEW.sensor_id
	and updated >= @windowStart and updated <= @windowStop into @READING;

  replace delayed into sensor_reading_daily (id, hostid, sensor_id, updated, reading) values (@windowID, NEW.hostid, NEW.sensor_id, @windowStop, @READING);

END;
$$
DELIMITER ;


DROP TRIGGER IF EXISTS sensor_reading_daily_consolidator;
DELIMITER $$
CREATE TRIGGER  sensor_reading_daily_consolidator
AFTER INSERT ON sensor_reading_daily
FOR EACH ROW
BEGIN
  set @window = 180;
  set @windowID = 0;
  select from_unixtime(unix_timestamp(NEW.updated) - unix_timestamp(NEW.updated) % (@window * 60)) into @windowStart;
  select from_unixtime(unix_timestamp(NEW.updated) + @window*60 - (unix_timestamp(NEW.updated) % (@window * 60))) into @windowStop;
  select id from sensor_reading_weekly where hostid = NEW.hostid and updated = @windowStop and sensor_id = NEW.sensor_id into @windowID;

  select avg(reading) from sensor_reading_daily where hostid = NEW.hostid and sensor_id = NEW.sensor_id
	and updated >= @windowStart and updated <= @windowStop into @READING;

  replace delayed into sensor_reading_weekly (id, hostid, sensor_id, updated, reading) values (@windowID, NEW.hostid, NEW.sensor_id, @windowStop, @READING);

END;
$$
DELIMITER ;


DROP TRIGGER IF EXISTS sensor_reading_weekly_consolidator;
DELIMITER $$
CREATE TRIGGER  sensor_reading_weekly_consolidator
AFTER INSERT ON sensor_reading_weekly
FOR EACH ROW
BEGIN
  set @window = 180;
  set @windowID = 0;
  select from_unixtime(unix_timestamp(NEW.updated) - unix_timestamp(NEW.updated) % (@window * 60)) into @windowStart;
  select from_unixtime(unix_timestamp(NEW.updated) + @window*60 - (unix_timestamp(NEW.updated) % (@window * 60))) into @windowStop;
  select id from sensor_reading_monthly where hostid = NEW.hostid and updated = @windowStop and sensor_id = NEW.sensor_id into @windowID;

  select avg(reading) from sensor_reading_weekly where hostid = NEW.hostid and sensor_id = NEW.sensor_id
	and updated >= @windowStart and updated <= @windowStop into @READING;

  replace delayed into sensor_reading_monthly (id, hostid, sensor_id, updated, reading) values (@windowID, NEW.hostid, NEW.sensor_id, @windowStop, @READING);

END;
$$
DELIMITER ;
