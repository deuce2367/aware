#!/usr/bin/perl -w

# ------------------------------------------------------------
# $Id: alert.cgi,v 1.16 2008-04-08 14:35:30 aps1 Exp $
# $RCSfile: alert.cgi,v $
# $Revision: 1.16 $
# $Date: 2008-04-08 14:35:30 $
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
my $_name = "alerts.cgi"; 
my $_title = "Alerts";

# -------------------------------------------------------------------
# Begin Script
# -------------------------------------------------------------------
my $cgi = new CGI;

my $action = $cgi->param('action') || "default";
my $type = $cgi->param('type');
my $updated = $cgi->param('updated');
my $skip = $cgi->param('skip') || 0;
my $maxCount = $cgi->param('maxCount') || 20;
my $displayHost = $cgi->param('displayHost') || "%";
my $popup = $cgi->param('popup') || 0;

if ($popup) {
	print_header_simple($_title, $_name, 0);
} else {
	print_header($_title, $_name, 0);
}
my $dbh = get_db_connection(0);
if (!defined($dbh)) {
	print "<p class=alert>Unable to connect to DB</p>\n";
	exit();
}


my $limit = $skip + $maxCount;
my $limitClause = "and b.id = '$displayHost'";
if ($displayHost eq "%") {
	$limitClause = "";
}

print "<div id=wrapper><center><div id=mainsection>\n";

if ($action eq "add") {
	my $message = addAlert();
	print "<script language=javascript>update_status('$message')</script>\n";
} elsif($action eq "del") {
	my $message = delAlert();
	print "<script language=javascript>update_status('$message')</script>\n";
} elsif($action eq "clear") {
	my $message = clearAlert();
	print "<script language=javascript>update_status('$message')</script>\n";
} elsif($action eq "clearAll") {
	my $message = clearAll();
	print "<script language=javascript>update_status('$message')</script>\n";
}
print "<table>\n";

listAlerts();

print "</table>";
if ($popup) { print "<br><table><tr><td><input type=button class=button onClick=\"window.close()\" value=\"Close\"></td></tr></table>\n"; }
print "</div></center></div>\n";
print "</body></html>\n";

# Disconnect from the database.
$dbh->disconnect();



#
#
# ------------------------------Subroutines----------------------------------
#
#

