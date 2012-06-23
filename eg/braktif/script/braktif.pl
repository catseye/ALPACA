#!/usr/bin/perl
# eg/braktif/script/braktif.pl - automatically generated from eg/braktif/src/braktif.alp by:
# alpaca.pl v0.93
# http://catseye.webhop.net/projects/alpaca/
######################################################

use Alpaca qw(true false guess
	      adjacent_state adjacent_class
	      load_playfield display_playfield process_playfield);

sub SpaceStateRules {
  return 'SkipBack' if (($Playfield->[$x][$y-1] eq 'WakeMark' and $Playfield->[$x+1][$y-1] eq 'WendCmd') or ($Playfield->[$x+1][$y] eq 'SkipBack'));
  return 'SkipStart' if ($Playfield->[$x-1][$y-1] eq 'SkipReply' and $Playfield->[$x][$y-1] eq 'InstrMark');
  return 'SkipFore' if ($Playfield->[$x-1][$y+1] eq 'SkipStart' or $Playfield->[$x-1][$y] eq 'SkipFore');
  return 'Space'
 };

sub BusStateRules {
  return $Playfield->[$x+1][$y] if (SignalClassMember($Playfield->[$x+1][$y]));
  return $Playfield->[$x+1][$y-1] if (SignalClassMember($Playfield->[$x+1][$y-1]));
  return $Playfield->[$x+1][$y+1] if (SignalClassMember($Playfield->[$x+1][$y+1]));
  return $Playfield->[$x-1][$y] if (ReplyClassMember($Playfield->[$x-1][$y]));
  return $Playfield->[$x-1][$y-1] if (ReplyClassMember($Playfield->[$x-1][$y-1]));
  return $Playfield->[$x-1][$y+1] if (ReplyClassMember($Playfield->[$x-1][$y+1]));
  return 'ContTool' if ($Playfield->[$x+1][$y] eq 'LeftTool' or $Playfield->[$x-1][$y] eq 'RightTool');
  return 'ContReply' if ($Playfield->[$x-1][$y] eq 'ContTool');
  return 'SkipReply' if ($Playfield->[$x-1][$y] eq 'SkipTool');
  return 'LeftSig' if ($Playfield->[$x+1][$y] eq 'InstrPtr' and $Playfield->[$x+1][$y-1] eq 'LeftCmd');
  return 'RightSig' if ($Playfield->[$x+1][$y] eq 'InstrPtr' and $Playfield->[$x+1][$y-1] eq 'RightCmd');
  return 'FlipSig' if ($Playfield->[$x+1][$y] eq 'InstrPtr' and $Playfield->[$x+1][$y-1] eq 'FlipCmd');
  return 'QuerySig' if ($Playfield->[$x+1][$y] eq 'InstrPtr' and $Playfield->[$x+1][$y-1] eq 'WhileCmd');
  return 'InstrPtr' if ($Playfield->[$x-1][$y] eq 'WakeMark' or $Playfield->[$x-1][$y+1] eq 'WakeMark' or $Playfield->[$x-1][$y-1] eq 'Wakemark');
  return 'InstrPtr' if ($Playfield->[$x-1][$y] eq 'InstrPtr' and $Playfield->[$x-1][$y-1] eq 'Space');
  return 'InstrPtr' if ($Playfield->[$x+1][$y] eq 'SkipBack');
  return 'SkipStop' if ($Playfield->[$x-1][$y] eq 'SkipFore');
  return 'InstrPtr' if ($Playfield->[$x-1][$y] eq 'SkipStop');
  return 'Bus'
 };

sub SignalClassRules {
  return 'Bus' if (1);
  return 0
 };

sub ReplyClassRules {
  return 'Bus' if (1);
  return 0
 };

sub LeftSigStateRules {
  return SignalClassRules() || 'LeftSig'
 };

sub RightSigStateRules {
  return SignalClassRules() || 'RightSig'
 };

sub FlipSigStateRules {
  return SignalClassRules() || 'FlipSig'
 };

sub QuerySigStateRules {
  return SignalClassRules() || 'QuerySig'
 };

sub ContReplyStateRules {
  return ReplyClassRules() || 'ContReply'
 };

sub SkipReplyStateRules {
  return ReplyClassRules() || 'SkipReply'
 };

sub DataPtrStateRules {
  return 'FlipTool' if ($Playfield->[$x+1][$y] eq 'FlipSig');
  return 'LeftTool' if ($Playfield->[$x+1][$y] eq 'LeftSig');
  return 'RightTool' if ($Playfield->[$x+1][$y] eq 'RightSig');
  return 'SkipTool' if ($Playfield->[$x+1][$y] eq 'QuerySig' and $Playfield->[$x][$y-1] eq 'OffBit');
  return 'ContTool' if ($Playfield->[$x+1][$y] eq 'QuerySig' and $Playfield->[$x][$y-1] eq 'OnBit');
  return 'DataPtr'
 };

sub FlipToolStateRules {
  return 'ContTool' if (1);
  return 'FlipTool'
 };

sub LeftToolStateRules {
  return 'Bus' if (1);
  return 'LeftTool'
 };

sub RightToolStateRules {
  return 'Bus' if (1);
  return 'RightTool'
 };

sub ContToolStateRules {
  return 'DataPtr' if (1);
  return 'ContTool'
 };

sub SkipToolStateRules {
  return 'DataPtr' if (1);
  return 'SkipTool'
 };

sub OnBitStateRules {
  return 'OffBit' if ($Playfield->[$x][$y+1] eq 'FlipTool');
  return 'OnBit'
 };

