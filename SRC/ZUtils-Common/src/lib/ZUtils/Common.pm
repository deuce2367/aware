package ZUtils::Common;

############################################################################################
############################################################################################
####
#### General Purpose Utilities
####
############################################################################################
############################################################################################

#--------------------------------------------------------------------------------------------
# $Revision: 1.45 $
# $Date: 2010-09-13 13:22:39 $
# $Author: xxxxxx $
# $Name: not supported by cvs2svn $
#--------------------------------------------------------------------------------------------

use 5.008;
use warnings;
use strict;
use DBI;
use POSIX;
use Time::Local;
use Net::FTP;
use HTTP::Request::Common;
require Exporter;
our(@ISA, @EXPORT);
@ISA = qw(Exporter);
@EXPORT = qw(auheader base36 clear_pid comma_format html_comment human_time date_convert db_error 
epoch_to_date exec_sql ftp_get_filesize frformat from_unixtime get_config get_date get_day 
get_db_connection get_description get_epoch get_file_count get_mailorder_filename get_next_number 
get_boot_time get_next_sequence get_row_type get_time get_unix_date lat_dms launch_daemon
load_config lon_dms med mtd min max avg std post_status print_vars print_env print_logfile 
print_log print_status read_config save_chart send_file set_config set_pid signal_handler 
start_daemon stop_daemon store_file unix_timestamp unix_timestamp_midas xprint wrap_text space_pad);

#--------------------------------------------------------------------------------------------
# CVS/Version Info
#--------------------------------------------------------------------------------------------

our $VERSION = sprintf "%d.%03d", q$Revision: 1.45 $ =~ /(\d+)/g;

#--------------------------------------------------------------------------------------------
# members
#--------------------------------------------------------------------------------------------

my %configuration;

my @b36 = (
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B',
        'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
        'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
);

#--------------------------------------------------------------------------------------------
# functions 
#--------------------------------------------------------------------------------------------


###########################################################################################
#
# auheader (filename, offset, length, srate)
#
# - this function will set the length in the AU header for an aufile 
#   the offset parameter is optional, default is 0 (probably should use 512 for Bluefiles)
#   the length parameter is optional, default is -1 
#   the srate parameter is optional, default is 8000
#
###########################################################################################

sub auheader {
    
    my ($filename, $offset, $length, $srate) = @_;

    if (!defined($offset)) { $offset = 0; }
    if (!defined($length)) { $length = -1; }
    if (!defined($srate)) { $srate = 8000; }

    if (! -e $filename) {
        return 0;
    }

    # -- write the length to the AU-header
    open(FILE, "+<$filename") || return 0;
    binmode(FILE);
    seek(FILE, 8 + $offset, 0);
    my $aulen = pack("N", $length);
    print FILE $aulen;

    # -- write the sample length to the AU-header
    seek(FILE, 16 + $offset, 0);
    $srate = pack("N", $srate);
    print FILE $srate;
    close(FILE);

    return 1;

}


###########################################################################################
#
# base36 (number)
#
# - this function will return the base-36 formatted (i.e. mailorder) version of the number
#
###########################################################################################

sub base36 {

        my ($number) = @_;

    if (!defined($number)) { return "000"; }

        my $p1 = $number % 36;
        my $d1 = $p1;
        $number = $number - $p1;

        my $p2 = $number % 1296;
        my $d2 = $p2 / 36;
        $number = $number - $p2;

        my $p3 = $number % 46656;
        my $d3 = $p3 / 1296;

        return "$b36[$d3]$b36[$d2]$b36[$d1]";

}


###########################################################################################
#
# clear_pid (pifile)
#
# - this routine should clean up the specified pid file
#
###########################################################################################

sub clear_pid {
    my ($pidfile) = @_;

    if (! -f $pidfile) { return; }

    my $hostName = `hostname -s`;
    chomp $hostName;
    my $whoami = `whoami`;
    chomp $whoami;

    chomp(my $curPid = `cat $pidfile`);
    my ($serverName,$userName) = ('','');
    if ($curPid =~ /\:/) {
      ($curPid,$serverName,$userName,undef,undef) = split(":",$curPid,5);
    }
    if (length($serverName) <= 0) {
      if ($curPid eq $$) {
        print_log("my pid = $$, curPid = $curPid, removing '$pidfile'", 1);
    unlink($pidfile);
      }
    } else {
      if (($curPid eq $$) && ($serverName eq $hostName) && ($userName eq $whoami)) {
        print_log("my pid = $$, curPid = $curPid ($serverName), removing '$pidfile'", 1);
    unlink($pidfile);
      } else {
        print_log("Unable to remove '$pidfile', my pid=$$ ($hostName), curPid=$curPid ($serverName)", 1);
      }
    }
}


###########################################################################################
#
# comma_format(number)
#
# - this routine should format the specified number with commas
#
###########################################################################################

sub comma_format {

    my ($number) = @_;

    if (!defined($number)) { return ""; }

    my $decimal = "";

    if ($number =~ m/\./) {
        $decimal =~ s/^.*\.//g;
        $number =~ s/\..*$//g;
    }

    my @array = ();

    while ($number =~ /\d\d\d\d/) {

        $number =~ s/(\d\d\d)$//;
        unshift(@array, $1);
    }
    unshift(@array, $number);
    $number = join(",", @array);
    $number = "$number\.$decimal" if $decimal =~ /\d/;
    return $number;
}


###########################################################################################
#
# html_comment(string)
#
# - this routine will print the specified string as an html formatted comment
#
###########################################################################################

sub html_comment {
    my ($message) = @_;
    if ($message) { print "<!-- $message -->\n"; }
}


########################################################################################
#
# human_time (time) 
#
# - given a time value (in seconds) convert that time to "human" time
#
########################################################################################

sub human_time {

    my ($time) = @_;

    if (!defined($time)) { return ""; }

    # -- time conversion to friendly units
    $time = $time / 86400;
    if ($time > 365) { 
        $time = sprintf("%0.2f yrs.", $time / 365);
    } elsif ($time > 2) {
        $time = sprintf("%0.1f days", $time);
    } elsif ($time > .3) {
        $time = sprintf("%0.2f hrs.", $time * 24);
    } elsif ($time > .0014) {
        $time = sprintf("%0.0f min.", $time * 1440);
    } else {
        $time = sprintf("%0.0f sec.", $time * 1440 * 60);
    }

    return $time;
}


