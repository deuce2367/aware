package ZUtils::Aware;

#############################################################################################
#############################################################################################
####
#### Aware-Specific Routines
####
#############################################################################################
#############################################################################################


#--------------------------------------------------------------------------------------------
# $Revision: 1.48 $
# $Date: 2010-07-29 19:15:53 $
# $Author: xxxxxx $
# $Name: not supported by cvs2svn $
#--------------------------------------------------------------------------------------------

use strict;
use ZUtils::Common;
use Time::Local;
use Sys::Hostname;
use DBI;

require Exporter;
our(@ISA, @EXPORT);
@ISA = qw(Exporter);
@EXPORT = qw(clear_profile_threshold_cache get_profile_threshold get_setting get_version graph_cpuload graph_diskload 
graph_diskutilization graph_device_utilization graph_filesystem graph_memory graph_shmemory graph_network_device 
graph_network_combined graph_netload graph_procs graph_sysio graph_sysload graph_temperature lookup_country 
lookup_gid print_array print_header print_header_simple get_window_fields graph_fans graph_power graph_device_svctimes);

#--------------------------------------------------------------------------------------------
# Perl Makefile Version Info 
#--------------------------------------------------------------------------------------------

our $VERSION = sprintf "%d.%03d", q$Revision 1.23 $ =~ /(\d+)/g;


#--------------------------------------------------------------------------------------------
# Subroutines
#--------------------------------------------------------------------------------------------


########################################################################################
#
# get_version()
#
# return the AWARE version
#
########################################################################################

sub get_version {

        return $VERSION;

}

########################################################################################
#
# get_profile_threshold (dbh, profile, threshold)
#
# - given a database connection, profile name, and threshold this routine will return
#   the value of that threshold, if N/A the default threshold will be returned
#
########################################################################################

my %thresholds;
sub get_profile_threshold {

    my ($dbh, $profile, $threshold) = @_;

    # -- cache the results to cut down on unnecessary DB hits
    if (!defined($thresholds{"$profile.$threshold"})) {

        my $sql = "select $threshold from thresholds, profile where profile.name = '$profile' and profile.id = thresholds.profile_id";
        my $sth = $dbh -> prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
        $sth -> execute() || print "Database Error (<b>$sql</b>): <font class=alert>" . $dbh->errstr . "</font>\n";
        my @row = $sth->fetchrow();
        my $value = $row[0];
        if (!defined($value)) {
            $value = get_setting($dbh, $threshold, "");
        }
        $sth->finish();

        $thresholds{"$profile.$threshold"} = $value;
    }

    return $thresholds{"$profile.$threshold"};
}



########################################################################################
#
# clear_profile_thresholds ()
#
# - clear the threshold cache if so requested by client
#
########################################################################################

sub clear_profile_threshold_cache {

        %thresholds = {};

}



########################################################################################
#
# lookup_country (dbh, latitude, longitude)
#
# - look up a country by latitude and longitude
#
########################################################################################

sub lookup_country {

    my ($dbh, $latitude, $longitude) = @_;

    my $country = "";
    my $sql;

    my $database = get_config("database");

    if ($database eq "oracle") {
        $sql = "select name from world_geometry where sdo_relate(shape, mdsys.SDO_GEOMETRY(2001, 8307,
        mdsys.SDO_POINT_TYPE($longitude, $latitude, NULL), NULL, NULL), 'mask=contains querytype=WINDOW') = 'TRUE'";
    } elsif ($database eq "mysql") {
        $sql = "select a.name from world_data a, world_geometry b where a.gid = b.gid and 
            contains(b.poly, GeomFromText('Point($longitude $latitude)'))";
    }
    
    my $sth = $dbh->prepare($sql) || print_log("ERROR ($sql): " . $dbh->errstr, 0);
    $sth->execute() || print_log("ERROR ($sql): " . $dbh->errstr, 0);
    my @row = $sth->fetchrow();
    $country = $row[0] || "Unknown";
    $sth->finish();

    return $country;

}


########################################################################################
#
# lookup_gid (dbh, country)
#
# - look up a gid for a country
#
########################################################################################

sub lookup_gid {

    my ($dbh, $country) = @_;

    $country =~ s/'/''/g;

    my $sql = "select gid from world where name = '$country'";
    my $sth = $dbh->prepare($sql) || print_log("ERROR ($sql): " . $dbh->errstr, 0);
    $sth->execute() || print_log("ERROR ($sql): " . $dbh->errstr, 0);
    my @row = $sth->fetchrow();
    my $gid = $row[0] || 0;
    $sth->finish();

    return $gid;

}


########################################################################################
#
# print_array(array)
#
# - print_array will print (html-format) the members of an array -- mostly used for
#   plot debugging
#
########################################################################################

sub print_array {

    my (@datasets) = @_;
    my $item;
    my @array;
    my $icount;
    my $inner;
    print "<table><tr class=even>\n";
    foreach $item (@datasets) {
        print "<td valign=top>$item:<br>\n";
        @array = @$item;
        $icount = 1;
        foreach $inner (@array) {
            print "  $icount) $inner<br>\n";
            $icount++;
        }
        print "</td>\n";
    }
    print "</tr></table>\n";
}


########################################################################################
#
# print_header (title, path, ajax)
#
# - given a title string print_header will print a web page header to the STDOUT 
#
########################################################################################

sub print_header {
    my ($title, $path, $ajaxBanner, $ajaxEnabled, $ajaxTimeout) = @_;

    my $datetime = get_time();
    if (!defined($ajaxBanner)) { $ajaxBanner = 0; }

    print "Content-type: text/html\n\n";

    print "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\"\n";
    print "\"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n";
    print "<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"en\" lang=\"en\">\n";
    #print "<html>\n";
    my $hostname = hostname();
    print "<title>$title ($hostname)</title>\n";

    my $site = get_config("site") || "N/A";
    
    my $banner = get_config("banner") || "N/A";
    $banner = "<p class=alert>$banner</p>";

    my $cssfile = get_config("cssfile") || "default.css";
    my $webdir = get_config("web_dir") || "aware";

    # -- check DB connectivity status 
    my $dbh = get_db_connection(0);
    my $dbconn = "<img src=images/db_ok>";
    if (!defined($dbh)) {
        $dbconn = "<img src=images/db_fail>";
    } else {
        $dbh->disconnect();
    }

    print "<link rel=stylesheet type=text/css href=/$webdir/css/$cssfile />\n";
    print "<script type=text/javascript src=/$webdir/includes/browser.js></script>\n";
    print "<script type=text/javascript src=/$webdir/menu_config.js></script>\n";
    print "<script type=text/javascript src=/$webdir/aware.js></script>\n";

    print "<div id=logo><center>\n";
    print "$banner";
    print "</center>";
    print "<div id=status>";
    print "<table>";
    print "<tr>";
    print "<th width=\"10%\" valign=top>System</th><td width=\"25%\" valign=top>$site</td>";
    print "<th valign=top>Updated</th><td id=ajaxUpdated valign=top>$datetime</td>";
    print "</tr>";
    print "<tr>";
    print "<th valign=top>Module</th><td valign=top>$title</td>";
    print "<th width=\"10%\" valign=top>Status</th><td width=\"55%\" id=ajaxStatusMessage valign=top>OK</td>";
    print "</tr>";
    print "</table>\n";
    print "</div>\n";
    print "</div>";
    print "<div id=menu><body onload=\"init();\">";
    if ($ajaxBanner) {
        #print "<input class=\"button\" onClick=\"document.getElementById('ajaxTimeout').value--;\" type=\"button\" value=\"<\">";
        print "<input id=\"ajaxTimeout\" name=\"ajaxTimeout\" value=\"$ajaxTimeout\" class=tinytext>\n";
        #print "<input class=\"button\" onClick=\"document.getElementById('ajaxTimeout').value++;\" type=\"button\" value=\">\">";
        print "<input class=button type=button onclick=\"toggle_refresh('/$webdir/$path');\" value=\"Auto-Update\">\n";
        if ($ajaxEnabled eq "yes") {
            print "<img id=ajaxEnabledImg src=images/reload>\n";
        } else {
            print "<img id=ajaxEnabledImg src=images/remove>\n";
        }
    }
    print "<b>Database:</b> $dbconn</body></div>\n";

}


########################################################################################
#
# print_header_simple (title)
#
# - given a title string print_header_simple will print a simplified (no menu) web page
#   header to the STDOUT 
#
########################################################################################

sub print_header_simple
{
    my ($title) = @_;

    print "Content-type: text/html\n\n";
    print "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\"\n";
    print "\"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n";
    print "<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"en\" lang=\"en\">\n";
    #print "<html>\n";
    print "<title>$title</title>\n";

    my $cssfile = get_config("cssfile") || "default.css";
    my $webdir = get_config("web_dir") || "aware";
    print "<link rel=stylesheet type=text/css href=/$webdir/css/$cssfile />\n";
    print "<script type=text/javascript src=/$webdir/aware.js></script>\n";
    print "<body>\n";

}


##############################################################################
#
# get_setting (dbh, name, default)
#
# - this function will return the value of the provided name from the database
#   unless it is not found or an error occurs, in that case the default value
#   will be returned

##############################################################################

sub get_setting {

    my ($dbh, $name, $default) = @_;

    my $sql = "select value from settings where label = '$name'";
    my $sth = $dbh->prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
    $sth -> execute() || print "Database Error (<b>$sql</b>): <font class=alert>" . $dbh->errstr . "</font>\n";

    my @row = $sth->fetchrow();
    $sth->finish();

    if (defined($row[0])) { $default = $row[0]; }

    return $default;

}



########################################################################################
#
# graph_filesystem (dbh, hostid, index, xsize, ysize, type)
#
# - plot the consumption for the specified filesystem
#
########################################################################################

sub graph_filesystem {

    my $dbh = $_[0];
    my $hostid = $_[1];
    my $device = $_[2];
    my $partition = $_[3];
    my $x_size = $_[4];
    my $y_size = $_[5];
    my $type = $_[6] || "pct"; 
    my $queries = $_[7] || "pct"; 
    my $image = $_[8];

    my $deviceStr = $device;
    $deviceStr =~ s/\//-/g;

    my @cols;
    my @pct;
    my $mount;
    my @legend = ("Used", "Free");


    my $sql = "select a.$type, a.mount, a.free from filesystem a where a.hostid = '$hostid' and a.device = '$device' and a.partition = '$partition'";
    my $sth = $dbh -> prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
    $sth -> execute() || print "Database Error (<b>$sql</b>): <font class=alert>" . $dbh->errstr . "</font>\n"; ${$queries}++;
    
    while (my @row = $sth -> fetchrow_array) {

        my $free = 100 - $row[0];
        my $used = $row[0];
    
        push(@pct,  $used);
        push(@pct,  $free);
        push(@cols, $used . "%");
        push(@cols, $free . "%");
        $mount = $row[1];

    }
    $sth->finish();
    
    my $data = GD::Graph::Data->new([[@cols],[@pct]]);
    my $my_graph =  GD::Graph::pie3d->new($x_size,$y_size);
    if ($type eq "pct") {
        $my_graph->set ( dclrs => [ qw(red green) ]);
    } else {
        $my_graph->set ( dclrs => [ qw(orange gold) ]);
    }
    
    #$my_graph -> set( title => "$mount",) or warn $my_graph->error;
    
    $my_graph->set_legend(@legend);
    $my_graph->plot($data) or return "Unable to plot Filesystem data";

    my $_htdoc = get_config("aware_home");
    my $_webdir = get_config("web_dir");
    my $suffix = "_$deviceStr\_$partition\_$type\_filesystem";
    save_chart($my_graph, "$_htdoc/web/$image-$suffix");
    my $IMGFORMAT = $my_graph->export_format();
    return "<IMG SRC=$_webdir/$image-$suffix.$IMGFORMAT>";

}


