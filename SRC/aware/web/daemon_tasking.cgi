#!/usr/bin/perl -w

# ------------------------------------------------------------
# $Id: daemon_tasking.cgi,v 1.2 2006-09-18 12:55:55 aps1 Exp $_name,v 1.10 2006/03/26 20:12:30 aps1 Exp $
# $RCSfile: daemon_tasking.cgi,v $_name,v $
# $Revision: 1.2 $
# $Date: 2006-09-18 12:55:55 $
# $Author: aps1 $
# $Name: not supported by cvs2svn $
# ------------------------------------------------------------

use strict;
use CGI;
use DBI;
use Time::Local;
use Time::HiRes qw(usleep ualarm gettimeofday tv_interval);
use ZUtils::Common;
use ZUtils::Aware;

# -------------------------------------------------------------------
# Initialize Configuration Settings
# -------------------------------------------------------------------
my $cfgfile = $ENV{ZUTILS_CFGFILE} || "/etc/aware/aware.cfg";
load_config($cfgfile);
my $_name = "daemon_tasking.cgi"; 
my $_title = "Daemon Tasking";

# -------------------------------------------------------------------
# Begin Script
# -------------------------------------------------------------------
my $cgi = new CGI;

print_header($_title, $_name, 0);
my $dbh = get_db_connection(0);
if (!defined($dbh)) {
	print "<p class=alert>Unable to connect to DB</p>\n";
	exit();
}


my $action 	= $cgi->param('action') || "default";
my $sortCol1 	= $cgi->param ('sortCol1') || "node.idx";
my $sortOrder1 	= $cgi->param ('sortOrder1') || "asc";
my $sortCol2 	= $cgi->param ('sortCol2') || "node.idx";
my $sortOrder2	= $cgi->param ('sortOrder2') || "asc";
my $sortCol3 	= $cgi->param ('sortCol3') || "node.idx";
my $sortOrder3	= $cgi->param ('sortOrder3') || "asc";
my $sortCol4 	= $cgi->param ('sortCol4') || "node.idx";
my $sortOrder4 	= $cgi->param ('sortOrder4') || "asc";
my $refresh	= $cgi->param ('refresh') || 60;
my $daemon	= $cgi->param ('daemon') || "aware_daemon";


my $revSortOrder = "desc";
if ($sortOrder1 eq "desc") { $revSortOrder = "asc"; }

my $sortStr = "$sortCol1 $sortOrder1";
my @sortCols;
my @sortOrders;
push(@sortCols, $sortCol1);
push(@sortOrders, $sortOrder1);

if ($sortOrder2 && $sortCol2) { 
	$sortStr = "$sortStr, $sortCol2 $sortOrder2"; 
	push(@sortCols, $sortCol2); 
	push(@sortOrders, $sortOrder2); 
}
if ($sortOrder3 && $sortCol3) { 
	$sortStr = "$sortStr, $sortCol3 $sortOrder3";
	push(@sortCols, $sortCol3); 
	push(@sortOrders, $sortOrder3); 
}
if ($sortOrder4 && $sortCol4) { 
	$sortStr = "$sortStr, $sortCol4 $sortOrder4"; 
	push(@sortCols, $sortCol4); 
	push(@sortOrders, $sortOrder4); 
}

print "<meta http-equiv=refresh content=\"$refresh;url=$_name?refresh=$refresh&daemon=$daemon&sortCol1=$sortCol1&sortOrder1=$sortOrder1&sortCol2=$sortCol2&sortOrder2=$sortOrder2&sortCol3=$sortCol3&sortOrder3=$sortOrder3&sortCol4=$sortCol4&sortOrder4=$sortOrder4\">\n";
print "<div id=wrapper><center><div id=mainsection>\n";

if ($action eq "add") {
	my $message = add();
	print "<script language=javascript>update_status('$message')</script>\n";
} elsif($action eq "del") {
	my $message = del();
	print "<script language=javascript>update_status('$message')</script>\n";
} elsif($action eq "update") {
	my $message = update();
	print "<script language=javascript>update_status('$message')</script>\n";
}
list();

print "</table></div></center></div>\n";
print "</body></html>\n";

# Disconnect from the database.
$dbh->disconnect();



#
#
# ------------------------------Subroutines----------------------------------
#
#

