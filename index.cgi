#!/usr/bin/perl -w
use strict;
use CGI qw/:standard/;
use POSIX qw(strftime);

binmode STDOUT, ":utf8";

die("No data/ subdir!") if not -d "data";
chdir "data";


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

sub dirname($)
{
    my $filename = shift @_;
    $filename =~ m{(.*)/([^/]+)}  &&  return $1;
    return ".";
}

sub basename($)
{
    my $filename = shift @_;
    $filename =~ m{(.*)/([^/]+)}  &&  return $2;
    return $filename;
}

sub stripwhite($)
{
    my $s = shift @_;
    $s =~ s/^\s+//g;
    $s =~ s/\s+$//g;
    return $s;
}

sub shorten($$)
{
	my ($s, $len) = @_;
	if (length($s) > $len) {
	        return substr($s, 0, $len/2)
	            . "\n\n ... PARTS OMITTED FROM RSS FEED ...\n\n"
	            . substr($s, length($s)-$len/2);
	} else {
		return $s;
	}
}





my $url = url();
my $relative = url(-relative=>1);
$url =~ s{/$relative$}{};

print "Content-Type: text/xml\n";
print "\n";

my $fail_only = defined(param('q')) && param('q') eq "failed";
my $ptitle = $fail_only ? "Cron FAIL" : "Cron";

print qq{<rss version='2.0' xmlns:atom="http://www.w3.org/2005/Atom">
	<channel>
		<title>$ptitle</title>
		<description>$ptitle</description>
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
    $description =~ s/\&/\&amp;/g;
    $description =~ s/</&lt;/g;
    $description = shorten($description, 10240);

    die unless utf8::valid($description . $title . $date . $link);
    
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

my @wanted = ();

for my $_dir (glob("*"))
{
    my $dir = basename($_dir);
    next if ! -d $dir;
    
    my @files = glob("$dir/*");
    @files = sort { mtime($b) <=> mtime($a) } @files;

    my $i = 0;
    while ($i < 5 && @files) {
        my $file = shift @files;
        my $ok = -r $file && (-z $file || $file =~ /\.ok$/);
        next if $ok && $fail_only;
        $i++;
	push @wanted, $file;
    }
}

foreach my $file (sort { mtime($b) <=> mtime($a) } @wanted) {
    my $ok = -r $file && (-z $file || $file =~ /\.ok$/);
    my $title = sprintf("%s %s", $ok ? "ok" : "ERROR", $file);
    
    print rss_item("$url/data/$file", mtime($file), $title, catfile($file));
}

print "</channel></rss>";