########################################################################################
#
# graph_memory (dbh, hostid, xsize, ysize, numpoints, now, window)
#
# - plot the memory status for the specified host
#
########################################################################################

sub graph_memory {

    my ($dbh, $hostid, $x_size, $y_size, $now, $window, $queries, $image) = @_;

    my $graphWindow = human_time($window * 3600);

    my @datasets;
    my @legend;
    my @label;
    my @used;
    my @free;
    my @cached;
    my @buffers;
    my @usedSwap;
    my @freeSwap;

    push(@legend, "used");
    push(@legend, "free");
    push(@legend, "cached");
    push(@legend, "buffers");
    push(@legend, "usedSwap");
    push(@legend, "freeSwap");

    # -- time window calculations
    my $graphdate = get_time($now);
    my $to_time = $now;
    my $from_time = $to_time - ($window * 3600);

    my $point = 0;
    my $max = 0;
    my $sth;
    my ($table, $dateFormat) = get_window_fields($window);

    my $sql = "select date_format(updated, '$dateFormat'), used, free, cached, buffers, usedSwap, freeSwap
        from memory$table where hostid = '$hostid' and updated >= from_unixtime($from_time) 
        and updated < from_unixtime($to_time) order by updated";

    $sth = $dbh -> prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
    $sth -> execute() || print "Database Error (<b>$sql</b>): <font class=alert>" . $dbh->errstr . "</font>\n"; ${$queries}++;

    while (my @row = $sth -> fetchrow_array) {
        $label[$point] = $row[0] || "No Data";
        $used[$point] = $row[1];
        $free[$point] = $row[2];
        $cached[$point] = $row[3];
        $buffers[$point] = $row[4];
        $usedSwap[$point] = $row[5];
        $freeSwap[$point] = $row[6];

        if ($max < 1) {
            my $cmax = $used[$point] + $free[$point] + $cached[$point] + $buffers[$point] + $usedSwap[$point] + $freeSwap[$point];
            $max = sprintf("%d", $cmax);
        }

        $point++;
    }
    $sth->finish();

    $max = sprintf("%d", $max + (100 - ($max % 100)) );

    push @datasets, [@label];
    push @datasets, [@used];
    push @datasets, [@free];
    push @datasets, [@cached];
    push @datasets, [@buffers];
    push @datasets, [@usedSwap];
    push @datasets, [@freeSwap];

    if (get_config("debug")) { print_array(@datasets)};

    my $skip = $point / 42;

    my $data = GD::Graph::Data->new([@datasets]);

    my $my_graph;
    if ($point >= 20) {
        $my_graph =  GD::Graph::bars->new($x_size,$y_size);
    } else {
        $my_graph =  GD::Graph::bars3d->new($x_size,$y_size);
    }


    $my_graph->set( 
        x_label           => "$graphdate -- $graphWindow",
        y_label           => 'Memory (MB)',
        title             => "Memory Usage",
        textclr           => get_config("g_textcolor"),
        labelclr          => get_config("g_labelcolor"),
        boxclr            => get_config("g_boxcolor"),
        fgclr             => get_config("g_fgcolor"),
        shadowclr         => get_config("g_shadowcolor"),
        legendclr         => get_config("g_legendcolor"),
        bgclr             => get_config("g_bgcolor"),
        axislabelclr      => get_config("g_axislabelcolor"),
        line_width        => get_config("g_linewidth"),
        x_labels_vertical => get_config("g_verticallabels"), 
        long_ticks        => get_config("g_longticks"),
        y_max_value       => $max,
        y_tick_number     => 10,
        y_min_value       => 0,
        accent_treshold   => $x_size,
        correct_width     => 0,
        cumulate          => 1,
        x_label_skip      => $skip,
        transparent       => get_config("g_transparent"),
    ) 
    or warn $my_graph->error;

    $my_graph->set ( dclrs => [ qw(red blue lgreen dgreen orange gold black) ]);
    $my_graph->set_legend(@legend);
    $my_graph->plot($data) or return "Unable to plot Memory Allocation";

    my $_htdoc = get_config("aware_home");
    my $_webdir = get_config("web_dir");
    my $suffix = "memory";
    save_chart($my_graph, "$_htdoc/web/$image-$suffix");
    my $IMGFORMAT = $my_graph->export_format();
    return "<IMG SRC=/$_webdir/$image-$suffix.$IMGFORMAT>";
}


########################################################################################
#
# graph_shmemory (dbh, hostid, xsize, ysize, numpoints, now, window)
#
# - plot the shared memory status for the specified host
#
########################################################################################

sub graph_shmemory {

    my ($dbh, $hostid, $x_size, $y_size, $now, $window, $queries, $image) = @_;

    my $graphWindow = human_time($window * 3600);

    my @datasets;
    my @legend;
    my @label;
    my @shmseg;
    my @shmsize;
    my @shmsem;

    push(@legend, "total shared memory");
    push(@legend, "# shared memory segments");

    # -- time window calculations
    my $graphdate = get_time($now);
    my $to_time = $now;
    my $from_time = $to_time - ($window * 3600);

    my $point = 0;
    my $max = 0;
    my $smax = 0;
    my $sth;
    my ($table, $dateFormat) = get_window_fields($window);

    my $sql = "select date_format(updated, '$dateFormat'), shmseg, shmsize / (1024 * 1024) 
        from memory$table where hostid = '$hostid' and updated >= from_unixtime($from_time) 
        and updated < from_unixtime($to_time) order by updated";

    $sth = $dbh -> prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
    $sth -> execute() || print "Database Error (<b>$sql</b>): <font class=alert>" . $dbh->errstr . "</font>\n"; ${$queries}++;

    while(my @row = $sth -> fetchrow_array) {

        $label[$point] = $row[0] || "No Data";
        $shmseg[$point] = $row[1] || 0;
        $shmsize[$point] = $row[2] || 0;

        if ($max < $shmsize[$point]) { $max = $shmsize[$point]; }
        if ($smax < $shmseg[$point]) { $smax = $shmseg[$point]; }

        $point++;
    }
    $sth->finish();

    $max = int($max * 1.15); if ($max < 10) { $max = 10; }
    $smax = int($smax * 1.15); if ($smax < 10) { $smax = 10; }

    push @datasets, [@label];
    push @datasets, [@shmsize];
    push @datasets, [@shmseg];

    if (get_config("debug")) { print_array(@datasets)};

    my $skip = $point / 42;

    my $data = GD::Graph::Data->new([@datasets]);

    my $my_graph =  GD::Graph::lines->new($x_size,$y_size);


    $my_graph->set( 
        x_label           => "$graphdate -- $graphWindow",
        y1_label          => 'Memory (MB)',
        y2_label          => '# of Segments',
        title             => "Shared Memory Usage",
        textclr           => get_config("g_textcolor"),
        labelclr          => get_config("g_labelcolor"),
        boxclr            => get_config("g_boxcolor"),
        fgclr             => get_config("g_fgcolor"),
        shadowclr         => get_config("g_shadowcolor"),
        legendclr         => get_config("g_legendcolor"),
        bgclr             => get_config("g_bgcolor"),
        axislabelclr      => get_config("g_axislabelcolor"),
        line_width        => get_config("g_linewidth"),
        x_labels_vertical => get_config("g_verticallabels"), 
        long_ticks        => get_config("g_longticks"),
        y_min_value      => 0,
        y_max_value      => $max,
        y1_min_value      => 0,
        y1_max_value      => $max,
        y2_min_value      => 0,
        y2_max_value      => $smax,
        y_tick_number     => 10,
        two_axes          => 1,
        accent_treshold   => $x_size,
        correct_width     => 0,
        cumulate          => 0,
        x_label_skip      => $skip,
        transparent       => get_config("g_transparent"),
    ) 
    or warn $my_graph->error;

    $my_graph->set ( dclrs => [ qw(red blue lgreen dgreen orange gold black) ]);
    $my_graph->set_legend(@legend);
    $my_graph->plot($data) or return "Unable to plot Shared Memory Allocation";

    my $_htdoc = get_config("aware_home");
    my $_webdir = get_config("web_dir");
    my $suffix = "shared_memory";
    save_chart($my_graph, "$_htdoc/web/$image-$suffix");
    my $IMGFORMAT = $my_graph->export_format();
    return "<IMG SRC=/$_webdir/$image-$suffix.$IMGFORMAT>";
}


########################################################################################
#
# graph_power(dbh, hostid, xsize, ysize, numpoints, daysAgo, cpus)
#
# - plot the power sensors for the specified host
#
########################################################################################