sub list { 

	my $count = 0;

	print "<table>\n";
	print "<tr><th colspan=6 class=tableheader>Daemon Tasking</th></tr>\n";
	print "<tr><th>Daemon</th><th>Status</th><th>Frequency (seconds)</th><th>Description</th><th>Modify</th><th>Remove</th></tr>\n";
	my $sth = $dbh->prepare("select daemon, status, id, description, frequency from daemon_tasking order by daemon");
	$sth->execute() || die "Database Error: " . $dbh->errstr;
	while (my @row = $sth->fetchrow_array()) {
  		my $rowtype = get_row_type($count);
		my $on = "";
		my $off = "";
		if ($row[1] == 1) { $on = "checked"; }
		if ($row[1] == 0) { $off = "checked"; }

		print "<tr class=$rowtype><form action=$_name method=post>\n";
 		print "<td class=cell><input class=largetext name=daemont value=\"$row[0]\"></td>\n";
		print "<td class=lcell nowrap>";
		print "on <input $on type=radio name=status value=1>";
		print " off<input $off type=radio name=status value=0>";
		print "<input type=hidden name=id value=$row[2]>";
		print "</td>\n";
		print "<td class=cell><input class=mediumtext name=frequency value=$row[4]></td>\n";
		print "<td class=cell><textarea class=smallarea name=description>$row[3]</textarea></td>\n";
		print "<td class=cell><input type=submit value=\"Update\" class=button>\n";
		print "<input type=hidden name=action value=update></form></td>\n";
		print "<td class=cell><form method=post action=$_name>\n";
		print "<input type=submit value=\"Delete\" class=button></td>\n";
		print "<input type=hidden name=action value=del>\n";
		print "<input type=hidden name=id value=\"$row[2]\">\n";
		print "<input type=hidden name=daemont value=$row[0]>\n";
  		print "</form></tr>\n";
 		$count++;
	}
	$sth->finish();
	my $rowtype = get_row_type($count);
	print "<tr class=$rowtype><form action=$_name method=post>\n";
 	print "<td class=cell><input class=largetext name=daemont value=></td>\n";
	print "<td class=lcell nowrap>";
	print "on <input checked type=radio name=status value=1>";
	print " off<input type=radio name=status value=0>";
	print "</td>\n";
 	print "<td class=cell><input class=mediumtext name=frequency value=></td>\n";
	print "<td class=cell><textarea class=smallarea name=description></textarea></td>\n";
	print "<td colspan=2 class=cell><input type=submit value=\"Add Daemon\" class=button>\n";
	print "<input type=hidden name=action value=add></form></td></tr>\n";
	print "</table>\n";

}

sub add {

	my $description = $cgi->param("description");
	$description =~ s/'/''/g;
	my $daemon = $cgi->param("daemont");
	my $status = $cgi->param("status");
	my $frequency = $cgi->param("frequency");
	my $sql = "insert into daemon_tasking (daemon, status, description, frequency) values ('$daemon', $status, '$description', $frequency)";
	$dbh->do($sql);

	my $username = $ENV{'REMOTE_USER'};
	my $agent = $ENV{'HTTP_USER_AGENT'};
	my $ip = $ENV{'REMOTE_ADDR'};
	$sql = "insert into tasking_log (agent, facility, message, updated, ip, username) values ('$agent', 'daemon', 'added daemon: $daemon',  now(), '$ip', '$username')";
	$dbh->do($sql);

	return "$daemon added";
}

sub update {

	my $description = $cgi->param("description");
	$description =~ s/'/''/g;
	my $daemon = $cgi->param("daemont");
	my $id = $cgi->param("id");
	my $status = $cgi->param("status");
	my $frequency = $cgi->param("frequency");
	my $sql = "select count(*) from daemon_tasking where id = '$id'";
	my $sth = $dbh->prepare($sql);
	$sth->execute();
	my @row = $sth->fetchrow();
	my $count = $row[0];
	
	if ($count) {
		$sql = "update daemon_tasking set daemon = '$daemon', status = $status, description = '$description', frequency = $frequency where id = $id";
	} else {
		$sql = "insert into daemon_tasking (daemon, status, description, frequency) values ('$daemon', $status, '$description', $frequency)";
	}
	$dbh->do($sql);

	my $username = $ENV{'REMOTE_USER'};
	my $agent = $ENV{'HTTP_USER_AGENT'};
	my $ip = $ENV{'REMOTE_ADDR'};
	$sql = "insert into tasking_log (agent, facility, message, updated, ip, username) values ('$agent', 'daemon', 'updated daemon: $daemon', now(), '$ip', '$username')";
	$dbh->do($sql);

	return "$daemon updated";
}

sub del {

	my $id = $cgi->param("id");
	my $daemon = $cgi->param("daemont");
	my $sql = "delete from daemon_tasking where id = '$id'";
	$dbh->do($sql);

	my $username = $ENV{'REMOTE_USER'};
	my $agent = $ENV{'HTTP_USER_AGENT'};
	my $ip = $ENV{'REMOTE_ADDR'};
	$sql = "insert into tasking_log (agent, facility, message, updated, ip, username) values ('$agent', 'daemon', 'removed daemon: $daemon', now(), '$ip', '$username')";
	$dbh->do($sql);

	return "$daemon deleted";
}
