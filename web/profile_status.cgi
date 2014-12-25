#!/usr/bin/perl -w

# -----------------------------
# $Revision: 1.15 $
# $Date: 2007-11-25 17:42:09 $
# $Author: aps1 $
# $Name: not supported by cvs2svn $
# -----------------------------

use strict;
use CGI;
use DBI;
use URI::URL qw(url);
use GD::Graph::lines;
use GD::Graph::bars;
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

my $_name = "profile_status.cgi"; 
my $_title = "Profile Summary";

# -------------------------------------------------------------------
# Begin Script
# -------------------------------------------------------------------
my $cgi = new CGI();


my $dbh = get_db_connection();
if (!defined($dbh)) {
	print "<p class=alert>Unable to connect to DB</p>\n";
	exit();
}


my $t0 = [gettimeofday];
my $queries = 0;

my $profile_id = $cgi->param('profile_id') || 0;
my $maxRows = $cgi->param('maxRows') || 60;
my $refresh = $cgi->param('refresh') || 180;
my $popup = $cgi->param('popup') || 0;
my $daysAgo = $cgi->param('daysAgo') || 0;
my $archive = $cgi->param('archive') || 0;
my $window = $cgi->param('window') || 24;
my $message = "OK";
my %profileIDs;
my @profiles;

my $sth = $dbh->prepare("select name, id from profile order by name;");
$sth->execute(); $queries++;
my $currentProfile = "default";
while (my @row = $sth->fetchrow()) { 
	$profileIDs{lc($row[0])} = $row[1];
	push(@profiles, lc($row[0]));
	if ($row[1] == $profile_id) { $currentProfile = lc($row[0]); }
}

if ($popup) {
	print_header_simple($_title, $_name, 0);
} else {
	print_header($_title, $_name, 0);
	print "<meta http-equiv=refresh content=\"$refresh;url=profile_status.cgi?refresh=$refresh&profile_id=$profile_id&daysAgo=$daysAgo\">\n";

	print "<div id=wrapper><center><div id=mainsection>\n";
	print "<table>\n";
	print "<form action=profile_status.cgi method=get>\n";
	print "<tr>\n";
	print "<th>Display Profile:</th>\n";
	print "<td><select class=medselect name=profile_id>\n";

	for (my $i = 0; $i <= $#profiles; $i++) {
		my $selected = "";
		if ($profile_id eq $profileIDs{$profiles[$i]}) {
			$selected = "selected";
		}
		print "<option value=\"$profileIDs{$profiles[$i]}\" $selected>$profiles[$i]</option>\n";
	}
	print "</select>\n";
	print "</td>\n";

	print "<th>Plot Window:</th>\n";
	print "<td><select onChange=\"document.forms[0].submit();\" class=medselect name=window>\n";
	my $selected = "";
	if ($window == 24) { $selected = "selected"; }
	for (my $i = 24; $i >= 1;) {
		my $selected = "";
		if ($window == $i) { $selected = "selected"; }
		print "<option value=$i $selected>$i hours</option>\n";
		$i = $i - 2;
	}
	print "</select>";
	print "</td>";
	
	print "<th>From:</th>\n";
	print "<td><select class=medselect name=daysAgo>\n";
	$selected = "";
	if ($daysAgo == 0) { $selected = "selected"; }
	my $archiveDays = get_setting($dbh, "archiveDays", 7);
	print "<option value=0 $selected>Today</option>\n";
	for (my $i = 1; $i < $archiveDays; $i++) {
		my $selected = "";
		if ($daysAgo == $i) { $selected = "selected"; }
		print "<option value=$i $selected>$i day(s) ago</option>\n";
	}
	print "</select>";
	print "</td>\n";
	
	print "<td><input type=hidden name=message value=\"Filter Changed\"><input class=button type=submit value=\"Update Page\"></td>\n";
	print "</form></tr>\n";
	print "</table>\n";

}


main();

$dbh->disconnect();

exit(0);