sub graph_power {

    my ($dbh, $hostid, $x_size, $y_size, $now, $window, $cpucount, $queries, $image) = @_;

    my $graphWindow = human_time($window * 3600);

    my @legend;
    my @times;
    my %readings;
    my %labels;
    my %datetimes;

    # -- time window calculations
    my $graphdate = get_time($now);
    my $to_time = $now;
    my $from_time = $to_time - ($window * 3600);
    
    my $point = 0;
    my $max = 0;
    my $sth;
    my ($table, $dateFormat) = get_window_fields($window);

    my $sql = "select date_format(sensor_reading$table.updated, '$dateFormat'), reading, label 
        from sensor_reading$table, sensor 
        where sensor.hostid = '$hostid' and sensor.id = sensor_reading$table.sensor_id and units = 'V' 
        and sensor_reading$table.updated >= from_unixtime($from_time) and sensor_reading$table.updated < from_unixtime($to_time) 
        order by sensor_reading$table.updated, sensor.label";

    $sth = $dbh -> prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
    $sth -> execute() || print "Database Error (<b>$sql</b>): <font class=alert>" . $dbh->errstr . "</font>\n"; ${$queries}++;


    while(my @row = $sth -> fetchrow_array) {
        my $datetime = $row[0] || "";
        my $reading = $row[1] || 0;
        my $label = $row[2] || next;

        if ($reading > $max) { $max = $reading; }

        if (!defined($labels{$label})) { 
            $labels{$label} = 1;
            push(@legend, $label); 
        }

        if (!defined($datetimes{$datetime})) { 
            push(@times, $datetime); 
            $datetimes{$datetime} = 1;
            $point++;
        }

        if (!defined($readings{"$datetime-$label"})) {
            $readings{"$datetime-$label"} = $reading;
        } 

    }
    $sth->finish();
    $max = int($max * 1.10);
    $max = sprintf("%.0f", $max + 5 - ($max % 5));

    my @datasets;
    push (@datasets, [@times]);
    foreach my $label (@legend) {
        my @array;
        foreach my $time (@times) {
            if (defined($readings{"$time-$label"})) {
                push(@array, $readings{"$time-$label"});
            } else {
                push(@array, 0);
            }
        }
        push(@datasets, [@array]);
    }

    if (get_config("debug")) { print_array(@datasets)};

    my $skip = $point / 42;

    my $data = GD::Graph::Data->new([@datasets]);

    my $my_graph = GD::Graph::lines->new($x_size,$y_size);

    $my_graph->set( 
        x_label           => "$graphdate -- $graphWindow",
        y_label           => 'Power (Voltage)',
        title             => "Power Sensors",
        textclr           => get_config("g_textcolor"),
        labelclr          => get_config("g_labelcolor"),
        boxclr            => get_config("g_boxcolor"),
        fgclr             => get_config("g_fgcolor"),
        shadowclr         => get_config("g_shadowcolor"),
        legendclr         => get_config("g_legendcolor"),
        bgclr             => get_config("g_bgcolor"),
        axislabelclr      => get_config("g_axislabelcolor"),
        line_width        => 3,
        x_labels_vertical => get_config("g_verticallabels"), 
        long_ticks        => get_config("g_longticks"),
        y_tick_number     => 16,
        y_max_value       => $max,
        y_min_value       => 0,
        correct_width     => 0,
        x_label_skip      => $skip,
        transparent       => get_config("g_transparent"),
    ) 
    or warn $my_graph->error;

    $my_graph->set ( dclrs => [ qw( white lblue lred gold cyan dblue purple gray pink) ]); 
    $my_graph->set_legend(@legend);
    $my_graph->plot($data) or return "Unable to plot Power";

    my $_htdoc = get_config("aware_home");
    my $_webdir = get_config("web_dir");
    my $suffix = "power";
    save_chart($my_graph, "$_htdoc/web/$image-$suffix");
    my $IMGFORMAT = $my_graph->export_format();
    return "<IMG SRC=/$_webdir/$image-$suffix.$IMGFORMAT>";
}


########################################################################################
#
# graph_fans(dbh, hostid, xsize, ysize, numpoints, daysAgo, cpus)
#
# - plot the fan sensors for the specified host
#
########################################################################################

sub graph_fans {

    my ($dbh, $hostid, $x_size, $y_size, $now, $window, $cpucount, $queries, $image) = @_;

    my $graphWindow = human_time($window * 3600);

    my @legend;
    my @times;
    my %readings;
    my %labels;
    my %datetimes;

    # -- time window calculations
    my $graphdate = get_time($now);
    my $to_time = $now;
    my $from_time = $to_time - ($window * 3600);
    
    my $point = 0;
    my $max = 0;
    my $sth;
    my ($table, $dateFormat) = get_window_fields($window);

    my $sql = "select date_format(sensor_reading$table.updated, '$dateFormat'), reading, label 
        from sensor_reading$table, sensor 
        where sensor.hostid = '$hostid' and sensor.id = sensor_reading$table.sensor_id and units = 'RPM' 
        and sensor_reading$table.updated >= from_unixtime($from_time) and sensor_reading$table.updated < from_unixtime($to_time) 
        order by sensor_reading$table.updated, sensor.label";

    $sth = $dbh -> prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
    $sth -> execute() || print "Database Error (<b>$sql</b>): <font class=alert>" . $dbh->errstr . "</font>\n"; ${$queries}++;


    while(my @row = $sth -> fetchrow_array) {
        my $datetime = $row[0] || "";
        my $reading = $row[1] || 0;
        my $label = $row[2] || next;

        if ($reading > $max) { $max = $reading; }

        if (!defined($labels{$label})) { 
            $labels{$label} = 1;
            push(@legend, $label); 
        }

        if (!defined($datetimes{$datetime})) { 
            push(@times, $datetime); 
            $datetimes{$datetime} = 1;
            $point++;
        }

        if (!defined($readings{"$datetime-$label"})) {
            $readings{"$datetime-$label"} = $reading;
        } 

    }
    $sth->finish();
    $max = int($max * 1.10);
    $max = sprintf("%.0f", $max + 1000 - ($max % 1000));

    my @datasets;
    push (@datasets, [@times]);
    foreach my $label (@legend) {
        my @array;
        foreach my $time (@times) {
            if (defined($readings{"$time-$label"})) {
                push(@array, $readings{"$time-$label"});
            } else {
                push(@array, 0);
            }
        }
        push(@datasets, [@array]);
    }

    if (get_config("debug")) { print_array(@datasets)};

    my $skip = $point / 42;

    my $data = GD::Graph::Data->new([@datasets]);

    my $my_graph = GD::Graph::lines->new($x_size,$y_size);

    $my_graph->set( 
        x_label           => "$graphdate -- $graphWindow",
        y_label           => 'Fan Speed(RPMS)',
        title             => "Fan Sensors",
        textclr           => get_config("g_textcolor"),
        labelclr          => get_config("g_labelcolor"),
        boxclr            => get_config("g_boxcolor"),
        fgclr             => get_config("g_fgcolor"),
        shadowclr         => get_config("g_shadowcolor"),
        legendclr         => get_config("g_legendcolor"),
        bgclr             => get_config("g_bgcolor"),
        axislabelclr      => get_config("g_axislabelcolor"),
        line_width        => 3,
        x_labels_vertical => get_config("g_verticallabels"), 
        long_ticks        => get_config("g_longticks"),
        y_tick_number     => 16,
        y_max_value       => $max,
        y_min_value       => 0,
        correct_width     => 0,
        x_label_skip      => $skip,
        transparent       => get_config("g_transparent"),
    ) 
    or warn $my_graph->error;

    $my_graph->set ( dclrs => [ qw( white lblue lred gold cyan dblue purple gray pink) ]); 
    $my_graph->set_legend(@legend);
    $my_graph->plot($data) or return "Unable to plot Fans";

    my $_htdoc = get_config("aware_home");
    my $_webdir = get_config("web_dir");
    my $suffix = "fans";
    save_chart($my_graph, "$_htdoc/web/$image-$suffix");
    my $IMGFORMAT = $my_graph->export_format();
    return "<IMG SRC=/$_webdir/$image-$suffix.$IMGFORMAT>";
}


########################################################################################
#
# graph_temperature (dbh, hostid, xsize, ysize, numpoints, daysAgo, cpus)
#
# - plot the temperature sensors for the specified host
#
########################################################################################

sub graph_temperature {

    my ($dbh, $hostid, $x_size, $y_size, $now, $window, $cpucount, $queries, $image) = @_;

    my $graphWindow = human_time($window * 3600);

    my @legend;
    my @times;
    my %readings;
    my %labels;
    my %datetimes;

    # -- time window calculations
    my $graphdate = get_time($now);
    my $to_time = $now;
    my $from_time = $to_time - ($window * 3600);
    
    my $point = 0;
    my $max = 0;
    my $sth;
    my ($table, $dateFormat) = get_window_fields($window);

    my $sql = "select date_format(sensor_reading$table.updated, '$dateFormat'), reading, label 
        from sensor_reading$table, sensor 
        where sensor.hostid = '$hostid' and sensor.id = sensor_reading$table.sensor_id and units = 'C' 
        and sensor_reading$table.updated >= from_unixtime($from_time) and sensor_reading$table.updated < from_unixtime($to_time) 
        order by sensor_reading$table.updated, sensor.label";

    $sth = $dbh -> prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
    $sth -> execute() || print "Database Error (<b>$sql</b>): <font class=alert>" . $dbh->errstr . "</font>\n"; ${$queries}++;


    while(my @row = $sth -> fetchrow_array) {
        my $datetime = $row[0] || "";
        my $reading = $row[1] || 0;
        my $label = $row[2] || next;

        if ($reading > $max) { $max = $reading; }

        if (!defined($labels{$label})) { 
            $labels{$label} = 1;
            push(@legend, $label); 
        }

        if (!defined($datetimes{$datetime})) { 
            push(@times, $datetime); 
            $datetimes{$datetime} = 1;
            $point++;
        }

        if (!defined($readings{"$datetime-$label"})) {
            $readings{"$datetime-$label"} = $reading;
        } 

    }
    $sth->finish();
    $max = $max * 1.10;
    $max = sprintf("%.0f", $max + 5 - ($max % 5));

    my @datasets;
    push (@datasets, [@times]);
    foreach my $label (@legend) {
        my @array;
        foreach my $time (@times) {
            if (defined($readings{"$time-$label"})) {
                push(@array, $readings{"$time-$label"});
            } else {
                push(@array, 0);
            }
        }
        push(@datasets, [@array]);
    }

    if (get_config("debug")) { print_array(@datasets)};

    my $skip = $point / 42;

    my $data = GD::Graph::Data->new([@datasets]);

    my $my_graph = GD::Graph::lines->new($x_size,$y_size);

    $my_graph->set( 
        x_label           => "$graphdate -- $graphWindow",
        y_label           => 'Temperature (Celsius)',
        title             => "Temperature Sensors",
        textclr           => get_config("g_textcolor"),
        labelclr          => get_config("g_labelcolor"),
        boxclr            => get_config("g_boxcolor"),
        fgclr             => get_config("g_fgcolor"),
        shadowclr         => get_config("g_shadowcolor"),
        legendclr         => get_config("g_legendcolor"),
        bgclr             => get_config("g_bgcolor"),
        axislabelclr      => get_config("g_axislabelcolor"),
        line_width        => 3,
        x_labels_vertical => get_config("g_verticallabels"), 
        long_ticks        => get_config("g_longticks"),
        y_tick_number     => 16,
        y_max_value       => $max,
        y_min_value       => 0,
        correct_width     => 0,
        x_label_skip      => $skip,
        transparent       => get_config("g_transparent"),
    ) 
    or warn $my_graph->error;

    $my_graph->set ( dclrs => [ qw( white lblue lred gold cyan dblue purple gray pink) ]); 
    $my_graph->set_legend(@legend);
    $my_graph->plot($data) or return "Unable to plot Temperature Sensors";

    my $_htdoc = get_config("aware_home");
    my $_webdir = get_config("web_dir");
    my $suffix = "temperature";
    save_chart($my_graph, "$_htdoc/web/$image-$suffix");
    my $IMGFORMAT = $my_graph->export_format();
    return "<IMG SRC=/$_webdir/$image-$suffix.$IMGFORMAT>";
}


