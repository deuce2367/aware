use Test::More tests => 14;

# -- load the module
use ZUtils::Common;
load_config("t/sample.cfg");

# -- the tests

# -- test base36() function
ok(base36() eq "000", 'base36()');
ok(base36(123456) eq "N9C", 'base36(123456)');
ok(base36(654321) eq "0VL", 'base36(654321)');
ok(base36(1) eq "001", 'base36(1)');

# -- test comma_format() function
ok(comma_format() eq "", "comma_format() test");
ok(comma_format(123456) eq "123,456", "comma_format(123456) test");
ok(comma_format(123) eq "123", "comma_format(123) test");
ok(comma_format(1234) eq "1,234", "comma_format(1234) test");


# -- test human_time() function
ok(human_time() eq "", "human_time() test");
ok(human_time(12) eq "12 sec.", "human_time(12) test");
ok(human_time(1234) eq "21 min.", "human_time(1234) test");
ok(human_time(123456) eq "34.29 hrs.", "human_time(123456) test");
ok(human_time(12345678) eq "142.9 days", "human_time(12345678) test");
ok(human_time(123456789) eq "3.91 yrs.", "human_time(123456789) test");