sub main {


	if (!defined($profile_id)) {
		print "<p class=message>Please select a profile</p><br>\n";
		return;
	}
	print "<hr width=500>\n";

	my $datestring = get_date(-$daysAgo);
	$datestring =~ s/\s.*//g;

	my $sql = "select max(a.sysload), min(a.sysload), avg(a.sysload),
				max(a.uptime), min(a.uptime), avg(a.uptime),
				max(a.procs), min(a.procs), avg(a.procs),
				count(*), avg(numcpu), b.name from node a, profile b 
				where a.profile_id = $profile_id and b.id = a.profile_id
				group by b.name";

	my $sth = $dbh -> prepare($sql) || print "<font class=alert>ERROR ($sql): " . $dbh->errstr . "</font><br>\n";
	$sth -> execute || print "<font class=alert>ERROR ($sql): " . $dbh->errstr . "</font><br>\n";
	$queries++;

	print "<table>\n";
	my @row = $sth->fetchrow();

	my $sysload_max = $row[0] || 0;
	my $sysload_min = $row[1] || 0;
	my $sysload_avg = $row[2] || 0;
	my $uptime_max = human_time($row[3]);
	my $uptime_min = human_time($row[4]);
	my $uptime_avg = human_time($row[5]);
	my $procs_max = $row[6];
	my $procs_min = $row[7];
	my $procs_avg = $row[8];
	my $num_nodes = $row[9];
	my $cpucount = $row[10];
	my $profile_name = $row[11];

	$sysload_avg = sprintf("%0.0f", $sysload_avg) . "%";
	$procs_avg = sprintf("%0.0f", $procs_avg);

	print "<tr><th colspan=3 class=tableheader>Profile Status: $profile_name</th></tr>\n";
	print "<tr class=even><th colspan=2 class=header>Details</th><th class=header>Nodes</th></tr>";
	print "<tr class=even>";
	print "<th class=label>Profile Name:</th>\n";
	print "<td class=lcell>$profile_name</td>\n";
	print "<td class=cell rowspan=6 valign=top><center>\n";
	my $isth = $dbh->prepare("select a.hostname, a.id, b.name from node a, profile b  where a.profile_id = b.id and a.profile_id = $profile_id order by a.hostname");
	$isth->execute();	
	$queries++;
	my $count = 0;
	while (my @irow = $isth->fetchrow()) {
		$count++;
		my $hostname = $irow[0];
		$hostname =~ s/\..*//g;
		my $hostid = $irow[1];
		my $profile = $irow[2];
		if ($archive) {
			my $ldate = $datestring;
			$ldate =~ s/-//g;
			print "<a href=$hostname-$profile-$ldate-host.html>$hostname</a> ";
		} else {
			print "<a href=node_tabs.cgi?hostid=$hostid>$hostname</a> ";
		}
		if ($count % 7 == 0) { 
			print "<br>\n"; 
		} else {
			print "&nbsp;&nbsp;\n"; 
		}
	}
	print "</td>\n";
	print "</tr>\n";


	print "<tr class=odd><th class=label># Nodes:</th><td class=lcell>$num_nodes</td></tr>\n";
	print "<tr class=even><th class=label>Average System Load:</th><td class=lcell>$sysload_avg</td></tr>\n";
	print "<tr class=even><th class=label>Average # Processes</th><td class=lcell>$procs_avg</td></tr>\n";
	print "<tr class=even><th class=label>Average Uptime:</th><td class=lcell>$uptime_avg</td></tr>\n";

	# determine graph dimensions
	my $x = get_config("graph_width");
	my $y = get_config("graph_height");

	my $_htdoc = get_config("aware_home");
	my $imageDir = $_htdoc."/web/images/tmp/";
	if (!-e $imageDir || !-w $imageDir) {
		chomp(my $username = `whoami`);
		print "ERROR: cannot write files to '$imageDir' (ensure that directory exists and is writable by user: $username)\n";
		return;
	}
	my $startTime = unix_timestamp(get_date()) - ($daysAgo * 86400);
	my $image = "images/tmp/profile-$profile_name";
	if ($archive) {
		$startTime = $datestring;
		$startTime .= " 00:00:00";
		$startTime = unix_timestamp($startTime);

		$datestring =~ s/-//g;

		my $archDir = get_config("aware_home")."/web/archive/$datestring";

		if (!-d $archDir) {
			mkdir($archDir) || die "ERROR: could not find/create directory: $archDir";
			chmod(0777, $archDir);
			mkdir("$archDir/images") || die "ERROR: could not find/create directory: $archDir/images";
			chmod(0777, "$archDir/images");
		}
		$image = "archive/$datestring/images/profile-$profile_name-$datestring";
	}

	print "<!-- Start Graphing = " . tv_interval($t0, [gettimeofday]) . " -->\n"; 
	my @plots;
	push(@plots, graph_sysload($dbh, $profile_id, "Profile", $x, $y, $startTime, $window, \$queries, $image)); 
	push(@plots, graph_cpuload($dbh, $profile_id, "Profile", $x, $y, $startTime, $window, \$queries, $image)); 
	push(@plots, graph_sysio($dbh, $profile_id, "Profile", $x, $y, $startTime, $window, \$queries, $image)); 
	push(@plots, graph_netload($dbh, $profile_id, "Profile", $x, $y, $startTime, $window, \$queries, $image)); 
	push(@plots, graph_procs($dbh, $profile_id, "Profile", $x, $y, $startTime, $window, \$queries, $image)); 
	print "<!-- Combined Plots = " . tv_interval($t0, [gettimeofday]) . " -->\n"; 

	print "<tr><th class=header colspan=3>System Plots</th></tr>\n";

	for (my $i = 0; $i <= $#plots; $i++) {
		my $class = get_row_type($i);
		my $plot = $plots[$i];
		print "<tr class=$class><td class=cell colspan=3><center>$plot</center></td></tr>\n";
	}

	my $interval = sprintf("%0.3f", tv_interval $t0, [gettimeofday]);
	print "<tr><th class=footer align=center colspan=11>$interval second(s)</th></tr>";

	print "</table></td></tr>\n";


	print "</div></center></div>\n";
	print "</body></html>\n";	

	$sth->finish();
	$dbh->disconnect();

}
