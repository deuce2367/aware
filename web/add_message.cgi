#!/usr/bin/perl -w

# ------------------------------------------------------------
# $Id: add_message.cgi,v 1.2 2006-09-18 12:55:55 aps1 Exp $
# $RCSfile: add_message.cgi,v $
# $Revision: 1.2 $
# $Date: 2006-09-18 12:55:55 $
# $Author: aps1 $
# $Name: not supported by cvs2svn $
# ------------------------------------------------------------

use strict;
use CGI;
use DBI;
use Time::HiRes qw(usleep ualarm gettimeofday tv_interval);
use HTML::Entities;
use ZUtils::Common;
use ZUtils::Aware;
use Time::Local;

# -------------------------------------------------------------------
# Initialize Configuration Settings
# -------------------------------------------------------------------
my $cfgfile = $ENV{ZUTILS_CFGFILE} || "/etc/aware/aware.cfg";
load_config($cfgfile);

###########################################################################################
# Program Block 
###########################################################################################
my $cgi = new CGI();
my $dbh = get_db_connection();

# -----------------------Main Block-------------------------------------

my $_name = "add_message.cgi";
my $title = "Message Editor";

my $action = $cgi->param('action') || "default";
my $component_id = $cgi->param('component_id') || 0;
my $content = $cgi->param('content') || "";

my $sth = $dbh->prepare("select id, name from component where report = 'true'") || print "SQL Error: " . $dbh->errstr;
$sth->execute() || print "Database Error" . $dbh->errstr;
my %components;
while (my @row = $sth->fetchrow()) { $components{$row[0]} = $row[1]; }
$sth->finish();

print_header_simple($title);
print "<title>Status Log Entry</title>\n";
print "<center><div id=popup>\n";

my $message = localtime();
if ($action eq "update") {
	$message = add_message();
}

my $username = $ENV{REMOTE_USER} || "nobody";
my $ipaddr = $ENV{REMOTE_ADDR} || "unknown";


print "<p class=alert>$message</p>\n";

print "<table class=optiontable>\n<form method=post action=$_name>\n";
print "<input type=hidden name=action value=update>\n";
print "<tr><th colspan=3 class=tableheader>Log Entry</th></tr>\n";
print "<tr><th colspan=3 class=header>Current SID is <font color=gold>$username</font> ($ipaddr)</th></tr>\n";
print "<tr><td colspan=3><textarea class=largearea name=content>$content</textarea></td></tr>\n";
print "<tr><th colspan=2>Component: <select name=component_id>";
foreach my $current_id (sort(keys(%components))) {
	my $selected = "";
	if ($component_id == $current_id) { $selected = "selected"; }
	print "<option value=$current_id $selected>$components{$current_id}</option>\n";
}
print "</select></th>\n";
print "<tr><td class=cell colspan=3>";
print "<input class=button type=button onClick=window.close() value=\"Close\"> ";
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

sub add_message {

	my $sid = $ENV{REMOTE_USER} || "voicesail_op";
	my $sql = "insert into status_message (status, message, created, component_id, sid) values ('operator', ?, now(), ?, '$sid')";
	my $sth = $dbh->prepare($sql);

	$content =~ s/'/''/g;
	my $message = "Message added at " . localtime();
	if (!$sth->execute($content, $component_id)) {
		$message = $dbh->errstr;
	} else {
		my $insertID = $sth->{'mysql_insertid'} || 0;
		my $sql = "update component set status_message_id = $insertID where id = $component_id";
		$dbh->do($sql) || printLog("ERROR ($sql): " . $dbh->errstr, 0);
	}
	$sth->finish();
	$dbh->commit();


	return $message;
}

