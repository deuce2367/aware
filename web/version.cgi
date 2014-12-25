#!/usr/bin/perl -w

# ------------------------------------------------------------
# $Id: version.cgi,v 1.11 2006-09-18 12:55:55 aps1 Exp $
# $RCSfile: version.cgi,v $
# $Revision: 1.11 $
# $Date: 2006-09-18 12:55:55 $
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
my $_name = "version.cgi"; 
my $_title = "AWARE Version Information";

# -------------------------------------------------------------------
# Begin Script
# -------------------------------------------------------------------
my $cgi = new CGI();

print_header($_title, $_name, 0);

my $dbh = get_db_connection(0);
if (!defined($dbh)) {
	print "<p class=alert>Unable to connect to DB</p>\n";
	exit();
}

my $message = "OK";

print "<body>\n";
print "<div id=wrapper><center><div id=mainsection>\n";

print "<table>\n";
print "<tr><th class=tableheader colspan=8>Aware Revision Information</th></tr>\n";
listFiles();

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

sub listFiles { 


	my $count = 0;
	print "<tr><th colspan=2>Filename</th><th>Format</th><th>Filesize</th><th>File Mtime</th>";
	print "<th>CVS Date</th><th>CVS Tag</th><th>CVS Revision</th></tr>\n";


	my %files;
	open(IN, "<../cfg/files.cfg");
	while(<IN>) { 
		if (length($_) > 5 && $_ !~ m/^#/) {
			my ($name, $format) = split('\s+', $_);
			$files{$name} = $format;
		}
	}
	close(IN);


	$count = 0;
	foreach my $filename (sort(keys(%files))) {
		$count++;
		my $rowtype = get_row_type($count); 

		my $format = $files{$filename};
		my $revision = "";
		my $cvsdate = "";
		my $cvsname = "";


		open(IN, "<$filename");

		my (@stats) = stat(IN);
		my $filesize = $stats[7];
		my $filedate = from_unixtime($stats[9]);

		my $revString = "Revision";
		my $dateString = "Date";
		my $nameString = "Name";

		while(<IN>) { 
			if (m/.*\$$revString: .*\$/ && !($revision)) {
				$_ =~ s/.*: //;
				$_ =~ s/\$.*$//g;
				$revision = $_;
			} elsif (m/.*\$$dateString: .*$/ && !($cvsdate)) {
				$_ =~ s/.*: //;
				$_ =~ s/\$.*$//g;
				$cvsdate = $_;
			} elsif (m/.*\$$nameString: .*\$/ && !($cvsname)) {
				$_ =~ s/.*: //;
				$_ =~ s/\$.*$//g;
				$cvsname = $_;
			}

		}
		close(IN);

		print "<tr class=$rowtype><form action=store.cgi method=post>\n";
 		print "<td>$count</td>\n";
 		print "<td class=lcell>$filename</td>\n";
 		print "<td class=lcell>$format</td>\n";
 		print "<td class=rcell>$filesize</td>\n";
 		print "<td class=lcell>$filedate</td>\n";
 		print "<td class=lcell>$cvsdate</td>\n";
 		print "<td class=lcell>$cvsname</td>\n";
 		print "<td class=lcell>$revision</td>\n";
		
  		print "</tr>\n";
	}

}

