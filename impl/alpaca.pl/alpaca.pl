#!/usr/bin/perl

# alpaca.pl v0.93 Chris Pressey
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

# Usage: [perl] alpaca[.pl] alpaca-file [program-file]

# If alpaca-file is a badly formed ALPACA file, nothing is
# guaranteed - there is very little error checking.

# If alpaca-file is not specified, it is read from standard
# input.

# If program-file is not specified, the results of the
# compilation are routed to the standard output.

use strict vars, refs, subs;

### GLOBALS ###

my %State = ();
my %Class = ();

my %Relation =
(
  'n'     => '$Playfield->[$x][$y-1]',
  's'     => '$Playfield->[$x][$y+1]',
  'e'     => '$Playfield->[$x+1][$y]',
  'w'     => '$Playfield->[$x-1][$y]',
  'ne'    => '$Playfield->[$x+1][$y-1]',
  'nw'    => '$Playfield->[$x-1][$y-1]',
  'se'    => '$Playfield->[$x+1][$y+1]',
  'sw'    => '$Playfield->[$x-1][$y+1]',

  'me'    => '$Playfield->[$x][$y]',

  '^'     => '$Playfield->[$x][$y-1]',
  'v'     => '$Playfield->[$x][$y+1]',
  '>'     => '$Playfield->[$x+1][$y]',
  '<'     => '$Playfield->[$x-1][$y]',
  '^>'    => '$Playfield->[$x+1][$y-1]',
  '^<'    => '$Playfield->[$x-1][$y-1]',
  'v>'    => '$Playfield->[$x+1][$y+1]',
  'v<'    => '$Playfield->[$x-1][$y+1]'
);

my $Program = '';
my $Token = '';
my $TokenType = '';
my $Emission = '';

my $Class = '';

my $line = '';
my $emit_comments = 0;

### UTILITY SUBROUTINES ###

