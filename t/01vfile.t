#!/usr/bin/perl
use strict;
use warnings;
use Test::More tests => 13;

if (eval "require Test::Differences") {
    no warnings 'redefine';
    *is_deeply = \&Test::Differences::eq_or_diff;
}

my $class = 'Text::vFile::asData';
require_ok( $class );
isa_ok( my $p = $class->new, $class );

# rfc2445 4.1
is_deeply( [ $p->_unwrap_lines(
    "FOO:This is a te",
    " st.  Not a",
    "  real foo." )
            ],
   [ "FOO:This is a test.  Not a real foo." ],
   "line unwrapping",
);

is_deeply( $p->parse_lines(
    "FOO:This is a te",
    " st.  Not a",
    "  real foo." ),
        {
            properties => {
                FOO => [ { value => "This is a test.  Not a real foo." }
                   ],
            },
        },
        "simple property"
       );


is_deeply( $p->parse_lines( 'CHECK:one\, two' ),
           {
               properties => {
                   CHECK => [ { value => 'one\, two' } ],
               },
           },
           "value containing an escaped comma"
          );

is_deeply( $p->parse_lines( "CHECK:one,two" ),
           {
               properties => {
                   CHECK => [ { value => "one,two" } ],
               },
           },
           "value containing an unescaped comma"
          );

is_deeply( $p->parse_lines( "CHECK;testing=one:two" ),
	   {
	    properties => {
			   CHECK => [ { value => 'two',
					param => { testing => 'one' }
				      } ],
			   },
	    },
	   "a single parameter"
	 );

is_deeply( $p->parse_lines( "CHECK;testing1=one;testing2=two:ffff" ),
	   {
	    properties => {
			   CHECK => [ { value => 'ffff',
					param => { testing1 => 'one',
						   testing2 => 'two', }
						 } ],
				 },
			  },
	    "multiple parameters"
	   );

is_deeply( $p->parse_lines(
    "BEGIN:PIE",
    "FILLING:MEAT",
    "END:PIE",
   ),
           {
               objects => [
                   {
                       type => "PIE",
                       properties => {
                           FILLING => [ { value => 'MEAT' } ],
                       },
                   },
                  ],
           },
           "nest 1"
          );

is_deeply( $p->parse_lines(
    "BEGIN:PIE",
    "FILLING:MEAT",
    "BEGIN:CRUST",
    "BASE:CORN",
    "END:CRUST",
    "END:PIE",
   ),
           {
               objects => [
                   {
                       type       => "PIE",
                       properties => {
                           FILLING => [ { value => 'MEAT' } ],
                       },
                       objects   => [
                           {
                               type       => "CRUST",
                               properties => {
                                   BASE => [ { value => "CORN" } ],
                               }
                          },
                          ],
                   },
                  ],
           },
           "nest two"
          );

is_deeply( $p->parse_lines(
    "FOO;BAR=BAZ;QUUX=FLANGE:FROOBLE" ),
           {
               properties => {
                   FOO => [
                       {
                           param => {
                               BAR  => 'BAZ',
                               QUUX => 'FLANGE',
                           },
                           value => 'FROOBLE',
                       },
                      ],
               },
           },
           "simple params" );


is_deeply( $p->parse_lines(
    'FOO;BAR="BAZ was here";QUUX="FLANGE":FROOBLE' ),
           {
               properties => {
                   FOO => [
                       {
                           param => {
                               BAR  => 'BAZ was here',
                               QUUX => 'FLANGE',
                           },
                           value => 'FROOBLE',
                       },
                      ],
               },
           },
           "quoted params" );

is_deeply( $p->parse_lines(
    'FOO;BAR="BAZ was here";QUUX="FLANGE wants the colon: ":FROOBLE' ),
           {
               properties => {
                   FOO => [
                       {
                           param => {
                               BAR  => 'BAZ was here',
                               QUUX => 'FLANGE wants the colon: ',
                           },
                           value => 'FROOBLE',
                       },
                      ],
               },
           },
           "quoted params" );