########################################################################################
#
# graph_sysload (dbh, hostid, type, xsize, ysize, numpoints, daysAgo, windowSize)
#
# - plot the sysload for the specified host
#
########################################################################################

sub graph_sysload {

    my ($dbh, $id, $type, $x_size, $y_size, $now, $window, $queries, $image) = @_;

    # -- figure out if this is a profile or a host plot
    my $field = "b.profile_id";
    if (lc($type) eq "host") { $field = "a.hostid"; }
    
    # -- common variables
    my @label;
    my @datasets;
    my %plots;
    my $graphWindow = human_time($window * 3600);

    # -- sysload variables
    my @sysload_legend;
    my @userload;
    my @sysload;

    # -- sysload legend
    for (my $i = 0; $i < 1; $i++) { 
        push (@sysload_legend, "User"); 
        push (@sysload_legend, "System"); 
    }

    # -- time window calculations
    my $graphdate = get_time($now);
    my $to_time = $now;
    my $from_time = $to_time - ($window * 3600);
    
    my $point = 0;
    my $sth;
    my ($table, $dateFormat) = get_window_fields($window);

    my $sql = "select date_format(a.updated, '$dateFormat'), avg(a.user), avg(a.idle)
            from sysload$table a, node b where a.hostid = b.id and $field = '$id' and a.updated >= from_unixtime($from_time) 
            and a.updated < from_unixtime($to_time) group by date_format(a.updated, '$dateFormat') order by a.updated";

    $sth = $dbh -> prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
    $sth -> execute() || print "Database Error (<b>$sql</b>): <font class=alert>" . $dbh->errstr . "</font>\n"; ${$queries}++;

    my %dates;
    my $rows = 0;
    
    while(my @row = $sth -> fetchrow_array) {
        #if ($point == 0) { print $sql; }
        my $updated = $row[0];

        # -- determine if this is a new date
        if (!defined($dates{$updated})) {
            $dates{$updated} = 1;
            if ($rows) {
                $point++;
            }
        } 

        # -- sysload data point
        $label[$point] = $row[0] || "No Data";
        $userload[$point] = $row[1] || 0;
        $sysload[$point] = 100 - ($row[1] + $row[2]) || 0;

        $rows++;
    }
    $sth->finish();


    # -- generic plot setting(s)    
    my $skip = $point / 42;

    # plot the sysload
    @datasets = ();
    push @datasets, [@label];
    push @datasets, [@userload];
    push @datasets, [@sysload];

    if (get_config("debug")) { print_array(@datasets)};

    my $sysload_data = GD::Graph::Data->new([@datasets]);

    my $sysload_my_graph =  GD::Graph::area->new($x_size,$y_size);

    $sysload_my_graph->set( 
        x_label           => "$graphdate -- $graphWindow",
        y_label           => 'Load (%)',
        title             => "System Load",
        textclr           => get_config("g_textcolor"),
        labelclr          => get_config("g_labelcolor"),
        boxclr            => get_config("g_boxcolor"),
        fgclr             => get_config("g_fgcolor"),
        shadowclr         => get_config("g_shadowcolor"),
        legendclr         => get_config("g_legendcolor"),
        bgclr             => get_config("g_bgcolor"),
        axislabelclr      => get_config("g_axislabelcolor"),
        line_width        => get_config("g_linewidth"),
        x_labels_vertical => get_config("g_verticallabels"), 
        long_ticks        => get_config("g_longticks"),
        accent_treshold   => $x_size,
        y_tick_number     => 10,
        cumulate          => 1,
        y_max_value       => 100,
        y_min_value       => 0,
        x_label_skip      => $skip,
        transparent       => get_config("g_transparent"),
    ) 
    or warn $sysload_my_graph->error;

    $sysload_my_graph->set ( dclrs => [ qw(lgreen red lgray black) ]);
    $sysload_my_graph->set ( borderclrs => [ qw(dred gray black) ]);
    $sysload_my_graph->set_legend(@sysload_legend);
    $sysload_my_graph->plot($sysload_data) or return "Unable to plot System Load";

    my $_htdoc = get_config("aware_home");
    my $_webdir = get_config("web_dir");
    my $suffix = "sysload";
    save_chart($sysload_my_graph, "$_htdoc/web/$image-$suffix");
    my $IMGFORMAT = $sysload_my_graph->export_format();
    return "<IMG SRC=/$_webdir/$image-$suffix.$IMGFORMAT>";

}


########################################################################################
#
# graph_cpuload(dbh, hostid, type, xsize, ysize, numpoints, daysAgo, cpus)
#
# - plot the various sysloads for the specified host
#
########################################################################################

sub graph_cpuload {

    my ($dbh, $id, $type, $x_size, $y_size, $now, $window, $queries, $image) = @_;

    # -- figure out if this is a profile or a host plot
    my $field = "b.profile_id";
    if (lc($type) eq "host") { $field = "a.hostid"; }
    
    # -- common variables
    my @label;
    my @datasets;
    my %plots;
    my $graphWindow = human_time($window * 3600);

    # -- cpu bar graph variables
    my @cpu_user;
    my @cpu_system;
    my @cpu_iowait;
    my @cpu_nice;
    my @cpu_irq;
    my @cpu_softirq;
    #my @cpu_idle;
    my @cpu_legend;

    # -- cpu legend
    push(@cpu_legend, "user");
    push(@cpu_legend, "system");
    push(@cpu_legend, "iowait");
    push(@cpu_legend, "nice");
    push(@cpu_legend, "irq");
    push(@cpu_legend, "softirq");
    #push(@cpu_legend, "idle");

    # -- time window calculations
    my $graphdate = get_time($now);
    my $to_time = $now;
    my $from_time = $to_time - ($window * 3600);
    
    my $point = 0;
    my $sth;
    my ($table, $dateFormat) = get_window_fields($window);

    my $sql = "select date_format(a.updated, '$dateFormat'), avg(user), avg(system), avg(iowait), avg(nice), avg(irq), avg(softirq)
        from sysload$table a, node b where a.hostid = b.id and $field = '$id' and a.updated >= from_unixtime($from_time) 
        and a.updated < from_unixtime($to_time) group by date_format(a.updated, '$dateFormat') order by a.updated";

        $sth = $dbh -> prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
        $sth -> execute() || print "Database Error (<b>$sql</b>): <font class=alert>" . $dbh->errstr . "</font>\n"; ${$queries}++;

    my %dates;
    my $rows = 0;

    while (my @row = $sth -> fetchrow_array) {

        my $updated = $row[0];

        # -- determine if this is a new date
        if (!defined($dates{$updated})) {
            $dates{$updated} = 1;
            if ($rows) {
                $point++;
            }
        } 

        # -- cpu data points
        $label[$point] = $row[0] || "";
        $cpu_user[$point] = $row[1] || 0;
        $cpu_system[$point] = $row[2] || 0;
        $cpu_iowait[$point] = $row[3] || 0;
        $cpu_nice[$point] = $row[4] || 0;
        $cpu_irq[$point] = $row[5] || 0;
        $cpu_softirq[$point] = $row[6] || 0;
        #$cpu_idle[$point] = 100 - $cpu_user[$point] - $cpu_system[$point] - $cpu_iowait[$point] - $cpu_nice[$point] - $cpu_irq[$point] - $cpu_softirq[$point];

        $rows++;
    }
    $sth->finish();


    # -- generic plot setting(s)    
    my $skip = $point / 42;

    # -- handle CPU Graph
    @datasets = ();
    push @datasets, [@label];
    push @datasets, [@cpu_user];
    push @datasets, [@cpu_system];
    push @datasets, [@cpu_iowait];
    push @datasets, [@cpu_nice];
    push @datasets, [@cpu_irq];
    push @datasets, [@cpu_softirq];
    #push @datasets, [@cpu_idle];

    if (get_config("debug")) { print_array(@datasets)};

    my $data = GD::Graph::Data->new([@datasets]);

    my $cpuload_my_graph;
    if ($point < 20) {
        $cpuload_my_graph =  GD::Graph::bars3d->new($x_size,$y_size);
    } else {
        $cpuload_my_graph =  GD::Graph::bars->new($x_size,$y_size);
    }

    $cpuload_my_graph->set( 
        x_label           => "$graphdate -- $graphWindow",
        y_label           => 'Usage (%)',
        title             => "CPU Utilization",
        textclr           => get_config("g_textcolor"),
        labelclr          => get_config("g_labelcolor"),
        shadowclr         => get_config("g_shadowcolor"),
        legendclr         => get_config("g_legendcolor"),
        boxclr            => get_config("g_boxcolor"),
        fgclr             => get_config("g_fgcolor"),
        bgclr             => get_config("g_bgcolor"),
        axislabelclr      => get_config("g_axislabelcolor"),
        line_width        => get_config("g_linewidth"),
        x_labels_vertical => get_config("g_verticallabels"), 
        long_ticks        => get_config("g_longticks"),
        y_max_value       => 100,
        y_tick_number     => 10,
        y_min_value       => 0,
        accent_treshold   => $x_size,
        correct_width     => 0,
        cumulate          => 1,
        x_label_skip      => $skip,
        transparent       => get_config("g_transparent"),
    ) 
    or warn $cpuload_my_graph->error;

    $cpuload_my_graph->set ( dclrs => [ qw(dblue lblue cyan pink white gold black) ]);
    $cpuload_my_graph->set_legend(@cpu_legend);
    $cpuload_my_graph->plot($data) or return "Unable to plot CPU Allocation";

    my $_htdoc = get_config("aware_home");
    my $_webdir = get_config("web_dir");
    my $suffix = "$type\_cpuload";
    save_chart($cpuload_my_graph, "$_htdoc/web/$image-$suffix");
    my $IMGFORMAT = $cpuload_my_graph->export_format();
    
    return "<IMG SRC=/$_webdir/$image-$suffix.$IMGFORMAT>";

}


########################################################################################
#
# graph_network_combined (dbh, hostid, xsize, ysize, numpoints, daysAgo)
#
# - plot the statistics for all network devices on the specified host
#
########################################################################################