sub listAlerts { 
	# Now retrieve data from the table.
	my $sql = "select count(*) from alert where hostid = $displayHost";
	if ($displayHost eq "%") {
		$sql = "select count(*) from alert";
	}
	my $sth = $dbh->prepare($sql) || print "<font class=alert>Error($sql): " . $dbh->errstr . "</font>\n";
	$sth->execute();
	my @row = $sth->fetchrow_array();
	my $rowCount = $row[0];
	$sth->finish();

	my $shown = $maxCount;
	if ($rowCount - $skip < $maxCount) {
		$shown = $rowCount - $skip;
	}
	my $start = $skip + 1;
	my $stop = $skip + $shown;

	my $backwards = "<a href=alert.cgi?skip=$skip&displayHost=$displayHost&maxCount=$maxCount&popup=$popup><img border=0 src=images/left.png></a>";
	my $forwards = "<a href=alert.cgi?skip=$skip&displayHost=$displayHost&maxCount=$maxCount&popup=$popup><img border=0 src=images/right.png></a>";

	if ($stop < $rowCount) {
		my $skipForward = $stop;
		$forwards = "<a href=alert.cgi?skip=$skipForward&displayHost=$displayHost&maxCount=$maxCount&popup=$popup><img border=0 src=images/right.png></a>";
	}		
	if ($start > 1) {
		my $skipBackward = $start - $maxCount - 1;
		if ($skipBackward < 0) { $skipBackward = 0; }
		$backwards = "<a href=alert.cgi?skip=$skipBackward&displayHost=$displayHost&maxCount=$maxCount&popup=$popup><img border=0 src=images/left.png></a>";
	}		
		
	print "<tr><th class=tableheader colspan=8>Alert Log</th></tr>\n";
	print "<tr><th colspan=3>Date</th><th>Host</th><th nowrap>Alert Type</th><th>Alert</th>\n";
	if ($rowCount) {
		print "<th colspan=2 nowrap>$backwards ($start - $stop) of $rowCount $forwards</th>\n";
	} else {
		print "<th colspan=2 nowrap></th>\n";
	}


	my $count = 0;
	my $printed = 0;
	my $printHeader = 1;
	my $hostid;
	my $hostname;
	
	$sql = "select a.hostid, a.type, a.message, date_format(a.updated, '%M %D, %Y<br> %H:%i:%s'), a.updated, b.hostname, a.display
		from alert a, node b where a.hostid = b.id $limitClause order by a.updated desc limit $limit";
	$sth = $dbh->prepare($sql) || print "<font class=alert>Error($sql): " . $dbh->errstr . "</font>\n";
	$sth->execute() || print "<font class=alert>Error($sql): " . $dbh->errstr . "</font>\n";
 
	while ((my @row = $sth->fetchrow_array()) && $printed < $maxCount) {
  		my $rowtype = get_row_type($count);
 		$count++;
		if ($count > $skip) {
			$printed++;

			$hostid = $row[0];
			my $type = $row[1];
			my $alert = $row[2];
			my $datetime = $row[3];
			my $updated = $row[4];
			$hostname = $row[5];
			$hostname =~ s/\..*//g;
			my $display = $row[6] || 0;

			my $displayImg = "&nbsp;";

			if ($display) { $displayImg = "<img src=images/eventnew.png border=0>"; }

			print "<tr class=$rowtype>\n";
 			print "<td class=\"cell\" nowrap>$count</td>\n";
			print "<td>$displayImg</td>\n";
 			print "<td class=cell nowrap>$datetime</td>\n";
 			print "<td class=cell nowrap>$hostname</td>\n";
 			print "<td class=cell nowrap>$type</td>\n";
			print "<td class=lcell nowrap>$alert</td>\n";
			print "<td class=cell>";
			if ($display) {
				print "<form action=alert.cgi method=post>\n";
				print "<input type=submit value=\"Clear\" class=button></td>\n";
				print "<input type=hidden name=action value=clear>\n";
				print "<input type=hidden name=hostid value=$hostid>\n";
				print "<input type=hidden name=skip value=$skip>\n";
				print "<input type=hidden name=maxCount value=$maxCount>\n";
				print "<input type=hidden name=displayHost value=$displayHost>\n";
				print "<input type=hidden name=type value=$type>\n";
				print "<input type=hidden name=popup value=$popup>\n";
				print "<input type=hidden name=updated value=\"$updated\">\n";
  				print "</form>";
			}
			print "</td>\n";
			print "<td class=cell>";
			print "<form action=alert.cgi method=post>\n";
			print "<input type=submit value=\"Delete\" class=button></td>\n";
			print "<input type=hidden name=action value=del>\n";
			print "<input type=hidden name=hostid value=$hostid>\n";
			print "<input type=hidden name=skip value=$skip>\n";
			print "<input type=hidden name=maxCount value=$maxCount>\n";
			print "<input type=hidden name=displayHost value=$displayHost>\n";
			print "<input type=hidden name=type value=$type>\n";
			print "<input type=hidden name=popup value=$popup>\n";
			print "<input type=hidden name=updated value=\"$updated\">\n";
  			print "</form></td>\n";
			print "</tr>\n";
		}
	}
	$sth->finish();

	if (!$count) {
		print "<tr class=even><td class=cell colspan=100%>No Entries</td></tr>\n";
	}

	print "<tr><td colspan=6>&nbsp;</td>";

	print "<td class=cell>\n";
	print "<form action=alert.cgi>\n";
	print "<input  type=hidden name=hostid value=$displayHost>\n";
	print "<input type=hidden name=type value=%>\n";
	print "<input type=hidden name=displayHost value=$displayHost>\n";
	print "<input type=hidden name=skip value=$skip>\n";
	print "<input type=hidden name=maxCount value=$maxCount>\n";
	print "<input type=hidden name=updated value=%>\n";
	print "<input type=hidden name=popup value=$popup>\n";
	print "<input type=hidden name=action value=clearAll>\n";
	if ($displayHost eq "%") {
		print "<input type=submit class=button value=\"Clear All Alerts\"></form>\n";
	} else {
		print "<input type=submit class=button value=\"Clear All\"></form>\n";
	}
	print "</form></td>\n";

	print "<td class=cell>\n";
	print "<form action=alert.cgi>\n";
	print "<input  type=hidden name=hostid value=$displayHost>\n";
	print "<input type=hidden name=type value=%>\n";
	print "<input type=hidden name=displayHost value=$displayHost>\n";
	print "<input type=hidden name=skip value=$skip>\n";
	print "<input type=hidden name=maxCount value=$maxCount>\n";
	print "<input type=hidden name=popup value=$popup>\n";
	print "<input type=hidden name=updated value=%>\n";
	print "<input type=hidden name=action value=del>\n";
	if ($displayHost eq "%") {
		print "<input type=submit class=button value=\"Delete All Alerts\"></form>\n";
	} else {
		print "<input type=submit class=button value=\"Delete All\"></form>\n";
	}

	print "</tr>\n";

}

sub clearAll {
	my $hostid  = $cgi->param("hostid");
	my $whereStr = "where hostid = $hostid";
	if ($hostid eq "%") { $whereStr = ""; }
	my $sql = "update alert set display = 0 $whereStr";
	my $sth = $dbh->prepare($sql);
	my $rowcount = $sth->execute();
	$sth->finish();
	$sth->finish();
	$dbh->commit();

	updateAlerts();

	return "$rowcount alert(s) cleared";
}

sub clearAlert {
	my $hostid  = $cgi->param("hostid");
	my $whereStr = "where hostid = $hostid and type = '$type' and updated = '$updated'";
	if ($hostid eq "%") { $whereStr = ""; }
	my $sql = "update alert set display = 0 $whereStr";
	my $sth = $dbh->prepare($sql);
	my $rowcount = $sth->execute();
	$sth->finish();
	$dbh->commit();

	updateAlerts();

	return "$rowcount alert(s) cleared";
}

sub delAlert {

	my $hostid = $cgi->param("hostid");
	my $whereStr = "where hostid = $hostid and type = '$type' and updated = '$updated'";
	if ($hostid eq "%") { $whereStr = ""; }
	my $display = $cgi->param("display");
	my $sql = "delete from alert $whereStr";
	my $sth = $dbh->prepare($sql);
	my $rowcount = $sth->execute();
	$sth->finish();
	$dbh->commit();

	updateAlerts();

	return "$rowcount alert(s) deleted";
}

sub updateAlerts {

	my $sql = "select sum(b.display), a.id from node a left join alert b on a.id = b.hostid group by a.id";
	my $sth = $dbh->prepare($sql);
	$sth->execute();
	while (my @row = $sth->fetchrow()) {
		my $count = $row[0] || 0; 
		my $hostid = $row[1];
		$dbh->do("update node set alert = $count where id = $hostid");
	}
	$sth->finish();
	$dbh->commit();

}

