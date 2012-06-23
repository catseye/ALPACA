#!/usr/bin/perl
# eg/wireworld/script/wireworld.pl - automatically generated from eg/wireworld/src/wireworld.alp by:
# alpaca.pl v0.93
# http://catseye.webhop.net/projects/alpaca/
######################################################

use Alpaca qw(true false guess
	      adjacent_state adjacent_class
	      load_playfield display_playfield process_playfield);

sub SpaceStateRules {
  return 'Space'
 };

sub SparkStateRules {
  return 'Tail' if (1);
  return 'Spark'
 };

sub TailStateRules {
  return 'Wire' if (1);
  return 'Tail'
 };

sub WireStateRules {
  return 'Spark' if ((adjacent_state('Spark') >= 1) and (not (adjacent_state('Spark') >= 3)));
  return 'Wire'
 };

$Appearance = {
  'Space' => ' ',
  'Spark' => '#',
  'Tail' => '-',
  'Wire' => '=',

};

$InputCodec = {
  ' ' => 'Space',
  '#' => 'Spark',
  '-' => 'Tail',
  '=' => 'Wire',

};

$StateRule = {
  'Space' => \&main::SpaceStateRules,
  'Spark' => \&main::SparkStateRules,
  'Tail' => \&main::TailStateRules,
  'Wire' => \&main::WireStateRules,

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