###########################################################################################
#
# date_convert(datestring)
#
# - this routine will convert a date string to a time object
#
###########################################################################################

sub date_convert {
        my ($dateString) = @_;

        my ($date, $time) = split(/ /, $dateString);
        my ($year, $month, $day) = split(/-/, $date);
        my ($hour, $minute, $second) = split(/:/, $time);

        $year -= 1900;
        $month--;

        return get_epoch($second, $minute, $hour, $day, $month, $year);
}


###########################################################################################
#
# db_error(error)
#
# - this routine will print the specified error out as an html formatted error message
#
###########################################################################################

sub db_error {

    my ($error) = @_;
    print "<font class=alert>$error</font>\n";
}


###########################################################################################
#
# epoch_to_date(date)
#
# - this routine will convert an epoch date to the current date
#
###########################################################################################

sub epoch_to_date {

        my ($epoch) = @_;
        # Perform Extration/Conversion
        my ($sec, $min, $hour, $day, $month, $year) = (get_time($epoch)) [0,1,2,3,4,5];
        my $date = sprintf("%04d-%02d-%02d %02d:%02d:%02d", $year + 1900, $month + 1, $day, $hour, $min, $sec);
        return $date;
}


###########################################################################################
#
# exec_sql (dbh, sql)
#
# - this function will return the first row retrieved from the database using the provided
#   database handle and sql statment
#
###########################################################################################

sub exec_sql {
    my ($dbh, $sql) = @_;
    my $sth = $dbh->prepare($sql) || print STDERR "SQL Error: " . $dbh->errstr . "\n";
    $sth->execute() || print STDERR "Database Error: " . $dbh->errstr . "\n";
    my @row = $sth->fetchrow();
    $sth->finish();
    return @row;
}


################################################################################################
#
# ftp_get_filesize (hostname, username, password, directory, filename)
#
# this routine is responsible for files from a remote ftp server
#
################################################################################################

sub ftp_get_filesize {

    my ($hostname, $username, $password, $directory, $filename) = @_;

    my $errors = 0;

    # -- connect to FTP server
    my $ftp = Net::FTP->new($hostname, Debug => 0) || $errors++;
    if ($errors) {
        print_log("ERROR: ftp unable to connect to remote host '$hostname'", 0);
        return -1;
    }

    # -- log in w/ provided credentials
    $ftp->login($username, $password) || $errors++;
    if ($errors) {
        print_log("ERROR: ftp unable to log in to remote host '$hostname' ($username/$password)", 0);
        return -1;
    }

    # -- change to the target directory
    $ftp->cwd($directory) || $errors++;
    if ($errors) {
        print_log("ERROR: ftp unable to change to remote directory '$directory' on '$hostname'", 0);
        return -1;
    }

    my $size = $ftp->size($filename) || $errors++;
    if ($errors) {
        return -1;
    }

    $ftp->quit();

    return $size;

}


################################################################################################
#
# frformat(num, size, places)
#
# -given a number round and truncate to the specified size and number of places
#
# -return the formatted number
#
################################################################################################

sub frformat {

    my ($num, $size, $places) = @_;

    if ($num eq "NaNQ" ) {
        $num = -1;
    } else {
        my $diff = 1 / 10**$places;
        $num = sprintf("%.$places" . "f", $num / 1000000);

        if ($num =~ m/9$/ || $num =~ m/4$/) { $num = $num + $diff; }
        if ($num =~ m/1$/ || $num =~ m/6$/) { $num = $num - $diff; }
    }

    return $num;
}


################################################################################################
#
# from_unixtime(epoch)
#
# - this function will return the date object using the provided epoch date
#
################################################################################################

sub from_unixtime {

    my ($epoch) = @_;
    # Perform Extration/Conversion
    my ($sec, $min, $hour, $day, $month, $year) = (get_time($epoch)) [0,1,2,3,4,5];
    my $date = sprintf("%04d-%02d-%02d %02d:%02d:%02d", $year + 1900, $month + 1, $day, $hour, $min, $sec);
    return $date;
}


#--------------------------------------------------------------------------------------------------------------------------
# get_boot_time()
#
# get_boot_time will try to determine the date/time when the system was booted based on /proc/uptime
#
#--------------------------------------------------------------------------------------------------------------------------

sub get_boot_time {

    # -- calculate System Boot time based on /proc/uptime
    my $uptime = 0;
    my $epoch = unix_timestamp(get_date());
    open(IN, "</proc/uptime");
    while(<IN>) { 
        my $uptimeStr = $_; 
        ($uptime, undef) = split(/\s+/, $uptimeStr);
    }
    close(IN);

    my $booted = from_unixtime($epoch - $uptime);

    return $booted;

}


################################################################################################
# 
# get_config (variable, [default])
#
# - this function will return the value of the provided variable from the configuration hash
#   if a default value is provided, that will be returned if the setting doesn't exist
#
################################################################################################

sub get_config {

    my ($variable, $default) = @_;

    my $result = undef;
    if (defined($configuration{$variable})) {
        $result = $configuration{$variable};
    } elsif (defined($default)) {
        $result = $default;
    }

    return $result;

}


################################################################################################
#
# get_date (offset)
#
# - this function will return the date (YYYY-MM-DD HH24:MM:SS) using the provided offset (in days)
#
################################################################################################

sub get_date {

        my ($offset) = shift || 0;
        # Perform Extration/Conversion
        my ($_sec, $_min, $_hour, $_day, $_month, $_year) = (get_time()) [0,1,2,3,4,5];
        my $time = get_epoch($_sec, $_min, $_hour, $_day, $_month, $_year);
        $time = $time + ($offset * 86400);

        my ($sec, $min, $hour, $day, $month, $year) = (get_time($time)) [0,1,2,3,4,5];
        my $date = sprintf("%04d-%02d-%02d %02d:%02d:%02d", $year + 1900, $month + 1, $day, $hour, $min, $sec);
        return $date;
}


