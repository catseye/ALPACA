#!/usr/local/bin/perl

# alpaca.pl v0.90-1999.07.14                    Chris Pressey
# http://www.cats-eye.com/esoteric/alpaca/
# (c)1999 Cat's-Eye Technologies.  Freely redistributable.
#   All I ask is if you hack or use this for your own purposes,
#   drop me a line at alpaca@cats-eye.com.
#   Or better yet, join the Esoteric mailing list by going to
#   http://www.cats-eye.com/mailing-lists.cgi?esoteric

# Usage: [perl] alpaca[.pl] alpaca-file [program-file]

# If alpaca-file is a badly formed ALPACA file, nothing is
# guaranteed - there is no error checking as such.

# If program-file is not specified, the results of the
# compilation are routed to the standard output.

use strict 'vars refs subs';

%State = ();
%Class = ();

%Relation =
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

$Program = '';
$Token = '';
$TokenType = '';
$Emission = '';

$Class = '';

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

sub BoolPrimitive
{
  # $Emission .= "\n# BoolPrimitive\n";
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

sub AdjacentcyFunc
{
  # $Emission .= "\n# AdjacentcyFunc\n";
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

sub StateDesignator # this one RETURNS text
{
  # $Emission .= "\n# StateDesignator: ($Token, $TokenType)\n";

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

sub RelationalFunc
{
  # $Emission .= "\n# RelationalFunc ($Token, $TokenType)\n";
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

sub Expression;
sub Term
{
  # $Emission .= "\n# Term\n";
  if ($TokenType eq 'integer')
  {
    AdjacentcyFunc();
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

sub Expression
{
  # $Emission .= "\n# Expression\n";
  Term();
  while ($Token eq 'and' or $Token eq 'or' or $Token eq 'xor')
  {
    $Emission .= " $Token ";
    gtok();
    Term();
  }
}

sub Rule
{
  # $Emission .= "\n# Rule\n";
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

sub Rules
{
  # $Emission .= "\n# Rules\n";
  Rule();
  while ($Token eq ',')
  {
    gtok();
    Rule();
  }
}

sub ClassDesignator
{
  # $Emission .= "\n# ClassDesignator\n";
  if ($Token eq 'is')
  {
    gtok();
    $Class = $Token;
    gtok();
    return 1;
  }
  return 0;
}

sub State
{
  my @supers = ();

  # $Emission .= "\n# State\n";
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

sub Class
{
  my @supers = ();

  # $Emission .= "\n# Class\n";
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

sub Entry
{
  # $Emission .= "\n# Entry\n";
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
  return 0;
}

sub Entries
{
  # $Emission .= "\n# Entries\n";
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
  $Emission .= "#!/usr/local/bin/perl\n
# $ARGV[1] - automatically generated from $ARGV[0] by:
# alpaca.pl v0.90-1999.07.14
# http://www.cats-eye.com/esoteric/alpaca/\n
######################################################\n\n";
  $Emission .= "use Alpaca;\n\n";
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

    $Emission .= "load_playfield();\n\ndisplay_playfield();\n\n";
    $Emission .= "while (!\$done)\n{\n  process_playfield();\n  display_playfield();\n}\n\n";
    $Emission .= "exit(0);\n\n### END ###\n";

    return 1;
  }
  return 0;
}

########### MAIN ###########

$Program = '';

open FILE, "<$ARGV[0]";
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
