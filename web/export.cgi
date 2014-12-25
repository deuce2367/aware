#!/usr/bin/perl -w

# -----------------------------
# $Revision: 1.7 $
# $Date: 2008-05-24 17:10:27 $
# $Author: aps1 $
# $Name: not supported by cvs2svn $
# -----------------------------

use strict;
use CGI;
use DBI;
use ZUtils::Common;
use ZUtils::Aware;

# -------------------------------------------------------------------
# Initialize Configuration Settings
# -------------------------------------------------------------------
my $cfgfile = $ENV{ZUTILS_CFGFILE} || "/etc/aware/aware.cfg";
load_config($cfgfile);
my $cgi = new CGI();

my $sql = $cgi->param('sql') || 0;

if (!$sql) {
	print "Content-type: text/html\n\n";
	print "Error: no data requested!\n";
	exit();
}

print $cgi->header(-type => 'text/csv',
                 -content_disposition => "attachment; filename=export.txt");

my $dbh = get_db_connection();

my $sth = $dbh->prepare($sql) || print "SQL Error: " . $dbh->errstr;
$sth->execute() || print "Database Error: " . $dbh->errstr;

my $num_cols = $sth->{NUM_OF_FIELDS};
for (my $i = 0; $i < $num_cols;) {
	print $sth->{NAME}->[$i];
	$i++;
	if ($i < $num_cols) { print ", "; }
}
print "\n";

while (my @row = $sth->fetchrow()) {

	for (my $i = 0; $i <= $#row; $i++) {
		my $data = "";
		if (defined($row[$i])) { $data = $row[$i]; }
		$data =~ s/^\s+//g;
		$data =~ s/\s+$//g;
		if ($data =~ m/,/) {
			if ($data =~ m/"/) {
				$data =~ s/"/""/g;
			}
			$data = "\"$data\"";
		}

		print $data;
		if ($i < $#row) { print ", "; }
	}
	print "\n";
}

$sth->finish();
$dbh->disconnect();

