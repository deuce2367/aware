#!perl

BEGIN { eval { require bytes; }; }
use strict;
no strict "vars";

use Date::Calendar;
use Date::Calc::Object;

Date::Calc->date_format(2);

$cal = Date::Calendar->new( {} );

$date = $cal->add_delta_workdays(2002,11,11,-1);

print "\$date = $date\n";

$date = $cal->add_delta_workdays(2002,11,10,-1);

print "\$date = $date\n";

$date = $cal->add_delta_workdays(2002,11,9,-1);

print "\$date = $date\n";

$date = $cal->add_delta_workdays( $cal->add_delta_workdays(2002,11,11,+1), -2 );

print "\$date = $date\n";

$date = $cal->add_delta_workdays( $cal->add_delta_workdays(2002,11,10,+1), -2 );

print "\$date = $date\n";

$date = $cal->add_delta_workdays( $cal->add_delta_workdays(2002,11,9,+1), -2 );

print "\$date = $date\n";

__END__

