#!/usr/bin/perl -w
use strict;

print "Content-Type: text/plain\n";
print "\n";

my $filename = $ENV{"QUERY_STRING"};

if ($filename =~ m{/\.} || $filename =~ m{^/} || $filename =~ m{\.\.}) {
    print "Invalid filename given!\n";
}

$filename = "data/$filename";

if (! -e $filename) {
    print "File does not exist.\n";
}

open my $fh, "<$filename" or die("$filename: $!\n");
while (<>) {
    print;
}
close $fh;
