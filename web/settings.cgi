#!/usr/bin/perl -w

# -----------------------------
# $Revision: 1.11 $
# $Date: 2008-07-22 20:55:52 $
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

my $_name = "settings.cgi"; 
my $_title = "AWARE Settings";

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

my $action = $cgi->param('action') || "default";

print "<div id=wrapper><center><div id=mainsection>\n";

if ($action eq "add") {
	my $message = addThreshold();
	print "<script language=javascript>update_status('$message')</script>\n";
} elsif($action eq "del") {
	my $message = delThreshold();
	print "<script language=javascript>update_status('$message')</script>\n";
} elsif($action eq "update") {
	my $message = updateThreshold();
	print "<script language=javascript>update_status('$message')</script>\n";
}
print "<table>\n";
print "<tr><th colspan=5 class=tableheader>AWARE System Variables</th></tr>\n";
listThresholds();

print "</table>";
print "</div></center></div>\n";
print "</center></body></html>\n";

# Disconnect from the database.
$dbh->disconnect();



#
#
# ------------------------------Subroutines----------------------------------
#
#

sub listThresholds { 


	# Now retrieve data from the table.
	my $sth = $dbh->prepare("select count(*) from checklist");
	$sth->execute();
	my @row = $sth->fetchrow_array();
	my $rowCount = $row[0];
	$sth->finish();

	my $count = 0;
	my $printHeader = "yes";

	$sth = $dbh->prepare("select label, value, id, description from settings order by label");
	$sth->execute() || die "Error retrieving data...";
	while (my @row = $sth->fetchrow_array()) {
  		my $rowtype = "odd";
  		if ($count % 2 == 1) { $rowtype = "even"; }
		if ($printHeader eq "yes") {
			print "<tr><th>Name</th><th>Value</th><th>Description</th><th>Modify</th><th>Remove</th></tr>\n";
			$printHeader = "no";
		}
		print "<tr class=$rowtype><form action=settings.cgi method=post>\n";
 		print "<td class=cell><input class=hugetext name=label value=\"$row[0]\"></td>\n";
		print "<td class=lcell><input class=mediumtext name=value value=\"$row[1]\"></td>\n";
		print "<input type=hidden name=id value=\"$row[2]\"></td>\n";
		print "<td class=cell><textarea name=description>$row[3]</textarea></td>\n";
		print "<td class=cell><input type=submit value=\"Update\" class=button>\n";
		print "<input type=hidden name=action value=update></form></td>\n";
		print "<td class=cell><form method=post action=settings.cgi>\n";
		print "<input type=submit value=\"Delete\" class=button></td>\n";
		print "<input type=hidden name=action value=del>\n";
		print "<input type=hidden name=id value=\"$row[2]\">\n";
		print "<input type=hidden name=label value=$row[0]>\n";
  		print "</form></tr>\n";
 		$count++;
	}
	$sth->finish();
	my $rowtype = get_row_type($count);
	print "<tr class=$rowtype><form action=settings.cgi method=post>\n";
 	print "<td class=cell><input class=hugetext name=label value=></td>\n";
	print "<td class=lcell><input class=mediumtext name=value value=></td>\n";
	print "<td class=cell><textarea name=description></textarea></td>\n";
	print "<td colspan=2 class=cell><input type=submit value=\"Add Variable\" class=button>\n";
	print "<input type=hidden name=action value=add></form></td></tr>\n";

}

sub addThreshold {

	my $description = $cgi->param("description");
	$description =~ s/'/''/g;
	my $label = $cgi->param("label");
	my $value = $cgi->param("value");
	my $sql = "insert into settings (label, value, description) values ('$label', '$value', '$description')";
	$dbh->do($sql);

	my $username = $ENV{'REMOTE_USER'};
	my $agent = $ENV{'HTTP_USER_AGENT'};
	my $ip = $ENV{'REMOTE_ADDR'};
	$sql = "insert into tasking_log (agent, facility, message, updated, ip, username) values ('$agent', 'settings', 'added variable: $label', now(), '$ip', '$username')";
	$dbh->do($sql);

	return "$label added";
}

sub updateThreshold {

	my $description = $cgi->param("description");
	$description =~ s/'/''/g;
	my $label = $cgi->param("label");
	my $id = $cgi->param("id");
	my $value = $cgi->param("value");
	my $sql = "select count(*) from settings where id = '$id'";
	my $sth = $dbh->prepare($sql);
	$sth->execute();
	my @row = $sth->fetchrow();
	my $count = $row[0];
	
	if ($count) {
		$sql = "update settings set label = '$label', value = '$value', description = '$description' where id = $id";
	} else {
		$sql = "replace into settings (label, value, description) values ('$label', '$value', '$description')";
	}
	$dbh->do($sql);

	my $username = $ENV{'REMOTE_USER'};
	my $agent = $ENV{'HTTP_USER_AGENT'};
	my $ip = $ENV{'REMOTE_ADDR'};
	$sql = "insert into tasking_log (agent, facility, message, updated, ip, username) values ('$agent', 'settings', 'modified variable: $label', now(), '$ip', '$username')";
	$dbh->do($sql);

	return "$label updated";
}

sub delThreshold {

	my $id = $cgi->param("id");
	my $label = $cgi->param("label");
	my $sql = "delete from settings where id = '$id'";
	$dbh->do($sql);

	my $username = $ENV{'REMOTE_USER'};
	my $agent = $ENV{'HTTP_USER_AGENT'};
	my $ip = $ENV{'REMOTE_ADDR'};
	$sql = "insert into tasking_log (agent, facility, message, updated, ip, username) values ('$agent', 'settings', 'deleted variable: $label', now(), '$ip', '$username')";
	$dbh->do($sql);

	return "$label deleted";
}
