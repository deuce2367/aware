#!/usr/bin/perl -w

# -----------------------------
# $Revision: 1.15 $
# $Date: 2007-11-03 15:02:39 $
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

my $_name = "update.cgi"; 
my $_title = "Node Editor";

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

my %profiles;
my $sql = "select name, id from profile order by name";
my $sth = $dbh->prepare($sql);
$sth->execute();
while (my @row = $sth->fetchrow()) { $profiles{$row[0]} = $row[1]; }

my $hostid = $cgi->param('hostid');
if ($action && $action eq "update") {
	my $message = update();
	print "<script language=javascript>update_status('$message')</script>\n";
	listNodes();
} elsif ($action eq "addNode") {
	addNode();
} else {
	listNodes();
}

print "</table>\n";
print "</div></center></div>\n";
print "</body></html>\n";

# Disconnect from the database.
$dbh->disconnect();


sub listNodes { 
	
		if (!defined($hostid)) { $hostid = "%"; }
	
	print "<div id=wrapper><center><div id=mainsection>\n";
	print "<table>\n<form method=post action=update.cgi>\n";
	
	# Now retrieve data from the table.
	my $sql = "SELECT macaddr,hostname,ipaddr,port,profile_id,rack,hostid,password,ilomac,iloaddr,iloport,idx,online
		FROM node where id like '$hostid' order by idx, profile_id, hostname";
	my $sth = $dbh->prepare($sql);
	$sth->execute();
	print "<tr><th class=tableheader colspan=13>Edit Nodes</th></tr>\n";
	print "<tr>\n";
	#print "<th>MAC Address</th>\n";
	print "<th>Hostname</th>\n";
	print "<th>Hostid</th>\n";
	print "<th>IP Address</th>\n";
	print "<th>Profile</th>\n";
	print "<th>Polling Port(s)</th>\n";
	print "<th>SortID</th>\n";
	print "<th>Rack #</th>\n";
	print "<th>Enabled</th>\n";
	print "<th>Password</th>\n";
	#print "<th>ILO MAC</th>\n";
	print "<th>ILO IP</th>\n";
	#print "<th>ILO Port</th>\n";
	print "</tr>\n";
	
	my $count = 0;
	my $onChange = "onchange=\"input_value_changed(this);\"";
	while (my @row = $sth->fetchrow_array()) {
	  my $rowtype = "odd";
	  if ($count % 2 == 1) { 
		$rowtype = "even"; 
	  }

		my $macaddr = $row[0] || "";
		my $hostname = $row[1] || "";
		my $ipaddr = $row[2] || "";
		my $port = $row[3] || "";
		my $profile_id = $row[4] || "";
		my $rack = $row[5] || "";
		my $hostid = $row[6] || "";
		my $password = $row[7] || "";
		my $ilomac = $row[8] || "";
		my $iloaddr = $row[9] || "";
		my $iloport = $row[10] || "";
		my $idx = $row[11] || "";
		my $online = $row[12] || "";




	  print "<tr class=$rowtype>\n";
          print "<input type=hidden name=hostid_$count value=\"$hostid\">\n";
	  print "<td>$hostname</td>\n";
	  print "<td>$hostid</td>\n";
	  print "<td>$ipaddr</td>\n";
	
	  print "<td $onChange class=cell><select class=medselect name=profile_$count>\n";
	  foreach my $profile (sort(keys(%profiles))) {
		my $selected = "";
		if ($profile_id == $profiles{$profile}) { $selected = "selected"; }
		print "<option value=\"$profiles{$profile}\" $selected>$profile</option>\n";
	  }
	  print "</select>\n";
	  print "</td>\n";
	
	  print "<td $onChange class=cell><input class=mediumtext type=text name=port_$count value=\"$port\"></td>\n";
	  print "<td $onChange class=hlcell><input class=tinytext type=text name=idx_$count value=\"$idx\"></td>\n";
	  print "<td $onChange class=cell><input class=tinytext type=text name=rack_$count value=\"$rack\"></td>\n";

	  print "<td $onChange class=cell><select class=medselect name=online_$count>\n";
	  if ($online) {
		  print "<option value=1 selected>on-line</option><option value=0>off-line</option>\n";
	  } else {
		  print "<option value=1>on-line</option><option value=0 selected>off-line</option>\n";
	  }
	  print "</select>\n";
	  print "</td>\n";

	  print "<td $onChange class=cell><input class=mediumtext type=text name=password_$count value=\"$password\"></td>\n";
	  print "<td $onChange class=cell><input class=supersizetext type=text name=ilomac_$count value=\"$ilomac\"></td>\n";
	  print "</tr>\n";
	  $count++;
	}
	$sth->finish();
	
	print "<tr><td colspan=13 class=cell>\n";
	print "<input type=hidden name=rowcount value=$count>\n";
	print "<input type=hidden name=action value=update>\n";
	print "<input type=hidden name=hostid value=$hostid>\n";
	print "<input class=button value=\"Update\" type=submit>\n";
	print "<input class=button type=reset value=\"Reset Form\">\n";
	print "</form>\n";
	print "</td></tr>\n";
	
}


