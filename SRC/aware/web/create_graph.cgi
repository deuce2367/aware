#!/usr/bin/perl -w

use strict;
use CGI;
use DBI;
use URI::URL qw(url);
use GD::Graph::lines;
use GD::Graph::lines3d;
use GD::Graph::bars;
use GD::Graph::bars3d;
use GD::Graph::area;
use GD::Graph::pie3d;
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
my $t0 = [gettimeofday];
my $queries = 0;

my $errorImageFile = "images/error.png";
my $errorImageContentType = "image/png";

my $hostid = $cgi->param('hostid') || 0;
my $archive = $cgi->param('archive') || 0;
my $daysAgo = $cgi->param('daysAgo') || 0;
my $window = $cgi->param('window') || 24;
my $graph = $cgi->param('graph') || undef;
my $device = $cgi->param('device') || undef;
my $vlan = $cgi->param('vlan');

# determine graph dimensions
my $x = get_config("graph_width");
my $y = get_config("graph_height");


my $dbh = get_db_connection(0);
if (!defined($dbh)) { errorResponse(); exit(); }

main();
$dbh->disconnect();
exit(0);


sub main {

    my @plots;
    my $imgfile;
    my $t1 = [gettimeofday];

    # -- let's first ensure that we have the appropriate permissions set
    my $_htdoc = get_config("aware_home");
    my $imageDir = $_htdoc."/web/images/tmp/";
    if (!-e $imageDir || !-w $imageDir) {
        chomp(my $username = `whoami`);
        print STDERR "ERROR: cannot write files to '$imageDir' (ensure that directory exists and is writable by user: $username)\n";
        errorReponse();
        return;
    }

    my $sql = "select a.hostname, a.numcpu, b.name from node a, profile b where a.id = '$hostid' and a.profile_id = b.id";
    my $sth = $dbh -> prepare($sql) || die "Error occurred preparing SQL: " . $dbh->errstr;
    $sth -> execute || die "Error occurred processing SQL: " . $dbh->errstr; $queries++;
    my @row = $sth->fetchrow();
    my $hostname = $row[0];
    my $cpucount = $row[1];
    my $profile = $row[2];
    $sth->finish();

    my $endtime = unix_timestamp(get_date()) - ($daysAgo * 86400);
    my $image = "images/tmp/$hostname";
    if ($graph eq "sysload") {
        $imgfile = graph_sysload($dbh, $hostid, "Host", $x, $y, $endtime, $window, \$queries, $image);
    } elsif ($graph eq "memory") {
        $imgfile = graph_memory($dbh, $hostid, $x, $y, $endtime, $window, \$queries, $image);
    } elsif ($graph eq "shmemory") {
        $imgfile = graph_shmemory($dbh, $hostid, $x, $y, $endtime, $window, \$queries, $image);
    } elsif ($graph eq "cpuload") {
        $imgfile = graph_cpuload($dbh, $hostid, "Host", $x, $y, $endtime, $window, \$queries, $image);
    } elsif ($graph eq "disk_utilization" && $device) {
        $imgfile = graph_device_utilization($dbh, $hostid, $device, $x, $y, $endtime, $window, \$queries, $image);
    } elsif ($graph eq "sysio") {
        $imgfile = graph_sysio($dbh, $hostid, "Host", $x, $y, $endtime, $window, \$queries, $image);
    } elsif ($graph eq "diskload") {
        $imgfile = graph_diskload($dbh, $hostid, $x, $y, $endtime, $window, \$queries, $image);
    } elsif ($graph eq "svctime") {
        $imgfile = graph_device_svctimes($dbh, $hostid, $x, $y * 1.5, $endtime, $window, \$queries, $image);
    } elsif ($graph eq "netload") {
        $imgfile = graph_netload($dbh, $hostid, "Host", $x, $y, $endtime, $window, \$queries, $image);
    } elsif ($graph eq "network") {
        $imgfile = graph_network_combined($dbh, $hostid, $x, $y, $endtime, $window, \$queries, $image);
    } elsif ($graph eq "network_device" && $device && defined($vlan)) {
        $imgfile = graph_network_device($dbh, $hostid, $device, $vlan, "Host", $x, $y, $endtime, $window, \$queries, $image);
    } elsif ($graph eq "procs") {
        $imgfile = graph_procs($dbh, $hostid, "Host", $x, $y, $endtime, $window, \$queries, $image);
    } elsif ($graph eq "temperature") {
        $imgfile = graph_temperature($dbh, $hostid, $x, $y, $endtime, $window, $cpucount, \$queries, $image);
    } elsif ($graph eq "power") {
        $imgfile = graph_power($dbh, $hostid, $x, $y, $endtime, $window, $cpucount, \$queries, $image);
    } elsif ($graph eq "fans") {
        $imgfile = graph_fans($dbh, $hostid, $x, $y, $endtime, $window, $cpucount, \$queries, $image);
    }

    # -- hack to clean up imgfile string
    $imgfile =~ s/<IMG SRC=\/aware\///g;
    $imgfile =~ s/>//g;

    if (! -f $imgfile) { errorResponse(); exit(); }
    imageResponse($imgfile);
    unlink($imgfile);
    exit();

}

sub errorResponse {
    print "Content-type: $errorImageContentType\n";
    my $imageSize = -s $errorImageFile;
    print "Content-length: $imageSize\n";
    print "\n";
    open(IN, "<$errorImageFile");
    binmode(IN);
    while(<IN>) { print $_ ; }
    close(IN);
}

sub imageResponse {
    my ($image) = @_;
    my $type = $image;
    $type =~ s/^.*\.//g;
    print "Content-type: image/$type\n";
    my $imageSize = -s $image;
    print "Content-length: $imageSize\n";
    print "\n";
    open(IN, "<$image");
    binmode(IN);
    while(<IN>) { print $_; }
    close(IN);

}
