%define _use_internal_dependency_generator 0
%define debug_package %{nil}

Summary: Core module for the ZUtils framework
Name: perl-ZUtils-Common
Version: 1.44
Release: 2
License: distributable
Group: Applications/CPAN
Source0: %{name}-%{version}.tar.gz
Url: http://www.cpan.org
BuildRoot: %{_tmppath}/%{name}-%{version}-root
Requires: perl
#BuildRequires: perl-ExtUtils-MakeMaker

%description 
A set of common utilities and functions for web development and system administration

%prep

%setup -q

%build
CFLAGS="$RPM_OPT_FLAGS" perl Makefile.PL   PREFIX=$RPM_BUILD_ROOT/usr INSTALLDIRS=vendor --ssl
make

%clean 
rm -rf $RPM_BUILD_ROOT

%install
rm -rf $RPM_BUILD_ROOT
make install

[ -x /usr/lib/rpm/brp-compress ] && /usr/lib/rpm/brp-compress

find $RPM_BUILD_ROOT \( -name perllocal.pod -o -name .packlist \) -exec rm -v {} \;

find $RPM_BUILD_ROOT/usr -type f -print | \
        sed "s@^$RPM_BUILD_ROOT@@g" | \
        grep -v perllocal.pod | \
        grep -v "\.packlist" > %{name}-%{version}-filelist
if [ "$(cat %{name}-%{version}-filelist)X" = "X" ] ; then
    echo "ERROR: EMPTY FILE LIST"
    exit -1
fi

%files -f %{name}-%{version}-filelist
%defattr(-,root,root)

%changelog
