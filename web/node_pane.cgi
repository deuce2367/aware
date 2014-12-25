#!/usr/bin/perl -w

# ------------------------------------------------------------
# $Id: node_pane.cgi,v 1.18 2010-05-04 16:55:02 xxxxxx Exp $
# $RCSfile: node_pane.cgi,v $
# $Revision: 1.18 $
# $Date: 2010-05-04 16:55:02 $
# $Author: xxxxxx $
# $Name: not supported by cvs2svn $
# ------------------------------------------------------------

use strict;
use CGI;
use DBI;
use URI::URL qw(url);
use GD::Graph::lines;
use GD::Graph::lines3d;
use GD::Graph::bars;
use GD::Graph::bars3d;
use GD::Graph::area;
use GD::Graph::pie3d;
use Time::HiRes qw(usleep ualarm gettimeofday tv_interval);
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
my $t0 = [gettimeofday];
my $queries = 0;

my $_title = "Node Disk I/O";
my $_name = "node_diskio.cgi";

my $hostid = $cgi->param('hostid') || 0;
my $archive = $cgi->param('archive') || 0;
my $daysAgo = $cgi->param('daysAgo') || 0;
my $window = $cgi->param('window') || 24;
my $tab = $cgi->param('tab') || "summary";
my $message = "OK";
my %hostID;
my @hosts;

my $all = 0;
if ($tab eq "combined") { $all = 1; }

# determine graph dimensions
my $x = get_config("graph_width");
my $y = get_config("graph_height");


print_header_simple($_title, $_name, 0);
my $dbh = get_db_connection(0);
if (!defined($dbh)) {
    print "<p class=alert>Unable to connect to DB</p>\n";
    exit();
}

print "<script type=\"text/javascript\" src=\"tabs.js\"></script>\n";
print "<script language=javascript>update_element_value('tab', '$tab')</script>\n";
print "<div id=tabpane><center>";
main();
print "</center></div>\n";
print "</body></html>\n";

$dbh->disconnect();

exit(0);


