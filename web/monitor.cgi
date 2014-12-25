#!/usr/bin/perl -w

# -----------------------------
# $Revision: 1.14 $
# $Date: 2006-09-18 12:55:55 $
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

my $_name = "monitor.cgi"; 
my $_title = "Node Monitor";

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

my $ok = "images/gclear.png";
my $err = "images/online_alert.png";
my $width=18;
my $height=18;

###########################################################################################
# Program Block 
###########################################################################################


my $refresh	= $cgi->param('refresh') || 60;
my $limit = $cgi->param('limit') || -1 ;
my $profile_id = $cgi->param('profile_id') || "%";
my $message	= $cgi->param('message') || "OK";

my @alerts;
my %thresholds;

my %profiles;
my $sql = "select name, id from profile order by name";
my $sth = $dbh->prepare($sql);
$sth->execute();
while (my @row = $sth->fetchrow()) { $profiles{$row[0]} = $row[1]; }
	
print "<div id=wrapper><center><div id=mainsection>\n";


print "<form action=monitor.cgi method=get>\n";
print "<table>\n";
print "<tr>\n";
print "<th>Node Type:</th>\n";
print "<td><select class=medselect name=profile_id>\n";
print "<option value=\"%\">All</option>\n";
foreach my $profile (sort(keys(%profiles))) {
	my $selected = "";
	if ($profile_id eq $profiles{$profile}) { $selected = "selected"; }
	print "<option value=\"$profiles{$profile}\" $selected>$profile</option>\n";
}
print "</select>\n";
print "</td>\n";
print "<th>Show:</th>\n";
print "<td><select class=medselect name=limit>\n";
my @options = ('10 Nodes', '25 Nodes', '50 Nodes', '100 Nodes', 'All Nodes');
my @values = ('10', '25', '50', '100', '-1');
for (my $i = 0; $i <= $#options; $i++) {
	my $selected = "";
	if ($limit eq $values[$i]) {
		$selected = "selected";
	}
	print "<option value=\"$values[$i]\" $selected>$options[$i]</option>\n";
}
print "</select>\n";
print "</td>\n";
print "<th>Refresh Every:</th>\n";
print "<td><select class=medselect name=refresh>\n";
@options = ('15 Seconds', '30 Seconds', '60 Seconds', '90 Seconds', '5 Minutes');
@values = ('15', '30', '60', '90', '300');
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
print "</tr>";
print "</table>\n";
print "</form>\n";


$sql = "select node.hostid, node.ipaddr, node.macaddr, node.procs, node.uptime, date_format(node.updated, ' %H:%i') reported, node.alert,
 	node.hostname, node.temperature, node.sysload, node.maxdisk, filesystem.mount, filesystem.pct, node.updated, profile.name, 
	node.memory, node.os, node.id, node.ping, node.online, node.iloaddr, unix_timestamp(now()) - unix_timestamp(node.updated), filesystem.ipct 
	from node, filesystem, profile where node.id = filesystem.hostid and node.maxdisk = filesystem.device and node.maxpart = filesystem.partition
	and profile.id = node.profile_id";
	
if ($profile_id ne "%") { $sql = "$sql and profile.id = '$profile_id'"; } 
$sql = "$sql order by node.idx";
if ($limit > 0) { $sql .= " limit $limit"; }

$sth = $dbh -> prepare($sql) || print "ERROR($sql): " . $dbh->errstr;
$sth -> execute || print "ERROR($sql): " . $dbh->errstr;

printTable($sth);

print "</div></center></div>\n";
print "</body></html>\n";

$sth->finish();
$dbh->disconnect();
exit(0);

sub printTable {

	my ($sth) = @_;

	print "<table>\n";

	print "<tr><th colspan=13 class=tableheader>Node Monitor</th></tr>\n";

	my $columns = 12;

	my $rowcount = 0;
	my $rownum = 0;
	while (my @row = $sth -> fetchrow_array) {

		my $hostid 	= $row[0];
		my $ipaddr 	= $row[1];
		my $macaddr 	= $row[2];
		my $procs	= $row[3];
		my $uptime	= $row[4];
		my $reported	= $row[5];
		my $hostname	= $row[7];
		my $temp	= $row[8];
		my $sysload	= $row[9];
		my $diskidx	= $row[10];
		my $diskmnt	= $row[11];
		my $diskpct	= $row[12];
		my $updated	= $row[13];
		my $profile	= $row[14];
		my $memory 	= $row[15];
		my $os		= $row[16];
		my $id		= $row[17];
		my $ping	= $row[18] || 0;
		my $poll	= $row[19] || 0;
		my $iloaddr	= $row[20];
		my $alert	= $row[6] || 0;
		my $lastUpdate 	= $row[21];
		my $inodepct = $row[22];

		$hostname =~ s/\..*//g;

		my $status = "<img width=$width height=$height src=$ok border=0>";

		my $rowtype = get_row_type($rownum);

		if ($ping > get_profile_threshold($dbh, $profile, "missedpings")) { $status = "<img src=$err width=$width height=$height border=0>"; }
		if ($poll > get_profile_threshold($dbh, $profile, "missedpolls")) { $status = "<img src=$err width=$width height=$height border=0>"; }
		if ($lastUpdate > get_profile_threshold($dbh, $profile, "maxreport")) { $status = "<img src=$err width=$width height=$height border=0>"; }
		if ($procs > get_profile_threshold($dbh, $profile, "maxprocs")) { $status = "<img src=$err width=$width height=$height border=0>"; }
		if ($temp > get_profile_threshold($dbh, $profile, "maxtemp")) { $status = "<img src=$err width=$width height=$height border=0>"; }
		if ($diskpct> get_profile_threshold($dbh, $profile, "maxdisk")) { $status = "<img src=$err width=$width height=$height border=0>"; }
		if ($inodepct > get_profile_threshold($dbh, $profile, "maxinodes")) { $status = "<img src=$err width=$width height=$height border=0>"; }
		if ($memory > get_profile_threshold($dbh, $profile, "maxmem")) { $status = "<img src=$err width=$width height=$height border=0>"; }
		if ($sysload > get_profile_threshold($dbh, $profile , "maxload")) { $status = "<img src=$err width=$width height=$height border=0>"; }
	
		if ($rowcount % $columns == 0 && $rowcount > 0) {
			$rownum++;
			print "</tr><tr class=$rowtype>\n";
			print "<td class=lcell>$rownum</td>\n";
		}
		if ($rowcount == 0) { 
			$rownum++;
			print "<tr class=$rowtype>\n";
			print "<td class=lcell>$rownum</td>\n";
		}
		print "<td class=rcell valign=center nowrap><a href=node_tabs.cgi?hostid=$id>$hostname $status</a></td>\n";
		$rowcount++;
	} 


	if ($rowcount) { print"</tr>\n"; }
	print "</table></center><br><br>\n";	

}