################################################################################################
#
# get_day (offset)
#
# - this function will return the date (YYYY-DD-MM) using the provided offset (in days) 
#
################################################################################################

sub get_day {

        my ($offset) = @_;

    # the default offset is 0
    if (!defined($offset)) { $offset = 0; }    

        # Perform Extration/Conversion
    my ($_sec, $_min, $_hour, $_day, $_month, $_year) = (get_time()) [0,1,2,3,4,5];
        my $time = get_epoch($_sec, $_min, $_hour, $_day, $_month, $_year);
        $time = $time + ($offset * 86400);

        my ($sec, $min, $hour, $day, $month, $year) = (get_time($time)) [0,1,2,3,4,5];
        my $dayStr = sprintf("%04d-%02d-%02d", $year + 1900, $month + 1, $day);
        return $dayStr;
}


################################################################################################
#
# get_db_connection
#
# - this function will open and return a connection to the database
#
################################################################################################

sub get_db_connection {

    my ($retries, $backoff) = @_;

    if (!defined($retries)) { $retries = 3; }
    if (!defined($backoff)) { $backoff = 20; }

    my $database = get_config("database");
    my $connect_string = get_config("connect_string");
    my $dbuser = get_config("dbuser");
    my $dbpass = get_config("dbpass");

    # -- oracle settings
    if ($database eq "oracle") {
        $ENV{ORACLE_HOME}       = $configuration{oracle_home};
        $ENV{LD_LIBRARY_PATH}   = "$configuration{oracle_home}/lib";
    }

    # connect to db
    my $dbh = DBI->connect($connect_string,$dbuser,$dbpass,{
       RaiseError => 0,
       PrintError => 0,
       AutoCommit => 0,
    });


    # -- see if our database connection is legit
    if (!defined($dbh) && $retries) {
        print_log("ERROR: Unable to connect to $database database (retries left = $retries)", 0);
        print_log(" - using ($connect_string, $dbuser, $dbpass)", 2);
        my $attempts = 0;
        while($attempts < $retries && !defined($dbh)) {
            sleep($backoff);
            $attempts++;
            print_log("Retrying DB connection -- $attempts / $retries", 1);

            $dbh = DBI->connect($connect_string,$dbuser,$dbpass,{
               RaiseError => 0,
               PrintError => 0,
               AutoCommit => 0,
            });
        } 
        if (!defined($dbh)) {
            print_log("ERROR: unable to connect to database after $attempts attempt(s)");
            print_log(" - using ($connect_string, $dbuser, $dbpass)", 2);
            print_log("------ exiting application ------", 0);
            exit();
        }
    }


    # adjust Oracle's useless default date format
    if ($database eq "oracle" && defined($dbh)) {
            $dbh->do("alter session set nls_date_format = 'yyyy-mm-dd hh24:mi:ss'");
    }

    return $dbh;

}


##############################################################################################
#
# get_description(dbh, setting)
#
# - return the description for the specified setting
#
##############################################################################################
    
sub get_description {

    my ($dbh, $setting) = @_;

    my $sql = "select description from settings where label = '$setting'";
    my $sth = $dbh -> prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
    $sth -> execute() || print "Database Error: " . $dbh->errstr . "\n";
    my @row = $sth->fetchrow();
    my $value = $row[0];
    $sth->finish();
    return $value;
}


########################################################################################
#
# get_epoch(sec, min, hour, day, month, year)
#
# - get_epoch will return an epoch string for the time format that is currently 
#   configured
#
########################################################################################


sub get_epoch {

    my ($_sec, $_min, $_hour, $_day, $_month, $_year) = @_;

    if (!defined($configuration{time_function})) { 
        $configuration{time_function} = "gmtime"; 
        return timegm($_sec, $_min, $_hour, $_day, $_month, $_year);
    } elsif ($configuration{time_function} eq "gmtime") {
        return timegm($_sec, $_min, $_hour, $_day, $_month, $_year);
    } else {
        return timelocal($_sec, $_min, $_hour, $_day, $_month, $_year);
    }

}


########################################################################################
#
# get_file_count(directory, pattern)
#
# - given a directory name and search pattern return the number of matching files from 
#   that directory
#
########################################################################################

sub get_file_count {

    my ($directory, $pattern) = @_;

    if (!defined($pattern)) { $pattern = ""; }

    if (! -d $directory) { return -1; }

    opendir(DIR, $directory) or return -1;
    my @files = grep {/$pattern/ && -f "$directory/$_" } readdir(DIR);
    closedir(DIR);
    my $matchCount = $#files + 1;

    return $matchCount;

}


########################################################################################
# 
# get_mailorder_filename(dbh, siteid, trigraph, prio)
#
# - this function returns the next mailorder filename
#
########################################################################################

sub get_mailorder_filename {

    my ($dbh, $siteID, $trigraph, $prio) = @_;

    my $database = get_config("database");

    my $moNum = "";

    if ($database eq "oracle") {
        my $sql = get_config("mo_sql") || "select nextcsdfid(1) from dual";
        my $sth = $dbh->prepare($sql) || print_log("ERROR ($sql): " . $dbh->errstr, 0);
        if (!$sth->execute()) { print_log("ERROR ($sql): " . $dbh->errstr, 0); }
        my @row = $sth->fetchrow();
        $moNum = $row[0] || 0;
        $sth->finish();
    } elsif ($database eq "mysql") {
        # -- lock the sequence table to make sure our read/write is clean
        $dbh->do("lock tables sequence write");
        my $sql = "select mailorder from sequence";
        my $sth = $dbh->prepare($sql) || print_log("ERROR ($sql): " . $dbh->errstr, 0);
        if (!$sth->execute()) { print_log("ERROR ($sql): " . $dbh->errstr, 0); }
        my @row = $sth->fetchrow();
        $sth->finish();
        $moNum = $row[0] || 1;
        $dbh->do("update sequence set mailorder = (mailorder + 1) % 46655");
        $dbh->do("unlock tables");
    } else {
        $moNum = int(rand() * 45000);
        print_log("WARNING: generating random mailorder sequence!", 0);
    }

    # -- check config to see if we need to convert this number to base-36
    my $encodeValue = get_config("mo_base36") || 0;
    if (!$encodeValue) { $moNum = base36($moNum); }

    my $moFile = $siteID . $trigraph . $configuration{digraph} . $prio . $moNum . $configuration{ft};

    return $moFile;
}



