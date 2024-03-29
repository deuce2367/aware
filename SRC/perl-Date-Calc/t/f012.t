#!perl -w

BEGIN { eval { require bytes; }; }
use strict;
no strict "vars";

use Date::Calc qw( Date_to_Text_Long Language Decode_Language );

# ======================================================================
#   $datestr = Date_to_Text_Long($year,$mm,$dd);
# ======================================================================

print "1..15\n";

$n = 1;
if (Date_to_Text_Long(1964,1,3) eq "Friday, January 3rd 1964") {print "ok $n\n";} else {print "not ok $n\n";}
$n++;
if (Date_to_Text_Long(1995,11,18) eq "Saturday, November 18th 1995") {print "ok $n\n";} else {print "not ok $n\n";}
$n++;
if (Date_to_Text_Long(1999,12,31) eq "Friday, December 31st 1999") {print "ok $n\n";} else {print "not ok $n\n";}
$n++;
if (Date_to_Text_Long(2000,1,1) eq "Saturday, January 1st 2000") {print "ok $n\n";} else {print "not ok $n\n";}
$n++;
if (Date_to_Text_Long(2000,1,2) eq "Sunday, January 2nd 2000") {print "ok $n\n";} else {print "not ok $n\n";}
$n++;

Language(Decode_Language("DE"));

if (Date_to_Text_Long(1964,1,3) eq "Freitag, den 3. Januar 1964") {print "ok $n\n";} else {print "not ok $n\n";}
$n++;
if (Date_to_Text_Long(1995,11,18) eq "Samstag, den 18. November 1995") {print "ok $n\n";} else {print "not ok $n\n";}
$n++;
if (Date_to_Text_Long(1999,12,31) eq "Freitag, den 31. Dezember 1999") {print "ok $n\n";} else {print "not ok $n\n";}
$n++;
if (Date_to_Text_Long(2000,1,1) eq "Samstag, den 1. Januar 2000") {print "ok $n\n";} else {print "not ok $n\n";}
$n++;
if (Date_to_Text_Long(2000,1,2) eq "Sonntag, den 2. Januar 2000") {print "ok $n\n";} else {print "not ok $n\n";}
$n++;

Language(Decode_Language("FR"));

if (Date_to_Text_Long(1964,1,3) eq "Vendredi 3 janvier 1964") {print "ok $n\n";} else {print "not ok $n\n";}
$n++;
if (Date_to_Text_Long(1995,11,18) eq "Samedi 18 novembre 1995") {print "ok $n\n";} else {print "not ok $n\n";}
$n++;
if (Date_to_Text_Long(1999,12,31) eq "Vendredi 31 d�cembre 1999") {print "ok $n\n";} else {print "not ok $n\n";}
$n++;
if (Date_to_Text_Long(2000,1,1) eq "Samedi 1 janvier 2000") {print "ok $n\n";} else {print "not ok $n\n";}
$n++;
if (Date_to_Text_Long(2000,1,2) eq "Dimanche 2 janvier 2000") {print "ok $n\n";} else {print "not ok $n\n";}

__END__