sub graph_network_combined {

    my ($dbh, $id, $x_size, $y_size, $now, $window, $queries, $image) = @_;

    # -- common variables
    my @label;
    my @datasets;
    my @legend;
    my $graphWindow = human_time($window * 3600);
    my $numdevices = 0;
    my $netload_max = 100;
    my @bytesIn;
    my @bytesOut;

    my ($sth, $sql);

    $sql = "select device from nic where hostid = $id group by device order by device";
    $sth = $dbh -> prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
    $sth -> execute() || print "Database Error (<b>$sql</b>): <font class=alert>" . $dbh->errstr . "</font>\n"; ${$queries}++;
    my %devices;
    while (my @row = $sth->fetchrow()) {
        my $device = $row[0];
        push(@legend, "$device (RX)");
        push(@legend, "$device (TX)");
        $devices{$device} = $numdevices;
        $numdevices++;
        
    }
    if (!$numdevices) { return "No network devices found for this host!"; }


    # -- time window calculations
    my $to_time = $now;
    my $from_time = $to_time - ($window * 3600);
    my $interval = 120;

    my $graphdate = get_time($to_time);

    my $point = 0;
    my ($table, $dateFormat) = get_window_fields($window);

    $sql = "select date_format(a.updated, '$dateFormat'), a.tx / 1000, a.rx / 1000, a.device 
            from netload$table a where a.updated >= from_unixtime($from_time) and a.hostid = $id 
            and a.updated < from_unixtime($to_time)
            order by a.updated, a.device";

    $sth = $dbh -> prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
    $sth -> execute() || print "Database Error (<b>$sql</b>): <font class=alert>" . $dbh->errstr . "</font>\n"; ${$queries}++;

    my $rows = 0;
    my $total = 0;
    my %dates;
    while (my @row = $sth -> fetchrow_array) {
        # -- only need one label
        my $updated = $row[0] || "No Data";
        my $tx = $row[1] || 0;
        my $rx = $row[2] || 0;
        my $device = $row[3] || "N/A";

        if (!defined($devices{$device})) { next; }

        # -- determine if this is a new date
        if (!defined($dates{$updated})) {
            $dates{$updated} = 1;
            if ($rows) {
                #$label[$point] =~ s/:[0-9]{2}$//;
                $point++;
                if ($total > $netload_max) { $netload_max = $total; }
                $total = 0;
            }
        } 

        $label[$point] = $updated; 
    
        # -- network throughput by device
        $bytesIn[$devices{$device}][$point] = $rx;
        $bytesOut[$devices{$device}][$point] = $tx;

        $total = $total + $tx + $rx;

        $rows++;

    }
    $label[$point] =~ s/:[0-9]{2}$//;

    $sth->finish();

    # -- generic plot setting(s)    
    my $skip = $point / 42;

    # -- handle netload graph
    @datasets = ();
    push @datasets, [@label];

    for (my $i = 0; $i <= $#bytesIn; $i++) {
        my @array;
        for (my $j = 0; $j < $point; $j++) {
            push(@array, $bytesIn[$i][$j]);
        }    
        push @datasets, [@array];

        @array = ();
        for (my $j = 0; $j < $point; $j++) {
            push(@array, $bytesOut[$i][$j]);
        }    
        push @datasets, [@array];
    }

    if (get_config("debug")) { print_array(@datasets)};

    my $data = GD::Graph::Data->new([@datasets]);
    $netload_max = sprintf("%.0f", $netload_max * 1.15);
    $netload_max = sprintf("%.0f", $netload_max + 1000 - ($netload_max % 1000));

    my $netload_my_graph;
    if ($point <= 20) {
        $netload_my_graph =  GD::Graph::bars3d->new($x_size,$y_size);
    } else {
        $netload_my_graph =  GD::Graph::bars->new($x_size,$y_size);
    }

    $netload_my_graph->set( 
        x_label           => "$graphdate -- $graphWindow",
        y_label           => 'Throughput (kB/s)',
        title             => "Combined Network I/O",
        textclr           => get_config("g_textcolor"),
        labelclr          => get_config("g_labelcolor"),
        shadowclr         => get_config("g_shadowcolor"),
        legendclr         => get_config("g_legendcolor"),
        boxclr            => get_config("g_boxcolor"),
        fgclr             => get_config("g_fgcolor"),
        bgclr             => get_config("g_bgcolor"),
        axislabelclr      => get_config("g_axislabelcolor"),
        line_width        => get_config("g_linewidth"),
        x_labels_vertical => get_config("g_verticallabels"), 
        long_ticks        => get_config("g_longticks"),
        y_max_value       => $netload_max,
        y_tick_number     => 10,
        y_min_value       => 0,
        accent_treshold   => $x_size,
        correct_width     => 0,
        cumulate          => 1,
        x_label_skip      => $skip,
        transparent       => get_config("g_transparent"),
    ) 
    or warn $netload_my_graph->error;

    $netload_my_graph->set ( dclrs => [ qw(cyan lblue lred dred white gray lyellow yellow 
            lpurple purple lorange orange pink dpink marine dpurple lbrown dbrown) ]);

    $netload_my_graph->set_legend(@legend);
    $netload_my_graph->plot($data) or return "Unable to plot Combined Network Load";

    my $_htdoc = get_config("aware_home");
    my $_webdir = get_config("web_dir");
    my $suffix = "netload-combined";
    save_chart($netload_my_graph, "$_htdoc/web/$image-$suffix");
    my $IMGFORMAT = $netload_my_graph->export_format();
    my $html = "<IMG SRC=/$_webdir/$image-$suffix.$IMGFORMAT>";
    return $html;
}



########################################################################################
#
# graph_network_device (dbh, hostid, device, vlan, type, xsize, ysize, numpoints, daysAgo, cpus)
#
# - plot the tx/rx traffic for a specified host, device, vlan
#
########################################################################################

sub graph_network_device {

    my ($dbh, $id, $device, $vlan, $type, $x_size, $y_size, $now, $window, $queries, $image) = @_;

    # -- figure out if this is a profile or a host plot
    my $field = "b.profile_id";
    if (lc($type) eq "host") { $field = "a.hostid"; }

    
    # -- common variables
    my @label;
    my @datasets;
    my %plots;
    my $graphWindow = human_time($window * 3600);
    my $deviceName = "/dev/$device";
    if ($vlan) { $deviceName .= ".$vlan"; }

    # -- netload variables
    my @netload_legend;
    my @tx;
    my @rx;
    my $netload_max = 100;

    # -- netload legend
    for (my $i = 0; $i < 1; $i++) { 
        push (@netload_legend, "TX"); 
        push (@netload_legend, "RX"); 
    }

    # -- time window calculations
    my $graphdate = get_time($now);
    my $to_time = $now;
    my $from_time = $to_time - ($window * 3600);
    
    my $point = 0;
    my $sth;
    my ($table, $dateFormat) = get_window_fields($window);

    my $sql = "select date_format(a.updated, '$dateFormat'), avg(a.tx/1000), avg(a.rx/1000) from netload$table a, node b 
        where a.hostid = b.id and $field = '$id' and a.updated >= from_unixtime($from_time) and a.vlan = $vlan and a.device = '$device'
        and a.updated < from_unixtime($to_time) group by date_format(a.updated, '$dateFormat') order by a.updated";

    $sth = $dbh -> prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
    $sth -> execute() || print "Database Error (<b>$sql</b>): <font class=alert>" . $dbh->errstr . "</font>\n"; ${$queries}++;

    my %dates;
    my $rows = 0;

    while(my @row = $sth -> fetchrow_array) {

        my $updated = $row[0];

        # -- determine if this is a new date
        if (!defined($dates{$updated})) {
            $dates{$updated} = 1;
            if ($rows) {
                $point++;
            }
        } 

        # -- netload data points
        $label[$point] = $row[0] || "";
        $tx[$point] = $row[1] || 0;
        $rx[$point] = $row[2] || 0;
        if ($tx[$point] + $rx[$point] > $netload_max) { $netload_max = $tx[$point] + $rx[$point]; }

        $rows++;
    }
    $sth->finish();


    # -- generic plot setting(s)    
    my $skip = $point / 42;

    # -- plot the netload
    $netload_max = sprintf("%.0f", $netload_max * 1.15);
    $netload_max = sprintf("%.0f", $netload_max + 1000 - ($netload_max % 1000));
    if (get_config("debug")) { print_array(@datasets)};

    @datasets = ();
    push @datasets, [@label];
    push @datasets, [@tx];
    push @datasets, [@rx];

    my $netload_data = GD::Graph::Data->new([@datasets]);

    my $netload_my_graph;
    if ($point <= 20) {
        $netload_my_graph =  GD::Graph::bars3d->new($x_size,$y_size);
    } else {
        $netload_my_graph =  GD::Graph::bars->new($x_size,$y_size);
    }

    $netload_my_graph->set( 
        x_label           => "$graphdate -- $graphWindow",
        y_label           => 'Throughput (kB/s)',
        title             => "Network I/O on $deviceName",
        textclr           => get_config("g_textcolor"),
        labelclr          => get_config("g_labelcolor"),
        boxclr            => get_config("g_boxcolor"),
        fgclr             => get_config("g_fgcolor"),
        shadowclr         => get_config("g_shadowcolor"),
        legendclr         => get_config("g_legendcolor"),
        bgclr             => get_config("g_bgcolor"),
        axislabelclr      => get_config("g_axislabelcolor"),
        line_width        => get_config("g_linewidth"),
        x_labels_vertical => get_config("g_verticallabels"), 
        long_ticks        => get_config("g_longticks"),
        y_max_value       => $netload_max,
        y_tick_number     => 10,
        y_min_value       => 0,
        #overwrite        => 0,
        cumulate          => 1,
        correct_width     => 0,
        x_label_skip      => $skip,
        transparent       => get_config("g_transparent"),
        ) 
        or warn $netload_my_graph->error;

    $netload_my_graph->set ( dclrs => [ qw(blue lgray black) ]);
    $netload_my_graph->set_legend(@netload_legend);
    $netload_my_graph->plot($netload_data) or return "Unable to plot network throughput";

    my $_htdoc = get_config("aware_home");
    my $_webdir = get_config("web_dir");
    my $suffix = "netload-$device-$vlan";
    save_chart($netload_my_graph, "$_htdoc/web/$image-$suffix");
    my $IMGFORMAT = $netload_my_graph->export_format();
    return "<IMG SRC=/$_webdir/$image-$suffix.$IMGFORMAT>";

}



########################################################################################
#
# graph_netload(dbh, hostid, type, xsize, ysize, numpoints, daysAgo, cpus)
#
# - plot the various sysloads for the specified host
#
########################################################################################

