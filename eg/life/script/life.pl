#!/usr/bin/perl
# eg/life/script/life.pl - automatically generated from eg/life/src/life.alp by:
# alpaca.pl v0.93
# http://catseye.webhop.net/projects/alpaca/
######################################################

use Alpaca qw(true false guess
	      adjacent_state adjacent_class
	      load_playfield display_playfield process_playfield);

sub DeadStateRules {
  return 'Alive' if ((adjacent_state('Alive') >= 3) and (adjacent_state('Dead') >= 5));
  return 'Dead'
 };

sub AliveStateRules {
  return 'Dead' if ((adjacent_state('Alive') >= 4) or (adjacent_state('Dead') >= 7));
  return 'Alive'
 };

$Appearance = {
  'Alive' => '*',
  'Dead' => ' ',

};

$InputCodec = {
  '*' => 'Alive',
  ' ' => 'Dead',

};

$StateRule = {
  'Alive' => \&main::AliveStateRules,
  'Dead' => \&main::DeadStateRules,

};

load_playfield($ARGV[0]);

display_playfield();

while (!$done)
{
  process_playfield();
  display_playfield();
}

exit(0);

### END ###
