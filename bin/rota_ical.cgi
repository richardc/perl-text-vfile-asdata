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

sub make_event {
    my $when = shift;
    my $who  = shift;

    my $year = DateTime->now->year;
    return unless $when =~ m{(\d+)\s*/\s*(\d+)};
    my ($day, $month) = ($1, $2);

    my $start = DateTime->new( year => $year, month => $month, day  => $day );
    my $end   = $start->clone->add( days => 1 );

    return {
        type => 'VEVENT',
        properties => {
            SUMMARY => [ { value => $who } ],
            DESCRIPTION => [ { value => "$when $who" } ],
            DTSTART => [ { value => $start->ymd(''),
                           param => { VALUE => 'DATE' },
                       } ],
            DTEND   => [ { value => $end->ymd(''),
                           param => { VALUE => 'DATE' },
                       } ],
            UID     => [ { value => md5_hex( "$when $who" ),
                       } ],
        },
    };
}

my $cal = {
    type => 'VCALENDAR',
    properties => {
        'X-WR-CALNAME' => [ { value => "Systems Rota" } ],
    },
    objects => [],
};
for (read_file( $file )) {
    next if /^\s*$/;
    /^\|(.*?)\|(.*)\|/ and do {
        push @{ $cal->{objects} }, make_event( $1, $2 );
        next;
    };
    # warn "unhandled line: $_";
}

print CGI->header('text/calendar');
print map "$_\n", Text::vFile::asData->generate_lines( $cal );
