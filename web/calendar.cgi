#!/usr/bin/perl -w

# ------------------------------------------------------------
# $Id: calendar.cgi,v 1.13 2006-10-18 19:09:11 aps1 Exp $
# $RCSfile: calendar.cgi,v $
# $Revision: 1.13 $
# $Date: 2006-10-18 19:09:11 $
# $Author: aps1 $
# $Name: not supported by cvs2svn $
# ------------------------------------------------------------

use strict;
use CGI;
use DBI;
use Date::Calc qw(:all);
use Time::Local;
use Time::HiRes qw(usleep ualarm gettimeofday tv_interval);
use ZUtils::Common;
use ZUtils::Aware;

# -------------------------------------------------------------------
# Initialize Configuration Settings
# -------------------------------------------------------------------
my $cfgfile = $ENV{ZUTILS_CFGFILE} || "/etc/aware/aware.cfg";
load_config($cfgfile);
my $_name = "calendar.cgi"; 
my $_title = "Calendar";

# -------------------------------------------------------------------
# Begin Script
# -------------------------------------------------------------------
my $cgi = new CGI;

print_header($_title, $_name, 0);
my $dbh = get_db_connection(0);
if (!defined($dbh)) {
	print "<p class=alert>Unable to connect to DB</p>\n";
	exit();
}


my $day = $cgi->param('day') || get_current_day();
my $month = $cgi->param('month') || get_current_month();
my $year = $cgi->param('year') || get_current_year();

print "<div id=wrapper><center><div id=mainsection>\n";

if ($month < 1 || $month > 12 || $day < 1 || $day > 31 || $year < 2001 || $year > 3000) {
	print "Error: invalid parameters (date not in range)\n";
	exit();
}
if ($day > Days_in_Month($year, $month)) {
	$day = Days_in_Month($year, $month);
}

my $noon = Date_to_Time($year, $month, $day, 12, 0, 0);

print_month($day, $month, $year);

print "</div></center></div>\n";
print "</body></html\n";
$dbh->disconnect();


sub print_month {

	my ($day, $month, $year) = @_;

	my $datetime = timelocal(localtime());

	my $last_month = ($month - 2) % 12 + 1;
	my $next_month = ($month) % 12 + 1;

	my $last_year = $year;
	my $next_year = $year;
	my $prev_year = $year - 1;
	my $foll_year = $year + 1;

	if ($last_month == 12) { $last_year--; }
	if ($next_month == 1) { $next_year++; }

	my $month_name = Month_to_Text($month);
	my $day_name = Day_of_Week_to_Text(Day_of_Week($year, $month, $day));
	my $num_days = Days_in_Month($year, $month);

	print "<table>\n";
	print "<tr>\n";
	print "<th class=tableheader colspan=7>$month_name</th>\n";
	print "<tr>\n";
	print "</tr>\n";
	print "<th class=header><a class=sortCol href=$_name?day=$day&month=$month&year=$prev_year>&lt;&lt;&lt;&lt;</th></th>\n";
	print "<th class=header><a class=sortCol href=$_name?day=$day&month=$last_month&year=$last_year>&lt;&lt;</th></th>\n";
	print "<th colspan=3 class=header>$year</th>\n";
	print "<th class=header><a class=sortCol href=$_name?day=$day&month=$next_month&year=$next_year>&gt;&gt;</th></th>\n";
	print "<th class=header><a class=sortCol href=$_name?day=$day&month=$month&year=$foll_year>&gt;&gt;&gt;&gt;</th></th>\n";
	print "</tr>\n";
	print "<tr>";
	print "<th class=calday>Monday</th>";
	print "<th class=calday>Tuesday</th>";
	print "<th class=calday>Wednesday</th>";
	print "<th class=calday>Thursday</th>";
	print "<th class=calday>Friday</th>";
	print "<th class=calday>Saturday</th>";
	print "<th class=calday>Sunday</th>";
	print "</tr>\n";

	my $curr_day = 1;

	while ($num_days > 0) {
		my $fdow = Day_of_Week($year, $month, $curr_day);

		my $rowtype = get_row_type($curr_day + $fdow);
		print "<tr class=$rowtype>";
		for (my $i = $fdow; $i > 1; $i--) {
			print "<td></td>";
		}

		my $thismonth = sprintf("%02d", $month);
		for (my $i = $fdow; $i <= 7; $i++) {

			if ($num_days < 1) { next; }

			my $hasReports = "";
			my $thisday = sprintf("%02d", $curr_day);

			my $directory = get_config("aware_home") . "/web/archive/$year$thismonth$thisday";
			if (-d $directory) {
				opendir(DIR, $directory);
				my $filename;
				while (!$hasReports && defined($filename = readdir(DIR))) {
					if ($filename =~ m/-profile\.html$/ || $filename =~ m/-host\.html$/) {
						$hasReports = "*";
					}
				}
				closedir(DIR);
			}

			my $epochtime = Date_to_Time($year, $month, $curr_day, 12, 0, 0);

			if ($curr_day == $day) {
				print "<td class=cell><font color=red>$curr_day$hasReports</font></td>\n";
			} else {
				print "<td class=cell><a href=$_name?day=$curr_day&month=$month&year=$year>$curr_day$hasReports</a></td>";
			}

			$num_days--;
			$curr_day++;
		}
		print "</tr>\n";

	}
	print "</table>\n";
	print "* <i>daily reports are available for this date</i>\n";
	print "<br><br><br>\n";

	$month = sprintf("%02d", $month);
	$day = sprintf("%02d", $day);
	list_available("$year$month$day");

}