##############################################################################
#
# get_next_sequence (sequence)
#
# - given the name of a an Oracle sequence in the database, get_next_sequence
#  will return the next value and increment the sequence
#
##############################################################################

sub get_next_sequence {

    my ($dbh, $sequence) = @_;

    my $sql = "select $sequence.nextval from dual";
    my $sth = $dbh->prepare($sql) || print_log("ERROR ($sql): " . $dbh->errstr, 0);
    $sth->execute() || print_log("ERROR ($sql): " . $dbh->errstr, 0);

    my @row = $sth->fetchrow();

    my $nextValue = $row[0];

    $sth->finish();

    return $nextValue;

}


##############################################################################
#
# get_row_type (number)
#
# - this is for html pages, it returns the string 'odd' if the number passed
#   was odd, 'even' if the number passed was even
#
##############################################################################

sub get_row_type {
    my ($num) = @_;
    my $row = "odd";
    if ($num % 2 == 0) { $row = "even"; }
    return $row;

}



########################################################################################
#
# get_time()
#
# - get_time will return the current time value (note that gmtime() vs localtime() will 
#   be chosen based on the current configuration)
#
########################################################################################

sub get_time {

    my ($epoch) = @_;

    if (!defined($configuration{time_function})) { 
        $configuration{time_function} = "gmtime"; 
        if (!defined($epoch)) {
            return gmtime();
        } else {
            return gmtime($epoch);
        }
    } elsif ($configuration{time_function} eq "gmtime") {
        if (!defined($epoch)) {
            return gmtime();
        } else {
            return gmtime($epoch);
        }
    } else {
        if (!defined($epoch)) {
            return localtime();
        } else {
            return localtime($epoch);
        }
    }

}


########################################################################################
#
# get_unix_date
#
# - this function will return the epoch string using the provided offset (in days)
#
########################################################################################

sub get_unix_date {

        my ($offset) = @_;
        if (!defined($offset)) { $offset = 0; }
        # Perform Extration/Conversion
        my ($_sec, $_min, $_hour, $_day, $_month, $_year) = (get_time()) [0,1,2,3,4,5];
        my $time = get_epoch($_sec, $_min, $_hour, $_day, $_month, $_year);
        $time = $time + ($offset * 86400);

        return $time;
}


##############################################################################################
#
# lat_dms (longitude)
#
# - given a latitude in decimal notation lat_dms() will return the degrees/minutes/seconds
#   representation of that latitude
#
##############################################################################################

sub lat_dms {

    my ($latitude) = @_;

    if (!defined($latitude)) { $latitude = 0; }

    my $v_deg_long = abs($latitude);
    my $v_deg = floor($v_deg_long);
    $v_deg =~ s/^999//g;

    my $v_min_long = ($v_deg_long-$v_deg)*60;
    my $v_min = floor($v_min_long);
    $v_min =~ s/^09//g;

    my $v_sec_long = ($v_min_long-$v_min)*60;
    my $v_sec = sprintf("%.0f", $v_sec_long);
    $v_sec =~ s/^09//g;

    my $sign = "";
    my $dir = "";

    if ($latitude >= 0) {
        $sign = "";
        $dir = "N";
    } elsif ($latitude < 0) {
        $sign = "-";
        $dir = "S";
    }

    return "$sign$v_deg.$v_min.$v_sec$dir";

}



########################################################################################
#
# launch_daemon ()
#
# - this function will fork this process as a daemon and detach
#
########################################################################################

sub launch_daemon {

    my ($name) = @_;

    # Fork child and exit from parent - i.e. launch the daemon
    my $pid = fork;
    my $pidfile = get_config("pidfile");
    exit if $pid;
    die "Error forking process: $!" unless defined($pid);
    setsid();

    if (set_pid($name, $pidfile) != $$) {
        print "$name already running\n";
        print_log("$name process already active (check '$pidfile')", 1);
        exit;
    }
    print "$name started (pid = $$)\n";

    # -- Important - helps prevent ssh/rsh hangs
    close(STDIN) unless get_config("debug");
    close(STDOUT) unless get_config("debug");
    close(STDERR) unless get_config("debug");

}

########################################################################################
#
# load_config (cfgfile)
#
# - this function will load values from the specified configuration file into the local
#   configuration hash structure
#
########################################################################################