sub main {

    my @plots;
    my $t1 = [gettimeofday];

    # -- let's first ensure that we have the appropriate permissions set
    my $_htdoc = get_config("aware_home");
    my $imageDir = $_htdoc."/web/images/tmp/";
    if (!-e $imageDir || !-w $imageDir) {
        chomp(my $username = `whoami`);
        print "ERROR: cannot write files to '$imageDir' (ensure that directory exists and is writable by user: $username)\n";
        return;
    }

    my $sql = "select a.hostname, a.numcpu, b.name from node a, profile b where a.id = '$hostid' and a.profile_id = b.id";
    my $sth = $dbh -> prepare($sql) || die "Error occurred preparing SQL: " . $dbh->errstr;
    $sth -> execute || die "Error occurred processing SQL: " . $dbh->errstr; $queries++;
    my @row = $sth->fetchrow();
    my $hostname = $row[0];
    my $cpucount = $row[1];
    my $profile = $row[2];
    $sth->finish();
    print "<table>\n";
    print "<tr><th colspan=14 class=tableheader>$hostname</th></tr>\n";

    my $endTime = unix_timestamp(get_date()) - ($daysAgo * 86400);
    my $image = "images/tmp/$hostname";
    if ($archive) {

        my $datestring = get_date(-$daysAgo);

        $datestring =~ s/\s.*//g;
        $endTime = $datestring;
        $endTime .= " 23:59:59";
        $endTime = unix_timestamp($endTime);

        $datestring =~ s/-//g;

        my $archDir = get_config("aware_home")."/web/archive/$datestring";

        if (!-d $archDir) {
            mkdir($archDir) || die "ERROR: could not find/create directory: $archDir";
            chmod(0777, $archDir);
            mkdir("$archDir/images") || die "ERROR: could not find/create directory: $archDir/images";
            chmod(0777, "$archDir/images");
        }
        $image = "archive/$datestring/images/$hostname-$profile-$datestring";
    }
    #print "$image<br>\n";
    #print "Start Time: $endTime, Window = $window\n";

    # -- plot the appropriate subsystems
    if ($tab eq "summary" || $all) {
        push(@plots, graph_sysload($dbh, $hostid, "Host", $x, $y, $endTime, $window, \$queries, $image)); 
        print "<!-- PLOTTED $plots[$#plots] -->\n";
    }


    if ($tab eq "memory" || $all) {

        push(@plots, graph_memory($dbh, $hostid, $x, $y, $endTime, $window, \$queries, $image)); 
        print "<!-- PLOTTED $plots[$#plots] -->\n";
        push(@plots, graph_shmemory($dbh, $hostid, $x, $y, $endTime, $window, \$queries, $image)); 
        print "<!-- PLOTTED $plots[$#plots] -->\n";
    }


    if ($tab eq "utilization" || $all) {
        push(@plots, graph_cpuload($dbh, $hostid, "Host", $x, $y, $endTime, $window, \$queries, $image)); 
        print "<!-- PLOTTED $plots[$#plots] -->\n";

        my $sql = "select distinct(device) from diskload where hostid = $hostid and updated > now() - 60*60 and device not like '/dev/md%' order by device";
        my $sth = $dbh -> prepare($sql) || die "Error occurred preparing SQL: " . $dbh->errstr;
        $sth -> execute || die "Error occurred processing SQL: " . $dbh->errstr; $queries++;
        while (my @row = $sth->fetchrow()) {
            my $device = $row[0];
            push(@plots, graph_device_utilization($dbh, $hostid, $device, $x, $y, $endTime, $window, \$queries, $image)); 
        }
    } 


    if ($tab eq "diskio" || $all) {

        push(@plots, graph_sysio($dbh, $hostid, "Host", $x, $y, $endTime, $window, \$queries, $image)); 
        push(@plots, graph_diskload($dbh, $hostid, $x, $y, $endTime, $window, \$queries, $image)); 
        push(@plots, graph_device_svctimes($dbh, $hostid, $x, $y * 1.5, $endTime, $window, \$queries, $image)); 
    } 


    if ($tab eq "network" || $all) {
        push(@plots, graph_netload($dbh, $hostid, "Host", $x, $y, $endTime, $window, \$queries, $image)); 
        push(@plots, graph_network_combined($dbh, $hostid, $x, $y, $endTime, $window, \$queries, $image)); 

        my $sql = "select device, vlan from nic where hostid = $hostid order by device, vlan";
        my $sth = $dbh -> prepare($sql) || die "Error occurred preparing SQL: " . $dbh->errstr;
        $sth -> execute || die "Error occurred processing SQL: " . $dbh->errstr; $queries++;
        while (my @row = $sth->fetchrow()) {
            my $device = $row[0];
            my $vlan = $row[1];
            push(@plots, graph_network_device($dbh, $hostid, $device, $vlan, "Host", $x, $y, $endTime, $window, \$queries, $image)); 
        }
    } 


    if ($tab eq "procs" || $all) {
        push(@plots, graph_procs($dbh, $hostid, "Host", $x, $y, $endTime, $window, \$queries, $image)); 
    } 


    if ($tab eq "temperature" || $all) {
        push(@plots, graph_temperature($dbh, $hostid, $x, $y, $endTime, $window, $cpucount, \$queries, $image)); 
        push(@plots, graph_power($dbh, $hostid, $x, $y, $endTime, $window, $cpucount, \$queries, $image)); 
        push(@plots, graph_fans($dbh, $hostid, $x, $y, $endTime, $window, $cpucount, \$queries, $image)); 
    } 
    

    # -- the main information table

    if ($tab eq "summary" || $all) {
        my $pie_x = get_config("pie_graph_width");
        my $pie_y = get_config("pie_graph_height");
    
        my $sql = "select a.hostname, a.hostid, a.ipaddr, a.macaddr, a.procs, a.uptime, a.updated, a.os, a.iloaddr, a.ilomac, 
            c.name, count(b.mount), a.description, a.notes, a.sysload, a.memory, a.temperature, a.maxdisk, a.ping, a.online, 
            a.numcpu, a.cpu_type, a.profile_id 
        from node a, filesystem b, profile c where a.profile_id = c.id and a.id = b.hostid and a.id = '$hostid' group by a.id";

        print "<!-- $sql -->\n";
    
        my $sth = $dbh -> prepare($sql) || die "Error occurred preparing SQL: " . $dbh->errstr;
        $sth -> execute || die "Error occurred processing SQL: " . $dbh->errstr; $queries++;
        
        my @row = $sth->fetchrow();
        my $uptime = human_time($row[5]);
        my $hostname = $row[0];
        my $serial = $row[1];
        my $ipaddr = $row[2];
        my $macaddr = $row[3];
        my $procs = $row[4];
        my $updated = $row[6];
        my $os = $row[7];
        my $iloaddr = $row[8];
        my $ilomac  = $row[9];
        my $profile = $row[10];
        my $fscount = $row[11];
        my $description = $row[12] || "";
        my $notes = $row[13] || "";
        my $sysload = $row[14];
        my $memload = $row[15];
        my $temperature = $row[16];
        my $maxdisk = $row[17];
        my $ping = $row[18];
        my $poll = $row[19];
        my $cpucount = $row[20];
        my $cpu_type = $row[21];
        my $profile_id = $row[22];
    
        if ($ping) { $ping = "FAIL"; } else { $ping = "OK"; }
        if (!$poll) { $poll = "FAIL"; } else { $poll = "OK"; }
    
        my $isth = $dbh->prepare("select count(*) from alert where display = 1 and hostid = $hostid");
        $isth->execute(); $queries++;
        my @irow = $isth->fetchrow();
        my $alerts = $irow[0] || 0;
    
        print "<tr class=even><th colspan=14 class=header>Details</th></tr>";
    
        print "<tr class=even>";
        print "<th class=label colspan=2>Hostname:</th>\n";
        print "<td class=lcell colspan=2>$hostname</td>\n";
        print "<th class=label colspan=3>Profile:</th><td class=lcell colspan=3>";
        #print "<a href=profile_status.cgi?profile_id=$profile_id>$profile</a></td></tr>\n";
        print "$profile</td>";
        print "<th class=label colspan=2>Hostid:</th><td class=lcell colspan=2>$serial</td>\n";
        print "</tr>\n";
    
        print "<tr class=odd>";
        print "<th class=label colspan=2>Kernel:</th><td class=lcell colspan=2>$os</td>\n";
        print "<th class=label colspan=3>IP Address:</th><td class=lcell colspan=3>$ipaddr</td>\n";
        print "<th class=label colspan=2>MAC Address:</th><td class=lcell colspan=2>$macaddr</td>\n";
        print "</tr>\n";
    
        print "<tr class=even>";
        print "<th class=label colspan=2>Last Update Received:</th><td class=lcell colspan=2>$updated</td>\n";
        print "<th class=label colspan=3>Uptime:</th><td class=lcell colspan=3>$uptime</td>\n";
        print "<th class=label colspan=2>Alerts:</th><td class=lcell colspan=2><a onClick=\"openWin('popup', 1024, 700);\" target=popup href=alert.cgi?displayHost=$hostid&popup=1>$alerts</a></td>\n";
        print "</tr>\n";
    
        print "<tr class=odd>";
        print "<th class=label colspan=2># of CPUs:</th><td class=lcell colspan=2>$cpucount x $cpu_type</td>\n";
        print "<th class=label colspan=3>System Load:</th><td class=lcell colspan=3>$sysload%</td>\n";
        print "<th class=label colspan=2># of Processes:</th><td class=lcell colspan=2>";
        print "<a onClick=\"openWin('popup', 1024, 700);\" href=process.cgi?hostid=$hostid&popup=1 target=popup>$procs</a></td>\n";
        print "</tr>\n";
    
        print "<tr class=even>";
        print "<th class=label colspan=2>Memory Usage:</th><td class=lcell colspan=2>$memload\%</td>\n";
        print "<th class=label colspan=3>Temperature:</th><td class=lcell colspan=3>$temperature&deg; C</td>\n";
        print "<th class=label colspan=2>Ping Status:</th><td class=lcell colspan=2>$ping</td>\n";
        print "</tr>\n";

        print "<tr><th colspan=14 class=header>Filesystem Summary</th></tr>\n";
        filesystem_summary();
    
        print "<tr><th colspan=14 class=header>System Plots</th></tr>\n";
    
        $sth->finish();

    
    } 


    # -- the filesystem summary table
    if ($tab eq "filesystem") {

        print "<tr><th colspan=14 class=header>Filesystem Summary</th></tr>\n";
        filesystem_summary();

    } 


    # -- the history page (needs some work)
    if ($tab eq "history") {

        my $sql = "select a.hostname, a.hostid, a.ipaddr, a.macaddr, a.procs, a.uptime, a.updated, a.os, a.iloaddr, a.ilomac, 
            c.name, count(b.mount), a.description, a.notes, a.sysload, a.memory, a.temperature, a.maxdisk, a.ping, a.online, 
            a.numcpu, a.cpu_type, a.profile_id 
        from node a, filesystem b, profile c where a.profile_id = c.id and a.id = b.hostid and a.id = '$hostid' group by a.id";
    
        my $sth = $dbh -> prepare($sql) || die "Error occurred preparing SQL: " . $dbh->errstr;
        $sth -> execute || die "Error occurred processing SQL: " . $dbh->errstr; $queries++;
        
        print "<table width=960>\n";
        my @row = $sth->fetchrow();
        my $uptime = human_time($row[5]);
        my $hostname = $row[0];
        my $serial = $row[1];
        my $ipaddr = $row[2];
        my $macaddr = $row[3];
        my $procs = $row[4];
        my $updated = $row[6];
        my $os = $row[7];
        my $iloaddr = $row[8];
        my $ilomac  = $row[9];
        my $profile = $row[10];
        my $fscount = $row[11];
        my $description = $row[12] || "";
        my $notes = $row[13] || "";
        my $sysload = $row[14];
        my $memload = $row[15];
        my $temperature = $row[16];
        my $maxdisk = $row[17];
        my $ping = $row[18];
        my $poll = $row[19];
        my $cpucount = $row[20];
        my $cpu_type = $row[21];
        my $profile_id = $row[22];
    
        if ($ping) { $ping = "FAIL"; } else { $ping = "OK"; }
        if (!$poll) { $poll = "FAIL"; } else { $poll = "OK"; }
    
        my $isth = $dbh->prepare("select count(*) from alert where display = 1 and hostid = $hostid");
        $isth->execute(); $queries++;
        my @irow = $isth->fetchrow();
        my $alerts = $irow[0] || 0;
    
        print "<tr class=even><th class=header>Description</th><th class=header>Notes/History</th><th class=header>Disk Information</th></tr>";
    
    
        print "<tr class=even>";
    
        my $durlDesc = url("field_edit.cgi");
        $durlDesc->query_form("field" => "description", "idvalue" => "$hostid", "id" => "id",
        "content" => "$description", "table" => "node");
        print "<td valign=top class=lcell><pre>$description</pre></td>";
        
        my $durlNotes = url("field_edit.cgi");
        $durlNotes->query_form("field" => "notes", "idvalue" => "$hostid", "id" => "id",
        "content" => "$notes", "table" => "node");
        print "<td valign=top class=lcell><pre>$notes</pre></td>";
    
        print "</tr>\n";
    
    
        print "<tr class=odd>";
        print "<td class=cell>(<a onClick=\"openWin('field_edit', 600, 400);\" target=field_edit href=$durlDesc>Edit</a>)</td>";    
        print "<td class=cell>(<a onClick=\"openWin('field_edit', 600, 400);\" target=field_edit href=$durlNotes>Edit</a>)</td>";    
        print "</tr\n";
    
        print "</table>\n";
    
    
        $sth->finish();
    
    }

    my $plotTime = sprintf("%.3f", tv_interval($t1, [gettimeofday]));
    foreach my $plot (@plots) {
        print "<tr class=odd>";
        print "<td class=cell colspan=14>$plot</td>";
        print "</td>\n";
        print "</tr>\n";
    }
    print "</table>\n";
    print "<p class=message>$queries query(s), $plotTime sec.</p>\n";


}

