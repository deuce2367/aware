#!/usr/bin/perl -w

# -----------------------------
# $Revision: 1.18 $
# $Date: 2008-02-05 13:56:34 $
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

my $_name = "report.cgi"; 
my $_title = "Node Report";

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

my $action = $cgi->param('action');
my $sortCol = $cgi->param('sortCol') || "hostname";
my $sortOrder = $cgi->param('sortOrder') || "asc";
my $id = $cgi->param('id') || 0;


my $revSortOrder = "desc";
if ($sortOrder eq "desc") { $revSortOrder = "asc"; }

if ($action eq "remove") {
	my $message = removeNode();
	print "<script language=javascript>update_status('$message')</script>\n";
	$id = 0;
}

print "<div id=wrapper><center><div id=mainsection>\n";
print "<table>\n";


print "<tr>\n";
print "<th class=tableheader colspan=16>Node Report</th>\n";
print "</tr>\n";
print "<tr>\n";
print "<th colspan=2><a class=sortCol href=report.cgi?sortOrder=$revSortOrder&sortCol=hostname>Hostname</a></th>\n";
print "<th><a class=sortCol href=report.cgi?sortOrder=$revSortOrder&sortCol=hostid>Hostid</a></th>\n";
print "<th><a class=sortCol href=report.cgi?sortOrder=$revSortOrder&sortCol=ipaddr>IP Address</a></th>\n";
print "<th><a class=sortCol href=report.cgi?sortOrder=$revSortOrder&sortCol=>MAC Address</a></th>\n";
print "<th><a class=sortCol href=report.cgi?sortOrder=$revSortOrder&sortCol=profile.name>Profile</a></th>\n";
print "<th><a class=sortCol href=report.cgi?sortOrder=$revSortOrder&sortCol=port>Port</a></th>\n";
print "<th><a class=sortCol href=report.cgi?sortOrder=$revSortOrder&sortCol=idx>Index</a></th>\n";
print "<th><a class=sortCol href=report.cgi?sortOrder=$revSortOrder&sortCol=rack>Rack #</a></th>\n";
print "<th><a class=sortCol href=report.cgi?sortOrder=$revSortOrder&sortCol=online>Enabled</th>\n";
print "<th><a class=sortCol href=report.cgi?sortOrder=$revSortOrder&sortCol=iloaddr>ILO IP</a></th>\n";
print "<th><a class=sortCol href=report.cgi?sortOrder=$revSortOrder&sortCol=password>Password</a></th>\n";
print "<th colspan=2>Administration</th>\n";
print "</tr>\n";

# -- prepare SQL
my $sql = "SELECT macaddr,hostname,ipaddr,port,profile.name,rack,hostid,password,ilomac,iloaddr,iloport,idx,status,online,node.id
	FROM node, profile where profile.id = node.profile_id";
if ($id) { $sql = "$sql  and node.id = '$id'"; }
$sql = "$sql order by $sortCol $sortOrder";

# -- execute query
my $sth = $dbh->prepare($sql) || print "SQL Error ($sql): " . $dbh->errstr . "\n";
$sth->execute() || print "Database Error" . $dbh->errstr . "\n";

# -- display results
my $count = 1;
while (my @row = $sth->fetchrow_array()) {
	my $rowtype = get_row_type($count);

	my $macaddr = $row[0];
	my $hostname = $row[1] || "";
	my $ipaddr = $row[2];
	my $port = $row[3];
	my $profile = $row[4];
	my $rack = $row[5];
	my $hostid = $row[6];
	my $password = $row[7];
	my $ilomac = $row[8];
	my $iloaddr = $row[9];
	my $iloport = $row[10];
	my $idx = $row[11];
	my $status = $row[12];
	my $online = $row[13];
	my $current_id = $row[14];

	if ($online) {
		$online = "on-line";
	} else {
		$online = "off-line";
	}

	print "<tr class=$rowtype>\n";
	print "<td>$count</td><td>$hostname</td>\n";
	print "<td>$hostid</td>\n";
	print "<td>$ipaddr</td>\n";
	print "<td>$macaddr</td>\n";
	print "<td>$profile</td>\n";
	print "<td>$port</td>\n";
	print "<td>$idx</td>\n";
	print "<td>$rack</td>\n";
	print "<td>$online</td>\n";
	print "<td>$iloaddr</td>\n";
	print "<td>$password</td>\n";
	print "<td class=cell><form action=update.cgi><input class=button type=submit value=\"Edit Node\">\n";
	print "<input type=hidden name=hostid value=$current_id>\n";
	print "<input type=hidden name=action value=edit>\n";
	print "</form></td>\n";
	print "<td class=cell><form action=report.cgi><input class=button type=submit value=\"Remove Node\">\n";
	print "<input type=hidden name=id value=$current_id>\n";
	print "<input type=hidden name=hostname value=$hostname>\n";
	print "<input type=hidden name=action value=remove>\n";
	print "</form></td>\n";
	print "</tr>\n";
	$count++;
}

$sth->finish();
print "</table>\n";
print "</div></center></div>\n";
print "</body></html>\n";

$dbh->disconnect();


sub removeNode {

	my $hostname = $cgi->param('hostname');

	$dbh->do("delete from temperature where hostid = '$id'");
	$dbh->do("delete from memory where hostid = '$id'");
	$dbh->do("delete from sysload where hostid = '$id'");
	$dbh->do("delete from filesystem where hostid = '$id'");
	$dbh->do("delete from process where hostid = '$id'");
	$dbh->do("delete from alert where hostid = '$id'");
	$dbh->do("delete from daemon where hostid = '$id'");
	$dbh->do("delete from cfgfile where hostid = '$id'");
	$dbh->do("delete from cfghash where hostid = '$id'");
	$dbh->do("delete from node where id = '$id'");
	$dbh->commit;

	return "Removed \"$hostname\" from database"; 

}