sub graph_netload {

    my ($dbh, $id, $type, $x_size, $y_size, $now, $window, $queries, $image) = @_;

    # -- figure out if this is a profile or a host plot
    my $field = "b.profile_id";
    if (lc($type) eq "host") { $field = "a.hostid"; }
    
    # -- common variables
    my @label;
    my @datasets;
    my %plots;
    my $graphWindow = human_time($window * 3600);

    # -- netload variables
    my @netload_legend;
    my @tx;
    my @rx;
    my $netload_max = 100;

    # -- netload legend
    for (my $i = 0; $i < 1; $i++) { 
        push (@netload_legend, "TX"); 
        push (@netload_legend, "RX"); 
    }

    # -- time window calculations
    my $graphdate = get_time($now);
    my $to_time = $now;
    my $from_time = $to_time - ($window * 3600);
    
    my $point = 0;
    my $sth;
    my ($table, $dateFormat) = get_window_fields($window);

    my $sql = "select date_format(a.updated, '$dateFormat'), avg(a.tx/1000), avg(a.rx/1000)
            from sysload$table a, node b where a.hostid = b.id and $field = '$id' and a.updated >= from_unixtime($from_time) 
            and a.updated < from_unixtime($to_time) group by date_format(a.updated, '$dateFormat') order by a.updated";

    $sth = $dbh -> prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
    $sth -> execute() || print "Database Error (<b>$sql</b>): <font class=alert>" . $dbh->errstr . "</font>\n"; ${$queries}++;

    my %dates;
    my $rows = 0;

    while(my @row = $sth -> fetchrow_array) {

        my $updated = $row[0];

        # -- determine if this is a new date
        if (!defined($dates{$updated})) {
            $dates{$updated} = 1;
            if ($rows) {
                $point++;
            }
        } 

        # -- netload data points
        $label[$point] = $row[0] || "";
        $tx[$point] = $row[1] || 0;
        $rx[$point] = $row[2] || 0;
        if ($tx[$point] + $rx[$point] > $netload_max) { $netload_max = $tx[$point] + $rx[$point]; }

        $rows++;
    }
    $sth->finish();


    # -- generic plot setting(s)    
    my $skip = $point / 42;

    # -- plot the netload
    $netload_max = sprintf("%.0f", $netload_max * 1.15);
    $netload_max = sprintf("%.0f", $netload_max + 1000 - ($netload_max % 1000));
    if (get_config("debug")) { print_array(@datasets)};

    @datasets = ();
    push @datasets, [@label];
    push @datasets, [@tx];
    push @datasets, [@rx];

    my $netload_data = GD::Graph::Data->new([@datasets]);

    my $netload_my_graph;
    if ($point <= 20) {
        $netload_my_graph = GD::Graph::bars3d->new($x_size,$y_size);
    } else {
        $netload_my_graph = GD::Graph::bars->new($x_size,$y_size);
    }

    $netload_my_graph->set( 
        x_label           => "$graphdate -- $graphWindow",
        y_label           => 'Throughput (kB/s)',
        title             => "Total Network I/O",
        textclr           => get_config("g_textcolor"),
        labelclr          => get_config("g_labelcolor"),
        boxclr            => get_config("g_boxcolor"),
        fgclr             => get_config("g_fgcolor"),
        shadowclr         => get_config("g_shadowcolor"),
        legendclr         => get_config("g_legendcolor"),
        bgclr             => get_config("g_bgcolor"),
        axislabelclr      => get_config("g_axislabelcolor"),
        line_width        => get_config("g_linewidth"),
        x_labels_vertical => get_config("g_verticallabels"), 
        long_ticks        => get_config("g_longticks"),
        y_max_value       => $netload_max,
        y_tick_number     => 10,
        y_min_value       => 0,
        #overwrite        => 0,
        cumulate          => 1,
        correct_width     => 0,
        x_label_skip      => $skip,
        transparent       => get_config("g_transparent"),
        ) 
        or warn $netload_my_graph->error;

    $netload_my_graph->set ( dclrs => [ qw(blue lgray black) ]);
    $netload_my_graph->set_legend(@netload_legend);
    $netload_my_graph->plot($netload_data) or return "Unable to plot network I/O";

    my $_htdoc = get_config("aware_home");
    my $_webdir = get_config("web_dir");
    my $suffix = "netload";
    save_chart($netload_my_graph, "$_htdoc/web/$image-$suffix");
    my $IMGFORMAT = $netload_my_graph->export_format();
    return "<IMG SRC=/$_webdir/$image-$suffix.$IMGFORMAT>";

}


########################################################################################
#
# graph_procs(dbh, hostid, type, xsize, ysize, numpoints, daysAgo, cpus)
#
# - plot the various sysloads for the specified host
#
########################################################################################

sub graph_procs {

    my ($dbh, $id, $type, $x_size, $y_size, $now, $window, $queries, $image) = @_;

    # -- figure out if this is a profile or a host plot
    my $field = "b.profile_id";
    if (lc($type) eq "host") { $field = "a.hostid"; }
    
    # -- common variables
    my @label;
    my @datasets;
    my %plots;
    my $graphWindow = human_time($window * 3600);

    # -- process variables
    my @procs_legend;
    my @procs_today;
    my $procs_max = 0;

    # -- process legend 
    for (my $i = 0; $i < 1; $i++) { 
        push (@procs_legend, "# of processes"); 
    }

    # -- time window calculations
    my $graphdate = get_time($now);
    my $to_time = $now;
    my $from_time = $to_time - ($window * 3600);
    
    my $point = 0;
    my $sth;
    my ($table, $dateFormat) = get_window_fields($window);

    my $sql = "select date_format(a.updated, '$dateFormat'), avg(a.procs) 
        from sysload$table a, node b where a.hostid = b.id and $field = '$id' and a.updated >= from_unixtime($from_time) 
        and a.updated < from_unixtime($to_time) group by date_format(a.updated, '$dateFormat') order by a.updated";

    $sth = $dbh -> prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
    $sth -> execute() || print "Database Error (<b>$sql</b>): <font class=alert>" . $dbh->errstr . "</font>\n"; ${$queries}++;

    my %dates;
    my $rows = 0;

    while(my @row = $sth -> fetchrow_array) {

        my $updated = $row[0];

        # -- determine if this is a new date
        if (!defined($dates{$updated})) {
            $dates{$updated} = 1;
            if ($rows) {
                $point++;
            }
        } 

        # -- number of processes
        $label[$point] = $row[0] || "";
        $procs_today[$point] = $row[1] || 0;
        if ($procs_today[$point] > $procs_max) { $procs_max = $procs_today[$point]; }

        $rows++;
    }
    $sth->finish();

    # -- generic plot setting(s)    
    my $skip = $point / 42;

    # -- plot process load
    @datasets = ();
    push @datasets, [@label];
    push @datasets, [@procs_today];

    $procs_max = $procs_max * 1.15;
    $procs_max = sprintf("%d", $procs_max + (100 - ($procs_max % 100)) );

    if (get_config("debug")) { print_array(@datasets)};

    my $data = GD::Graph::Data->new([@datasets]);

    my $my_graph =  GD::Graph::lines->new($x_size,$y_size);
    if ($point <= 20) {
        $my_graph =  GD::Graph::lines3d->new($x_size,$y_size);
    } else {
        $my_graph =  GD::Graph::lines->new($x_size,$y_size);
    }


    $my_graph->set( 
        x_label           => "$graphdate -- $graphWindow",
        y_label           => '# of Processes',
        title             => "Process Load",
        textclr           => get_config("g_textcolor"),
        labelclr          => get_config("g_labelcolor"),
        boxclr            => get_config("g_boxcolor"),
        fgclr             => get_config("g_fgcolor"),
        shadowclr         => get_config("g_shadowcolor"),
        legendclr         => get_config("g_legendcolor"),
        bgclr             => get_config("g_bgcolor"),
        axislabelclr      => get_config("g_axislabelcolor"),
        line_width        => get_config("g_linewidth"),
        x_labels_vertical => get_config("g_verticallabels"), 
        long_ticks        => get_config("g_longticks"),
        y_max_value       => $procs_max,
        y_tick_number     => 10,
        y_min_value       => 0,
        correct_width     => 0,
        x_label_skip      => $skip,
        transparent       => get_config("g_transparent"),
    ) 
    or warn $my_graph->error;

    $my_graph->set ( dclrs => [ qw(red lgray black) ]);
    $my_graph->set_legend(@procs_legend);
    $my_graph->plot($data) or return "Unable to plot Process Load";

    my $_htdoc = get_config("aware_home");
    my $_webdir = get_config("web_dir");
    my $suffix = "$type\_process";
    save_chart($my_graph, "$_htdoc/web/$image-$suffix");
    my $IMGFORMAT = $my_graph->export_format();
    return "<IMG SRC=/$_webdir/$image-$suffix.$IMGFORMAT>";
}


########################################################################################
#
# graph_sysio(dbh, hostid, type, xsize, ysize, numpoints, daysAgo, cpus)
#
# - plot the various sysloads for the specified host
#
########################################################################################

sub graph_sysio {

    my ($dbh, $id, $type, $x_size, $y_size, $now, $window, $queries, $image) = @_;

    # -- figure out if this is a profile or a host plot
    my $field = "b.profile_id";
    if (lc($type) eq "host") { $field = "a.hostid"; }
    
    # -- common variables
    my @label;
    my @datasets;
    my %plots;
    my $graphWindow = human_time($window * 3600);

    # -- diskload variables
    my @diskload_datasets;
    my @diskload_legend;
    my @bytesIn;
    my @bytesOut;
    my $diskload_max = 100;

    # -- diskload legend
    for (my $i = 0; $i < 1; $i++) { 
        push (@diskload_legend, "Read"); 
        push (@diskload_legend, "Write"); 
    }

    # -- time window calculations
    my $graphdate = get_time($now);
    my $to_time = $now;
    my $from_time = $to_time - ($window * 3600);
    
    my $point = 0;
    my $sth;
    my ($table, $dateFormat) = get_window_fields($window);

    my $sql = "select date_format(a.updated, '$dateFormat'), avg(a.bi), avg(a.bo)
        from sysload$table a, node b where a.hostid = b.id and $field = '$id' and a.updated >= from_unixtime($from_time) 
        and a.updated < from_unixtime($to_time) group by date_format(a.updated, '$dateFormat') order by a.updated";

    $sth = $dbh -> prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
    $sth -> execute() || print "Database Error (<b>$sql</b>): <font class=alert>" . $dbh->errstr . "</font>\n"; ${$queries}++;

    my %dates;
    my $rows = 0;

    while(my @row = $sth -> fetchrow_array) {
        
        my $updated = $row[0];

        # -- determine if this is a new date
        if (!defined($dates{$updated})) {
            $dates{$updated} = 1;
            if ($rows) {
                $point++;
            }
        } 

        # -- diskload data points 
        $label[$point] = $row[0] || "";
        $bytesIn[$point] = $row[1] || 0;
        $bytesOut[$point] = $row[2] || 0;
        if ($bytesIn[$point] + $bytesOut[$point] > $diskload_max) { $diskload_max = $bytesIn[$point] + $bytesOut[$point]; }

        $rows++;
    }
    $sth->finish();

    # -- generic plot setting(s)    
    my $skip = $point / 42;

    # - plot the diskload
    $diskload_max = sprintf("%.0f", $diskload_max * 1.15);
    $diskload_max = sprintf("%.0f", $diskload_max + 1000 - ($diskload_max % 1000));

    # -- prepare the graph data
    @datasets = ();
    push @datasets, [@label];
    push @datasets, [@bytesIn];
    push @datasets, [@bytesOut];

    if (get_config("debug")) { print_array(@datasets)};

    my $diskload_data = GD::Graph::Data->new([@datasets]);

    my $diskload_my_graph;
    if ($point < 20) {
        $diskload_my_graph =  GD::Graph::bars3d->new($x_size,$y_size);
    } else {
        $diskload_my_graph =  GD::Graph::bars->new($x_size,$y_size);
    }

    $diskload_my_graph->set( 
        x_label           => "$graphdate -- $graphWindow",
        y_label           => 'Disk Throughput (kB/s)',
        title             => "Total Disk I/O",
        textclr           => get_config("g_textcolor"),
        labelclr          => get_config("g_labelcolor"),
        boxclr            => get_config("g_boxcolor"),
        fgclr             => get_config("g_fgcolor"),
        shadowclr         => get_config("g_shadowcolor"),
        legendclr         => get_config("g_legendcolor"),
        bgclr             => get_config("g_bgcolor"),
        axislabelclr      => get_config("g_axislabelcolor"),
        line_width        => get_config("g_linewidth"),
        x_labels_vertical => get_config("g_verticallabels"), 
        long_ticks        => get_config("g_longticks"),
        y_max_value       => $diskload_max,
        y_tick_number     => 10,
        y_min_value       => 0,
        #overwrite        => 0,
        cumulate          => 1,
        correct_width     => 0,
        x_label_skip      => $skip,
        transparent       => get_config("g_transparent"),
    ) 
    or warn $diskload_my_graph->error;

    $diskload_my_graph->set ( dclrs => [ qw(lgray red black) ]);
    $diskload_my_graph->set_legend(@diskload_legend);
    $diskload_my_graph->plot($diskload_data) or return %plots;

    my $_htdoc = get_config("aware_home");
    my $_webdir = get_config("web_dir");
    my $suffix = "$type\_sysio";
    save_chart($diskload_my_graph, "$_htdoc/web/$image-$suffix");
    my $IMGFORMAT = $diskload_my_graph->export_format();
    return "<IMG SRC=/$_webdir/$image-$suffix.$IMGFORMAT>";

}


