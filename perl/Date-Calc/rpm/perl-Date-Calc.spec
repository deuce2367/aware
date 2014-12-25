%define debug_package %{nil}
%define perl_vendorlib %(eval "`perl -V:installvendorlib`"; echo $installvendorlib)
%define perl_vendorarch %(eval "`perl -V:installvendorarch`"; echo $installvendorarch)

Name:           perl-Date-Calc
Version:        5.4
Release:        1.2.2.1
Summary:        A module for extended and efficient date calculations in Perl
Group:          Development/Libraries
License:        GPL or Artistic
URL:            http://search.cpan.org/dist/Date-Calc/
Source:         %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  perl >= 1:5.6.1
#BuildRequires:  perl-Bit-Vector >= 6.4
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
Requires:       perl-Bit-Vector >= 6.4

%description
The library provides all sorts of date calculations based on the
Gregorian calendar (the one used in all western countries today),
thereby complying with all relevant norms and standards: ISO/R
2015-1971, DIN 1355 and, to some extent, ISO 8601 (where applicable).

%prep
%setup -q -n %{name}-%{version} 
%{__perl} -pi -e 's|^#!perl\b|#!%{__perl}|' examples/*.{pl,cgi} tools/*.pl

%build
CFLAGS="$RPM_OPT_FLAGS" %{__perl} Makefile.PL INSTALLDIRS=vendor
make %{?_smp_mflags} OPTIMIZE="$RPM_OPT_FLAGS"

%install
rm -rf $RPM_BUILD_ROOT
make pure_install PERL_INSTALL_ROOT=$RPM_BUILD_ROOT
find $RPM_BUILD_ROOT -type f -name .packlist -exec rm -f {} ';'
find $RPM_BUILD_ROOT -type f -name '*.bs' -a -size 0 -exec rm -f {} ';'
find $RPM_BUILD_ROOT -type d -depth -exec rmdir {} 2>/dev/null ';'
chmod -R u+w $RPM_BUILD_ROOT/*

file=$RPM_BUILD_ROOT%{_mandir}/man3/Date::Calc.3pm
iconv -f iso-8859-1 -t utf-8 < "$file" > "${file}_"
mv -f "${file}_" "$file"

%check
make test
/bin/rm -rf $RPM_BUILD_ROOT/%{perl_vendorarch}/Carp/


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc Artistic.txt GNU_GPL.txt GNU_LGPL.txt
%doc CHANGES.txt CREDITS.txt README.txt
%doc EXAMPLES.txt examples/ TOOLS.txt tools/
%{perl_vendorarch}/Date/
%{perl_vendorarch}/auto/Date/
%{_mandir}/man3/*.3*

%changelog
* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - sh: line 0: fg: no job control
- rebuild

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 5.4-1.2.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 5.4-1.2.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Fri Feb 03 2006 Jason Vas Dias <jvdias@redhat.com> - 5.4-1.2
- rebuild for new perl-5.8.8

* Fri Dec 16 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt for new gcc

* Sat Apr  2 2005 Jose Pedro Oliveira <jpo at di.uminho.pt> - 5.4-1
- Update to 5.4.
- Bring up to date with current Fedora.Extras perl spec template.

* Thu Nov 25 2004 Miloslav Trmac <mitr@redhat.com> - 5.3-10
- Convert man page to UTF-8

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Chip Turner <cturner@redhat.com> 5.3-5
- rebuilt

* Thu Jun 05 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Dec 10 2002 Chip Turner <cturner@redhat.com>
- update to latest version from CPAN

* Tue Aug  6 2002 Chip Turner <cturner@redhat.com>
- automated release bump and build

* Wed Jan 30 2002 cturner@redhat.com
- Specfile autogenerated

