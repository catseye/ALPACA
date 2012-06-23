#!/usr/bin/perl
# eg/redgreen/script/redgreen.pl - automatically generated from eg/redgreen/src/redgreen.alp by:
# alpaca.pl v0.93
# http://catseye.webhop.net/projects/alpaca/
######################################################

use Alpaca qw(true false guess
	      adjacent_state adjacent_class
	      load_playfield display_playfield process_playfield);

sub FallableClassRules {
  return 'Air' if ((not SupportClassMember($Playfield->[$x][$y+1])) and (adjacent_state('Air') >= 2) and (not (adjacent_state('DuctTape') >= 1)));
  return 'Water' if ((not SupportClassMember($Playfield->[$x][$y+1])) and (adjacent_state('Water') >= 4) and (not (adjacent_state('DuctTape') >= 1)));
  return $Playfield->[$x][$y] if (($Playfield->[$x][$y+1] eq 'ConveyorLeft' and (not PassthruClassMember($Playfield->[$x-1][$y]))) or ($Playfield->[$x][$y+1] eq 'ConveyorRight' and (not PassthruClassMember($Playfield->[$x+1][$y]))));
  return 0
 };

sub PassthruClassRules {
  return $Playfield->[$x][$y-1] if (FallableClassMember($Playfield->[$x][$y-1]));
  return $Playfield->[$x+1][$y] if (FallableClassMember($Playfield->[$x+1][$y]) and $Playfield->[$x+1][$y+1] eq 'ConveyorLeft');
  return $Playfield->[$x-1][$y] if (FallableClassMember($Playfield->[$x-1][$y]) and $Playfield->[$x-1][$y+1] eq 'ConveyorRight');
  return 0
 };

sub FlammableClassRules {
  return 'Fire' if ((adjacent_class(\&BurnerClassMember) >= 1));
  return 0
 };

sub SteamyClassRules {
  return 'Water' if ($Playfield->[$x-1][$y] eq 'Water' or $Playfield->[$x+1][$y] eq 'Water' or $Playfield->[$x-1][$y-1] eq 'Water' or $Playfield->[$x+1][$y-1] eq 'Water' or $Playfield->[$x][$y-1] eq 'Water');
  return 'Air' if (1);
  return 0
 };

sub BurnerClassRules {
  return 0
 };

sub SupportClassRules {
  return 0
 };

sub AirStateRules {
  return 'Water' if ($Playfield->[$x][$y-1] eq 'Water' or $Playfield->[$x-1][$y-1] eq 'Water' or $Playfield->[$x+1][$y-1] eq 'Water' or ($Playfield->[$x-1][$y] eq 'Water' and SupportClassMember($Playfield->[$x-1][$y+1])) or ($Playfield->[$x-1][$y] eq 'Water' and $Playfield->[$x-1][$y+1] eq 'Water' and $Playfield->[$x][$y+1] eq 'Water') or ($Playfield->[$x+1][$y] eq 'Water' and SupportClassMember($Playfield->[$x+1][$y+1])) or ($Playfield->[$x+1][$y] eq 'Water' and $Playfield->[$x+1][$y+1] eq 'Water' and $Playfield->[$x][$y+1] eq 'Water'));
  return 'Steam' if ($Playfield->[$x][$y+1] eq 'Steam' or $Playfield->[$x-1][$y+1] eq 'Steam' or $Playfield->[$x+1][$y+1] eq 'Steam');
  return 'Smoke' if ($Playfield->[$x][$y+1] eq 'Smoke' or $Playfield->[$x-1][$y+1] eq 'Smoke' or $Playfield->[$x+1][$y+1] eq 'Smoke');
  return 'Zappy' if ((adjacent_state('Spark') >= 1));
  return PassthruClassRules() || 'Air'
 };

sub WaterStateRules {
  return 'Steam' if ((adjacent_state('Fire') >= 1) or (adjacent_state('Magma') >= 1));
  return 'Bubble' if ($Playfield->[$x][$y+1] eq 'Bubble' or $Playfield->[$x][$y+1] eq 'Smoke' or $Playfield->[$x][$y+1] eq 'Steam');
  return 'Fish' if ((adjacent_state('Fish') >= 3) and (adjacent_state('Water') >= 5));
  return PassthruClassRules() || 'Water'
 };

