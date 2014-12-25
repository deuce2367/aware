#!/usr/bin/perl -w

# -----------------------------
# $Revision: 1.12 $
# $Date: 2008-04-08 14:35:30 $
# $Author: aps1 $
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

my $_name = "process.cgi"; 
my $_title = "Process Status";

# -------------------------------------------------------------------
# Begin Script
# -------------------------------------------------------------------
my $cgi = new CGI();

# -- retrieve & determine  CGI parameters
my $sortCol1      = $cgi->param('sortCol1') || "cpu";
my $sortOrder1    = $cgi->param('sortOrder1') || "desc";
my $sortCol2      = $cgi->param('sortCol2') || "pid";
my $sortOrder2    = $cgi->param('sortOrder2') || "asc";
my $hostid        = $cgi->param('hostid') || 0;
my $maxRows       = $cgi->param('maxRows') || 60;
my $refresh       = $cgi->param('refresh') || 180;
my $message       = $cgi->param('message') || "OK";
my $popup         = $cgi->param('popup') || 0;


if ($popup) { 
	print_header_simple($_title, $_name, 0);
} else {
	print_header($_title, $_name, 0);
}
print "<script language=javascript>update_status('$message')</script>\n";

my $dbh = get_db_connection();
if (!defined($dbh)) {
	print "<p class=alert>Unable to connect to DB</p>\n";
	exit();
}


# -- handle the sorting and page view parameters
my $revSort = "asc";
if ($sortOrder1 eq $revSort) { $revSort = "desc"; }
my $sortStr = "order by $sortCol1 $sortOrder1";
if ($sortCol2 && $sortOrder2) { $sortStr .= ", $sortCol2 $sortOrder2"; }
my $params = "sortOrder1=$revSort&sortCol2=$sortCol1&sortOrder2=$sortOrder1&hostid=$hostid&popup=$popup";

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

print "<meta http-equiv=refresh content=\"$refresh;url=process.cgi?refresh=$refresh&hostid=$hostid&message=Auto-Refresh&popup=$popup\">\n";

print "<div id=wrapper><center><div id=mainsection>\n";
print "<table>\n";
print "<form action=process.cgi method=get>\n";
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

print "<td>";
print "<input type=hidden name=message value=\"Filter Changed\">";
print "<input type=hidden name=popup value=\"$popup\">";
print "<input class=button type=submit value=\"Update Page\"></td>\n";
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

	print "<table width=\"94%\">";
	print "<tr><th colspan=11 class=tableheader>Processes: $currentHost</th></tr>";
	print "<tr>";
	print "<th nowrap><a class=sortCol href=$_name?sortCol1=pid&$params>Process ID</a></th>\n";
	print "<th nowrap><a class=sortCol href=$_name?sortCol1=ppid&$params>Parent ID</a></th>\n";
	print "<th nowrap><a class=sortCol href=$_name?sortCol1=user&$params>User</a></th>\n";
	print "<th nowrap><a class=sortCol href=$_name?sortCol1=cpu&$params>CPU</a></th>\n";
	print "<th nowrap><a class=sortCol href=$_name?sortCol1=mem&$params>Memory</a></th>\n";
	print "<th nowrap><a class=sortCol href=$_name?sortCol1=nice&$params>Nice</a></th>\n";
	print "<th nowrap><a class=sortCol href=$_name?sortCol1=prio&$params>Priority</a></th>\n";
	print "<th nowrap><a class=sortCol href=$_name?sortCol1=stime&$params>Start Time</a></th>\n";
	print "<th nowrap><a class=sortCol href=$_name?sortCol1=etime&$params>Elapsed Time</a></th>\n";
	print "<th nowrap><a class=sortCol href=$_name?sortCol1=cmd&$params>Command</a></th>\n";
	print "<th nowrap><a class=sortCol href=$_name?sortCol1=args&$params>Args</a></th>\n";
	print "</tr>";

	my $sql = "select pid, ppid, user, cpu, mem, nice, prio, rsz, vsz, sz, stime, etime, cmd, args 
		from process where hostid = $hostid $sortStr";
	$sth = $dbh->prepare($sql);
	$sth->execute();

	my $count = 0;
	while (my @row = $sth->fetchrow()) {
		my $pid = $row[0]; 
		my $ppid = $row[1]; 
		my $user = $row[2]; 
		my $cpu = $row[3]; 
		my $mem = $row[4]; 
		my $nice = $row[5]; 
		my $prio = $row[6]; 
		my $rsz = $row[7]; 
		my $vsz = $row[8]; 
		my $sz = $row[9]; 
		my $start = $row[10]; 
		my $elapsed = $row[11]; 
		my $cmd = $row[12]; 
		my $args = $row[13]; 

		my $rowtype = get_row_type($count);
		print "<tr class=$rowtype>";
		print "<td>$pid</td><td>$ppid</td><td>$user</td><td>$cpu\%</td><td>$mem\%</td>";
		print "<td>$nice</td><td>$prio</td>";
		print "<td>$start</td><td>$elapsed</td><td class=lcell>$cmd</td><td class=lcell>$args</td>";
		print "</tr>\n";
		$count++;

	}
	my $interval = sprintf("%0.3f", tv_interval $t0, [gettimeofday]);
	print "<tr><th align=center colspan=11 class=footer>$interval second(s)</td></tr>";

	print "</table></td></tr>\n";

	if ($popup) { print "<br><table><tr><td><input type=button class=button onClick=\"window.close()\" value=\"Close\"></td></tr></table>\n"; }

	print "</div>\n";
	print "</center>\n";	

	$sth->finish();
	$dbh->disconnect();

}
