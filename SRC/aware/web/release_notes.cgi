#!/usr/bin/perl -w

# -----------------------------
# $Revision: 1.4 $
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

my $_name = "release_notes.cgi"; 
my $_title = "Release Notes";

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


########################################################################################
##### Initialization 
########################################################################################

my $message = "OK";

main();

$dbh->disconnect();


########################################################################################
##### Sub-routines
########################################################################################


sub main {

	print "<body>\n";
	print "<div id=wrapper><center><div id=mainsection>\n";
	print "<br>\n";
	
	print "<table>";

    print "<tr><th class=tableheader colspan=2>AWARE Release Notes</th></tr>\n";
	print "<tr class=odd><td class=lcell>";
	print "<pre>";
	
	open(IN, "<../doc/release_notes.txt");
	while (<IN>) { if ($_ !~ m/^#/) { print $_; } }
	close(IN);
	
	print "</pre>";
	print "</td></tr>";


    if (-f "../doc/revision_history.txt") {
        print "<tr><th class=tableheader colspan=2>AWARE Revision History</th></tr>\n";
	    print "<tr class=odd><td class=lcell>";
	    print "<pre>";
	
	    open(IN, "<../doc/revision_history.txt");
	    while (<IN>) { if ($_ !~ m/^#/) { print $_; } }
	    close(IN);
	
	    print "</pre>";
	    print "</td></tr>";
    }

    print "</table>\n";
	
	print "</div></center></div>";
	print "</body></html>\n";

}
