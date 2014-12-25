#!/usr/bin/perl -w

# ------------------------------------------------------------
# $Id: status.cgi,v 1.34 2008-05-05 17:30:45 aps1 Exp $
# $RCSfile: status.cgi,v $
# $Revision: 1.34 $
# $Date: 2008-05-05 17:30:45 $
# $Author: aps1 $
# $Name: not supported by cvs2svn $
# ------------------------------------------------------------

use strict;
use CGI;
use DBI;
use Time::HiRes qw(usleep ualarm gettimeofday tv_interval);
use HTML::Entities;
use ZUtils::Common;
use ZUtils::Aware;

# -------------------------------------------------------------------
# Initialize Configuration Settings
# -------------------------------------------------------------------
my $cfgfile = $ENV{ZUTILS_CFGFILE} || "/etc/aware/aware.cfg";
load_config($cfgfile);

# -------------------------------------------------------------------
# Begin Script
# -------------------------------------------------------------------
my $cgi = new CGI();

# -- retrieve & determine CGI parameters
my $ajax          = $cgi->param('ajax') || 0;
my $ajaxTimeout   = $cgi->param('ajaxTimeout') || 5;
my $ajaxEnabled   = $cgi->param('ajaxEnabled') || "no";
my $sortCol       = $cgi->param('sortCol') || "a.hostname";
my $sortOrder     = $cgi->param('sortOrder') || "asc";
my $profile_id    = $cgi->param('profile_id');
my $expandView    = $cgi->param('expandView') || 0;
my $lastUpdate = $cgi->param('lastUpdate') || unix_timestamp(get_date());
my $thisUpdate = unix_timestamp(get_date());

# -- figure out what, if anything should be expanded
my $expandCpu       = 0;
my $expandDiskIO    = 0;
my $expandDiskUsage = 0;
my $expandHost      = 0;
my $expandNet       = 0;
my $expandTemp      = 0;
my $expandMem       = 0;

if ($expandView == 1) { $expandCpu = 1; }
if ($expandView == 2) { $expandDiskIO = 1; }
if ($expandView == 3) { $expandDiskUsage = 1; }
if ($expandView == 4) { $expandHost = 1; }
if ($expandView == 5) { $expandNet = 1; }
if ($expandView == 6) { $expandTemp = 1; }
if ($expandView == 7) { $expandMem = 1; }
if ($expandView == 8) { $expandCpu = $expandDiskIO = $expandDiskUsage = $expandHost = $expandNet = $expandTemp = $expandMem = 1; }

# -- profile_id 0 is a special case
if (!defined($profile_id)) { $profile_id = -1; }

# -- handle the sorting and page view parameters
my $revSort = "asc";
if ($sortOrder eq $revSort) { $revSort = "desc"; }
my $sortStr = "$sortCol $sortOrder";

my $params = "sortOrder=$revSort&amp;profile_id=$profile_id&amp;ajaxEnabled=$ajaxEnabled&amp;expandView=$expandView";

# -- obtain a database connection
my $dbh = get_db_connection(0);

# -- intro/setup stuff 
my $t0 = [gettimeofday];
my $_name = "status.cgi";
my $_title = "Node Status";
if ($ajax) {
    print "Content-type: text/xml\n\n";
    print "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
    print "<ajax>\n";
    print_table();
    print "</ajax>\n";
    exit();
} else {
    print_header($_title, $_name, 1, $ajaxEnabled, $ajaxTimeout);
    print "<div id=wrapper><center><div id=mainsection>\n";
}


# -- build up a hash of known profiles
my %profiles;
my $sql = "select name, id from profile order by name";
my $sth = $dbh->prepare($sql) || print "ERROR: " . $dbh->errstr;
$sth->execute() || print "ERROR: " . $dbh->errstr;
while (my @row = $sth->fetchrow()) { $profiles{$row[0]} = $row[1]; }
    

# -- call print_table() to display the results
print_filters();
print "<center><hr width=\"500\"/></center>";
print_table();
print "</div></center></div>\n";

if ($ajaxEnabled eq "yes") {
    print "<script language=javascript>schedule_update('$_name')</script>\n";
}
print "</body></html>\n";

exit(0);


#----------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------


