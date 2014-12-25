#!/usr/bin/perl -w

# -----------------------------
# $Revision: 1.17 $
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

my $_name = "profiles.cgi"; 
my $_title = "Profile Manager";

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
my $profile_id = $cgi->param('profile_id') || 0;

my @threshold_list = ('maxmem', 'maxdisk', 'maxload', 'maxtemp', 'missedpings', 'maxprocs', 'maxreport', 'missedpolls', 'maxinodes');
my %thresholds;

print "<div id=wrapper><center><div id=mainsection>\n";


if ($action eq "add") {
	my $message = addProfile();
	print "<script language=javascript>update_status('$message')</script>\n";
	$action = "display";
} elsif($action eq "delete") {
	my $message = delProfile();
	print "<script language=javascript>update_status('$message')</script>\n";
} elsif($action eq "update") {
	my $message = updateProfile();
	print "<script language=javascript>update_status('$message')</script>\n";
	$action = "display";
}

my %profiles;
my $sql = "select name, id from profile";
my $sth = $dbh->prepare($sql);
$sth->execute();
while (my @row = $sth->fetchrow()) { $profiles{$row[0]} = $row[1]; }

printTable();

displayProfiles();

print "</table>";
print "</div></center></div>\n";
print "</body></html>\n";

# Disconnect from the database.
$dbh->disconnect();


#
#
# ------------------------------Subroutines----------------------------------
#
#

sub printTable {

	print "<table>\n";
	print "<tr><th colspan=3 class=tableheader>System Profiles</th></tr>\n";
	print "<tr><td colspan=3><hr></td></tr>\n";

	print "<tr><th class=label>Add New Profile</th>";
	print "<form action=profiles.cgi><input type=hidden name=action value=add>";
	print "<td><input class=biggiesizetext name=name></td>";
	print "<td><input class=button type=submit value=\"Add Profile\"></form></td></tr>";
	print "<tr><td colspan=3><hr></td></tr>\n";

	print "<tr><th class=label>Remove Existing Profile</th>";
	print "<form action=profiles.cgi><input type=hidden name=action value=delete>";
	print "<td><select name=profile_id>";
	foreach my $profile (sort(keys(%profiles))) {
		if (!$profiles{$profile}) { next; }
		my $selected = "";
		if ($profiles{$profile} == $profile_id) { $selected = "selected"; }
		print "<option value=$profiles{$profile} $selected>$profile</option>";
	}
	print "</select></td>\n";
	print "<td><input class=button type=submit value=\"Delete Profile\"></form></td></tr>";
	print "<tr><td colspan=3><hr></td></tr>\n";

	print "</table>\n";
				

}