sub addNode {
	my $count = 0;
	
	my $hostid = $cgi->param('hostid');
	my $macaddr = "";
	my $hostname = "";
	my $ipaddr = "";
	my $port = "";
	my $profile = "";
	my $idx = "";
	my $rack = "";
	my $online = "";
	my $password = "";
	my $ilomac = "";
	my $iloaddr = "";
	my $iloport = "";
	
	if ($hostid) {
	
		my $sql = "select macaddr, hostname, ipaddr, port, profile, idx, rack, online, password, ilomac, iloaddr, iloport from node where hostid = '$hostid'"; 
		my $sth = $dbh->prepare($sql);
		$sth->execute();
		my @row = $sth->fetchrow();
		$macaddr = $row[0];
		$hostname = $row[1];
		$ipaddr = $row[2];
		$port = $row[3];
		$profile = $row[4];
		$idx = $row[5];
		$rack = $row[6];
		$online = $row[7];
		$password = $row[8];
		$ilomac = $row[9];
		$iloaddr = $row[10];
		$iloport = $row[11];
		$sth->finish();
		$dbh->commit();
	}
	
	print "<center><div id=mainsection>\n";
	print "<table>\n<form method=post action=update.cgi>\n";
	print "<tr>\n";
	print "<th class=tableheader colspan=13>Add Node</th>\n";
	print "</tr>\n";
	print "<tr>\n";
	print "<th>MAC Address</th>\n";
	print "<th>Hostname</th>\n";
	print "<th>IP Address</th>\n";
	print "<th>Profile</th>\n";
	print "<th>Polling Port(s)</th>\n";
	print "<th>Index</th>\n";
	print "<th>Rack #</th>\n";
	print "<th>Status</th>\n";
	print "<th>Hostid</th>\n";
	print "<th>Password</th>\n";
	print "<th>ILO MAC</th>\n";
	print "<th>ILO IP</th>\n";
	print "<th>ILO Port</th>\n";
	print "</tr>\n";
	print "<tr class=even>\n";
	print "<td class=hlcell><input class=supersizetext type=text name=macaddr_$count value=\"$macaddr\"> </td>\n";
	print "<td class=hlcell><input class=smalltext type=text name=hostname_$count value=\"$hostname\"> </td>\n";
	print "<td class=cell><input class=largetext type=text name=ipaddr_$count value=\"$ipaddr\"> </td>\n";
	
	print "<td class=cell><select class=medselect name=profile_$count>\n";
	foreach my $profile (sort(keys(%profiles))) {
		my $selected = "";
		if ($profile eq $profiles{$profile}) { $selected = "selected"; }
		print "<option value=\"$profiles{$profile}\" $selected>$profile</option>\n";
	}
	print "</select>\n";
	print "</td>\n";
	
	print "<td class=cell><input class=mediumtext type=text name=port_$count value=\"$port\"> </td>\n";
	print "<td class=hlcell><input class=tinytext type=text name=idx_$count value=\"$idx\"> </td>\n";
	print "<td class=cell><input class=tinytext type=text name=rack_$count value=\"$rack\"> </td>\n";
	print "<td class=cell><input class=smalltext type=text name=online_$count value=\"$online\"> </td>\n";
	print "<td class=hlcell><input class=largetext type=text name=hostid_$count value=\"$hostid\"> </td>\n";
	print "<td class=cell><input class=mediumtext type=text name=password_$count value=\"$password\"> </td>\n";
	print "<td class=cell><input class=supersizetext type=text name=ilomac_$count value=\"$ilomac\"> </td>\n";
	print "<td class=cell><input class=largetext type=text name=iloaddr_$count value=\"$iloaddr\"> </td>\n";
	print "<td class=cell><input class=smalltext type=text name=iloport_$count value=\"$iloport\"> </td>\n";
	$count++;
	print "</tr>\n";
	print "<tr><td colspan=13 class=cell>\n";
	print "<input type=hidden name=rowcount value=$count>\n";
	print "<input type=hidden name=action value=update>\n";
	print "<input class=button value=\"Add Node\" type=submit>\n";
	print "<input class=button type=reset value=\"Clear Form\" type=submit>\n";
	print "</form>\n";
	print "</td></tr>\n";
	

}


sub update {
	my $rowcount = $cgi->param('rowcount');
	my $message = "Updated $rowcount host(s)";

	for (my $i = 0; $i < $rowcount; $i++) {

		my $port       = $cgi->param("port_$i");
		my $profile_id = $cgi->param("profile_$i");
		my $idx        = $cgi->param("idx_$i");
		my $rack       = $cgi->param("rack_$i");
		my $online     = $cgi->param("online_$i");
		my $hostid     = $cgi->param("hostid_$i");
		my $password   = $cgi->param("password_$i");
		my $iloaddr    = $cgi->param("iloaddr_$i");

		my $sql = "select count(hostid) from node where hostid = '$hostid'";
		my $sth = $dbh->prepare($sql);
		$sth->execute();
		my $node_exists = 0;
		my @row = $sth->fetchrow();
		if ($row[0] >= 1) { $node_exists = 1; }

		if ($node_exists) {
			$sql = "update node set ";
			$sql = $sql . "port = '$port', ";
			$sql = $sql . "profile_id = '$profile_id', ";
			$sql = $sql . "idx = '$idx', ";
			$sql = $sql . "rack = '$rack', ";
			$sql = $sql . "online = '$online', ";
			$sql = $sql . "password = '$password', ";
			$sql = $sql . "iloaddr = '$iloaddr' ";
			$sql = $sql . "where hostid = '$hostid'";

		} else {
			$sql = "replace into node (port, profile_id, idx, ";
			$sql = $sql . "rack, online, hostid, password, iloaddr) values (";
			$sql = $sql . "'$port', '$profile_id', '$idx',";
			$sql = $sql . "'$rack', '$online', '$hostid', '$password', ";
			$sql = $sql . "'$iloaddr');";
		}
		$dbh->do($sql) || print "ERROR ($sql): " . $dbh->errstr;

	}
	$dbh->commit();
	return $message;
}
