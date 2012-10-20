# alpaca.pm v0.93 Chris Pressey
# http://catseye.webhop.net/projects/alpaca/
# Copyright (c)1999-2005 Cat's Eye Technologies.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 
#   Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# 
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.
# 
#   Neither the name of Cat's Eye Technologies nor the names of its
#   contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission. 
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE. 

# Alpaca.pm: Support for alpaca.pl-compiled CA's.
# You'll probably want to place this in your Perl site library path.
# usage: Use Alpaca;

package Alpaca;

use strict vars, refs, subs;
use Exporter;
@Alpaca::ISA       = ( 'Exporter' );
@Alpaca::EXPORT_OK = (
			'true', 'false', 'guess',
			'adjacent_state', 'adjacent_class',
			'load_playfield', 'display_playfield',
			'process_playfield'
		     );

my $PlayfieldA = [];
my $PlayfieldB = [];

$::Playfield = $PlayfieldA;

$::Appearance = {};
$::InputCodec = {};
$::StateRule = {};

my $Width = 72;
my $Height = 22;

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

sub adjacent_state($)
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

sub adjacent_class($)
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

sub load_playfield($)
{
  my $filename = shift;

  print "\e[2J";
  open USERPLAY, "<$filename";
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

sub display_playfield()
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

sub process_playfield()
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
