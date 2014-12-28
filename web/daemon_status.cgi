#!/usr/bin/perl -w

# ------------------------------------------------------------
# $Id: daemon_status.cgi,v 1.13 2006-09-18 12:55:55 aps1 Exp $
# $RCSfile: daemon_status.cgi,v $
# $Revision: 1.13 $
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
my $_name = "daemon_status.cgi"; 
my $_title = "Daemon Status";

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
my $sortCol1 	= $cgi->param ('sortCol1') || "node.hostname";
my $sortOrder1 	= $cgi->param ('sortOrder1') || "asc";
my $sortCol2 	= $cgi->param ('sortCol2') || "node.hostname";
my $sortOrder2	= $cgi->param ('sortOrder2') || "asc";
my $sortCol3 	= $cgi->param ('sortCol3') || "node.hostname";
my $sortOrder3	= $cgi->param ('sortOrder3') || "asc";
my $sortCol4 	= $cgi->param ('sortCol4') || "node.hostname";
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

print "<meta http-equiv=refresh content=\"$refresh;url=daemon_status.cgi?refresh=$refresh&daemon=$daemon&sortCol1=$sortCol1&sortOrder1=$sortOrder1&sortCol2=$sortCol2&sortOrder2=$sortOrder2&sortCol3=$sortCol3&sortOrder3=$sortOrder3&sortCol4=$sortCol4&sortOrder4=$sortOrder4\">\n";
print "<div id=wrapper><center><div id=mainsection>\n";

printStatus();

print "</table></div></center></div>\n";
print "</body></html>\n";

# Disconnect from the database.
$dbh->disconnect();



#
#
# ------------------------------Subroutines----------------------------------
#
#

