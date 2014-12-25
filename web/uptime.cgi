#!/usr/bin/perl -w

# -----------------------------
# $Revision: 1.5 $
# $Date: 2010-02-23 15:22:40 $
# $Author: xxxxxx $
# $Name: not supported by cvs2svn $
# -----------------------------

use strict;
use CGI;
use DBI;
use URI::URL qw(url);
use Time::HiRes qw(usleep ualarm gettimeofday tv_interval);
use ZUtils::Common;
use ZUtils::Aware;

# -------------------------------------------------------------------
# Initialize Configuration Settings
# -------------------------------------------------------------------
my $cfgfile = $ENV{ZUTILS_CFGFILE} || "/etc/aware/aware.cfg";
load_config($cfgfile);

my $_name = "uptime.cgi"; 
my $_title = "Boot Log";

# -------------------------------------------------------------------
# Begin Script
# -------------------------------------------------------------------
my $cgi = new CGI();

print_header($_title, $_name, 0);

my $dbh = get_db_connection();
if (!defined($dbh)) {
	print "<p class=alert>Unable to connect to DB</p>\n";
	exit();
}

# -- retrieve & determine  CGI parameters
my $sortCol1      = $cgi->param('sortCol1') || "booted";
my $sortOrder1    = $cgi->param('sortOrder1') || "desc";
my $sortCol2      = $cgi->param('sortCol2') || "";
my $sortOrder2    = $cgi->param('sortOrder2') || "";
my $hostid        = $cgi->param('hostid') || 0;
my $maxRows       = $cgi->param('maxRows') || 60;
my $refresh       = $cgi->param('refresh') || 180;
my $message       = $cgi->param('message') || "OK";
print "<script language=javascript>update_status('$message')</script>\n";

# -- handle the sorting and page view parameters
my $revSort = "asc";
if ($sortOrder1 eq $revSort) { $revSort = "desc"; }
my $sortStr = "order by $sortCol1 $sortOrder1";
if ($sortCol2 && $sortOrder2) { $sortStr .= ", $sortCol2 $sortOrder2"; }
my $params = "sortOrder1=$revSort&sortCol2=$sortCol1&sortOrder2=$sortOrder1&hostid=$hostid";

my $t0 = [gettimeofday];
my %hostID;
my @hosts;

my $sth = $dbh->prepare("select hostname, id from node order by idx;");
$sth->execute();
my $currentHost;
while (my @row = $sth->fetchrow()) { 
	$hostID{$row[0]} = $row[1];
	push(@hosts, $row[0]);
	if ($row[1] == $hostid) { $currentHost = $row[0]; }
}

print "<div id=wrapper><center><div id=mainsection>\n";
print "<table>\n";
print "<form action=$_name method=get>\n";
print "<tr>\n";
print "<th>Display Node:</th>\n";
print "<td><select onChange=\"document.forms[0].submit();\" class=medselect name=hostid>\n";

for (my $i = 0; $i <= $#hosts; $i++) {
	my $selected = "";
	if ($hostid eq $hostID{$hosts[$i]}) {
		$selected = "selected";
	}
	print "<option value=\"$hostID{$hosts[$i]}\" $selected>$hosts[$i]</option>\n";
}
print "</select>\n";
print "</td>\n";
print "<th>Refresh Every:</th>\n";
print "<td><select onChange=\"document.forms[0].submit();\" class=medselect name=refresh>\n";
my @options = ('15 Seconds', '30 Seconds', '60 Seconds', '90 Seconds', '3 Minutes', '5 Minutes', '30 Minutes', '60 Minutes', 'Never');
my @values = ('15', '30', '60', '90', '180', '300', '1800', '3600', '-1');
for (my $i = 0; $i <= $#options; $i++) {
	my $selected = "";
	if ($refresh eq $values[$i]) {
		$selected = "selected";
	}
	print "<option value=\"$values[$i]\" $selected>$options[$i]</option>\n";
}
print "</select>\n";
print "</td>\n";

print "<td><input type=hidden name=message value=\"Filter Changed\"><input class=button type=submit value=\"Update Page\"></td>\n";
print "</form></tr>\n";
print "</table>\n";

if (!defined($currentHost)) {
	print "<p class=message>Please select a node from the drop-down menu above</p>\n";
} else {
	main();
}

print "</div></center></div>\n";
print "</body></html>\n";

$dbh->disconnect();

exit(0);

#######################################################################################################################
#######################################################################################################################

sub main {

	print "<table>";
	print "<tr><th colspan=11 class=tableheader>Boot Log: $currentHost</th></tr>";
	print "<tr>";
	print "<th nowrap><a class=sortCol href=$_name?sortCol1=booted&$params>Booted</a></th>\n";
	print "<th nowrap><a class=sortCol href=$_name?sortCol1=updated&$params>Last Update</a></th>\n";
	print "<th nowrap><a class=sortCol href=$_name?sortCol1=uptime&$params>Uptime</a></th>\n";
	print "<th nowrap>Downtime</th>\n";
	print "</tr>";

	my $sql = "select unix_timestamp(booted), unix_timestamp(updated), uptime from uptime where hostid = $hostid $sortStr";
	$sth = $dbh->prepare($sql);
	$sth->execute();

	my $count = 0;

	my $lasttime = 0;
	my $totalTime = 0;
	my $upTotal;

	while (my @row = $sth->fetchrow()) {
		my $booted = $row[0]; 
		my $updated = $row[1]; 
		my $uptime = $row[2]; 
		
		
		my $downtime = "N/A";
		if ($lasttime) { 
			$downtime = $lasttime - $updated;
			if ($downtime < 0) {
				my $sql = "delete from uptime where hostid = $hostid and booted = from_unixtime('$booted') 
				and updated = from_unixtime($updated) and uptime = '$uptime'";
				$dbh->do($sql) || print "ERROR ($sql): " . $dbh->errstr;
				next;

			}
			$totalTime += $downtime;
			$downtime = human_time($lasttime - $updated); 
		}

		$upTotal += $uptime;
		$totalTime += $uptime;

		my $bootedTime = get_time($booted);
		my $updatedTime = get_time($updated);

		$uptime = human_time($uptime);	

		my $rowtype = get_row_type($count);
		print "<tr class=$rowtype>";
		print "<td>$bootedTime</td><td>$updatedTime</td><td>$uptime</td><td>$downtime</td>";
		print "</tr>\n";
		$count++;

		$lasttime = $booted;

	}
	my $upPct = sprintf("%.3f", 100 * ($upTotal / $totalTime));

    my $periodStart = get_time($lasttime);
	print "<tr><th align=center colspan=11 class=footer>$upPct% uptime since $periodStart</td></tr>\n";

	print "</table></td></tr>\n";

	my $interval = sprintf("%0.3f", tv_interval $t0, [gettimeofday]);
	print "<center><p>pageload: $interval second(s)</p></center>\n";

	print "</div>\n";
	print "</center>\n";	

	$sth->finish();
	$dbh->disconnect();

}
