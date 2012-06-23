#!/usr/bin/perl
# eg/circute/script/circute.pl - automatically generated from eg/circute/src/circute.alp by:
# alpaca.pl v0.93
# http://catseye.webhop.net/projects/alpaca/
######################################################

use Alpaca qw(true false guess
	      adjacent_state adjacent_class
	      load_playfield display_playfield process_playfield);

sub SpaceStateRules {
  return 'Space'
 };

sub NANDStateRules {
  return 'NAND'
 };

sub WireStateRules {
  return 'Spark' if ($Playfield->[$x-1][$y] eq 'Spark' or $Playfield->[$x+1][$y] eq 'Spark' or $Playfield->[$x][$y-1] eq 'Spark' or $Playfield->[$x][$y+1] eq 'Spark' or ($Playfield->[$x][$y+1] eq 'NAND' and ($Playfield->[$x-1][$y+1] eq 'Wire' or $Playfield->[$x+1][$y+1] eq 'Wire')) or ($Playfield->[$x][$y-1] eq 'NAND' and ($Playfield->[$x-1][$y-1] eq 'Wire' or $Playfield->[$x+1][$y-1] eq 'Wire')));
  return 'Wire'
 };

sub SparkStateRules {
  return 'Tail' if ($Playfield->[$x-1][$y] eq 'Tail' or $Playfield->[$x+1][$y] eq 'Tail' or $Playfield->[$x][$y-1] eq 'Tail' or $Playfield->[$x][$y+1] eq 'Tail' or ($Playfield->[$x][$y+1] eq 'NAND' and $Playfield->[$x-1][$y+1] eq 'Spark' and $Playfield->[$x+1][$y+1] eq 'Spark') or ($Playfield->[$x][$y-1] eq 'NAND' and $Playfield->[$x-1][$y-1] eq 'Spark' and $Playfield->[$x+1][$y-1] eq 'Spark'));
  return 'Spark'
 };

sub TailStateRules {
  return 'Wire' if (1);
  return 'Tail'
 };

$Appearance = {
  'NAND' => 'N',
  'Space' => ' ',
  'Spark' => '#',
  'Tail' => '-',
  'Wire' => '=',

};

$InputCodec = {
  'N' => 'NAND',
  ' ' => 'Space',
  '#' => 'Spark',
  '-' => 'Tail',
  '=' => 'Wire',

};

$StateRule = {
  'NAND' => \&main::NANDStateRules,
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
