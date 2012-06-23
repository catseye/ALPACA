#!/usr/local/bin/perl

# life\life.pl - automatically generated from life\life.alp by:
# alpaca.pl v0.90-1999.07.14
# http://www.cats-eye.com/esoteric/alpaca/

######################################################

use Alpaca;

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

load_playfield();

display_playfield();

while (!$done)
{
  process_playfield();
  display_playfield();
}

exit(0);

### END ###
