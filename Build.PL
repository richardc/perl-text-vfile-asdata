use strict;
use Module::Build;
Module::Build->new(
    module_name => 'Text::vFile::asData',
    license     => 'perl',
    requires    => {
        'Class::Accessor::Chained' => 0,
        'perl' => 5.006,
    },
    build_requires => {
        'Test::More' => '0.88',
    },
    create_makefile_pl => 'traditional',
   )->create_build_script;
