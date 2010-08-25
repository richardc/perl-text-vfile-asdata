use ExtUtils::MakeMaker;
WriteMakefile(
    'NAME'         => 'Text::vFile::asData',
    'VERSION_FROM' => 'lib/Text/vFile/asData.pm',
    'PREREQ_PM'    => {
        'Test::More'               => '0.88',
        'Class::Accessor::Chained' => 0
    }
);
