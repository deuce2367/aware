#!/usr/bin/perl -w

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
my $_name = "about.cgi"; 
my $_title = "Help/About";

# -------------------------------------------------------------------
# Begin Script
# -------------------------------------------------------------------
print_header($_title, $_name, 0);

my $dbh = get_db_connection(0);
if (!defined($dbh)) {
	print "<p class=alert>Unable to connect to DB</p>\n";
	exit();
}

my $cgi = new CGI;
my $message = localtime();

main();

$dbh->disconnect();


########################################################################################
##### Sub-routines
########################################################################################


sub main {

	print "<body>\n";
	print "<div id=wrapper><center><div id=mainsection>\n";
	print "<br>\n";
	
	print "<table><tr><th class=tableheader colspan=2>AWARE Systems Monitor</th></tr>\n";
	print "<tr class=even><th class=label>Developer(s):</th><td>APS, Zorin Industries (a SkyNet Subsidiary)</td></tr>\n";

    my $sql = "select major, minor, updated from aware";	
    my $sth = $dbh->prepare($sql);
    $sth->execute();
    my @row = $sth->fetchrow();

	my $release = $row[0] || "UNKNOWN";
	my $revision = $row[1] || "UNKNOWN";
	my $installed = $row[2] || "UNKNOWN";
	
	print "<tr class=odd><th class=label>Release:</th><td>$release</td></tr>\n";
	print "<tr class=odd><th class=label>Revision:</th><td>$revision</td></tr>\n";
	print "<tr class=even><th class=label>Installed:</th><td>$installed</td></tr>\n";
	
	print "</table>";
	
	print "</div></center></div>\n";
	print "</center></body></html>\n";

}