sub FireStateRules {
  return 'Smoke' if ((adjacent_state('Water') >= 1) or (not (adjacent_state('Air') >= 1)) or ((not (adjacent_state('Torch') >= 1)) and (not (adjacent_state('DuctTape') >= 1)) and (not (adjacent_state('Twig') >= 1))));
  return PassthruClassRules() || BurnerClassRules() || 'Fire'
 };

sub EarthStateRules {
  return 'Magma' if ((adjacent_state('Fire') >= 1));
  return SupportClassRules() || 'Earth'
 };

sub MagmaStateRules {
  return 'Earth' if ((not (adjacent_state('Fire') >= 1)) and (not (adjacent_state('Magma') >= 2)));
  return SupportClassRules() || BurnerClassRules() || 'Magma'
 };

sub SteamStateRules {
  return PassthruClassRules() || SteamyClassRules() || 'Steam'
 };

sub SmokeStateRules {
  return PassthruClassRules() || SteamyClassRules() || 'Smoke'
 };

sub BubbleStateRules {
  return PassthruClassRules() || SteamyClassRules() || 'Bubble'
 };

sub FishStateRules {
  return 'Air' if ((not (adjacent_state('Water') >= 1)));
  return 'Water' if ((adjacent_state('Fish') >= 4) or (adjacent_state('Water') >= 7));
  return 'Fish'
 };

sub OnePebbleStateRules {
  return 'TwoPebble' if ($Playfield->[$x][$y-1] eq 'OnePebble' and (SupportClassMember($Playfield->[$x][$y+1])));
  return FallableClassRules() || 'OnePebble'
 };

sub TwoPebbleStateRules {
  return FallableClassRules() || SupportClassRules() || 'TwoPebble'
 };

sub SparkStateRules {
  return 'Tail' if (1);
  return SupportClassRules() || BurnerClassRules() || 'Spark'
 };

sub TailStateRules {
  return 'Wire' if (1);
  return SupportClassRules() || 'Tail'
 };

sub WireStateRules {
  return 'Spark' if ((adjacent_state('Spark') >= 1) and (not (adjacent_state('Spark') >= 4)));
  return SupportClassRules() || 'Wire'
 };

sub DuctTapeStateRules {
  return 'UnravelTape' if (((not (adjacent_state('DuctTape') >= 2))) or ((not ((adjacent_state('DuctTape') >= 1) and (adjacent_class(\&SupportClassMember) >= 1)))));
  return SupportClassRules() || FlammableClassRules() || 'DuctTape'
 };

sub UnravelTapeStateRules {
  return FallableClassRules() || FlammableClassRules() || 'UnravelTape'
 };

sub TwigStateRules {
  return FallableClassRules() || SupportClassRules() || FlammableClassRules() || 'Twig'
 };

sub ZappyStateRules {
  return 'BigZappy' if (1);
  return PassthruClassRules() || 'Zappy'
 };

sub BigZappyStateRules {
  return 'Air' if (1);
  return PassthruClassRules() || 'BigZappy'
 };

sub RandomizerStateRules {
  return SupportClassRules() || 'Randomizer'
 };

sub ConveyorLeftStateRules {
  return 'ConveyorRight' if ($Playfield->[$x][$y+1] eq 'Randomizer' and guess());
  return 'ConveyorLeft'
 };

sub ConveyorRightStateRules {
  return 'ConveyorLeft' if ($Playfield->[$x][$y+1] eq 'Randomizer' and guess());
  return 'ConveyorRight'
 };

sub TorchStateRules {
  return 'Torch'
 };

sub BurnerClassMember {
  return $_[0] eq 'Fire' ||
         $_[0] eq 'Magma' ||
         $_[0] eq 'Spark' ||
         0
};

sub FallableClassMember {
  return $_[0] eq 'OnePebble' ||
         $_[0] eq 'TwoPebble' ||
         $_[0] eq 'UnravelTape' ||
         $_[0] eq 'Twig' ||
         0
};