sub filesystem_summary {

        my $pie_x = get_config("pie_graph_width");
        my $pie_y = get_config("pie_graph_height");
    
        my $sql = "select a.hostname, a.hostid, a.ipaddr, a.macaddr, a.procs, a.uptime, a.updated, a.os, a.iloaddr, a.ilomac, 
            c.name, count(b.mount), a.description, a.notes, a.sysload, a.memory, a.temperature, a.maxdisk, a.ping, a.online, 
            a.numcpu, a.cpu_type, a.profile_id 
        from node a, filesystem b, profile c where a.profile_id = c.id and a.id = b.hostid and a.id = '$hostid' group by a.id";
    
        my $sth = $dbh -> prepare($sql) || die "Error occurred preparing SQL: " . $dbh->errstr;
        $sth -> execute || die "Error occurred processing SQL: " . $dbh->errstr; $queries++;
        
        my @row = $sth->fetchrow();
        my $uptime = human_time($row[5]);
        my $hostname = $row[0];
        my $serial = $row[1];
        my $ipaddr = $row[2];
        my $macaddr = $row[3];
        my $procs = $row[4];
        my $updated = $row[6];
        my $os = $row[7];
        my $iloaddr = $row[8];
        my $ilomac  = $row[9];
        my $profile = $row[10];
        my $fscount = $row[11];
        my $description = $row[12] || "";
        my $notes = $row[13] || "";
        my $sysload = $row[14];
        my $memload = $row[15];
        my $temperature = $row[16];
        my $maxdisk = $row[17];
        my $ping = $row[18];
        my $poll = $row[19];
        my $cpucount = $row[20];
        my $cpu_type = $row[21];
        my $profile_id = $row[22];
    
        if ($ping) { $ping = "FAIL"; } else { $ping = "OK"; }
        if (!$poll) { $poll = "FAIL"; } else { $poll = "OK"; }
    
        my $isth = $dbh->prepare("select count(*) from alert where display = 1 and hostid = $hostid");
        $isth->execute(); $queries++;
        my @irow = $isth->fetchrow();
        my $alerts = $irow[0] || 0;
    
        print "<tr>";
        print "<th class=label>Device</th>";
        print "<th class=label>Partition</th>";
        print "<th class=label>Format</th>";
        print "<th class=label>Mount</th>";
        print "<th class=label colspan=2>Blocks</th>";
        print "<th class=label colspan=2>Inodes</th>";
        print "<th class=label>Total Blocks</th>";
        print "<th class=label>Blocks Used</th>";
        print "<th class=label>Blocks Free</th>";
        print "<th class=label>Total Inodes</th>";
        print "<th class=label>Inodes Used</th>";
        print "<th class=label>Inodes Free</th>";
        print "</tr>\n";
        $isth = $dbh->prepare("select mount, free, ifree, type, device, partition, pct, ipct from filesystem where hostid = $hostid order by device, partition");
        $isth->execute(); $queries++;
        my $gcount = 0;
        while(my @irow = $isth->fetchrow()) {
            $gcount++;
            my $mount = $irow[0];
            my $free = comma_format($irow[1]);
            my $ifree = comma_format($irow[2]);
            my $fstype = $irow[3];
            my $device = $irow[4] || "";
            my $partition = $irow[5] || "";
            my $fpct = $irow[6];
            my $ipct = $irow[7];
            my $class = get_row_type($gcount);

            my $total = $irow[1] / (1 - $fpct / 100);
            my $utotal = comma_format($total * $fpct / 100);
            $total = comma_format($total);

            my $itotal = $irow[2] / (1 - $ipct / 100);
            my $iutotal = comma_format($itotal * $ipct / 100);
            $itotal = comma_format($itotal);

            print "<tr class=$class>";
            print"<td class=lcell>$device</td>\n";
            print"<td class=cell>$partition</td>\n";
            print"<td class=lcell>$fstype</td>\n";
            print"<td class=lcell>$mount</td>\n";
            print"<td class=rcell>$fpct%</td>\n";
            print "<td class=cell nowrap>";
            my $inner = "";
            my $ticks = 10;
            for (my $i = 0; $i < $fpct / 10; $i++) {
                $inner .= "<img src=\"/aware/images/slice_3.png\"/>";
                $ticks--;
            }
            while ($ticks > 0) {
                $inner .= "<img src=\"/aware/images/rbar.png\"/>";
                $ticks--;
            }
            print "$inner</td>";
    
            print"<td class=rcell>$ipct%</td>\n";
            print "<td class=cell nowrap>";
            $inner = "";
            $ticks = 10;
            for (my $i = 0; $i < $ipct / 10; $i++) {
                $inner .= "<img src=\"/aware/images/slice_4.png\"/>";
                $ticks--;
            }
            while ($ticks > 0) {
                $inner .= "<img src=\"/aware/images/rbar.png\"/>";
                $ticks--;
            }
            print "$inner</td>";
    
            print"<td class=rcell>$total MB</td>\n";
            print"<td class=rcell>$utotal MB</td>\n";
            print"<td class=rcell>$free MB</td>\n";
            print"<td class=rcell>$itotal</td>\n";
            print"<td class=rcell>$iutotal</td>\n";
            print"<td class=rcell>$ifree</td>\n";
    
            print "</tr>\n";
        }
        $sth->finish();

}