########################################################################################
#
# graph_diskload (dbh, hostid, xsize, ysize, numpoints, daysAgo)
#
# - plot the statistics on the specified disk partition
#
########################################################################################

sub graph_diskload {

    my ($dbh, $id, $x_size, $y_size, $now, $window, $queries, $image) = @_;

    # -- common variables
    my @label;
    my @datasets;
    my @legend;
    my $graphWindow = human_time($window * 3600);
    my $numDevices = 0;
    my $diskload_max = 100;
    my @bytesIn;
    my @bytesOut;
    my %devices;

    my ($sth, $sql);

    # -- time window calculations
    my $to_time = $now;
    my $from_time = $to_time - ($window * 3600);
    my $interval = 120;

    my $graphdate = get_time($to_time);

    my $point = 0;
    my ($table, $dateFormat) = get_window_fields($window);

    $sql = "select date_format(a.updated, '$dateFormat'), a.bi, a.bo, a.device 
            from diskload$table a where a.updated >= from_unixtime($from_time) and a.hostid = $id 
            and a.updated < from_unixtime($to_time) and a.device not like '/dev/md%' and a.device not like '/dev/mapper/%'
            order by a.updated, a.device";

    $sth = $dbh -> prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
    $sth -> execute() || print "Database Error (<b>$sql</b>): <font class=alert>" . $dbh->errstr . "</font>\n"; ${$queries}++;

    my $rows = 0;
    my $total = 0;
    my %dates;
    while (my @row = $sth -> fetchrow_array) {
        # -- only need one label
        my $updated = $row[0] || "No Data";
        my $bi = $row[1] || 0;
        my $bo = $row[2] || 0;
        my $device = $row[3] || "N/A";

        if (!defined($devices{$device})) { 
            $devices{$device} = $numDevices++;
            push(@legend, "$device (Read)");
            push(@legend, "$device (Write)");
        }

        # -- determine if this is a new date
        if (!defined($dates{$updated})) {
            $dates{$updated} = 1;
            if ($rows) {
                $point++;
                if ($total > $diskload_max) { $diskload_max = $total; }
                $total = 0;
            }
        } 

        $label[$point] = $updated; 
    
        # -- disk loads by device
        $bytesIn[$devices{$device}][$point] = $bi;
        $bytesOut[$devices{$device}][$point] = $bo;

        $total = $total + $bi + $bo;

        $rows++;

    }
    $sth->finish();

    # -- generic plot setting(s)    
    my $skip = $point / 42;

    # -- handle diskload graph
    @datasets = ();
    push @datasets, [@label];

    for (my $i = 0; $i <= $#bytesIn; $i++) {
        my @array;
        for (my $j = 0; $j <= $point; $j++) {
            push(@array, $bytesIn[$i][$j]);
        }    
        push @datasets, [@array];

        @array = ();
        for (my $j = 0; $j <= $point; $j++) {
            push(@array, $bytesOut[$i][$j]);
        }    
        push @datasets, [@array];
    }

    if (get_config("debug")) { print_array(@datasets)};

    my $data = GD::Graph::Data->new([@datasets]);
    $diskload_max = sprintf("%.0f", $diskload_max * 1.15);
    $diskload_max = sprintf("%.0f", $diskload_max + 1000 - ($diskload_max % 1000));

    my $diskload_my_graph;
    if ($point < 20) {
        $diskload_my_graph =  GD::Graph::bars3d->new($x_size,$y_size);
    } else {
        $diskload_my_graph =  GD::Graph::bars->new($x_size,$y_size);
    }

    $diskload_my_graph->set( 
        x_label           => "$graphdate -- $graphWindow",
        y_label           => 'Disk Throughput (kB/s)',
        title             => "Individual Disk I/O",
        textclr           => get_config("g_textcolor"),
        labelclr          => get_config("g_labelcolor"),
        shadowclr         => get_config("g_shadowcolor"),
        legendclr         => get_config("g_legendcolor"),
        boxclr            => get_config("g_boxcolor"),
        fgclr             => get_config("g_fgcolor"),
        bgclr             => get_config("g_bgcolor"),
        axislabelclr      => get_config("g_axislabelcolor"),
        line_width        => get_config("g_linewidth"),
        x_labels_vertical => get_config("g_verticallabels"), 
        long_ticks        => get_config("g_longticks"),
        y_max_value       => $diskload_max,
        y_tick_number     => 10,
        y_min_value       => 0,
        accent_treshold   => $x_size,
        correct_width     => 0,
        cumulate          => 1,
        x_label_skip      => $skip,
        transparent       => get_config("g_transparent"),
    ) 
    or warn $diskload_my_graph->error;

    $diskload_my_graph->set ( dclrs => [ qw(white lblue lred gold cyan green dblue lyellow yellow dyellow
            lgreen dgreen dred lpurple purple dpurple lorange orange pink dpink marine lbrown dbrown) ]);

    $diskload_my_graph->set_legend(@legend);
    $diskload_my_graph->plot($data) or return "Unable to plot Disk Load";

    my $_htdoc = get_config("aware_home");
    my $_webdir = get_config("web_dir");
    my $suffix = "diskload";
    save_chart($diskload_my_graph, "$_htdoc/web/$image-$suffix");
    my $IMGFORMAT = $diskload_my_graph->export_format();
    my $html = "<IMG SRC=/$_webdir/$image-$suffix.$IMGFORMAT>";
    return $html;
}



########################################################################################
#
# graph_device_svctimes (dbh, hostid, x_size, y_size, now, window, queries, image)
#
# - plot the service times for the disks in the system 
#
########################################################################################

sub graph_device_svctimes {

    my ($dbh, $hostid, $x_size, $y_size, $now, $window, $queries, $image) = @_;

    my $graphWindow = human_time($window * 3600);

    my @legend;
    my @times;
    my %svctimes;
    my %devices;
    my %datetimes;

    # -- time window calculations
    my $graphdate = get_time($now);
    my $to_time = $now;
    my $from_time = $to_time - ($window * 3600);
    
    my $point = 0;
    my $max = 0;
    my $sth;
    my ($table, $dateFormat) = get_window_fields($window);

    my $sql = "select date_format(diskload$table.updated, '$dateFormat'), svctime, device
        from diskload$table where diskload$table.hostid = $hostid 
        and diskload$table.updated >= from_unixtime($from_time) and diskload$table.updated < from_unixtime($to_time) 
        order by diskload$table.updated";

    $sth = $dbh -> prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
    $sth -> execute() || print "Database Error (<b>$sql</b>): <font class=alert>" . $dbh->errstr . "</font>\n"; ${$queries}++;


    while(my @row = $sth -> fetchrow_array) {
        my $datetime = $row[0] || "";
        my $svctime = $row[1] || 0;
        my $device = $row[2] || next;
    
        if ($svctime > 15) { $svctime = 15; }

        if ($svctime > $max) { $max = $svctime; }

        if (!defined($devices{$device})) { 
            $devices{$device} = 1;
            push(@legend, $device); 
        }

        if (!defined($datetimes{$datetime})) { 
            push(@times, $datetime); 
            $datetimes{$datetime} = 1;
            $point++;
        }

        if (!defined($svctimes{"$datetime-$device"})) {
            $svctimes{"$datetime-$device"} = $svctime;
        } 

    }
    $sth->finish();
    $max = $max * 1.10;
    $max = sprintf("%.0f", $max + 5 - ($max % 5));

    my @datasets;
    push (@datasets, [@times]);
    foreach my $device (@legend) {
        my @array;
        foreach my $time (@times) {
            if (defined($svctimes{"$time-$device"})) {
                push(@array, $svctimes{"$time-$device"});
            } else {
                push(@array, 0);
            }
        }
        push(@datasets, [@array]);
    }

    if (get_config("debug")) { print_array(@datasets)};

    my $skip = $point / 42;

    my $data = GD::Graph::Data->new([@datasets]);

    my $my_graph = GD::Graph::lines->new($x_size,$y_size);

    $my_graph->set( 
        x_label           => "$graphdate -- $graphWindow",
        y_label           => 'Service Time(ms)',
        title             => "Disk Service Times",
        textclr           => get_config("g_textcolor"),
        labelclr          => get_config("g_labelcolor"),
        boxclr            => get_config("g_boxcolor"),
        fgclr             => get_config("g_fgcolor"),
        shadowclr         => get_config("g_shadowcolor"),
        legendclr         => get_config("g_legendcolor"),
        bgclr             => get_config("g_bgcolor"),
        axislabelclr      => get_config("g_axislabelcolor"),
        line_width        => 3,
        x_labels_vertical => get_config("g_verticallabels"), 
        long_ticks        => get_config("g_longticks"),
        y_tick_number     => 16,
        y_max_value       => $max,
        y_min_value       => 0,
        correct_width     => 0,
        x_label_skip      => $skip,
        transparent       => get_config("g_transparent"),
    ) 
    or warn $my_graph->error;

    $my_graph->set ( dclrs => [ qw( white lblue lred gold cyan dblue purple gray pink) ]); 
    $my_graph->set_legend(@legend);
    $my_graph->plot($data) or return "Unable to plot Temperature Sensors";

    my $_htdoc = get_config("aware_home");
    my $_webdir = get_config("web_dir");
    my $suffix = "svctime";
    save_chart($my_graph, "$_htdoc/web/$image-$suffix");
    my $IMGFORMAT = $my_graph->export_format();
    return "<IMG SRC=/$_webdir/$image-$suffix.$IMGFORMAT>";
}