sub FlammableClassMember {
  return $_[0] eq 'DuctTape' ||
         $_[0] eq 'UnravelTape' ||
         $_[0] eq 'Twig' ||
         0
};

sub PassthruClassMember {
  return $_[0] eq 'Air' ||
         $_[0] eq 'Water' ||
         $_[0] eq 'Fire' ||
         $_[0] eq 'Steam' ||
         $_[0] eq 'Smoke' ||
         $_[0] eq 'Bubble' ||
         $_[0] eq 'Zappy' ||
         $_[0] eq 'BigZappy' ||
         0
};

sub SteamyClassMember {
  return $_[0] eq 'Steam' ||
         $_[0] eq 'Smoke' ||
         $_[0] eq 'Bubble' ||
         0
};

sub SupportClassMember {
  return $_[0] eq 'Earth' ||
         $_[0] eq 'Magma' ||
         $_[0] eq 'TwoPebble' ||
         $_[0] eq 'Spark' ||
         $_[0] eq 'Tail' ||
         $_[0] eq 'Wire' ||
         $_[0] eq 'DuctTape' ||
         $_[0] eq 'Twig' ||
         $_[0] eq 'Randomizer' ||
         0
};

$Appearance = {
  'Air' => ' ',
  'BigZappy' => 'Z',
  'Bubble' => 'o',
  'ConveyorLeft' => '<',
  'ConveyorRight' => '>',
  'DuctTape' => 'D',
  'Earth' => '#',
  'Fire' => '%',
  'Fish' => 'f',
  'Magma' => '&',
  'OnePebble' => '.',
  'Randomizer' => '?',
  'Smoke' => '@',
  'Spark' => '*',
  'Steam' => 's',
  'Tail' => '-',
  'Torch' => 'T',
  'Twig' => 'l',
  'TwoPebble' => ':',
  'UnravelTape' => 'O',
  'Water' => '~',
  'Wire' => '=',
  'Zappy' => 'z',

};

$InputCodec = {
  ' ' => 'Air',
  'Z' => 'BigZappy',
  'o' => 'Bubble',
  '<' => 'ConveyorLeft',
  '>' => 'ConveyorRight',
  'D' => 'DuctTape',
  '#' => 'Earth',
  '%' => 'Fire',
  'f' => 'Fish',
  '&' => 'Magma',
  '.' => 'OnePebble',
  '?' => 'Randomizer',
  '@' => 'Smoke',
  '*' => 'Spark',
  's' => 'Steam',
  '-' => 'Tail',
  'T' => 'Torch',
  'l' => 'Twig',
  ':' => 'TwoPebble',
  'O' => 'UnravelTape',
  '~' => 'Water',
  '=' => 'Wire',
  'z' => 'Zappy',

};

$StateRule = {
  'Air' => \&main::AirStateRules,
  'BigZappy' => \&main::BigZappyStateRules,
  'Bubble' => \&main::BubbleStateRules,
  'ConveyorLeft' => \&main::ConveyorLeftStateRules,
  'ConveyorRight' => \&main::ConveyorRightStateRules,
  'DuctTape' => \&main::DuctTapeStateRules,
  'Earth' => \&main::EarthStateRules,
  'Fire' => \&main::FireStateRules,
  'Fish' => \&main::FishStateRules,
  'Magma' => \&main::MagmaStateRules,
  'OnePebble' => \&main::OnePebbleStateRules,
  'Randomizer' => \&main::RandomizerStateRules,
  'Smoke' => \&main::SmokeStateRules,
  'Spark' => \&main::SparkStateRules,
  'Steam' => \&main::SteamStateRules,
  'Tail' => \&main::TailStateRules,
  'Torch' => \&main::TorchStateRules,
  'Twig' => \&main::TwigStateRules,
  'TwoPebble' => \&main::TwoPebbleStateRules,
  'UnravelTape' => \&main::UnravelTapeStateRules,
  'Water' => \&main::WaterStateRules,
  'Wire' => \&main::WireStateRules,
  'Zappy' => \&main::ZappyStateRules,

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