sub print_filters {
    
    # -- print the selection filters table
    print "<form action=\"$_name\" id=ajaxParams method=\"get\">\n";
    print "<table>\n";
    print "<input type=\"hidden\" name=\"sortCol\" value=\"$sortCol\"/>\n";
    print "<input type=\"hidden\" name=\"sortOrder\" value=\"$sortOrder\"/>\n";
    print "<input id=\"lastUpdate\" type=\"hidden\" name=\"lastUpdate\" value=\"$lastUpdate\">\n";
    print "<input id=\"ajaxEnabled\" type=\"hidden\" name=\"ajaxEnabled\" value=\"$ajaxEnabled\"/>\n";
    print "<tr>\n";
    print "<th>Show Profile:</th>\n";
    print "<td><select onChange=\"document.forms[0].submit();\" name=\"profile_id\">\n";
    print "<option value=\"-1\">All</option>\n";
    foreach my $profile (sort(keys(%profiles))) {
        my $selected = "";
        if ($profile_id eq $profiles{$profile}) { $selected = "selected=\"selected\""; }
        print "<option value=\"$profiles{$profile}\" $selected>$profile</option>\n";
    }
    print "</select>\n";
    print "</td>\n";
    
    print "<th>Expand:</th>\n";
    print "<td><select onChange=\"document.forms[0].submit();\" name=\"expandView\">\n";
    print "<option value=\"0\">None</option>\n";
    my @options = ('CPU', 'Disk I/O', 'Disk Usage', 'Host', 'Network I/O', 'Temperatures', 'Memory', 'All');
    my @values = (1, 2, 3, 4, 5, 6, 7, 8);
    for (my $i = 0; $i <= $#options; $i++) {
        my $selected = "";
        if ($expandView eq $values[$i]) { $selected = "selected=\"selected\""; }
        print "<option value=\"$values[$i]\" $selected>$options[$i]</option>\n";
    }
    print "</select>\n";
    print "</td>\n";

    print "</tr>\n";
    print "</table>\n";
    print "</form>\n";
    
}
    