########################################################################################
#
# graph_device_utilization (dbh, hostid, device, xsize, ysize, numpoints, daysAgo)
#
# - plot the statistics on the specified disk partition
#
########################################################################################

sub graph_device_utilization {

    my ($dbh, $id, $device, $x_size, $y_size, $now, $window, $queries, $image) = @_;

    # -- common variables
    my @label;
    my @datasets;
    my @legend;
    my $graphWindow = human_time($window * 3600);
    my %utilizations;

    my ($sth, $sql);

    # -- time window calculations
    my $to_time = $now;
    my $from_time = $to_time - ($window * 3600);

    my $graphdate = get_time($to_time);

    my $point = 0;
    my ($table, $dateFormat) = get_window_fields($window);

    $sql = "select date_format(updated, '$dateFormat'), utilization
            from diskload$table where updated >= from_unixtime($from_time) and hostid = $id 
            and updated < from_unixtime($to_time) and device = '$device' order by updated";

    $sth = $dbh -> prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
    $sth -> execute() || print "Database Error (<b>$sql</b>): <font class=alert>" . $dbh->errstr . "</font>\n"; ${$queries}++;

    my %dates;
    my $rows = 0;
    while (my @row = $sth -> fetchrow_array) {

        # -- only need one label
        my $updated = $row[0] || "No Data";
        my $utilization = $row[1] || 0;

        # -- add this device if new
        if (!defined($utilizations{$device})) { 
            push(@legend, "$device");
            my @deviceArray = ();
            $utilizations{$device} = \@deviceArray;
        }

        # -- determine if this is a new date
        if (!defined($dates{$updated})) {
            $dates{$updated} = 1;
            if ($rows) {
                $point++;
            }
        } 

        # -- pull the date field
        $label[$point] = $updated;
    
        # -- disk utilizations by device
	    push(@{$utilizations{$device}}, $utilization);
        $rows++;
    
    }
    $sth->finish();

    # -- generic plot setting(s)    
    my $skip = $point / 42;

    # -- handle diskload graph
    @datasets = ();
    push @datasets, [@label];

    foreach my $device (@legend) {
        my @array = @{$utilizations{$device}};
	    push (@datasets, [@array]);
    }


    if (get_config("debug")) { print_array(@datasets)};

    my $data = GD::Graph::Data->new([@datasets]);

    my $diskload_my_graph;
    if ($point < 20) {
        $diskload_my_graph =  GD::Graph::bars3d->new($x_size,$y_size);
    } else {
        $diskload_my_graph =  GD::Graph::bars->new($x_size,$y_size);
    }

    $diskload_my_graph->set( 
        x_label           => "$graphdate -- $graphWindow",
        y_label           => 'Usage (%)',
        title             => "Disk Utilization for $device",
        textclr           => get_config("g_textcolor"),
        labelclr          => get_config("g_labelcolor"),
        shadowclr         => get_config("g_shadowcolor"),
        legendclr         => get_config("g_legendcolor"),
        boxclr            => get_config("g_boxcolor"),
        fgclr             => get_config("g_fgcolor"),
        bgclr             => get_config("g_bgcolor"),
        axislabelclr      => get_config("g_axislabelcolor"),
        line_width        => get_config("g_linewidth"),
        x_labels_vertical => get_config("g_verticallabels"), 
        long_ticks        => get_config("g_longticks"),
        y_max_value       => 100,
        y_tick_number     => 10,
        y_min_value       => 0,
        accent_treshold   => $x_size,
        correct_width     => 0,
        cumulate          => 0,
        x_label_skip      => $skip,
        transparent       => get_config("g_transparent"),
    ) 
    or warn $diskload_my_graph->error;

    $diskload_my_graph->set ( dclrs => [ qw(lorange lblue lred gold lgreen black lgray orange) ]);
    $diskload_my_graph->set_legend(@legend);
    $diskload_my_graph->plot($data) or return "Unable to plot Disk Load";

    my $_htdoc = get_config("aware_home");
    my $_webdir = get_config("web_dir");
    my $suffix = "utilization-$device";
    $suffix =~ s/\//_/g;
    save_chart($diskload_my_graph, "$_htdoc/web/$image-$suffix");
    my $IMGFORMAT = $diskload_my_graph->export_format();
    my $html = "<IMG SRC=/$_webdir/$image-$suffix.$IMGFORMAT>";
    return $html;
}


########################################################################################
#
# graph_diskutilization (dbh, hostid, xsize, ysize, numpoints, daysAgo)
#
# - plot the statistics on the specified disk partition
#
########################################################################################

sub graph_diskutilization {

    my ($dbh, $id, $x_size, $y_size, $now, $window, $queries, $image) = @_;

    # -- common variables
    my @label;
    my @datasets;
    my @legend;
    my $graphWindow = human_time($window * 3600);
    my $numDevices = 0;
    my %utilizations;

    my ($sth, $sql);

    # -- time window calculations
    my $to_time = $now;
    my $from_time = $to_time - ($window * 3600);

    my $graphdate = get_time($to_time);

    my $point = 0;
    my ($table, $dateFormat) = get_window_fields($window);

    $sql = "select date_format(a.updated, '$dateFormat'), a.utilization, a.device 
            from diskload$table a where a.updated >= from_unixtime($from_time) and a.hostid = $id 
            and a.updated < from_unixtime($to_time) order by a.updated, a.device";

    $sth = $dbh -> prepare($sql) || print "SQL Error: " . $dbh->errstr . "\n";
    $sth -> execute() || print "Database Error (<b>$sql</b>): <font class=alert>" . $dbh->errstr . "</font>\n"; ${$queries}++;

    my %dates;
    my $rows = 0;
    while (my @row = $sth -> fetchrow_array) {

        # -- only need one label
        my $updated = $row[0] || "No Data";
        my $utilization = $row[1] || 0;
        my $device = $row[2] || 0;

        # -- add this device if new
        if (!defined($utilizations{$device})) { 
            push(@legend, "$device");
            my @deviceArray = ();
            $utilizations{$device} = \@deviceArray;
        }

        # -- determine if this is a new date
        if (!defined($dates{$updated})) {
            $dates{$updated} = 1;
            if ($rows) {
                $point++;
            }
        } 

        # -- pull the date field
        $label[$point] = $updated;
    
        # -- disk utilizations by device
	    push(@{$utilizations{$device}}, $utilization);
        $rows++;
    
    }
    $sth->finish();

    # -- generic plot setting(s)    
    my $skip = $point / 42;

    # -- handle diskload graph
    @datasets = ();
    push @datasets, [@label];

    foreach my $device (@legend) {
        my @array = @{$utilizations{$device}};
	    push (@datasets, [@array]);
    }


    if (get_config("debug")) { print_array(@datasets)};

    my $data = GD::Graph::Data->new([@datasets]);

    my $diskload_my_graph;
    if ($point < 20) {
        $diskload_my_graph =  GD::Graph::bars3d->new($x_size,$y_size);
    } else {
        $diskload_my_graph =  GD::Graph::bars->new($x_size,$y_size);
    }

    $diskload_my_graph->set( 
        x_label           => "$graphdate -- $graphWindow",
        y_label           => 'Usage (%)',
        title             => "Disk Utilization",
        textclr           => get_config("g_textcolor"),
        labelclr          => get_config("g_labelcolor"),
        shadowclr         => get_config("g_shadowcolor"),
        legendclr         => get_config("g_legendcolor"),
        boxclr            => get_config("g_boxcolor"),
        fgclr             => get_config("g_fgcolor"),
        bgclr             => get_config("g_bgcolor"),
        axislabelclr      => get_config("g_axislabelcolor"),
        line_width        => get_config("g_linewidth"),
        x_labels_vertical => get_config("g_verticallabels"), 
        long_ticks        => get_config("g_longticks"),
        y_max_value       => 100,
        y_tick_number     => 10,
        y_min_value       => 0,
        accent_treshold   => $x_size,
        correct_width     => 0,
        cumulate          => 0,
        x_label_skip      => $skip,
        transparent       => get_config("g_transparent"),
    ) 
    or warn $diskload_my_graph->error;

    $diskload_my_graph->set ( dclrs => [ qw(lblue lred gold lgreen black lgray orange) ]);
    $diskload_my_graph->set_legend(@legend);
    $diskload_my_graph->plot($data) or return "Unable to plot Disk Load";

    my $_htdoc = get_config("aware_home");
    my $_webdir = get_config("web_dir");
    my $suffix = "diskutilization";
    save_chart($diskload_my_graph, "$_htdoc/web/$image-$suffix");
    my $IMGFORMAT = $diskload_my_graph->export_format();
    my $html = "<IMG SRC=/$_webdir/$image-$suffix.$IMGFORMAT>";
    return $html;
}

sub get_window_fields {

    my ($window) = @_;

    my $table = ""; 
    my $dateFormat = "%H:%i:%s";

    if ($window >= 24 * 180) {
        $table = "_monthly"; 
        $dateFormat = "%m/%d";
    } elsif ($window >= 24 * 30) {
        $table = "_weekly"; 
        $dateFormat = "%m/%d %H:00";
    } elsif ($window >= 24 * 7) { 
        $table = "_daily"; 
        $dateFormat = "%a %H:%i";
    }

    return ($table, $dateFormat);
}

1;
__END__
# Below is stub documentation for your module. You'd better edit it!

=head1 NAME

ZUtils::Aware - Perl extension for blah blah blah

=head1 SYNOPSIS

  use ZUtils::Aware;
  blah blah blah

=head1 DESCRIPTION

Stub documentation for ZUtils::Aware, created by h2xs. It looks like the
author of the extension was negligent enough to leave the stub
unedited.

Blah blah blah.

=head2 EXPORT

None by default.



=head1 SEE ALSO

Mention other useful documentation such as the documentation of
related modules or operating system documentation (such as man pages
in UNIX), or any relevant external documentation such as RFCs or
standards.

If you have a mailing list set up for your module, mention it here.

If you have a web site set up for your module, mention it here.

=head1 AUTHOR

=head1 COPYRIGHT AND LICENSE

Copyright (C) 2006

This library is free software; you can redistribute it and/or modify
it under the same terms as Perl itself, either Perl version 5.8.5 or,
at your option, any later version of Perl 5 you may have available.


=cut
