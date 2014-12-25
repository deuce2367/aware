#!/usr/bin/perl -w

# -----------------------------
# $Revision: 1.5 $
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


my %DBTYPES = (	'1' => 'CHAR', 
		'2' => 'NUMERIC',
		'3' => 'DECIMAL',
		'4' => 'INTEGER',
		'5' => 'SMALLINT',
		'6' => 'FLOAT',
		'7' => 'REAL',
		'8' => 'DOUBLE',
		'9' => 'DATE',
		'10' => 'TIME',
		'11' => 'TIMESTAMP',
		'12' => 'VARCHAR',
		'-1' => 'LONGVARCHAR',
		'-2' => 'BINARY',
		'-3' => 'VARBINARY',
		'-3' => 'LONGVARBINARY',
		'-5' => 'BIGINT',
		'-6' => 'TINYINT',
		'-7' => 'BIT',
		'-8' => 'WCHAR',
		'-9' => 'WVARCHAR',
		'-10' => 'WLONGVARCHAR',
		'93' => 'DATE');

# -------------------------------------------------------------------
# Begin Script
# -------------------------------------------------------------------
my $cgi = new CGI();
my $dbh = get_db_connection();

print_header_simple("Table Info");

my $database = get_config("database");
my $dbuser = get_config("dbuser");

# extract CGI standard variables
my $table_name = $cgi->param('table_name') || "";
my $query = $cgi->param('query') || "";
my $maxrows = $cgi->param('maxrows') || 250;
my $action = $cgi->param('action') || "default";

my $message = "OK";

if ($action eq "analyze") { $message = analyze_table(); }

print "<center><div id=popup>\n";
print "<p class=message>Status: $message</p>\n";
if ($database eq "oracle") {
	print_oracle_table_info();
} elsif ($database eq "mysql") {
	print_mysql_table_info();
}
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

sub print_mysql_table_info {

	print "<table>";
	print "<tr><th class=tableheader colspan=8>Table Information</th></tr>\n";
	print "<tr><th class=header colspan=8>Summary</th></tr>\n";
	print "<tr><th>Table</th><th>Engine</th><th># Rows</th><th>Data Size</th><th>Index Size</th><th>Updated</th><th colspan=2>Analyzed</th></tr>\n";

	my $sql = "show table status";
	if ($table_name) { $sql .= " like '" . lc($table_name) . "'"; }
	my $sth = $dbh->prepare($sql) || db_error("Error: " . $dbh->errstr);
	$sth->execute();

	my $count = 0;
	while(my $ref = $sth->fetchrow_hashref()) {
		my $rowtype = get_row_type($count);

		my $dbname = $ref->{'Name'} || "Unknown";
		my $engine = $ref->{'Engine'} || "Unknown";
		my $num_rows = $ref->{'Rows'} || 0;
		my $data = $ref->{'Data_length'} || 0;
		my $index = $ref->{'Index_length'} || 0;
		my $updated = $ref->{'Update_time'} || "Never";
		my $analyzed = $ref->{'Check_time'} || "Never";

		$num_rows = comma_format($num_rows);
		$data = comma_format($data);
		$index = comma_format($index);

		if ($num_rows) {
			$num_rows = "<a onClick=\"openWin('query', 1024, 768);\" target=query href=sql.cgi?query=select+*+from+$dbname>$num_rows</a>";
		}

		print "<tr class=$rowtype>";
		print "<td class=lcell><a href=table_info.cgi?table_name=$dbname>$dbname</a></td>";
		print "<td>$engine</td>";
		print "<td>$num_rows</td>";
		print "<td>$data</td>";
		print "<td>$index</td>";
		print "<td>$updated</td>";
		print "<td>$analyzed</td>";
		print "<td>";
		print "<form action=table_info.cgi>";
		print "<input type=hidden name=table_name value=$dbname>";
		print "<input type=hidden name=action value=analyze>";
		print "<input type=submit class=button value=\"Analyze\">";
		print "</form></td>\n";
		print "</tr>\n";
		
		$count++;
	}
	$sth->finish();

	if ($table_name) {

		print "<tr><th class=header colspan=8>Structure</th></tr>\n";
		print "<tr><th>#</th><th>Column</th><th>Type</th><th>Null OK</th><th>Key</th><th>Default</th><th colspan=2>Extra</th></tr>\n";
		$sql = "desc " . lc($table_name);
		$sth = $dbh->prepare($sql) || print "<font color=red>Error: " . $dbh->errstr . "</font><br>\n";
		$sth->execute() || print "<font color=red>Error: " . $dbh->errstr . "</font><br>\n";

		my $col = 0;
		while(my @row = $sth->fetchrow()) {
			$col++;

			my $name = $row[0] || "";
			my $type = $row[1] || "";
			my $null = $row[2] || "";
			my $key = $row[3] || "";
			my $def = $row[4] || "";
			my $ext = $row[5] || "";

			my $rowtype = get_row_type($col);
			print "<tr class=$rowtype>";
			print "<td>$col</td><td class=rcell>$name</td><td class=lcell>$type</td>";
			print "<td>$null</td><td>$key</td><td class=lcell>$def</td><td colspan=2>$ext</td>";
			print "</tr>\n";
		}
		print "<tr><td class=cell colspan=8><form action=table_info.cgi><input class=button type=submit value=\"All Tables\"></form></tr>\n";
	}

	if (!$count) { print "<tr><td colspan=8 class=cell>No Tables Found</td></tr>\n"; }

	print "</table>\n";


}


