#!/usr/bin/perl -w

# -----------------------------
# $Revision: 1.1 $
# $Date: 2007-11-25 17:07:52 $
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

# -------------------------------------------------------------------
# Begin Script
# -------------------------------------------------------------------
my $cgi = new CGI();
my $value = $cgi->param('value') || "";
my $field = $cgi->param('field') || "hostname";

my $exists = 0;
my $hostID = "";

my $dbh = get_db_connection();
if (defined($dbh)) {
	my $sql = "select hostid from node where $field = '$value'";
	my $sth = $dbh->prepare($sql);
	$sth->execute();
	my @row = $sth->fetchrow();
	if (defined($row[0])) {
		$hostID = $row[0];
		$exists = 1;
	}
	$sth->finish();	
}

if (!$exists) {
	$hostID = `uuidgen`;
	chomp($hostID);
}

# HTTP Response
print "Content-type: text/html\n";
print "Content-length: " . length($hostID) . "\n";
print "\n";
print "$hostID";

# Disconnect from the database.
$dbh->disconnect();


