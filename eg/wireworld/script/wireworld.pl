#!/usr/local/bin/perl

# wireworld\wireworld.pl - automatically generated from wireworld\wireworld.alp by:
# alpaca.pl v0.90-1999.07.14
# http://www.cats-eye.com/esoteric/alpaca/

######################################################

use Alpaca;

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

load_playfield();

display_playfield();

while (!$done)
{
  process_playfield();
  display_playfield();
}

exit(0);

### END ###
