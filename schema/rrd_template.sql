DROP TABLE IF EXISTS `TABLENAME_rrd_key`;
CREATE TABLE `TABLENAME_rrd_key` (
  `rrd_counter` BIGINT unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY
);

DROP TRIGGER IF EXISTS TABLENAME_insert;
DELIMITER $$
CREATE TRIGGER TABLENAME_insert
BEFORE INSERT ON TABLENAME
FOR EACH ROW 
BEGIN
  SET @rrd_key = 0;
  SET @rows = 10000000;
  IF NEW.id = 0 THEN
    SELECT rrd_counter + 1
      FROM TABLENAME_rrd_key
      INTO @rrd_key;
    SET NEW.id = @rrd_key;
  END IF;
  IF (NEW.id % @rows) THEN
    SET NEW.id = NEW.id % @rows;
  ELSE
    SET NEW.id = @rows;
  END IF;
  UPDATE TABLENAME_rrd_key SET rrd_counter = NEW.id;
END;
$$
DELIMITER;
