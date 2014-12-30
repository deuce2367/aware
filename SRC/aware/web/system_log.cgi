#!/usr/bin/perl -w

# ------------------------------------------------------------
# $Id: system_log.cgi,v 1.3 2006-09-18 12:55:55 aps1 Exp $
# $RCSfile: system_log.cgi,v $
# $Revision: 1.3 $
# $Date: 2006-09-18 12:55:55 $
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

###########################################################################################
# Program Block 
###########################################################################################
my $cgi = new CGI();
my $dbh = get_db_connection();

my $title = "System Monitor Log";
my $name = "system_log.cgi";

my $refresh = $cgi->param('refresh') || 180;
my $action = $cgi->param('action') || "default";
my $maxCount = $cgi->param('maxCount') || 20;
my $date = $cgi->param('date') || get_date();
my $skip = $cgi->param('skip') || 0;
my $component_id = $cgi->param('component_id') || "%";
my $status = $cgi->param('status') || "%";

my $limit = $skip + $maxCount;

print_header_simple($title, $name, 0, 0);

###########################################################################################
# Display Page View Options 
###########################################################################################

#print "<div id=wrapper><center><div id=mainsection>";
print "<center><div id=popup>\n";
print "<table class=optiontable>\n";
print "<form action=system_log.cgi method=get>\n";
print "<tr>\n";
print "<th>Component:</th>\n";
print "<td><select class=medselect name=component_id>\n";
my $selected = "";
if ($component_id eq "%") { $selected = "selected"; }
print "<option value=%>All</option>\n";
my $sql = "select name, id from component";
my $sth = $dbh->prepare($sql);
$sth->execute() || print "Database Error: " . $dbh->errstr;
while (my @row = $sth->fetchrow()) { 
	my $selected = "";
	if ($component_id == $row[1]) { $selected = "selected"; }
	print "<option value=\"$row[1]\" $selected>$row[0]</option>\n";
}
print "</select>\n";
print "</td>\n";
print "<th>Status:</th>\n";
print "<td><select class=medselect name=status>\n";
$selected = "";
my @status_types = ('OK', 'Info', 'Warning', 'Error', 'Operator', 'Unknown');
if ($status eq "%") { $selected = "selected"; }
print "<option value=%>All</option>\n";
for (my $i = 0; $i <= $#status_types; $i++) {
	my $selected = "";
	if ($status eq $status_types[$i]) { $selected = "selected"; }
	print "<option value=\"$status_types[$i]\" $selected>$status_types[$i]</option>\n";
}
print "</select>\n";
print "</td>\n";
print "<th>Date:</th><td><input class=biggiesizetext name=date value=\"$date\"></td>\n";
print "<th>Count:</th><td><input class=smalltext name=maxCount value=\"$maxCount\"></td>\n";
print "<th>Reload:</th>\n";
print "<td><select class=medselect name=refresh>\n";
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

print "<td><input type=hidden name=message value=\"Filter Changed\"><input class=button type=submit value=\"Refresh Display\"></td>\n";
print "</form></tr>\n";
print "</table><br>\n";

if ($action eq "del") { del_message(); }
view_log();

print "</table>\n";

print "</div></center></div>\n";
print "</body></html>\n";


$dbh->disconnect();

exit();


###########################################################################################
# Subroutines 
###########################################################################################


sub view_log { 


	# Now retrieve data from the table.
	my $whereStr = "where created < '$date'";
	my $sql = "select count(*) from status_message";
	if ($component_id ne "%") { $whereStr = "$whereStr and component_id = $component_id"; }
	if ($status ne "%") { $whereStr = "$whereStr and status = '" . lc($status) . "'"; }
	$sql = "$sql $whereStr";

	my $sth = $dbh->prepare($sql);
	$sth->execute();
	my @row = $sth->fetchrow_array();
	my $rowCount = $row[0];
	$sth->finish();

	my %components;
	$sql = "select id, name from component";
	$sth = $dbh->prepare($sql);
	$sth->execute() || print "Database Error: " . $dbh->errstr;
	while (my @row = $sth->fetchrow()) { $components{$row[0]} = $row[1]; }

	my $shown = $maxCount;
	if ($rowCount - $skip < $maxCount) {
		$shown = $rowCount - $skip;
	}
	my $start = $skip + 1;
	my $stop = $skip + $shown;
	my $dateurl = $date;
	$dateurl =~ s/\s/+/g;

	my $skipForward = $skip + $maxCount;
	my $skipBackward = $skip;


	if ($stop >= $rowCount) { $skipForward = $skip; }
	if ($start > 1) {
		$skipBackward = $start - $maxCount - 1;
		if ($skipBackward < 0) { $skipBackward = 0; }
	}

	my $backwards = "<a href=system_log.cgi?action=view&skip=$skipBackward&component_id=$component_id&maxCount=$maxCount&date=$dateurl&status=$status><img border=0 src=images/left.png></a>";
	my $forwards = "<a href=system_log.cgi?action=view&skip=$skipForward&component_id=$component_id&maxCount=$maxCount&date=$dateurl&status=$status><img border=0 src=images/right.png></a>";

	my $count = 0;
	my $printed = 0;
	my $printHeader = 1;
	my $hostid;
	
	$sql = "select component_id, status_message.status, message, date_format(status_message.created, '%M %D, %Y<br> %H:%i:%s'), 
		sid from status_message $whereStr order by created desc limit $limit";
	$sth = $dbh->prepare($sql);

	print "<table class=beamtable>\n";
	print "<tr><th class=tableheader colspan=7>System Status Log</th></tr>\n";
	print "<tr><th colspan=2>Date</th><th>Component</th><th>Sid</th><th nowrap>Status</th>\n";
	print "<th>";
	print "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;";
	print "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;";
	print "Message";
	print "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;";
	print "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;";
	print "</th>\n";
	print "<th nowrap>$backwards ($start - $stop) of $rowCount $forwards</th>\n";

	$sth->execute() || print "Database Error: " . $dbh->errstr;

	while ((my @row = $sth->fetchrow_array()) && $printed < $maxCount) {
  		my $rowtype = get_row_type($count);

		$count++;
		if ($count <= $skip) {
			next;
		}
		$printed++;

		my $component_id = $row[0];
		my $status = $row[1];
		my $message = $row[2];
		my $created = $row[3];
		my $sid = $row[4];

		my $icon = "images/" . lc($status) . ".png";

		my $component_name = $components{$component_id};

		print "<tr class=$rowtype>\n";
 		print "<td class=cell nowrap>$count</td>\n";
 		print "<td class=cell nowrap>$created</td>\n";
 		print "<td class=cell nowrap><a href=node_tabs.cgi?hostid=$component_id>$component_name</a></td>\n";
 		print "<td class=cell nowrap>$sid</td>\n";
 		print "<td class=cell nowrap><img src=$icon width=20 height=20></td>\n";
		print "<td colspan=2 class=lcell >$message</td>\n";
		print "<form action=system_log.cgi method=post>\n";
		#print "<td class=cell><input type=submit value=\"Delete\" class=button></td>\n";
		print "<input type=hidden name=action value=del>\n";
		print "<input type=hidden name=component_id value=$component_id>\n";
		print "<input type=hidden name=skip value=$skip>\n";
  		print "</form>\n";
		print "</tr>\n";
	}
	$sth->finish();
	if (!$count) {
		print "<tr class=even><td colspan=6 class=cell>No Entries</td></tr>\n";
	}

	print "</table>\n";
	print "<input class=button type=button onClick=window.close() value=\"Close\">";

}

