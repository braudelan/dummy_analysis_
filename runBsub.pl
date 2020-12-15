#!/usr/bin/env perl
use warnings;
use strict;

my $VERSION = "1.16"; my $AUTHOR="Prilusky"; my $YEAR="2015";
k":w$|++;
use FindBin;
use lib "$FindBin::Bin/../lib";
use File::Basename;
use File::Spec;
use File::Path qw(make_path remove_tree);
use Digest::MD5 qw(md5_hex);

  my $binD = $FindBin::Bin; 
  my $rotD = dirname($binD); 
  my $defQueue = 'bio'; # 'new-all.q';
  my $defShell = "bash";
  my $defMem  = 2;
  my $defErrD = File::Spec->catfile($binD,"err");
  my $defOutD = File::Spec->catfile($binD,"out");
  my $defJobD = File::Spec->catfile($binD,"job");
  my $defWrkD = File::Spec->rel2abs(File::Spec->curdir());

  my($verbose,$debug,$cmdF,$nCores,$jobsPrefix,$errD,$outD,$jobD,$queue,$shell,$mem,$wrkD);
  while (@ARGV) {
    my $word = shift(@ARGV);
    if ($word =~ /-c/i) { $cmdF = shift(@ARGV); next}
    if ($word =~ /-d/i) { $debug++; next}
    if ($word =~ /-e/i) { $errD = shift(@ARGV); next}
    if ($word =~ /-h/i) { giveHelp(); exit;}
    if ($word =~ /-j/i) { $jobD = shift(@ARGV); next}
    if ($word =~ /-m/i) { $mem = shift(@ARGV); next}
    if ($word =~ /-n/i) { $nCores = shift(@ARGV); next}
    if ($word =~ /-o/i) { $outD = shift(@ARGV); next}
    if ($word =~ /-p/i) { $jobsPrefix = shift(@ARGV); next}
    if ($word =~ /-q/i) { $queue = shift(@ARGV); next}
    if ($word =~ /-s/i) { $shell = shift(@ARGV); next}
    if ($word =~ /-v/i) { $verbose++; next}
    if ($word =~ /-w/i) { $wrkD = shift(@ARGV); next}
    print "\n\n*** Unknown option '$word'"; giveHelp(); exit;}

  giveHelp("\n*** Please provide a valid commands file\n") unless ($cmdF and (-f $cmdF));

  $queue ||= $defQueue; # the ||= operator is like saying $default_var = $default_var unless it is otherwise defined
  $shell ||= $defShell;
  $mem   ||= $defMem;
  $errD ||= $defErrD; make_path($errD) unless (-d $errD);
  $outD ||= $defOutD; make_path($outD) unless (-d $outD);
  $jobD ||= $defJobD; make_path($jobD) unless (-d $jobD);
  $wrkD ||= $defWrkD;  make_path($wrkD) unless (-d $wrkD);
  
  processCommandsFile($cmdF);
  
sub processCommandsFile {
  my($cmdF)=@_;
  local(*IN); open(IN,$cmdF);
  while (my $l=<IN>) {
    trim(\$l); 
    next if ($l =~ /^#|^ *$/); # next means skip to next itertion (same as continue in python)
    my($request,$jobID) = split(/\s*###\s*/,$l);
    next unless ($request);
    $jobID ||= substr(md5_hex($l . time()),0,10);
    my $errF = File::Spec->catfile($errD,"${jobsPrefix}job.${jobID}");
    my $outF = File::Spec->catfile($outD,"${jobsPrefix}job.${jobID}");
    my $jobF = File::Spec->catfile($jobD,"${jobsPrefix}job.${jobID}");
    saveToFile(qq{#!/bin/${shell}\ncd ${wrkD}\n${request}\n},$jobF);
    chmod (0755,$jobF);
    my $numOfCores = ($nCores) ? " -n $nCores" : '';
    my $memBytes = $mem * 1024;
    my $memUsage = qq{ -R "rusage[mem=${memBytes}]" };
    my $cmd = qq{bsub $memUsage -q $queue ${numOfCores}  -e $errF  $jobF };
    print "$cmd\n";
    system("$cmd &") unless ($debug);
  }
  close(IN);
  return;
}

sub trim { my($s)=@_;$$s=~s/^\s+//;$$s=~s/\s+$//;$$s=~s/\s+/ /g;}
sub saveToFile { my($data,$file)=@_; local(*OUT);open(OUT,">$file");print OUT $data;close OUT;}

sub giveHelp {
  my($msg)=@_; 
print qq {\n$0 version   $VERSION $msg
    -commands commands file text
    -debug    debug mode
    -errors   directory to store the errors [ $defErrD ]
    -help     this help
    -jobs     directory to store the jobs [ $defJobD ]
    -ncores   10 [ system default ]
    -output   directory to store the output [ $defOutD ]
    -prefix   to the log files
    -queue    queue to send the jobs to [ $defQueue ] ( new-all.q bio )
    -shell    login shell for environment [ $defShell ]
    -memory   runtime memory in GB [ $defMem ]
    -verbose  verbose
    -working  directory [ $defWrkD ]
\n}; exit;
}