sub printStatus {


	my @daemons;
	my @daemons_v;
	my $sql = "select daemon from daemon_tasking order by daemon";
	my $sth = $dbh->prepare($sql);
	$sth->execute();
	while (my @row = $sth->fetchrow()) { push(@daemons, $row[0]); push(@daemons_v, $row[0]); }
	push(@daemons, "all");
	push(@daemons_v, "%");

	print "<table>\n";
	print "<form action=daemon_status.cgi method=post>\n";
	print "<tr>\n";
	print "<th>Daemon:</th>\n";
	print "<td><select name=daemon>\n";
	
	for (my $i = 0; $i <= $#daemons; $i++) {
		my $selected = "";
		if ($daemon eq $daemons_v[$i]) {
			$selected = "selected";
		}
		print "<option value=\"$daemons_v[$i]\" $selected>$daemons[$i]</option>\n";
	}
	print "</select>\n";
	print "</td>\n";
	print "<th>Refresh Every:</th>\n";
	print "<td><select name=refresh>\n";
	my @options = ('Never', '15 Seconds', '30 Seconds', '60 Seconds', '90 Seconds', '5 Minutes');
	my @values = ('-1', '15', '30', '60', '90', '300');
	for (my $i = 0; $i <= $#options; $i++) {
		my $selected = "";
		if ($refresh eq $values[$i]) {
			$selected = "selected";
		}
		print "<option value=\"$values[$i]\" $selected>$options[$i]</option>\n";
	}
	print "</select>\n";
	print "</td>\n";
	
	print "<td><input type=hidden name=message value=\"Display Changed\"><input class=button type=submit value=\"Update Page\"></td>\n";
	print "</form></tr>\n";
	print "</table><br>\n";
	
	print "<table>\n";
	
	$sql = "select node.hostname, daemon.status, daemon.updated, daemon.name, unix_timestamp(now()) - unix_timestamp(daemon.updated) as age, daemon.version from node, daemon where node.id = daemon.hostid and daemon.name like '$daemon' order by $sortStr";
	$sth = $dbh->prepare($sql);
	$sth->execute();
	print "<tr>\n";
	print "<th class=tableheader colspan=7>Daemon Status</th>\n";
	print "</tr>\n"; 
	print "<tr>\n";
	my $i = 0;
	if ($sortCol1 eq "node.hostname") { $i = 1};  
	my $fieldClass = "sortField";
	if ($sortCol1 eq "node.hostname" && $sortOrder1 eq "desc") { $fieldClass = "sortFieldDesc"; }
	if ($sortCol1 eq "node.hostname" && $sortOrder1 eq "asc") { $fieldClass = "sortFieldAsc"; }
	print "<th nowrap colspan=2><p class=$fieldClass><a class=sortCol href=daemon_status.cgi?daemon=$daemon&sortCol1=node.hostname&sortOrder1=$revSortOrder&sortCol2=$sortCols[$i]&sortOrder2=$sortOrders[$i++]&sortCol3=$sortCols[$i]&sortOrder3=$sortOrders[$i++]&sortCol4=$sortCols[$i]&sortOrder4=$sortOrders[$i]>Hostname</a></th>\n";
	
	$i = 0;
	if ($sortCol1 eq "daemon.name") { $i = 1};  
	$fieldClass = "sortField";
	if ($sortCol1 eq "daemon.name" && $sortOrder1 eq "desc") { $fieldClass = "sortFieldDesc"; }
	if ($sortCol1 eq "daemon.name" && $sortOrder1 eq "asc") { $fieldClass = "sortFieldAsc"; }
	print "<th nowrap><p class=$fieldClass><a class=sortCol href=daemon_status.cgi?daemon=$daemon&sortCol1=daemon.name&sortOrder1=$revSortOrder&sortCol2=$sortCols[$i]&sortOrder2=$sortOrders[$i++]&sortCol3=$sortCols[$i]&sortOrder3=$sortOrders[$i++]&sortCol4=$sortCols[$i]&sortOrder4=$sortOrders[$i]>Daemon</a></th>\n";

	$i = 0;
	if ($sortCol1 eq "daemon.version") { $i = 1};  
	$fieldClass = "sortField";
	if ($sortCol1 eq "daemon.version" && $sortOrder1 eq "desc") { $fieldClass = "sortFieldDesc"; }
	if ($sortCol1 eq "daemon.version" && $sortOrder1 eq "asc") { $fieldClass = "sortFieldAsc"; }
	print "<th nowrap><p class=$fieldClass><a class=sortCol href=daemon_status.cgi?daemon=$daemon&sortCol1=daemon.version&sortOrder1=$revSortOrder&sortCol2=$sortCols[$i]&sortOrder2=$sortOrders[$i++]&sortCol3=$sortCols[$i]&sortOrder3=$sortOrders[$i++]&sortCol4=$sortCols[$i]&sortOrder4=$sortOrders[$i]>Version</a></th>\n";
	
	
	$i = 0;
	if ($sortCol1 eq "status") { $i = 1};  
	$fieldClass = "sortField";
	if ($sortCol1 eq "status" && $sortOrder1 eq "desc") { $fieldClass = "sortFieldDesc"; }
	if ($sortCol1 eq "status" && $sortOrder1 eq "asc") { $fieldClass = "sortFieldAsc"; }
	print "<th nowrap><p class=$fieldClass><a class=sortCol href=daemon_status.cgi?daemon=$daemon&sortCol1=status&sortOrder1=$revSortOrder&sortCol2=$sortCols[$i]&sortOrder2=$sortOrders[$i++]&sortCol3=$sortCols[$i]&sortOrder3=$sortOrders[$i++]&sortCol4=$sortCols[$i]&sortOrder4=$sortOrders[$i]>Status</a></th>\n";
	
	
	$i = 0;
	if ($sortCol1 eq "updated") { $i = 1};  
	$fieldClass = "sortField";
	if ($sortCol1 eq "updated" && $sortOrder1 eq "desc") { $fieldClass = "sortFieldDesc"; }
	if ($sortCol1 eq "updated" && $sortOrder1 eq "asc") { $fieldClass = "sortFieldAsc"; }
	print "<th nowrap><p class=$fieldClass><a class=sortCol href=daemon_status.cgi?daemon=$daemon&sortCol1=updated&sortOrder1=$revSortOrder&sortCol2=$sortCols[$i]&sortOrder2=$sortOrders[$i++]&sortCol3=$sortCols[$i]&sortOrder3=$sortOrders[$i++]&sortCol4=$sortCols[$i]&sortOrder4=$sortOrders[$i]>Updated</a></th>\n";
	
	$i = 0;
	if ($sortCol1 eq "age") { $i = 1};  
	$fieldClass = "sortField";
	if ($sortCol1 eq "age" && $sortOrder1 eq "desc") { $fieldClass = "sortFieldDesc"; }
	if ($sortCol1 eq "age" && $sortOrder1 eq "asc") { $fieldClass = "sortFieldAsc"; }
	print "<th nowrap><p class=$fieldClass><a class=sortCol href=daemon_status.cgi?daemon=$daemon&sortCol1=age&sortOrder1=$revSortOrder&sortCol2=$sortCols[$i]&sortOrder2=$sortOrders[$i++]&sortCol3=$sortCols[$i]&sortOrder3=$sortOrders[$i++]&sortCol4=$sortCols[$i]&sortOrder4=$sortOrders[$i]>Age</a></th>\n";


	print "</tr>\n"; my $count = 0;
	while (my @row = $sth->fetchrow_array ()) {
		my $rowtype = "odd";
   	 	if ($count % 2 == 1) {
   	 		$rowtype = "even";
		}
		$count++;
	
		my $hostname = $row[0];
		$hostname =~ s/\..*//g;
		my $status = $row[1];
		my $updated = $row[2];
		my $name = $row[3];
		my $age = $row[4];
		my $version = $row[5];

    	print "<tr class=$rowtype>\n";
		print "<td class=cell>$count</td>\n";
		print "<td class=cell>$hostname</td>\n";
		print "<td class=cell>$name</td>\n";
		print "<td class=cell nowrap>$version</td>\n";
		print "<td class=lcell nowrap>$status</td>\n";
		print "<td class=cell nowrap>$updated</td>\n";
		print "<td class=cell>$age s.</td>\n";
		print "</tr>\n"; 
	}
	$sth->finish ();
	print "</table>\n";

}