sub print_oracle_table_info {

	print "<table>";
	print "<tr><th class=tableheader colspan=8>Table Information</th></tr>\n";
	print "<tr><th class=header colspan=8>Summary</th></tr>\n";
	print "<tr><th>Table</th><th>Tablespace</th><th>Logging</th><th># Rows</th><th>Data Size</th><th>Partitioned</th><th colspan=2>Updated</th></tr>\n";

	my $sql = "select tablespace_name, logging, num_rows, to_char(last_analyzed, 'yyyy-mm-dd hh24:mi:ss'), partitioned, table_name from tabs"; 
	if ($table_name) { $sql .= " where table_name = '$table_name'"; }
	$sql .= " order by table_name asc";
	my $sth = $dbh->prepare($sql) || db_error("Error: " . $dbh->errstr);
	$sth->execute();

	my $count = 0;
	while(my @row = $sth->fetchrow()) {
		my $rowtype = get_row_type($count);

		my $tablespace = $row[0];
		my $logging = $row[1];
		my $num_rows = $row[2] || 0;
		my $analyzed = $row[3] || "Never";
		my $partitioned = $row[4];
		my $tabname = $row[5];

		$num_rows = comma_format($num_rows);

		if ($num_rows) {
			$num_rows = "<a onClick=\"openWin('query', 1024, 768);\" target=query href=sql.cgi?query=select+*+from+$tabname>$num_rows</a>";
		}

		my $isql = "select sum(bytes) from user_segments where segment_name = '$tabname'"; 
		my $isth = $dbh->prepare($isql) || db_error("Error: " . $dbh->errstr);
		$isth->execute();
		my @irow = $isth->fetchrow();
		my $data_size = $irow[0] || 0;
		$data_size = comma_format($data_size);


		print "<tr class=$rowtype>";
		print "<td class=lcell><a href=table_info.cgi?table_name=$tabname>$tabname</a></td>";
		print "<td>$tablespace</td>";
		print "<td>$logging</td>";
		print "<td>$num_rows</td>";
		print "<td>$data_size</td>";
		print "<td>$partitioned</td>";
		print "<td>$analyzed</td>";
		print "<td>";
		print "<form action=table_info.cgi>";
		print "<input type=hidden name=table_name value=$tabname>";
		print "<input type=hidden name=action value=analyze>";
		print "<input type=submit class=button value=\"Analyze\">";
		print "</form></td>\n";
		print "</tr>\n";
		
		$count++;
	}
	$sth->finish();

	if ($table_name) {

		print "<tr><th class=header colspan=8>Structure</th></tr>\n";
		print "<tr><th>#</th><th colspan=4>Column</th><th colspan=3>Type</th></tr>\n";
		$sql = "select * from $table_name where 1 = 0";
		$sth = $dbh->prepare($sql);
		$sth->execute();
		my $col_names = $sth->{NAME};
		my $col_types = $sth->{TYPE};

		my @names = @{$col_names};
		my @types = @{$col_types};
		my $col = 0;
		for (my $i = 0; $i <= $#names; $i++) {
			my $rowtype = get_row_type($col);
			$col++;
			print "<tr class=$rowtype>";
			print "<td>$col</td><td class=rcell colspan=4>$names[$i]</td><td class=lcell colspan=3>$DBTYPES{$types[$i]}</td>";
			print "</tr>\n";
		}
		print "<tr><td class=cell colspan=8><form action=table_info.cgi><input class=button type=submit value=\"All Tables\"></form></tr>\n";
	}

	if (!$count) { print "<tr><td colspan=8 class=cell>No Tables Found</td></tr>\n"; }

	print "</table>\n";


}




##########################################################################################################################################
#
# analyze_table()
#
# - analyze the specified table
#
##########################################################################################################################################

sub analyze_table {

	my $sql;
	my $result = "Analyzed table '$table_name'";

	if ($database eq "oracle") {
		$sql = "begin dbms_stats.gather_table_stats('$dbuser', '" . uc($table_name) . "'); end;";
	} else {
		$sql = "optimize table $table_name";
	}

	my $sth = $dbh->prepare($sql) || printLog("Error ($sql): " . $dbh->errstr, 0);
	if (!$sth->execute()) { $result = "Error ($sql): " . $dbh->errstr; }
	$sth->finish();

	return $result;

}