sub get_current_day { return (localtime)[3]; }
sub get_current_month { return (localtime)[4] + 1; }
sub get_current_year { return (localtime)[5] + 1900; }

sub list_available {

	my ($datestring) = @_;

	my $directory = get_config("aware_home") . "/web/archive/$datestring";
	my $webdir = get_config("web_dir") . "/archive/$datestring";


	my $cols = 4;
	my ($row, $col);
	my @profile_reports = ();
	my @host_reports = ();

	print "<table width=750><tr><th colspan=$cols class=tableheader>Daily Reports: $year-$month-$day</th></tr>\n";

	# -- go find any daily reports that are available
	if (-d $directory) {
		opendir(DIR, $directory);
		my $filename;
		while (defined($filename = readdir(DIR))) {
			if ($filename =~ m/-profile\.html$/) {
				push(@profile_reports, $filename);
			} elsif ($filename =~ m/-host\.html$/) {
				push(@host_reports, $filename);
			}
		}
		closedir(DIR);
	}

	print "<tr><th class=header colspan=$cols>Profiles</th></tr>\n";
	$row = 0;
	$col = 0;
	for (my $i = 0; $i <= $#profile_reports; $i++) {

		if ($col % $cols == 0) { 
			my $class = get_row_type($row);
			$row++;
			print "<tr class=$class>"; 
			
		}

		my $file = $profile_reports[$i];
		chomp($file);
		my $href = $file; 
		$href =~ s/.*\///g;

		print "<td class=lcell><a target=report href=\"/$webdir/$href\">$href</a></td>\n";

		if ($col % $cols == $cols - 1) { print "</tr>\n"; }
		$col++;

	}
	if ($#profile_reports % $cols != $cols - 1) { print "</tr>\n"; }
	if ($#profile_reports < 0) { print "<tr><td colspan=$cols class=cell>No profile reports available for this day</td></tr>\n"; }

	print "<tr><th class=header colspan=$cols>Hosts</th></tr>\n";
	$row = 0;
	$col = 0;
	for (my $i = 0; $i <= $#host_reports; $i++) {

		if ($col % $cols == 0) { 
			my $class = get_row_type($row);
			$row++;
			print "<tr class=$class>"; 
			
		}

		my $file = $host_reports[$i];
		chomp($file);
		my $href = $file; 
		$href =~ s/.*\///g;

		print "<td class=lcell><a target=report href=\"/$webdir/$href\">$href</a></td>\n";

		if ($col % $cols == $cols - 1) { print "</tr>\n"; }
		$col++;

	}
	if ($#host_reports % $cols != $cols - 1) { print "</tr>\n"; }
	if ($#host_reports < 0) { print "<tr><td colspan=$cols class=cell>No host reports available for this day</td></tr>\n"; }


	print "</table>\n";

}