sub gtok()
{
  $Program =~ s/^\s+//o;
  while ($Program =~ /^\/\*(.*?)\*\/(\s*)/o)
  {
    $Program = $';
  }
  if ($Program =~ /^\'(.*?)\'/o or $Program =~ /^\"(.*?)\"/o)
  {
    $Token = $1;
    $Program = $';
    $TokenType = 'text';
  }
  elsif ($Program =~ /^(\d+)/o)
  {
    $Token = $1;
    $Program = $';
    $TokenType = 'integer';
  }
  elsif ($Program =~ /^([A-Z_a-z]\w+)/o)
  {
    $Token = $1;
    $Program = $';
    $TokenType = 'bareword';
  }
  elsif ($Program =~ /^([\.\;\,\(\)])/o)
  {
    $Token = $1;
    $Program = $';
    $TokenType = 'symbol';
  }
  elsif ($Program =~ /^([v\^\>\<]+)/o)
  {
    $Token = $1;
    $Program = $';
    $TokenType = 'arrow';
  }
  else
  {
    $Token = '';
    $TokenType = 'eof';
  }
}

sub emit_comment($)
{
  my $comment = shift;
  if ($emit_comments) {
    $Emission .= "\n# " . $comment . ": ($Token, $TokenType)\n";
  }
}

### RECURSIVE DESCENT PARSER ###

sub BoolPrimitive()
{
  emit_comment("BoolPrimitive");
  if ($TokenType eq 'bareword')
  {
    if ($Token eq 'true')
    {
      $Emission .= "true()";      gtok();  return 1;
    }
    elsif ($Token eq 'false')
    {
      $Emission .= "false()";     gtok();  return 1;
    }
    elsif ($Token eq 'guess')
    {
      $Emission .= "guess()";     gtok();  return 1;
    }
  }
  return 0;
}

sub AdjacencyFunc()
{
  emit_comment("AdjacencyFunc");
  if ($TokenType eq 'integer')
  {
    my $n = 0 + $Token;
    gtok();
    if ($Token eq 'is')
    {
      $Emission .= "(adjacent_class(\\\&";
      ClassDesignator();
      $Emission .= "${Class}ClassMember";
    } else
    {
      $Emission .= "(adjacent_state(";
      $Emission .= StateDesignator();
    }
    $Emission .= ") >= $n)";
    return 1;
  }
  return 0;
}

sub StateDesignator() # this function RETURNS text rather than emitting it
{
  emit_comment("StateDesignator");

  my $e = '';
  if ($TokenType eq 'bareword' or $TokenType eq 'arrow')
  {
    if (exists $Relation{$Token})
    {
      $e .= $Relation{$Token};
      gtok();
      return $e;
    }
    else
    {
      $e .= "\'$Token\'";
      gtok();
      return $e;
    }
  }
  return '';
}

sub RelationalFunc()
{
  emit_comment("RelationalFunc");
  if ($TokenType eq 'bareword' or $TokenType eq 'arrow')
  {
    my $e = StateDesignator();

    if ($Token eq 'is')
    {
      ClassDesignator();
      $e = "${Class}ClassMember($e)";
    } else
    {
      $e .= " eq " . StateDesignator();
    }

    $Emission .= $e;
    return 1;
  }
  return 0;
}

sub Expression(); # forward
sub Term()
{
  emit_comment("Term");
  if ($TokenType eq 'integer')
  {
    AdjacencyFunc();
    return 1;
  }
  elsif ($Token eq '(')
  {
    gtok();
    $Emission .= "(";
    Expression();
    $Emission .= ")";
    gtok() if ($Token eq ')');
    return 1;
  }
  elsif ($Token eq 'not')
  {
    gtok();
    $Emission .= "(not ";
    Term();
    $Emission .= ")";
    return 1;
  }
  elsif ($Token eq 'true' or $Token eq 'false' or $Token eq 'guess')
  {
    BoolPrimitive();
    return 1;
  } else
  {
    RelationalFunc();
  }
  return 0;
}

sub Expression()
{
  emit_comment("Expression");
  Term();
  while ($Token eq 'and' or $Token eq 'or' or $Token eq 'xor')
  {
    $Emission .= " $Token ";
    gtok();
    Term();
  }
}

sub Rule()
{
  emit_comment("Rule");
  if ($Token eq 'to')
  {
    gtok();
    $Emission .= "  return ";
    $Emission .= StateDesignator();
    $Emission .= " if (";
    if ($Token eq 'when')
    {
      gtok();
      Expression();
    } else
    {
      $Emission .= '1';
    }
    $Emission .= ");\n";
    return 1;
  }
  return 0;
}

sub Rules()
{
  emit_comment("Rules");
  Rule();
  while ($Token eq ',')
  {
    gtok();
    Rule();
  }
}

sub ClassDesignator()
{
  emit_comment("ClassDesignator");
  if ($Token eq 'is')
  {
    gtok();
    $Class = $Token;
    gtok();
    return 1;
  }
  return 0;
}

sub State()
{
  my @supers = ();

  emit_comment("State");
  if ($Token eq 'state')
  {
    gtok();
    if ($TokenType eq 'bareword')
    {
      my $x = $Token; my $a = ' ';
      gtok();
      $Emission .= "sub ${x}StateRules {\n";
      if ($TokenType eq 'text')
      {
        $a = $Token;
        gtok();
      }
      while ($Token eq 'is')
      {
        ClassDesignator();
        push @{$Class{$Class}}, $x;
        push @supers, $Class;
      }
      if ($Token eq 'to')
      {
        Rules();
      }
      $Emission .= "  return ";
      foreach my $k (@supers)
      {
        $Emission .= "${k}ClassRules() || ";
      }
      $Emission .= "\'${x}\'\n };\n\n";
      $State{$x} = $a;
      return 1;
    }
  }
  return 0;
}

sub Class()
{
  my @supers = ();

  emit_comment("Class");
  if ($Token eq 'class')
  {
    gtok();
    if ($TokenType eq 'bareword')
    {
      my $x = $Token; my $a;
      gtok();
      $Emission .= "sub ${x}ClassRules {\n";
      if ($TokenType eq 'text')
      {
        $a = $Token;
        gtok();
      }
      while ($Token eq 'is')
      {
        ClassDesignator();
        push @supers, $Class;
      }
      if ($Token eq 'to')
      {
        Rules();
      }
      $Emission .= "  return ";
      foreach my $k (@supers)
      {
        $Emission .= "${k}ClassRules() || ";
      }
      $Emission .= "0\n };\n\n";
      $Class{$x} = [];
      return 1;
    }
  }
  return 0;
}

sub Entry()
{
  emit_comment("Entry");
  if ($Token eq 'class')
  {
    Class();
    return 1;
  }
  elsif ($Token eq 'state')
  {
    State();
    return 1;
  }
  else
  {
    die "Expected 'class' or 'state' but found '$Token'";
  }
  return 0;
}

sub Entries()
{
  emit_comment("Entries");
  Entry();
  while ($Token eq ';')
  {
    gtok();
    Entry();
  }
  return 1;
}

sub AlpacaProgram
{
  $Emission .= <<"END_OF_HEADER";
#!/usr/bin/perl
# $ARGV[1] - automatically generated from $ARGV[0] by:
# alpaca.pl v0.93
# http://catseye.webhop.net/projects/alpaca/
######################################################

use Alpaca qw(true false guess
	      adjacent_state adjacent_class
	      load_playfield display_playfield process_playfield);

END_OF_HEADER
  gtok();
  Entries();
  if ($Token eq '.')
  {
    foreach my $k (sort keys %Class)
    {
      $Emission .= "sub ${k}ClassMember {\n  return ";
      foreach my $q (@{$Class{$k}})
      {
        $Emission .= "\$_\[0] eq \'$q\' ||\n         ";
      }
      $Emission .= "0\n};\n\n";
    }

    $Emission .= "\$Appearance = {\n";
    foreach my $k (sort keys %State)
    {
      $Emission .= "  '$k' => '$State{$k}',\n";
    }
    $Emission .= "\n};\n\n";

    $Emission .= "\$InputCodec = {\n";
    foreach my $k (sort keys %State)
    {
      $Emission .= "  '$State{$k}' => '$k',\n";
    }
    $Emission .= "\n};\n\n";

    $Emission .= "\$StateRule = {\n";
    foreach my $k (sort keys %State)
    {
      $Emission .= "  '$k' => \\\&main\:\:${k}StateRules,\n";
    }
    $Emission .= "\n};\n\n";

    $Emission .= <<"END_OF_FOOTER";
load_playfield(\$ARGV[0]);

display_playfield();

while (!\$done)
{
  process_playfield();
  display_playfield();
}

exit(0);

### END ###
END_OF_FOOTER
    return 1;
  }
  return 0;
}

########### MAIN ###########

$Program = '';

if (defined($ARGV[0]))
{
  open FILE, "<$ARGV[0]";
} else {
  open FILE, "-"; # STDIN
}
while (defined($line = <FILE>))
{
  chomp $line;
  $Program .= $line;
}
close FILE;

AlpacaProgram();

if (defined($ARGV[1]))
{
  open FILE, ">$ARGV[1]";
  print FILE $Emission;
  close FILE;
} else
{
  print $Emission;
}

exit(0);
