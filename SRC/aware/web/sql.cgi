#!/usr/bin/perl -w

# -----------------------------
# $Revision: 1.6 $
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

# -------------------------------------------------------------------
# Begin Script
# -------------------------------------------------------------------
my $cgi = new CGI();
my $dbh = get_db_connection();
my $database = get_config("database");
my $dbuser = get_config("dbuser");

print_header_simple("Table Info");

# extract CGI standard variables
my $query = $cgi->param('query') || "";
my $maxrows = $cgi->param('maxrows') || 250;

my $message = "OK";

print "<center><div id=popup>\n";
print "<p class=message>Status: $message</p>\n";
do_query($query);
print "<br><table><tr><td><input type=button class=button onClick=\"window.close()\" value=\"Close\"></td></tr></table>\n";
print "</div>\n";

print "</center>\n";
print "</body>\n";
print "</html>\n";

# Close out DB Connection
$dbh->disconnect();

exit(0);


#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------


sub do_query {

	my ($queryStr) = @_;

	my (@queries) = split(/;/, $queryStr);

	foreach my $query (@queries) {
		print "<br>";

		my $t0 = [gettimeofday];
		chomp($query);
		$query =~ s/^\s+//g;
		$query =~ s/\s+$//g;

		if (length ($query) < 6) {
			next;
		}

		print "<!-- $query -->\n";

		if (lc($query) !~ m/^select/ && lc($query) !~ m/^desc/ && lc($query) !~ m/^explain/) {
			print "<table><tr><td>Ignoring non-select query '<font color=red>$query</font>'</td></tr></table><br><br>";
			next;
		}

		my $table_name = $query;
		$table_name =~ s/.* from //g;
		$table_name =~ s/ .*//g;

		my $sth;
		if (!($sth = $dbh->prepare($query))) {
			db_error("Error ($query): " . $dbh->errstr);
			next;
		}
		if (!$sth->execute()) { 
			db_error("Error ($query): " . $dbh->errstr);
			next;
		}
		
		print "<center><table>\n";	
		my $printHeader = 1;	
		my $num_cols = 0;
		my $colspan = 0;
		my $count = 0;
		my $moreRows = "";
		while (my @row = $sth->fetchrow()) {
			if ($count >= $maxrows) { 
				$moreRows = "+";
				last; 
			}
			$count++;
			my $rowType = "odd";
			if ($count % 2 == 0) { $rowType = "even"; }
			
			if ($printHeader) { 
				$num_cols = $sth->{NUM_OF_FIELDS};
				$colspan = $num_cols + 1;
				print "<tr><th colspan=$colspan class=tableheader>Query Results</th></tr>\n";
				print "<tr><th colspan=$colspan class=header>SQL</th></tr>\n";
				print "<tr class=even><td class=lcell colspan=$colspan><i>$query</i></td></tr>\n";


				my $durl = url("export.cgi");
				$durl->query_form("sql" => "$query");
				print "<tr><th colspan=$colspan class=header>Resultset (<a class=header href=$durl>CSV</a>)</th>\n";

				print "<tr><th>#</th>\n";
				for (my $i = 0; $i < $num_cols; $i++) {
					print "<th>" . $sth->{NAME}->[$i] . "</th>\n";
				}
				print "</tr>\n";
	
				print "<tr><th>&nbsp;</th>\n";
				for (my $i = 0; $i < $num_cols; $i++) {
					print "<th>";
					my $hr = $dbh->type_info($sth->{TYPE}->[$i]);
					if ($hr) {
						print $$hr{TYPE_NAME};	
					} else {
						print "Unknown";
					}
					print "</th>\n";
				}
				print "</tr>\n";
	
				$printHeader = 0;
			}
			print "<tr class=$rowType><td nowrap>$count</td>\n";
			for (my $i = 0; $i < $num_cols; $i++) {
				if (!defined($row[$i])) { $row[$i] = ""; }
				print "<td nowrap class=lcell>$row[$i]</td>\n";
			}
			print "</tr>\n";
	
		}
		
		my $t1 = [gettimeofday];
		my $interval = sprintf("%0.3f", tv_interval $t0, $t1);
		my $shown = $maxrows;
		if ($maxrows > $count) { $shown = $count; }
		print "<tr><th class=footer align=center colspan=$colspan>";
		print "Displaying $shown of $count$moreRows total rows, $interval second(s)</th></tr>";
		print "</table>";
	
	}
}
