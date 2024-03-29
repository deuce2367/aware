INSERT INTO daemon_tasking (daemon, status, description, id, frequency) VALUES ('aware_daemon','1','aware core daemon - runs on all monitored nodes',1,15);
INSERT INTO daemon_tasking (daemon, status, description, id, frequency) VALUES ('pinger','1','pinger daemon - runs on a single node',2,120);
INSERT INTO daemon_tasking (daemon, status, description, id, frequency) VALUES ('poller','1','poller daemon - runs on a single node',3,120);
INSERT INTO profile (id, name, description) VALUES (0,'default','the default profile');
INSERT INTO settings (id, label, value, description) VALUES (1, 'archive_alerts','21','Retain alerts for this many days');
INSERT INTO settings (id, label, value, description) VALUES (2, 'log_procs','1','Configures process logging (1 = on, 0 = off)');
INSERT INTO settings (id, label, value, description) VALUES (3, 'sample_window','5','Sample system performance for this many seconds per sample window');
INSERT INTO settings (id, label, value, description) VALUES (4, 'random','.05','Variable sampling probability factor (in the range from 0.0 to 1.0)');
INSERT INTO settings (id, label, value, description) VALUES (5, 'sensor_timeout','60','Timeout for system-call used to perform sensor lookups (in seconds)');
INSERT INTO thresholds (profile_id, maxmem, maxdisk, maxload, maxtemp, missedpings, maxprocs, maxreport, missedpolls, maxinodes) VALUES (0,75,95,98,71,1,750,300,1,85);
