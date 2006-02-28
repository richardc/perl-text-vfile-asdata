#!/usr/bin/perl
use strict;
use warnings;
use File::Slurp;
use Text::vFile::asData;
use Digest::MD5 qw(md5_hex);
use DateTime;
use CGI;

my $file = -e 'SystemsSupportRota' ? 'SystemsSupportRota' : 'http://intranet.fotango.private/index.php?title=Systems_Support_Rota&action=raw';

=head1 NAME

rota_ical.cgi - scrape the SystemsSupportRota wiki page into ics

=head1 DESCRIPTION

=cut

my @tasks;
sub make_events {
    my $when = shift;
    my %who;
    @who{ @tasks } = @_;

    my $year = DateTime->now->year;
    return unless $when =~ m{(\d+)\s*/\s*(\d+)};
    my ($day, $month) = ($1, $2);

    my $start = DateTime->new( year => $year, month => $month, day  => $day );
    my $end   = $start->clone->add( days => 1 );

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

# sometimes, we want to use a url so wrap read_file as get_lines
sub get_lines {
    my $file = shift;
    if ($file =~ m{^https?://}) {
        # s'really a url
        require LWP::Simple;
        my $content = LWP::Simple::get( $file );
        return split $/, $content;
    }
    return read_file( $file );
}

sub parse_tables {
    my (@rows, @row, $in_table);
    for (@_) {
        chomp;
        /^{\|/ and do { $in_table = 1; next };
        /^\|}/ and do { $in_table = 0; next };
        next unless $in_table;
        /^\|- / and do {
            push @rows, [@row] if @row;
            @row = ();
            next;
        };
        /^\| (.*)/ and do {
            push @row, $1;
            next;
        };
        print "Didn't expect: $_\n";
    }
    return @rows, (@row ? [@row] : ());
}

for (parse_tables( get_lines( $file ) )) {
    $_->[0] =~ /Date/ and do {
        (undef, @tasks) = @$_;
        next;
    };
    push @{ $cal->{objects} }, make_events( @$_ );
}

print CGI->header('text/calendar');
print map "$_\n", Text::vFile::asData->generate_lines( $cal );