sub print_table {

    # -- build up the query we are going to execute
    my $sql = "select a.hostid, a.ipaddr, a.macaddr, a.procs, a.uptime, 
        unix_timestamp(now()) - unix_timestamp(a.updated) reported, a.alert, a.hostname, a.temperature, a.sysload, 
        a.maxdisk, b.mount, b.pct, c.name, a.memory, a.os, a.id, a.ping, a.poll, a.iloaddr, b.ipct, 
        a.bytesIn / 1000, a.bytesOut / 1000, a.tx / (1000 * 1024), a.rx / (1000 * 1024), a.profile_id, a.arch
        from profile c, node a 
        left join filesystem b on a.id = b.hostid and a.maxdisk = b.device and a.maxpart = b.partition
        where c.id = a.profile_id and a.online = 1";
    if ($profile_id >= 0) { $sql = "$sql and a.profile_id = $profile_id"; }
    if ($ajax) { $sql = "$sql and a.updated > from_unixtime($lastUpdate)"; }
    $sql = "$sql order by $sortStr, a.hostname asc";
    
    # -- prepare and execute the query
    $sth = $dbh -> prepare($sql) || print "<p class=alert>SQL Error ($sql): " . $dbh->errstr . "</p>\n";
    $sth -> execute || print "<p class=alert>Database Error: " . $dbh->errstr . "</p>\n";
    print "<!-- $sql -->\n";
    

    if (!$ajax) {
        print "<table>\n";
        print "<tr><th colspan=\"100%\" class=\"tableheader\">Node Status Summary</th></tr>\n";
        print "<tr>";
        print "<th colspan=\"2\"><a class=\"sortCol\" href=\"$_name?sortCol=a.hostname&amp;$params\">Node</a></th>\n";
        if ($expandHost) {
            print "<th ><a class=\"sortCol\" href=\"$_name?sortCol=a.os&amp;$params\">Kernel</a></th>\n";
            print "<th ><a class=\"sortCol\" href=\"$_name?sortCol=a.arch&amp;$params\">Arch</a></th>\n";
        }
        print "<th ><a class=\"sortCol\" href=\"$_name?sortCol=c.name&amp;$params\">Profile</a></th>\n";
        print "<th ><a class=\"sortCol\" href=\"$_name?sortCol=a.updated&amp;$params\">Updated</a></th>\n";
        print "<th ><a class=\"sortCol\" href=\"$_name?sortCol=a.ping&amp;$params\">Ping</a></th>\n";
        print "<th ><a class=\"sortCol\" href=\"$_name?sortCol=a.poll&amp;$params\">Poll</a></th>\n";
        print "<th ><a class=\"sortCol\" href=\"$_name?sortCol=a.procs&amp;$params\"># Procs</a></th>\n";
        print "<th ><a class=\"sortCol\" href=\"$_name?sortCol=a.uptime&amp;$params\">Uptime</a></th>\n";
        #print "<th ><a class=\"sortCol\" href=\"$_name?sortCol=a.alert&amp;$params\">Alerts</a></th>\n";
        print "<th colspan=\"2\"><a class=\"sortCol\" href=\"$_name?sortCol=a.sysload&amp;$params\">CPU Load</a></th>\n";
        if ($expandDiskIO) { print "<th colspan=\"1\">Disk</th>\n"; }
        print "<th colspan=1><a class=sortCol title=\"Bytes read from disk (in MB/s)\"";
        print " href=$_name?sortCol=a.bytesIn&$params>READ</a></th>";
        print "<th colspan=1><a class=sortCol title=\"Bytes written to disk (in MB/s)\"";
        print " href=$_name?sortCol=a.bytesOut&$params>WRITE</a></th>\n";
        if ($expandNet) { print "<th colspan=\"1\">Device</th>\n"; }
        print "<th colspan=1><a class=sortCol title=\"Bytes transmitted across the network (in MB/s)\"";
        print " href=$_name?sortCol=a.tx&$params>TX</a></th>\n";
        print "<th colspan=1><a class=sortCol title=\"Bytes received over the network (in MB/s)\"";
        print " href=$_name?sortCol=a.rx&$params>RX</a></th>\n";
        print "<th colspan=\"2\"><a class=\"sortCol\" href=\"$_name?sortCol=a.temperature&amp;$params\">Temp</a></th>\n";
        print "<th ><a class=\"sortCol\" href=\"$_name?sortCol=b.mount&amp;$params\">Mount</a></th>\n";
        print "<th ><a class=\"sortCol\" href=\"$_name?sortCol=b.pct&amp;$params\">Blocks</a></th>\n";
        print "<th ><a class=\"sortCol\" href=\"$_name?sortCol=b.ipct&amp;$params\">Inodes</a></th>\n";
        print "<th colspan=\"2\"><a class=\"sortCol\" href=\"$_name?sortCol=a.memory&amp;$params\">Memory</a></th>\n";
        print "</tr>\n";
    }
    
    my $rowcount = 0;
    my $anodes = 0;
    while (my @row = $sth -> fetchrow_array) {
        $rowcount++;

        my $hostid      = $row[0];
        my $ipaddr      = $row[1];
        my $macaddr     = $row[2];
        my $procs       = $row[3];
        my $uptime      = human_time($row[4]);
        my $lastUpdate  = $row[5];
        #my $alert       = $row[6] || 0;
        my $hostname    = $row[7];
        my $temp        = $row[8];
        my $sysload_val = $row[9] || 0;
        my $diskidx     = $row[10];
        my $diskmnt     = $row[11] || "";
        my $diskpct     = $row[12] || 0;
        my $profile     = $row[13];
        my $memory      = $row[14];
        my $os          = $row[15];
        my $id          = $row[16];
        my $pingResult  = $row[17] || 0;
        my $pollResult  = $row[18] || 0;
        my $iloaddr     = $row[19] || "";
        my $inodepct    = $row[20] || 0;
        my $bytesIn     = sprintf("%.2f", $row[21]);
        my $bytesOut    = sprintf("%.2f", $row[22]);
        my $tx          = sprintf("%.2f", $row[23]);
        my $rx          = sprintf("%.2f", $row[24]);
        my $profile_id  = $row[25];
        my $arch        = $row[26] || "";

        my $reported = human_time($lastUpdate);

        $hostname =~ s/\..*//g;
        
        my $tdclass = "";
        my $hl = "";
        my $rowtype = get_row_type($rowcount);
        
        my $ping = "OK";    
        my $poll = "OK";
        my $sysload = $sysload_val . "%";

        # -- check ping time against defined thresholds 
        if ($pingResult > get_profile_threshold($dbh, $profile, "missedpings")) { 
            $ping = "<font class=\"alert\">FAILED</font>"; 
            $tdclass = " class=\"hlc\""; 
            $hl = "hl";
            $anodes++; 
        }

        # -- check poll time against profile threshold 
        if ($pollResult > get_profile_threshold($dbh, $profile, "missedpolls")) { 
            $poll = "<font class=\"alert\">FAILED</font>"; 
            $tdclass = " class=\"hlc\""; 
            $hl = "hl";
            $anodes++;
        } 

        # -- check update time against profile threshold 
        if ($lastUpdate > get_profile_threshold($dbh, $profile, "maxreport")) { 
            $reported = "<font class=\"alert\">$reported</font>"; 
            $tdclass = " class=\"hlc\""; 
            $hl = "hl";
            $anodes++; 
        }

        # -- check # of procs against profile threshold 
        if ($procs > get_profile_threshold($dbh, $profile, "maxprocs")) { 
            $procs = "<font class=\"alert\">$procs</font>"; 
            $tdclass = " class=\"hlc\""; 
            $hl = "hl";
            $anodes++;
        }

        # -- check temperature against profile threshold 
        if ($temp && $temp > get_profile_threshold($dbh, $profile, "maxtemp")) { 
            $temp = "<font class=\"alert\">$temp&deg;C</font>"; 
            $tdclass = " class=\"hlc\""; 
            $hl = "hl";
            $anodes++;
        } elsif ($temp) {
            $temp .= "&deg;C";
        } else {
            $temp = "";
        }

        # -- check disk value against profile threshold 
        if ($diskpct > get_profile_threshold($dbh, $profile, "maxdisk")) { 
            $diskpct = "<font class=\"alert\">$diskpct%</font>"; 
            $tdclass = " class=\"hlc\""; 
            $hl = "hl";
            $anodes++;
        } else {
            $diskpct .= "%";
        }

        # -- check inode value against profile threshold 
        if ($inodepct> get_profile_threshold($dbh, $profile, "maxinodes")) { 
            $inodepct = "<font class=\"alert\">$inodepct%</font>"; 
            $tdclass = " class=\"hlc\""; 
            $hl = "hl";
            $anodes++;
        } else {
            $inodepct .= "%";
        }

        # -- check memory value against profile threshold 
        if ($memory > get_profile_threshold($dbh, $profile, "maxmem")) { 
            $memory = "<font class=\"alert\">$memory\%</font>"; 
            $tdclass = " class=\"hlc\""; 
            $hl = "hl";
            $anodes++;
        } else {
            $memory .= "%";
        }

        # -- check system load value against profile threshold 
        if ($sysload_val > get_profile_threshold($dbh, $profile, "maxload")) { 
            $sysload = "<font class=\"alert\">$sysload_val%</font>\n"; 
            $tdclass = " class=\"hlc\""; 
            $hl = "hl";
            $anodes++;
        }


        #
        #
        # -- build the current row cells    
        #
        my @cells;
        my %contents;
        my $ccount = 1;

        push(@cells, "<td id=\"$id-0\"$tdclass>$rowcount</td>");
        push(@cells, "<td id=\"$id-$ccount\" class=\"l$hl\"><a href=\"node_tabs.cgi?hostid=$id\">$hostname</a></td>");
        $contents{$ccount++} = "<a href=\"node_tabs.cgi?hostid=$id\">$hostname</a>";
        if ($expandHost) {
            push(@cells, "<td id=\"$id-$ccount\"$tdclass>$os</td>");
            $contents{$ccount++} = $os;
            push(@cells, "<td id=\"$id-$ccount\"$tdclass>$arch</td>");
            $contents{$ccount++} = $arch;
        }
        push(@cells, "<td id=\"$id-$ccount\"$tdclass><a href=\"profile_status.cgi?profile_id=$profile_id\">$profile</a></td>");
        $contents{$ccount++} = "<a href=\"profile_status.cgi?profile_id=$profile_id\">$profile</a>";
        push(@cells, "<td id=\"$id-$ccount\" class=\"r$hl\">$reported</td>");
        $contents{$ccount++} = $reported;
        push(@cells, "<td id=\"$id-$ccount\"$tdclass>$ping</td>");
        $contents{$ccount++} = $ping;
        push(@cells, "<td id=\"$id-$ccount\"$tdclass>$poll</td>");
        $contents{$ccount++} = $poll;
        push(@cells, "<td id=\"$id-$ccount\" class=\"r$hl\"><a href=\"process.cgi?hostid=$id\">$procs</a></td>");
        $contents{$ccount++} = "<a href=\"process.cgi?hostid=$id\">$procs</a>";
        push(@cells, "<td id=\"$id-$ccount\" class=\"r$hl\"><a href=\"uptime.cgi?hostid=$id\" nowrap>$uptime</a></td>");
        $contents{$ccount++} = $uptime;

        # -- expand cpu view
        if ($expandCpu) {
            my $sql = "select user, system, iowait, nice, irq, softirq, idle from sysload where hostid = $id order by updated desc limit 1";
            my $sth = $dbh->prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
            $sth->execute() || print "Database Error: " . $dbh->errstr . "\n";
            my @row = $sth->fetchrow();

            push(@cells, "<td id=\"$id-$ccount\" class=\"r$hl\">User<br>System<br>IOWait<br>Nice<br>IRQ<br>SIRQ<br>Idle</td>");
            $contents{$ccount++} = "User<br>System<br>IOWait<br>Nice<br>IRQ<br>SIRQ<br>Idle";
            
            
            my $td = "<td id=\"$id-$ccount\" colspan=\"1\" class=\"r$hl\">";
            my $inner = "";

            for (my $j = 0; $j < 7; $j++) {
                my $sysload_val = $row[$j]; 
                $inner .= "$sysload_val% ";
                my $ticks = 10;
                for (my $i = 0; $i < $sysload_val / 10; $i++) {
                    $inner .= "<img src=\"images/slice_$j.png\"/>";
                    $ticks--;
                }
                while ($ticks > 0) {
                    $inner .= "<img src=\"images/rbar.png\"/>";
                    $ticks--;
                }
                $inner .= "<br>\n";
            }
            $td .= "$inner</td>";
            push(@cells, $td);
            $contents{$ccount++} = $inner;

            $sth->finish();
        } else {
            push(@cells, "<td id=\"$id-$ccount\" colspan=\"1\" class=\"r$hl\">$sysload</td>");
            $contents{$ccount++} = $sysload;

            my $td = "<td id=\"$id-$ccount\" colspan=\"1\" class=\"r$hl\" nowrap>";
            my $inner = "";
            my $ticks = 10;
            for (my $i = 0; $i < $sysload_val / 10; $i++) {
                $inner .= "<img src=\"images/gslice.png\"/>";
                $ticks--;
            }
            while ($ticks > 0) {
                $inner .= "<img src=\"images/rbar.png\"/>";
                $ticks--;
            }
            $td .= "$inner</td>";
            push(@cells, $td);
            $contents{$ccount++} = $inner;
        }


        if ($expandDiskIO) {

            my $sql = "select device, max(updated) from filesystem where hostid = $id group by device order by device";
            my $sth = $dbh->prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
            $sth->execute() || print "Database Error: " . $dbh->errstr . "\n";
            my $devStr = "";
            my $biStr = "";
            my $boStr = "";
            while (my @row = $sth->fetchrow()) {

                my $device = $row[0];
                my $updated = $row[1];
                $devStr .= "$device<br>";

                my $sql = "select bi/1024, bo/1024 from diskload where hostid = $id and device = '$device' and updated = '$updated'";
                my $isth = $dbh->prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
                $isth->execute() || print "Database Error: " . $dbh->errstr . "\n";

                my @irow = $isth->fetchrow();
                my $bi = sprintf("%.2f", $irow[0]);
                my $bo = sprintf("%.2f", $irow[1]);
                $biStr .= "$bi<br>";
                $boStr .= "$bo<br>";

            }

            push(@cells, "<td id=\"$id-$ccount\" class=\"r$hl\">$devStr</td>");
            $contents{$ccount++} = $devStr;

            push(@cells, "<td id=\"$id-$ccount\" class=\"r$hl\">$biStr</td>");
            $contents{$ccount++} = $biStr;

            push(@cells, "<td id=\"$id-$ccount\" class=\"r$hl\">$boStr</td>");
            $contents{$ccount++} = $boStr;

        } else {

            push(@cells, "<td id=\"$id-$ccount\" class=\"r$hl\">$bytesIn</td>");
            $contents{$ccount++} = $bytesIn;

            push(@cells, "<td id=\"$id-$ccount\" class=\"r$hl\">$bytesOut</td>");
            $contents{$ccount++} = $bytesOut;
        }

        if ($expandNet) {

            my $sql = "select device, max(updated) from nic where hostid = $id group by device order by device";
            my $sth = $dbh->prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
            $sth->execute() || print "Database Error: " . $dbh->errstr . "\n";
            my $devStr = "";
            my $rxStr = "";
            my $txStr = "";
            while (my @row = $sth->fetchrow()) {

                my $device = $row[0];
                my $updated = $row[1];
                $devStr .= "$device<br>";

                my $sql = "select rx/1000, tx/1000 from netload where hostid = $id and device = '$device' and updated = '$updated'";
                my $isth = $dbh->prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
                $isth->execute() || print "Database Error: " . $dbh->errstr . "\n";

                my @irow = $isth->fetchrow();
                my $rx = sprintf("%.2f", $irow[0]);
                my $tx = sprintf("%.2f", $irow[1]);
                $rxStr .= "$rx<br>";
                $txStr .= "$tx<br>";

            }

            push(@cells, "<td id=\"$id-$ccount\" class=\"r$hl\">$devStr</td>");
            $contents{$ccount++} = $devStr;

            push(@cells, "<td id=\"$id-$ccount\" class=\"r$hl\">$txStr</td>");
            $contents{$ccount++} = $txStr;

            push(@cells, "<td id=\"$id-$ccount\" class=\"r$hl\">$rxStr</td>");
            $contents{$ccount++} = $rxStr;

        } else {

            push(@cells, "<td id=\"$id-$ccount\" class=\"r$hl\">$tx</td>");
            $contents{$ccount++} = $tx;

            push(@cells, "<td id=\"$id-$ccount\" class=\"r$hl\">$rx</td>");
            $contents{$ccount++} = $rx;

        }

        # -- expand temperature details for this node
        if ($expandTemp) {
            my %temps;
            my $sql = "select label, reading from sensor, sensor_reading where sensor.hostid = $id and sensor.id = sensor_reading.sensor_id and sensor_reading.hostid = $id order by sensor_reading.updated desc limit 32";
            my $sth = $dbh->prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
            $sth->execute() || print "Database Error: " . $dbh->errstr . "\n";
            while (my @row = $sth->fetchrow()) {
                # -- skip empties
                if (!$row[1]) { next; }

                # -- skip sensors we've already seen
                if (defined($temps{$row[0]})) { last; }    

                # -- report the rest
                $temps{$row[0]} = $row[1];
            }

            #my @sorted = sort { $temps{$b} <=> $temps{$a} } keys %temps;

            my $td = "<td id=\"$id-$ccount\" class=\"r$hl\">";
            my $inner = "";
            foreach my $sort (sort(keys(%temps))) { $inner .= "$sort<br>"; }
            $td .= "$inner</td>";
            push(@cells, $td);
            $contents{$ccount++} = $inner;

            $td = "<td id=\"$id-$ccount\" class=\"r$hl\">";
            $inner = "";
            foreach my $sort (sort(keys(%temps))) { $inner .= "$temps{$sort}&deg;C<br>"; }
            $td .= "$inner</td>\n";
            push(@cells, $td);
            $contents{$ccount++} = $inner;

            $sth->finish();
        } else {
            push(@cells, "<td id=\"$id-$ccount\" colspan=\"2\" class=\"r$hl\">$temp</td>");
            $contents{$ccount++} = $temp;
        }
    
    
        # -- expand disk view
        if ($expandDiskUsage) {
            my $sql = "select mount, pct, ipct from filesystem where hostid = $id order by mount";
            my $sth = $dbh->prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
            $sth->execute() || print "Database Error: " . $dbh->errstr . "\n";
            my @mt;
            my @bp;
            my @ip;
            while (my @row = $sth->fetchrow()) {
                push(@mt, $row[0]);
                push(@bp, $row[1]);
                push(@ip, $row[2]);
            } 
    
            my $td = "<td id=\"$id-$ccount\"class=\"r$hl\">";
            my $inner = "";
            for (my $i = 0; $i <= $#mt; $i++) { $inner .= "$mt[$i]<br>"; }
            $td .= "$inner</td>\n";
            push(@cells, $td);
            $contents{$ccount++} = $inner;

            $td = "<td id=\"$id-$ccount\" class=\"r$hl\">";
            $inner = "";
            for (my $i = 0; $i <= $#bp; $i++) { $inner .= "$bp[$i]%<br>"; }
            $td .= "$inner</td>\n";
            push(@cells, $td);
            $contents{20} = $inner;

            $td = "<td id=\"$id-$ccount\" class=\"r$hl\">";
            $inner = "";
            for (my $i = 0; $i <= $#ip; $i++) { $inner .= "$ip[$i]%<br>"; }
            $td .= "$inner</td>\n";
            push(@cells, $td);
            $contents{$ccount++} = $inner;

            $sth->finish();

        } else {
            push(@cells, "<td id=\"$id-$ccount\" class=\"l$hl\">$diskmnt</td>");
            $contents{$ccount++} = $diskmnt;
            push(@cells, "<td id=\"$id-$ccount\" class=\"r$hl\">$diskpct</td>");
            $contents{$ccount++} = $diskpct;
            push(@cells, "<td id=\"$id-$ccount\" class=\"r$hl\">$inodepct</td>");
            $contents{$ccount++} = $inodepct;

        }

        # -- expand memory view
        if ($expandMem) {
            my $sql = "select used, free, cached, buffers, usedSwap, freeSwap from memory 
                where hostid = $id order by updated desc limit 1";
            my $sth = $dbh->prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
            $sth->execute() || print "Database Error: " . $dbh->errstr . "\n";
            my @row = $sth->fetchrow();
            push(@cells, "<td id=\"$id-$ccount\" class=\"r$hl\">Used<br>Free<br>Cached<br>Buffers<br>UsedSwap<br>FreeSwap</td>");
            $contents{$ccount++} = "Used<br>Free<br>Cached<br>Buffers<br>UsedSwap<br>FreeSwap";
            push(@cells, "<td id=\"$id-$ccount\" class=\"r$hl\">$memory<br>$row[1] MB<br>$row[2] MB<br>$row[3] MB<br>$row[4] MB<br>$row[5] MB</td>");
            $contents{$ccount++} = "$memory<br>$row[1] MB<br>$row[2] MB<br>$row[3] MB<br>$row[4] MB<br>$row[5] MB";
            $sth->finish();
        } else {
            push(@cells, "<td id=\"$id-$ccount\" colspan=\"2\" class=\"r$hl\">$memory</td>");
            $contents{$ccount++} = "$memory";
        }


        ##
        ##
        ## Figure out how to format and return the cell data
        ##
        ##

        if (!$ajax) {

            print "<tr class=\"$rowtype\" id=\"row_$rowcount\">\n";
            print @cells;
            print "</tr>\n";

        } else {
            
            foreach my $key (sort(keys(%contents))) {
                my $content = $contents{$key};
                print "<update id=\"$id-$key\" attr=\"innerHTML\">\n";
                print encode_entities($content);
                print "</update>\n";

            }

    
        }
    } 


    ##
    ##
    ## Figure out how to format and return the overall page status
    ##
    ##

    my $message = "Updated <font class=\"message\">$rowcount</font> node(s)";
    my $interval = sprintf("%0.3f", tv_interval $t0, [gettimeofday]);

    if ($ajax) {
        print "<update id=\"ajaxStatusMessage\" attr=\"innerHTML\">";
        print encode_entities($message);
        print "</update>\n";

        print "<update id=\"queryTime\" attr=\"innerHTML\">";
        print encode_entities("$interval second(s)");
        print "</update>\n";

        print "<update id=\"lastUpdate\" attr=\"value\">";
        print encode_entities($thisUpdate);
        print "</update>\n";


    } else {
        if (!$rowcount) {
            print "<tr class=\"odd\"><td class=\"cell\" colspan=\"23\">No Node(s) Available</td></tr>";
        }
        print "<tr><th id=\"queryTime\" class=\"footer\" align=\"center\" colspan=\"23\">$interval second(s)</th></tr>";
        print "</table>\n";    
        print "<script language=\"javascript\">update_status('$message')</script>\n";
    }

    $sth->finish();
    $dbh->disconnect();

}

