#!/usr/bin/perl -w
use strict;
use CGI qw/:standard/;
use POSIX qw(strftime);

use lib ".";

sub mtime($)
{
	my $filename = shift @_;
	my ($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,
	    $atime,$mtime,$ctime,$blksize,$blocks) = stat($filename)
	    or die("stat $filename: $!\n");
	return $mtime;
}

sub catfile(@)
{
	my @list = ();
	foreach my $file (@_) {
		open my $fh, "<$file" or return "(Can't read file!)";
		push @list, <$fh>;
		close $fh;
	}
	return join('', @list);
}

sub basename($)
{
	my $filename = shift @_;
	$filename =~ m{.*/([^/]+)}  &&  ($filename = $1);
	return $filename;
}

sub stripwhite($)
{
	my $s = shift @_;
	$s =~ s/^\s+//g;
	$s =~ s/\s+$//g;
	return $s;
}


my $url = url();
my $relative = url(-relative=>1);
$url =~ s{/$relative$}{};

print "Content-Type: text/xml\n";
print "\n";

print qq{<rss version='2.0' xmlns:atom="http://www.w3.org/2005/Atom">
	<channel>
		<title>Cron</title>
		<description>Cron</description>
		<link>$url</link>
		<atom:link href="$url/index.cgi" rel="self" type="application/rss+xml" />
		<language>en-ca</language>
		<generator>CGI</generator>
		<docs>http://blogs.law.harvard.edu/tech/rss</docs>
};

sub rss_item($$$$)
{
    my ($link, $datecode, $title, $description) = @_;
    
    my $date = strftime("%a, %d %b %Y %H:%M:%S %z", localtime($datecode));
    $description =~ s/</&lt;/g;
    
    return qq{
	<item>
	  <title>$title</title>
	  <pubDate>$date</pubDate>
	  <link>$link</link>
	  <guid isPermaLink='true'>$link</guid>
	  <description>$description</description>
	</item>
    };
}

chdir "data";

for my $_dir (glob("*"))
{
    my $dir = basename($_dir);
    next if ! -d $dir;
    
    my @files = glob("$dir/*");
    @files = sort { mtime($b) <=> mtime($a) } @files;
    
    foreach my $file (@files) {
	print rss_item("$url/data/$file", mtime($file), $file, $file);
    }
}


# for my $file (</tmp/*>) {
#    rss_item("$url/data/$file", mtime($file), "File: $file", catfile($file));
# }

print "</channel></rss>";
