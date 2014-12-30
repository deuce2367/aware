#!/usr/bin/perl -w

# ------------------------------------------------------------
# $Id: node_tabs.cgi,v 1.8 2008-07-22 19:03:59 aps1 Exp $
# $RCSfile: node_tabs.cgi,v $
# $Revision: 1.8 $
# $Date: 2008-07-22 19:03:59 $
# $Author: aps1 $
# $Name: not supported by cvs2svn $
# ------------------------------------------------------------

use strict;
use CGI;
use DBI;
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

my $_title = "Node Details";
my $_name = "node_tabs.cgi";

my $hostid = $cgi->param('hostid') || 0;
my $daysAgo = $cgi->param('daysAgo') || 0;
my $window = $cgi->param('window') || 3;
my $tab = $cgi->param('tab') || "summary";
my $message = "OK";
my %hostID;
my @hosts;

print_header($_title, $_name, 0);
my $dbh = get_db_connection(0);
if (!defined($dbh)) {
	print "<p class=alert>Unable to connect to DB</p>\n";
	exit();
}

my $sth = $dbh->prepare("select hostname, id from node order by idx;");
$sth->execute();
my $currentHost = "Unknown";
while (my @row = $sth->fetchrow()) { 
	my $hostname = $row[0];
	my $this_id = $row[1];
	$hostname =~ s/\..*//g;
	$hostname = lc($hostname);
	$hostID{$hostname} = $this_id;
	push(@hosts, $hostname);
	if ($this_id == $hostid) { $currentHost = $hostname; }
}
@hosts = sort(@hosts);

print "<div id=wrapper><center><div id=mainsection>\n";
print "<form action=$_name method=get>\n";
print "<input id=tab type=hidden name=tab value=\"$tab\">\n";
print "<table>\n";
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

print "<th>Plot Window:</th>\n";
print "<td><select onChange=\"document.forms[0].submit();\" class=medselect name=window>\n";
my $selected = "";
#if ($window == 24) { $selected = "selected"; }
my @intervals = (1, 2, 3, 4, 6, 12, 24, 48, 72, 168, 336, 720, 1440, 4320, 8760, 17520, 43800); 
foreach my $interval (@intervals) {
	my $selected = "";
	if ($window == $interval) { $selected = "selected"; }
	my $htime = human_time($interval * 3600);
	$htime =~ s/\.[0-9]*//g;
	print "<option value=$interval $selected>$htime</option>\n";
}
print "</select>";
print "</td>";

print "<th>From:</th>\n";
print "<td><select onChange=\"document.forms[0].submit();\" class=medselect name=daysAgo>\n";
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

print "</tr>\n";
print "</table>\n";
print "</form>\n";
print "<hr width=500>";
print "<br>\n";

print_tabs();

print "</div></body></html>\n";

$dbh->disconnect();

exit(0);


# -------------------------------------------------------------------
# Subroutines
# -------------------------------------------------------------------

sub print_tabs {

	print "<div class=\"tabArea\">\n";

	print "<a class=\"tab\" onClick=\"document.forms[0].tab.value='summary'\"; href=\"node_pane.cgi?tab=summary&hostid=$hostid&window=$window&daysAgo=$daysAgo\" target=\"myIframe\">Summary</a>\n";
	print "<a class=\"tab\" onClick=\"document.forms[0].tab.value='memory'\"; href=\"node_pane.cgi?tab=memory&hostid=$hostid&window=$window&daysAgo=$daysAgo\" target=\"myIframe\">Memory</a>\n";
	print "<a class=\"tab\" onClick=\"document.forms[0].tab.value='utilization'\"; href=\"node_pane.cgi?tab=utilization&hostid=$hostid&window=$window&daysAgo=$daysAgo\" target=\"myIframe\">Utilization</a>\n";
	print "<a class=\"tab\" onClick=\"document.forms[0].tab.value='diskio'\"; href=\"node_pane.cgi?tab=diskio&hostid=$hostid&window=$window&daysAgo=$daysAgo\" target=\"myIframe\">Disk I/O</a>\n";
	print "<a class=\"tab\" onClick=\"document.forms[0].tab.value='filesystem'\"; href=\"node_pane.cgi?tab=filesystem&hostid=$hostid&window=$window&daysAgo=$daysAgo\" target=\"myIframe\">Filesystems</a>\n";
	print "<a class=\"tab\" onClick=\"document.forms[0].tab.value='combined'\"; href=\"node_pane.cgi?tab=combined&hostid=$hostid&window=$window&daysAgo=$daysAgo\" target=\"myIframe\">Combined</a>\n";
	print "<a class=\"tab\" onClick=\"document.forms[0].tab.value='network'\"; href=\"node_pane.cgi?tab=network&hostid=$hostid&window=$window&daysAgo=$daysAgo\" target=\"myIframe\">Network</a>\n";
	print "<a class=\"tab\" onClick=\"document.forms[0].tab.value='procs'\"; href=\"node_pane.cgi?tab=procs&hostid=$hostid&window=$window&daysAgo=$daysAgo\" target=\"myIframe\">Processes</a>\n";
	print "<a class=\"tab\" onClick=\"document.forms[0].tab.value='history'\"; href=\"node_pane.cgi?tab=history&hostid=$hostid&window=$window&daysAgo=$daysAgo\" target=\"myIframe\">History</a>\n";
	print "<a class=\"tab\" onClick=\"document.forms[0].tab.value='temperature'\"; href=\"node_pane.cgi?tab=temperature&hostid=$hostid&window=$window&daysAgo=$daysAgo\" target=\"myIframe\">Sensors</a>\n";
	print "</div>\n";
	print "<div class=\"tabMain\">\n";
	print "<div class=\"tabIframeWrapper\">\n";
	print "<iframe class=\"tabContent\" name=\"myIframe\"  src=\"node_pane.cgi?tab=$tab&hostid=$hostid&window=$window&daysAgo=$daysAgo\" marginheight=\"8\" marginwidth=\"8\" frameborder=\"0\"></iframe>\n";
	print "</div>\n";
	print "</div>\n";

	return;

}