sub load_config {

    my ($cfgfile) = @_;

    if (! -e $cfgfile) {
        print "ERROR: unable to find a valid configuration file (using '$cfgfile')!\n\n";
        print "\tMake sure that the ZUTILS_CFGFILE environment variable exists and points\n";
        print "\tto a valid configuration file and that the permissions on this file\n";
        print "\tallow read access to this user account.\n\n";
        exit();
    }

    $configuration{cfgfile} = $cfgfile;

    open(CONFIG, "$configuration{cfgfile}") || die "Error opening '$configuration{cfgfile}'";
    while(<CONFIG>) {

        my $line = $_;
        chomp($line);
        if ($line =~ m/^#/ || length($line) < 2 || $line !~ m/=/) {
            next;
        }
        my ($name, @values) = split(/=/, $line);
        my $value = $values[0];
        for (my $i = 1; $i <= $#values; $i++) { $value .= "=$values[$i]"; }
        $name =~ s/^\s+//g;
        $value =~ s/^\s+//g;
        $name =~ s/\s+$//g;
        $value =~ s/\s+$//g;

        # -- support use of environment variables in config files
        #
        # notes on supported usage:
        # - MUST use syntax ${VAR}
        # - may use multiple variables
        # - nonexistent variables will be replaced by the empty string
        #
        # examples follow:
        #
        # logdir = ${SYSTEM_LOGDIR}
        # cfgfile = /home/${LOGNAME}/logs
        #

        while ($value =~ m/\$\{.*?\}/) {
            my $envvar = $value;
            $envvar =~ s/^.*?\$\{//;
            $envvar =~ s/\}.*$//;
            if (defined($ENV{$envvar})) {
                # -- replace w/ environment variable value
                $value =~ s/\$\{.*?\}/$ENV{$envvar}/;
            } else {
                # -- environment variable not found
                $value =~ s/\$\{.*?\}//;
            }
        }

        $configuration{$name} = $value;

    }
    close(CONFIG);

}


##############################################################################################
#
# lon_dms (longitude)
#
# - given a longitude in decimal notation lon_dms() will return the degrees/minutes/seconds
#   representation of that longitude
#
##############################################################################################

sub lon_dms {

    my ($longitude) = @_;

    if (!defined($longitude)) { $longitude = 0; }

    my $v_deg_long = abs($longitude);
    my $v_deg = floor($v_deg_long);
    $v_deg =~ s/^999//g;

    my $v_min_long = ($v_deg_long-$v_deg)*60;
    my $v_min = floor($v_min_long);
    $v_min =~ s/^09//g;

    my $v_sec_long = ($v_min_long-$v_min)*60;
    my $v_sec = sprintf("%.0f", $v_sec_long);
    $v_sec =~ s/^09//g;

    my $sign = "";
    my $dir = "";

    if ($longitude >= 0) {
        $sign = "";
        $dir = "E";
    } elsif ($longitude < 0) {
        $sign = "-";
        $dir = "W";
    }

    return "$sign$v_deg.$v_min.$v_sec$dir";

}

##############################################################################################
#
# space_pad (string, length)
#
# - pad a string with spaces to the specified length
#
##############################################################################################

sub space_pad {

    my ($string, $num) = @_;

    while(length($string) < $num) { $string .= " "; }

    return $string;
}


##############################################################################################
#
# wrap_text (string, length, padding)
#
# - try and format arbitrary text to the specified dimensions
#
##############################################################################################

sub wrap_text {
    my ($string, $length, $padding) = @_;

    if (length($string) > $length) {
        my $newString = "";

        while(length($string) > $length) {
            my $wrapped = 0;
            for (my $i = $length; $i > 0; $i--) {
                my $char = substr($string, $i, 1);
                if ($char eq ',' || $char eq ' ' || $char eq '-' || $char eq '.') {
                    $newString = $newString . substr($string, 0, $i + 1) . "\n";
                    $newString .= space_pad("", $padding);
                    $wrapped = 1;
                    $string = substr($string, $i + 1);  
                    $string =~ s/^\s+//g;
                    $i = 0;
                }
            }

            if (!$wrapped) {
                $newString = $newString . substr($string, 0, $length) . "...\n";
                $newString .= space_pad("", $padding);
                $string = substr($string, $length);
                $string =~ s/^\s+//g;
            }
        }

        if (length($string) > 0) { $newString .= $string; }
        $string = $newString;
    }

    return $string;

}


##############################################################################################
#
# mtd(array)
#
# - return the mtd of the specified set of numbers
#
##############################################################################################

sub mtd {

    my (@numbers) = @_;

    my $med = med(@numbers);
    my $n = scalar(@numbers);

    my $sum = 0;
    foreach my $x (@numbers) {
        my $diff = $x - $med;
        $sum += $diff * $diff;
    }
    return sqrt($sum / ($n));

}


##############################################################################################
#
# std(array)
#
# - return the std of the specified set of numbers
#
##############################################################################################

sub std {

    my (@numbers) = @_;

    my $avg = avg(@numbers);
    my $n = scalar(@numbers);

    my $sum = 0;
    foreach my $x (@numbers) {
        my $diff = $x - $avg;
        $sum += $diff * $diff;
    }
    return sqrt($sum / ($n));

}


##############################################################################################
#
# avg(array)
#
# - return the avg of the specified set of numbers
#
##############################################################################################

sub avg {

    my (@numbers) = @_;

    my $n = scalar(@numbers);
    my $sum = 0;
    foreach my $number (@numbers) { $sum += $number; }
    return $sum / $n;

}         


##############################################################################################
#
# min(array)
#
# - return the min of the specified set of numbers
#
##############################################################################################
    
sub min {

    my (@numbers) = @_;

    my $min = $numbers[0];
    my $n = scalar(@numbers);
    for (my $i = 1; $i < $n; $i++) {
        $min = $numbers[$i] unless $numbers[$i] > $min;
    }
    return $min;
}


##############################################################################################
#
# max(array)
#
# - return the max of the specified set of numbers
#
##############################################################################################
    
sub max {

    my (@numbers) = @_;

    my $max = $numbers[0];
    my $n = scalar(@numbers);
    for (my $i = 1; $i < $n; $i++) {
        $max = $numbers[$i] unless $numbers[$i] < $max;
    }
    return $max;
}


##############################################################################################
#
# med(array)
#
# - return the med of the specified set of numbers
#
##############################################################################################
    
sub med {

    my (@numbers) = @_;

    my $n = $#numbers + 1;
    @numbers = sort(@numbers);

    if ($n < 1) {
        return 0;
    } elsif ($n == 1) {
        return $numbers[0];
    } elsif ($n % 2 == 0) {
        return sprintf("%0.0f", ($numbers[($n / 2) - 1] + $numbers[$n / 2]) / 2); 
    } else {
        my $median = $numbers[($n - 1) / 2];
        return $numbers[($n - 1) / 2];
    }

}


##############################################################################################
#
# read_config (file)
#
# - read_config will return a hashtable containing the contents of 'file', which should contain
#   name/value pairs, # is a comment, empty lines are ignored
#
##############################################################################################

sub read_config {

    my ($file) = @_;

    my %config;
    open(CONFIG, "<$file") || return;
    while(<CONFIG>) {

        my $line = $_;
        chomp($line);
        if ($line =~ m/^#/ || length($line) < 2 || $line !~ m/=/) {
            next;
        }
        my ($name, $value) = split(/=/, $line);

    # -- handle the "missing" case for name and value as appropriate
    if (!defined($name)) { next; }
    if (!defined($value)) { $value = ""; }

        $name =~ s/^\s+//g;
        $value =~ s/^\s+//g;
        $name =~ s/\s+$//g;
        $value =~ s/\s+$//g;
        $config{$name} = $value;
    }
    close(CONFIG);
    return %config;

}



#################################################################################################
#
# save_chart (chart, name)
#
# - given a chart object and a filename save the chart, return the name of the resulting file
#
#################################################################################################

sub save_chart
{
    my $chart = shift or die "Error: Need a chart!\n";
    my $name = shift or die "Error: Need a name!\n";

    my $ext = $chart->export_format;
    my $filename = "$name.$ext";

    open(OUT, ">$filename") or die "ERROR: save_chart() cannot open $filename for write: $!\n";
    binmode OUT;
    print OUT $chart->gd->$ext();
    close OUT;
    return $filename;
}


#################################################################################################
#
# send_file (ftpserver, ftpuser, ftppass, ftpdir, filename)
#
# - given ftp params and a filename, send_file() will send that file to the designated FTP server
#
#################################################################################################

sub send_file {

    my ($ftpserver, $ftpuser, $ftppass, $ftpdir, $filename) = @_;

    my $srcfile = $filename;

    my $dstfile = $filename;
    $dstfile =~ s/.*\///g;

    print_log("Sending Files to $ftpserver:/$ftpdir", 2);

    my $ftp = Net::FTP->new($ftpserver, Debug=> 0);
    $ftp->login($ftpuser, $ftppass);
    $ftp->cwd($ftpdir);
    $ftp->binary();
    $ftp->put($srcfile, $dstfile);
    $ftp->quit();

    print_log("FTP transfer to $ftpserver complete: $srcfile -> $dstfile", 1);

}


###########################################################################################
#
# set_config(name, value)
#
# - this routine will set the provided variable name to the provided value in the local
#   configuration hash
#
###########################################################################################

sub set_config {

    my ($variable, $value) = @_;

    if (!defined($variable)) { return; }
    if (!defined($value)) { $value = ""; }
    
    $configuration{"$variable"} = $value;

    return;

}


###########################################################################################
#
# set_pid(name, pidfile)
#
# - this routine should try and determine if another instance of this process is running
#
###########################################################################################

sub set_pid {

    my ($name, $pidfile) = @_;
    my $curPid = $$;
    my $running = 0;
    my ($pidLine,$hostName,$whoami,$serverName,$userName);

    set_config("pidfile", $pidfile);

    my $logmode = get_config("logmode") || "LOAD";

    # Basic Assumptions:
    # IF
    # - pid file exists
    # - pid file is non-zero
    # - pid file contains pid of process that matches name of process
    # THEN
    # - for our purposes the process is considered to be running
    if (-f $pidfile && -s $pidfile > 0) {
        chomp($curPid = `cat $pidfile`);
        if ($curPid =~ /\:/) {
            ($curPid,$serverName,$userName,undef,undef) = split(":",$curPid,5);
        }

        print_log("setPid: curPid = $curPid, my pid = $$", 2);
        my @pids = `ps --no-headers -eo "pid cmd"`;
        foreach my $ps (@pids) {
            chomp($ps);
            $ps =~ s/^\s+//g;
            my $pid = $ps;
            $pid =~ s/^([0-9]+)\s.*/$1/;
            my $cmd = $ps;
            $cmd =~ s/^[0-9]+\s(.*)/$1/;
            print_log("checking ($pid and $cmd) against ($curPid and $name)", 2);
            if ($pid == $curPid && $cmd =~ m/$name/) { $running = 1; last; }
        }
    }

    if (!$running) {
        print_log("starting new $name", 2);
        $curPid = $$;
        $hostName = `hostname -s`;
        chomp $hostName;
        $whoami = `whoami`;
        chomp $whoami;

        my ($pageSecs,$pageMins,$pageHours,$mday,$mon,$year,undef,undef,undef) = gmtime(time);
        my $logTime = sprintf("%4d%02d%02d%02d%02d%02d",
        ($year+1900),($mon+1),$mday,$pageHours,$pageMins,$pageSecs);
        $pidLine = $curPid.":".$hostName.":".$whoami.":$logmode:XXX:".$logTime."\n";

        open(OUT, ">$pidfile") || die "Cannot write '$pidfile'";
        print OUT $pidLine;
        close(OUT);
        print_log("pid $curPid written to '$pidfile'", 2);
    }
    return $curPid ;

}


###########################################################################################
#
# signal_handler(signal)
#
# this is our signal handler for shutdowns, etc...
#
###########################################################################################

sub signal_handler {

    my ($sig) = @_;

    my $pidfile = get_config("pidfile") || "";
    my $verbosity = get_config("verbosity") || "";
    my $dbdate = get_config("dbdate") || "";
    my $name = get_config("name") || "";

    print_log("signal $sig received (pid = $$, verbosity = $verbosity)", 0);

    if (-e $pidfile) {
        my $hostName = (uname())[1];
        $hostName =~ s/\..*//g;
        chomp(my $whoami = `whoami`);

        chomp(my $curPid = `cat $pidfile`);
        my ($serverName,$userName) = ('','');
        if ($curPid =~ /\:/) {
            ($curPid,$serverName,$userName,undef,undef) = split(":",$curPid,5);
        }
        if (length($serverName) <= 0) {
            if ($curPid eq $$) {
                print_log("my pid = $$, curPid = $curPid, removing '$pidfile'", 1);
                unlink($pidfile);
            }
        } else {
            if (($curPid eq $$) && ($serverName eq $hostName) && ($userName eq $whoami)) {
                print_log("my pid = $$, curPid = $curPid ($serverName), removing '$pidfile'", 1);
                unlink($pidfile);
            } else {
                print_log("Unable to remove '$pidfile', my pid=$$ ($hostName), curPid=$curPid ($serverName)", 1);
            }
        }
    }

    print_log("$name shutting down (pid = $$, verbosity = $verbosity)", 1);
    exit();
}


########################################################################################
#
# start_daemon(name, path, user)
#
# start_daemon will try and start the daemon as the specified user
#
########################################################################################

sub start_daemon {

    my ($DAEMON , $CMD, $USER) = @_;

    my $PIDFILE = get_config("pidfile", "/var/run/$DAEMON.pid");

    # -- fork child and exit from parent
    setsid();
    my $pid = fork;
    if ($pid) { exit(); }

    die "Error forking process: $!" unless defined($pid);

    if (set_pid($DAEMON, $PIDFILE) != $$) {
        print "$DAEMON already running\n";
        print_log("$DAEMON process already active (check '$PIDFILE')", 1);
        exit;
    }

    print "$DAEMON started\n";

    # -- Important - helps prevent ssh/rsh hangs
    close(STDIN) unless get_config("debug");
    close(STDOUT) unless get_config("debug");
    close(STDERR) unless get_config("debug");

    chomp(my $current_user = `whoami`);

    if ($current_user eq "$USER") {
        system("$CMD");
    } else {
        system("su $USER -c '$CMD'");
    }
}


########################################################################################
#
# stop_daemon(pidfile, name)
#
# stop_daemon will try and shutdown the daemon, first gracefully then via brute force
#
########################################################################################

sub stop_daemon {

    my ($PIDFILE , $DAEMON) = @_;

    my $running = 1;
    my $attempts = 10;
    my $sig = "-HUP";

    if (-f $PIDFILE && -s $PIDFILE > 0) {
        my ($serverName,$userName) = ('','');
        my $hostName = `hostname -s`;
        chomp $hostName;
        my $whoami = `whoami`;
        chomp $whoami;

        chomp(my $curPid = `cat $PIDFILE`);
        if ($curPid =~ /\:/) {
          ($curPid,$serverName,$userName,undef,undef) = split(":",$curPid,5);
        }

        if ((length($serverName) <= 0) || ($serverName =~ /$hostName/i)) {
          # We will try 9 times to kill the existing daemon process gracefully
          # On the last attempt we will send a kill -9 just in case
          while ($curPid && $running && $attempts > 0) {
            if ($attempts == 1) { $sig = "-KILL"; }
            $running = 0;
            my @pids = `ps --no-headers -eo "pid cmd"`;
            foreach my $ps (@pids) {
              chomp($ps);
              $ps =~ s/^\s+//g;
              my $pid = $ps;
              $pid =~ s/\s.*$//g;
              my $cmd = $ps;
              $cmd =~ s/[0-9]+\s//g;
              if ($cmd =~ m/$DAEMON/ && $pid == $curPid) {
                `kill $sig $pid`;
                sleep(1);
                $running = 1;
                $attempts--;
              }
            }
          }
          print "$DAEMON stopped\n";
          if (-f $PIDFILE) {
            # -- in case the svc did not or could not clean up after itself
            unlink($PIDFILE);
          }
        } else {
          print "Wrong server: $PIDFILE ($DAEMON is running on $serverName not on $hostName)\n";
        }
    } else {
        print "Missing PID file: $PIDFILE (is $DAEMON running?)\n";
    }

}


########################################################################################
#
# post_status (target, filename, tracking)
#
# - given a target host, filename, filesize, and tracking number post_status will post 
#   an XML status message (PIN) to the specified MOC server
#
########################################################################################

sub post_status {

    my ($target, $filename, $filesize, $tracking) = @_;
    my $result = 0;

    print_log("Posting Status to $target", 0);

    my ($second, $minute, $hour, $day, $month, $year, $wday, $yday, $isdst) = localtime();
    $year = $year + 1900;
    $month++;

    my $outfile = new IO::File(">tracking.xml");
    my $writer = XML::Writer->new(OUTPUT => $outfile, DATA_MODE => 1, DATA_INDENT => 2);

    $writer->startTag('PIN');
    $writer->startTag('HDT');

    xprint($writer, "PINname", "TrackingLog");
    xprint($writer, "PINtype", "Data");
    xprint($writer, "PINclass", "NONE");

    $writer->startTag('PINdictionary', 'Version' => "1.1");
    $writer->characters("TrackingLog_Schema");
    $writer->endTag('PINdictionary');

    xprint($writer, "Source", "XXXXX");
    xprint($writer, "SourceLoc", "XX");
    xprint($writer, "SourceIP", "NONE");
    xprint($writer, "SourcePID", "14");
    xprint($writer, "PINdate", "$year-$month-$day");
    xprint($writer, "PINtime", "$hour:$minute:$second");

    $writer->endTag('HDT');
    $writer->startTag('tracking_log');

    xprint($writer, "tracking_number", "$tracking");
    xprint($writer, "timestamp", "$year-$month-$day" . "T$hour:$minute:$second");
    xprint($writer, "action", "MetaDataPush");
    xprint($writer, "comment", "INFO ON FILE");
    xprint($writer, "source", "XXXXX");
    xprint($writer, "source_location", "XX");
    xprint($writer, "aid", "");
    xprint($writer, "target_country", "");
    xprint($writer, "filename", "$filename");
    xprint($writer, "bytes", "$filesize");
    xprint($writer, "destination", "BPS");

    $writer->endTag('tracking_log');
    $writer->endTag('PIN');
    $writer->end();

    close($outfile);

    my $pinxml = "";
    open(XML, "<tracking.xml");
    while(<XML>) { $pinxml = $pinxml . $_; }
    close(XML);

    print_log("<pre>$pinxml</pre>", 2);

    my $user_agent = LWP::UserAgent->new(keep_alive=>1, timeout => 30);
    my $cookie_file = get_config("tmp_dir") . "/cookies_$$.txt";
    $user_agent->cookie_jar({ file => $cookie_file });

    my $request = POST "$target", Content => [ responseRequired => 'true', pin => $pinxml, ];
    my $response = $user_agent->request($request);

    if (-f $cookie_file) { unlink($cookie_file); }

}



########################################################################################
#
# print_vars()
#
# - print_vars will print the variables found in the provided CGI object
#
########################################################################################

sub print_vars {

    my ($cgi) = @_;
    my @vars = $cgi->param;
    print "<br><table><tr><th colspan=2 class=tableheader>CGI Variables</th></tr>\n";
    my $count = 0;
    foreach my $var (@vars) {
        $count++;
        my $class = get_row_type($count);
        print "<tr class=$class>";
        print "<td><font size=-2 color=green>$var</td><td></font><font color=black size=-2>" . Dumper($cgi->param("$var")) . "</font></td>";
        print "</tr>\n";
    }
    print "</table><br><br>\n";

    #print "<font size=-1 color=red>" . Dumper($cgi) . "</font>\n";

}




########################################################################################
# 
# print_env()
#
# - print_env will print all current environment variables in an HTML table
#
########################################################################################

sub print_env {

    my %vars = %ENV;
    print "<br><table><tr><th colspan=2 class=tableheader>Environment Variables</th></tr>\n";
    my $count = 0;
    foreach my $var (sort(keys(%vars))) {
        $count++;
        my $class = get_row_type($count);
        print "<tr class=$class><th class=label>$var</th><td class=lcell>" . $vars{$var} . "</font></td></tr>\n";
    }
    print "</table><br>\n";

}



########################################################################################
#
# print_logfile (logfile, message)
#
# - print_logfile will attempt to write the specified string to the provided log file
#
########################################################################################

sub print_logfile {

    my ($logfile, $message) = @_;

    my $datetime = get_time();

    open(LOG, ">>$logfile") || return 0;
    print LOG "$datetime $message\n";
    close(LOG);

    return 1;

}


########################################################################################
#
# print_log (message, level)
#
# - print the message to the log if current verbosity is equal to or less than the 
#   provided debugging level
#
########################################################################################

sub print_log {

    my ($message, $level) = @_;

    if (!defined($level)) { $level = 1; }
    if (!defined($configuration{daemon})) { $configuration{daemon} = 0; }
    if (!defined($configuration{verbosity})) { $configuration{verbosity} = 1; }

    if ($level <= $configuration{verbosity}) {
        my $message = get_time() . " |$level| $message\n";
        if ($configuration{daemon}) {
            my $logfile = $configuration{logfile};
            open(LOGFILE, ">>$logfile") || print STDOUT "ERROR: unable to open '$logfile' for writing";
            print LOGFILE $message;
            close(LOGFILE);
        } else {
            print STDOUT $message;
        }
    }
}


########################################################################################
#
# print_status(pidfile, name)
#
# print_status will print the status of the daemon to the standard out
#
########################################################################################

sub print_status {
    my ($PIDFILE, $DAEMON) = @_;

    my $running = 0;
    my $curPid;

    if (-f $PIDFILE && -s $PIDFILE > 0) {
        chomp($curPid = `cat $PIDFILE`);
        if ($curPid =~ /\:/) {
          ($curPid,undef,undef,undef,undef) = split(":",$curPid,5);
        }
        my @pids = `ps --no-headers -eo "pid cmd"`;
        foreach my $ps (@pids) {
            chomp($ps);
            $ps =~ s/^\s+//g;
            my $pid = $ps;
            $pid =~ s/\s.*$//g;
            my $cmd = $ps;
            $cmd =~ s/[0-9]+\s//g;
            if ($pid == $curPid && $cmd =~ m/$DAEMON/) {
                $running = 1;
                last;
            }
        }
    }

    if ($running) {
        print "$DAEMON is running (pid = $curPid)\n";
    } else {
        print "$DAEMON is not running\n";
    }
}


########################################################################################
#
# store_file (file, directory)
#
# - store_file will try to put the specified file into the specified directory, the
#   directory will be created if it does not exist
#
########################################################################################

sub store_file {

    my ($file, $directory) = @_;


    if (! -d $directory) { 
        print_log("Warning '$directory' doesn't exist -- creating it now", 2);
        chomp (my $result = `mkdir -p "$directory"`);
        if (! -d $directory) {
            print_log("ERROR: $result", 1);
            return;
        } 
    }
    print_log(" - STORING $file in $directory", 2);
    chomp(my $result = `mv -f $file $directory/ 2>&1`);

    # -- issue a warning if something went wrong
    if ($result || -e $file) { print_log("Warning: $result", 0); }


}


########################################################################################
#
# unix_timestamp (datestring)
#
# - this function will convert the provided date string to an epoch value
#
########################################################################################

sub unix_timestamp {

    my ($datestring) = @_;
    if (!$datestring) { return get_unix_date(0); }
    # Perform Extration/Conversion
    my ($date, $time) = split(/ /, $datestring);
    my ($_year, $_month, $_day) = split(/-/, $date);
    my ($_hour, $_min, $_sec) = split(/:/, $time);
    $_month--;
    my $timestamp = get_epoch($_sec, $_min, $_hour, $_day, $_month, $_year);
    return $timestamp;
}


###########################################################################################
#
# unix_timestamp_midas (datestring)
#
# - this function will return a midas formatted (using colons to delimit) date string
#
###########################################################################################

sub unix_timestamp_midas {

    my ($datestring) = @_;
    if (!$datestring) { return 0; }
    # Perform Extration/Conversion
    $datestring =~ s/::/ /g;
    my ($date, $time) = split(/ /, $datestring);
    my ($_year, $_month, $_day) = split(/:/, $date);
    my ($_hour, $_min, $_sec) = split(/:/, $time);
    $_month--;
    my $timestamp = get_epoch($_sec, $_min, $_hour, $_day, $_month, $_year);
    return $timestamp;
}


###########################################################################################
#
# xprint (writer, tag, value)
#
# - this function will print the specified value to the specified tag using the specified
#   xml writer object
#
###########################################################################################

sub xprint {
    my ($writer, $tag, $value) = @_;

    $writer->startTag($tag);
    $writer->characters($value);
    $writer->endTag($tag);
}


1;

__END__
# Below is stub documentation for your module. You'd better edit it!

=head1 NAME

ZUtils::Common - this is the core Perl module for the ZUtils framework

=head1 SYNOPSIS

  use ZUtils::Common;

=head1 DESCRIPTION

    contains common subroutines for the ZUtils framework

=head2 EXPORT

None by default.

=head1 SEE ALSO

    AWARE Systems Monitoring Package

=head1 AUTHOR


=head1 COPYRIGHT AND LICENSE

Copyright (C) 2005-2006

This library is free software; you can redistribute it and/or modify
it under the same terms as Perl itself, either Perl version 5.8.5 or,
at your option, any later version of Perl 5 you may have available.


=cut