sub OffBitStateRules {
  return 'OnBit' if ($Playfield->[$x][$y+1] eq 'FlipTool');
  return 'OffBit'
 };

sub InstrPtrStateRules {
  return 'Bus' if ($Playfield->[$x][$y-1] eq 'Space');
  return 'InstrMark' if (1);
  return 'InstrPtr'
 };

sub InstrMarkStateRules {
  return 'WakeMark' if ($Playfield->[$x-1][$y] eq 'ContReply');
  return 'Bus' if ($Playfield->[$x-1][$y] eq 'SkipReply');
  return 'InstrMark'
 };

sub WakeMarkStateRules {
  return 'Bus' if (1);
  return 'WakeMark'
 };

sub SkipStartStateRules {
  return 'Space' if (1);
  return 'SkipStart'
 };

sub SkipStopStateRules {
  return 'Bus' if (1);
  return 'SkipStop'
 };

sub SkipForeStateRules {
  return 'Space' if (1);
  return 'SkipFore'
 };

sub SkipBackStateRules {
  return 'Space' if (1);
  return 'SkipBack'
 };

sub FlipCmdStateRules {
  return 'FlipCmd'
 };

sub LeftCmdStateRules {
  return 'LeftCmd'
 };

sub RightCmdStateRules {
  return 'RightCmd'
 };

sub WhileCmdStateRules {
  return 'WhileCmd'
 };

sub WendCmdStateRules {
  return 'WendCmd'
 };

sub ReplyClassMember {
  return $_[0] eq 'ContReply' ||
         $_[0] eq 'SkipReply' ||
         0
};

sub SignalClassMember {
  return $_[0] eq 'LeftSig' ||
         $_[0] eq 'RightSig' ||
         $_[0] eq 'FlipSig' ||
         $_[0] eq 'QuerySig' ||
         0
};

$Appearance = {
  'Bus' => '-',
  'ContReply' => 'C',
  'ContTool' => 'c',
  'DataPtr' => 'd',
  'FlipCmd' => '*',
  'FlipSig' => 'F',
  'FlipTool' => 'f',
  'InstrMark' => 'I',
  'InstrPtr' => 'i',
  'LeftCmd' => '<',
  'LeftSig' => 'L',
  'LeftTool' => 'l',
  'OffBit' => '0',
  'OnBit' => '1',
  'QuerySig' => 'Q',
  'RightCmd' => '>',
  'RightSig' => 'R',
  'RightTool' => 'r',
  'SkipBack' => '{',
  'SkipFore' => '}',
  'SkipReply' => 'S',
  'SkipStart' => '!',
  'SkipStop' => '%',
  'SkipTool' => 's',
  'Space' => ' ',
  'WakeMark' => 'W',
  'WendCmd' => ']',
  'WhileCmd' => '[',

};

$InputCodec = {
  '-' => 'Bus',
  'C' => 'ContReply',
  'c' => 'ContTool',
  'd' => 'DataPtr',
  '*' => 'FlipCmd',
  'F' => 'FlipSig',
  'f' => 'FlipTool',
  'I' => 'InstrMark',
  'i' => 'InstrPtr',
  '<' => 'LeftCmd',
  'L' => 'LeftSig',
  'l' => 'LeftTool',
  '0' => 'OffBit',
  '1' => 'OnBit',
  'Q' => 'QuerySig',
  '>' => 'RightCmd',
  'R' => 'RightSig',
  'r' => 'RightTool',
  '{' => 'SkipBack',
  '}' => 'SkipFore',
  'S' => 'SkipReply',
  '!' => 'SkipStart',
  '%' => 'SkipStop',
  's' => 'SkipTool',
  ' ' => 'Space',
  'W' => 'WakeMark',
  ']' => 'WendCmd',
  '[' => 'WhileCmd',

};

$StateRule = {
  'Bus' => \&main::BusStateRules,
  'ContReply' => \&main::ContReplyStateRules,
  'ContTool' => \&main::ContToolStateRules,
  'DataPtr' => \&main::DataPtrStateRules,
  'FlipCmd' => \&main::FlipCmdStateRules,
  'FlipSig' => \&main::FlipSigStateRules,
  'FlipTool' => \&main::FlipToolStateRules,
  'InstrMark' => \&main::InstrMarkStateRules,
  'InstrPtr' => \&main::InstrPtrStateRules,
  'LeftCmd' => \&main::LeftCmdStateRules,
  'LeftSig' => \&main::LeftSigStateRules,
  'LeftTool' => \&main::LeftToolStateRules,
  'OffBit' => \&main::OffBitStateRules,
  'OnBit' => \&main::OnBitStateRules,
  'QuerySig' => \&main::QuerySigStateRules,
  'RightCmd' => \&main::RightCmdStateRules,
  'RightSig' => \&main::RightSigStateRules,
  'RightTool' => \&main::RightToolStateRules,
  'SkipBack' => \&main::SkipBackStateRules,
  'SkipFore' => \&main::SkipForeStateRules,
  'SkipReply' => \&main::SkipReplyStateRules,
  'SkipStart' => \&main::SkipStartStateRules,
  'SkipStop' => \&main::SkipStopStateRules,
  'SkipTool' => \&main::SkipToolStateRules,
  'Space' => \&main::SpaceStateRules,
  'WakeMark' => \&main::WakeMarkStateRules,
  'WendCmd' => \&main::WendCmdStateRules,
  'WhileCmd' => \&main::WhileCmdStateRules,

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