sub displayProfiles { 

	print "<br><hr><br>\n";
	print "<center><font size=-2>";
	print "<i>Note: position the cursor over a column header for more information on the threshold</i>";
	print "</font></center>\n";
	print "<table>\n";
	print "<tr>";
	print "<th>Profile</th>\n";
	print "<th>Description</th>\n";
	print "<th title=\"The maximum numer of reports a node can miss before an alert is raised\">MaxReport</th>\n";
	print "<th title=\"The maximum CPU load that a node can reflect before an alert will be raised\">MaxLoad</th>\n";
	print "<th title=\"The maximum usage % of memory that a node can use before an alert is raised\">MaxMem</th>\n";
	print "<th title=\"The maximum number of processes that can run on a node before an alert is raised\">MaxProcs</th>\n";
	print "<th title=\"The highest usage % (in blocks) that a partition can reach before an alert is raised\">MaxDisk</th>\n";
	print "<th title=\"The highest usage % (in inodes) that a partition can reach before an alert is raised\">MaxInodes</th>\n";
	print "<th title=\"The highest temperature that a node can hit without raising an alert\">MaxTemp</th>\n";
	print "<th title=\"The number of pings a node can fail before an alert is raised\">MissedPings</th>\n";
	print "<th title=\"The number of polls a node can fail before an alert is raised\">MissedPolls</th>\n";
	print "<th>Save Changes</th>\n";
	print "<tr>\n";

	my $sql = "select a.name, a.description, a.id, b.maxmem, b.maxdisk, b.maxload, b.maxtemp, 
		b.missedpings, b.maxprocs, b.maxreport, b.missedpolls, b.maxinodes from profile a, thresholds b
		where a.id = b.profile_id order by a.id";

	my $sth = $dbh->prepare($sql) || print "ERROR ($sql): " . $dbh->errstr;
	$sth->execute() || print "ERROR ($sql): " . $dbh->errstr;

	my $rowcount = 0;
	my $onChange = "onchange=\"input_value_changed(this);\"";
	while (my @row = $sth->fetchrow()) {
		$rowcount++;
		my $profile = $row[0];
		my $description = $row[1];
		my $profile_id = $row[2];
		my $maxmem = $row[3];
		my $maxdisk = $row[4];
		my $maxload = $row[5];
		my $maxtemp = $row[6];
		my $missedpings = $row[7];
		my $maxprocs = $row[8];
		my $maxreport = $row[9];
		my $missedpolls = $row[10];
		my $maxinodes = $row[11];
		
		print "<tr>";
		print "<form action=profiles.cgi method=get>\n";
		print "<input type=hidden name=profile_id value=$profile_id>\n";
		print "<input type=hidden name=action value=update>\n";
		if ($profile_id) {
			print "<td><input $onChange class=mediumtext name=name value=\"$profile\"></input></td>\n";
			print "<td><textarea $onChange name=description>$description</textarea></td>\n";
		} else {
			print "<td class=cell><b>" . uc($profile) . "</b></td>\n";
			print "<td class=cell><b>" . uc($description) . "</b></td>\n";
			print "<input type=hidden name=name value=\"default\">\n";
			print "<input type=hidden name=description value=\"the default profile\">\n";
		}
		print "<td><input $onChange class=smalltext name=maxreport value=\"$maxreport\"></input></td>\n";
		print "<td><input $onChange class=smalltext name=maxload value=\"$maxload\"></input></td>\n";
		print "<td><input $onChange class=smalltext name=maxmem value=\"$maxmem\"></input></td>\n";
		print "<td><input $onChange class=smalltext name=maxprocs value=\"$maxprocs\"></input></td>\n";
		print "<td><input $onChange class=smalltext name=maxdisk value=\"$maxdisk\"></input></td>\n";
		print "<td><input $onChange class=smalltext name=maxinodes value=\"$maxinodes\"></input></td>\n";
		print "<td><input $onChange class=smalltext name=maxtemp value=\"$maxtemp\"></input></td>\n";
		print "<td><input $onChange class=smalltext name=missedpings value=\"$missedpings\"></input></td>\n";
		print "<td><input $onChange class=smalltext name=missedpolls value=\"$missedpolls\"></input></td>\n";
		print "<td><input type=submit class=button value=\"SAVE\"></td>\n";
		print "</form>\n";
		print "</tr>\n";

		if (!$profile_id) {
			print "<tr><td colspan=\"100%\"><hr></td></tr>\n";
		}
	}


	print "</table>\n";
	print "<br>";

}

sub addProfile {

	my $name = $cgi->param("name");
	my $sql = "insert into profile (name) values ('$name')";
	$dbh->do($sql) || print "ERROR ($sql): " . $dbh->errstr;

	$sql = "select id from profile where name = '$name'";
	my $sth = $dbh->prepare($sql);
	$sth->execute();
	my @row = $sth->fetchrow();
	my $id = $row[0];

	$profile_id = $id;
	$sql = "insert into thresholds (profile_id) values ($profile_id)";
	$dbh->do($sql) || print "ERROR ($sql): " . $dbh->errstr;

	foreach my $thresh (@threshold_list) {

		my $tvalue = get_profile_threshold($dbh, "default", $thresh);
		my $sql = "update thresholds set $thresh = $tvalue where profile_id = $profile_id"; 
		$dbh->do($sql) || print "ERROR ($sql): " . $dbh->errstr;
	}
	$dbh->commit();
	
	return "\"$name\" profile added";
}

sub updateProfile {

	my $description = $cgi->param("description");
	$description =~ s/'/''/g;

	my $name = $cgi->param("name");

	my $sql = "update profile set description = '$description', name = '$name' where id = $profile_id"; 
	$dbh->do($sql) || print "ERROR ($sql): " . $dbh->errstr;

	foreach my $thresh (@threshold_list) {
		my $tvalue = $cgi->param("$thresh") || 0;
		my $sql = "update thresholds set $thresh = $tvalue where profile_id = $profile_id"; 
		$dbh->do($sql) || print "ERROR ($sql): " . $dbh->errstr;
	}
	$dbh->commit();

	return "\"$name\" profile updated";
}

sub delProfile {

	my $sql = "select name from profile where id = '$profile_id'";
	my $sth = $dbh->prepare($sql);
	$sth->execute();
	my @row = $sth->fetchrow();
	my $name = $row[0];

	if ($profile_id == 0) {
		return "not deleting 'default' profile";
	}

	$sql = "delete from profile where id = '$profile_id'";
	$dbh->do($sql) || print "ERROR ($sql): " . $dbh->errstr;

	$sql = "delete from thresholds where profile_id = '$profile_id'";
	$dbh->do($sql) || print "ERROR ($sql): " . $dbh->errstr;

	$sql = "update node set profile_id = 0 where profile_id = $profile_id";
	$dbh->do($sql) || print "ERROR ($sql): " . $dbh->errstr;
	$dbh->commit();

	return "\"$name\" profile deleted";
}


