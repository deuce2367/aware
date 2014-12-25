use Test::More tests => 1;

# -- load the module
use ZUtils::Common;
use ZUtils::Aware;
load_config("t/sample.cfg");

# -- the tests

# -- test comma_format() function
ok(comma_format() eq "", "comma_format() test");

