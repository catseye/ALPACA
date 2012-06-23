# alpaca.pm v0.90-1999.07.14                    Chris Pressey
# http://www.cats-eye.com/esoteric/alpaca/
# (c)1999 Cat's-Eye Technologies.  Freely redistributable.
#   All I ask is if you hack or use this for your own purposes,
#   drop me a line at alpaca_feedback@cats-eye.com.
#   Or better yet, join the Esoteric mailing list by going to
#   http://www.cats-eye.com/mailing-lists.cgi?esoteric

# Alpaca.pm: Support for alpaca.pl-compiled CA's.
# You'll probably want to place this in your Perl site library path.
# usage: Use Alpaca;

package Alpaca;

use strict 'vars refs subs';
use Exporter;
@ISA    = ( 'Exporter' );
@EXPORT = (
            'true', 'false', 'guess',
            'adjacent_state', 'adjacent_class',
            'load_playfield', 'display_playfield', 'process_playfield'
          );

$PlayfieldA = [];
$PlayfieldB = [];

$::Playfield = $PlayfieldA;

$::Appearance = {};
$::InputCodec = {};
$::StateRule = {};

$Width = 72;
$Height = 22;

for (my $i = 0; $i < $Width; $i++)
{
  for (my $j = 0; $j < $Height; $j++)
  {
    $PlayfieldA->[$i][$j] = '';
    $PlayfieldB->[$i][$j] = '';
  }
}

$::x = 0;
$::y = 0;
$::done = 0;
$::auto = 0;

sub true  { 1 }
sub false { 0 }
sub guess { rand >= .5 ? 1 : 0 }

sub adjacent_state
{
  my $state = shift;
  my $n = 0;

  $n++ if $::Playfield->[$::x-1][$::y-1] eq $state;
  $n++ if $::Playfield->[$::x][$::y-1] eq $state;
  $n++ if $::Playfield->[$::x+1][$::y-1] eq $state;
  $n++ if $::Playfield->[$::x-1][$::y] eq $state;
  $n++ if $::Playfield->[$::x+1][$::y] eq $state;
  $n++ if $::Playfield->[$::x-1][$::y+1] eq $state;
  $n++ if $::Playfield->[$::x][$::y+1] eq $state;
  $n++ if $::Playfield->[$::x+1][$::y+1] eq $state;

  return $n;
}

sub adjacent_class
{
  my $class = shift;
  my $n = 0;

  $n++ if &$class($::Playfield->[$::x-1][$::y-1]);
  $n++ if &$class($::Playfield->[$::x][$::y-1]);
  $n++ if &$class($::Playfield->[$::x+1][$::y-1]);
  $n++ if &$class($::Playfield->[$::x-1][$::y]);
  $n++ if &$class($::Playfield->[$::x+1][$::y]);
  $n++ if &$class($::Playfield->[$::x-1][$::y+1]);
  $n++ if &$class($::Playfield->[$::x][$::y+1]);
  $n++ if &$class($::Playfield->[$::x+1][$::y+1]);

  return $n;
}

sub load_playfield
{
  print "\e[2J";
  open USERPLAY, "<$ARGV[0]";
  my $i=0; my $j=0; my $a = '';
  while(defined(my $line = <USERPLAY>))
  {
    chomp $line;
    for($i=0; $i < $Width; $i++)
    {
      $a = substr($line, $i, 1);
      if (length($a) < 1) { $a = ' '; }
      $::Playfield->[$i][$j] = $::InputCodec->{$a};
    }
    $j++;  last if $j == $Height;
  }
  $Height = $j;
  close USERPLAY;
}

sub display_playfield
{
  my $k;
  print "\e[H";
  for (my $j = 0; $j < $Height; $j++)
  {
    for (my $i = 0; $i < $Width; $i++)
    {
      print $::Appearance->{$::Playfield->[$i][$j]};
    }
    print "\n";
  }
  if (!$::auto)
  {
    chomp($k = <STDIN>);
    $::done = 1 if $k =~ /^q/io;
    $::auto = 1 if $k =~ /^a/io;
  }
}

sub process_playfield
{
  my $NewPlayfield;

  if ($::Playfield eq $PlayfieldA)
  {
    $NewPlayfield = $PlayfieldB;
  } else
  {
    $NewPlayfield = $PlayfieldA;
  }

  for ($::y = 0; $::y < $Height; $::y++)
  {
    for ($::x = 0; $::x < $Width; $::x++)
    {
      if ($::StateRule->{$::Playfield->[$::x][$::y]})
      {
        $NewPlayfield->[$::x][$::y] = &{$::StateRule->{$::Playfield->[$::x][$::y]}};
        $NewPlayfield->[$::x][$::y] = $::Playfield->[$::x][$::y]
          if !defined $NewPlayfield->[$::x][$::y];
      } else
      {
        $NewPlayfield->[$::x][$::y] = $::Playfield->[$::x][$::y];
      }
    }
  }

  $::Playfield = $NewPlayfield;
}

1;
