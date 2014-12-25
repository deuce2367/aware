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

my $_name = "field_edit.cgi"; 
my $_title = "Field Editor";

# -------------------------------------------------------------------
# Begin Script
# -------------------------------------------------------------------
my $cgi = new CGI();

print_header_simple($_title);

my $dbh = get_db_connection();
if (!defined($dbh)) {
	print "<p class=alert>Unable to connect to DB</p>\n";
	exit();
}

my $action = $cgi->param('action') || "default";
my $field = $cgi->param('field') || "";
my $table = $cgi->param('table') || "";
my $id = $cgi->param('id') || "";
my $content = $cgi->param('content') || "";
my $idvalue = $cgi->param('idvalue') || "";

print "<center><div id=popup>\n";

my $message = localtime();
if ($action eq "update") {
	$message = updateField();
}

print "<p class=message>$message</p>\n";

print "<table>\n<form method=post action=field_edit.cgi>\n";
print "<input type=hidden name=action value=update>\n";
print "<input type=hidden name=field value=\"$field\">\n";
print "<input type=hidden name=table value=\"$table\">\n";
print "<input type=hidden name=id value=\"$id\">\n";
print "<input type=hidden name=idvalue value=\"$idvalue\">\n";
print "<tr><th>Edit Field</th></tr>\n";
print "<tr><td><textarea class=largearea name=content>$content</textarea></td></tr>\n";
print "<tr><td class=cell>";
print "<input class=button type=button onClick=window.close() value=\"Close\">";
print "<input class=button type=submit value=\"Submit\">";
print "</td></tr>\n";
print "</form></table>\n";


print "</table></div>\n";
print "</center></body></html>\n";

# Disconnect from the database.
$dbh->disconnect();



#
#
# ------------------------------Subroutines----------------------------------
#
#

sub updateField {

	my $sql = "update $table set $field = ? where $id = '$idvalue'";
	my $sth = $dbh->prepare($sql);

	$content =~ s/'/''/g;
	my $message = "Updated '$field' at " . localtime();
	if (!$sth->execute($content)) {
		$message = $dbh->errstr;
	}
	$sth->finish();
	$dbh->commit();
	return $message;
}
