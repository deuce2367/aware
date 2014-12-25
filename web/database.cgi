#!/usr/bin/perl -w

# -----------------------------
# $Revision: 1.14 $
# $Date: 2008-05-05 17:30:45 $
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
my $_title = "Database Tool";
my $_name = "database.cgi";

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

my $database = get_config("database");
my $connstr = get_config("connect_string");
my $user = get_config("dbuser");


# extract CGI standard variables
my $descTableName	= $cgi->param('descTableName');
my $query		= $cgi->param('query') || "";
my $maxrows		= $cgi->param('maxrows') || 250;

print "<body>\n";
print "<div id=wrapper><center><div id=mainsection>\n";
list_tables();
print "</div></center></div>\n";

print "</body>\n";
print "</html>\n";

# Close out DB Connection
$dbh->disconnect();

exit(0);


#------------------------------------------------------------------------------------


# -----------------
# list_tables
# -----------------

sub list_tables {

	my $sql;
	if ($database eq "oracle") {
		$sql = "select table_name from tabs order by table_name asc";
	} elsif ($database eq "mysql") {
		$sql = "show tables";
	}
	my $sth = $dbh->prepare($sql) || db_error("Error: " . $dbh->errstr);
	$sth->execute();

	print "<table>";
	print "<tr><th colspan=2 class=tableheader>Database Tool</th></tr>\n";
	print "<tr><th colspan=2 class=header>Table Info</th></tr>\n";
	print "<tr>";

	# -- table selection cell
	print "<td valign=center>\n";	
	print "<center>";
	print "<table>\n";
	print "<tr><th colspan=2 class=tableheader>Database Connection Information</th></tr>\n";
	print "<tr class=odd><th class=label>Database Platform</th><td>$database</td></th></tr>\n";
	print "<tr class=odd><th class=label>Connection String</th><td>$connstr</td></th></tr>\n";
	print "<tr class=even><th class=label>Database Username</th><td>$user</td></th></tr>\n";
	#print "<tr class=odd><th class=label>Database Password</th><td>******</td></th></tr>\n";
	print "</table>\n";


	print "</center>\n";
	print "</td>\n";

	# -- database connection info cell
	print "<td>";
	print "<center>";
	print "<table>\n";	
	print "<tr><th colspan=2 class=tableheader>Tables</th></tr>\n";
	print "<tr><th>Table</th><th>Details</th></tr>\n";
	print "<form action=table_info.cgi target=table_info>";
	print "<tr class=odd><td><select class=lgselect name=table_name>";
	while (my @row = $sth->fetchrow()) {
		my $table_name 	= uc($row[0]);
		print "<option value=$table_name>$table_name</option>\n";		

	}
	print "</select></td>\n";
	print "<td>";
	print "<input onClick=\"openWin('table_info', 700, 500);\" type=submit value=Display class=button>";
	print "</form>";
	print "</td>\n";
	print "</tr>\n";

	print "<form action=table_info.cgi target=table_info>";
	print "<tr><td class=cell colspan=2><input class=button onClick=\"openWin('table_info', 750, 800);\" type=submit value=\"All Tables\"></form></td></tr>\n";

	print "</table>\n";	
	print "</center></td>";
	print "</tr>\n";

	# -- spacer
	print "<tr><th colspan=2 class=header>Query Tool</th></tr>\n";


	# -- query interface	
	print "<tr><td colspan=2><center>";
	print "<table><tr><th colspan=2 class=tableheader>SQL Processor</th></tr>\n";
	print "<form action=sql.cgi target=query method=post>\n";
	print "<tr class=odd><td colspan=2><textarea cols=100 rows=20 name=query>$query</textarea></td></tr>\n";
	print "<tr><th>Max/Rows per Query <input class=mediumtext name=maxrows value=\"$maxrows\"></th>";
	print "<th><input onClick=\"openWin('query', 1024, 768);\" class=button type=submit value=\"Submit Query\"></form></th></tr>\n";
	print "</table>";
	print "</center></td>";
	print "</tr>\n";
	print "</center></td></tr></table>\n";


	print "<p class=message>Please select a table or enter some SQL</p>\n";

	$sth->finish();

}

