#!/usr/bin/perl
use strict;
use warnings;
use File::Slurp;
use Text::vFile::asData;
use Digest::MD5 qw(md5_hex);
use DateTime;
use CGI;

my $file = -e 'SystemsSupportRota' ? 'SystemsSupportRota' : '/usr/local/apache/htdocs/intranet/database/SystemsSupportRota';

=head1 NAME

rota_ical.cgi - scrape the SystemsSupportRota wiki page into ics

=head1 DESCRIPTION

=cut

my @tasks;
sub make_events {
    my $when = shift;
    my $who  = shift;

    my $year = DateTime->now->year;
    return unless $when =~ m{(\d+)\s*/\s*(\d+)};
    my ($day, $month) = ($1, $2);

    my $start = DateTime->new( year => $year, month => $month, day  => $day );
    my $end   = $start->clone->add( days => 1 );

    my %who;
    @who{ @tasks } = split /\|/, $who;


    return map +{
        type => 'VEVENT',
        properties => {
            SUMMARY => [ { value => "$who{$_} $_" } ],
            DESCRIPTION => [ { value => "$when $who{$_} $_" } ],
            DTSTART => [ { value => $start->ymd(''),
                           param => { VALUE => 'DATE' },
                       } ],
            DTEND   => [ { value => $end->ymd(''),
                           param => { VALUE => 'DATE' },
                       } ],
            UID     => [ { value => md5_hex( "$when $who{$_} $_" ),
                       } ],
        },
    }, sort grep { $who{$_} } @tasks;
}

my $cal = {
    type => 'VCALENDAR',
    properties => {
        'X-WR-CALNAME' => [ { value => "Systems Rota" } ],
    },
    objects => [],
};


for (read_file( $file )) {
    chomp;
    next if /^\s*$/;
    /^\| Date \|/ and do {
        (undef, @tasks) = split / \| ?/;
    };
    /^\|(.*?)\|(.*)/ and do {
        push @{ $cal->{objects} }, make_events( $1, $2 );
        next;
    };
    # warn "unhandled line: $_";
}

print CGI->header('text/calendar');
print map "$_\n", Text::vFile::asData->generate_lines( $cal );
