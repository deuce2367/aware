%define perl_vendorlib %(eval "`perl -V:installvendorlib`"; echo $installvendorlib)
%define perl_vendorarch %(eval "`perl -V:installvendorarch`"; echo $installvendorarch)

Name:           perl-XML-Writer
Version:        0.604
Release:        1%{?dist}
Summary:        A simple Perl module for writing XML documents

Group:          Development/Libraries
License:        GPL+ or Artistic
URL:            http://search.cpan.org/dist/XML-Writer/

Source: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
#BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
#BuildRequires:  perl(Test::Pod)
#BuildRequires:  perl(Test::Pod::Coverage)
BuildRequires:  perl(ExtUtils::MakeMaker)
Requires:  perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

%description
XML::Writer is a simple Perl module for writing XML documents: it
takes care of constructing markup and escaping data correctly, and by
default, it also performs a significant amount of well-formedness
checking on the output, to make certain (for example) that start and
end tags match, that there is exactly one document element, and that
there are not duplicate attribute names.


%prep
%setup -q -n perl-XML-Writer-%{version}


%build
%{__perl} Makefile.PL INSTALLDIRS=vendor
make %{?_smp_mflags} 


%install
rm -rf $RPM_BUILD_ROOT
make pure_install PERL_INSTALL_ROOT=$RPM_BUILD_ROOT
find $RPM_BUILD_ROOT -type f -a \( -name .packlist \
  -o \( -name '*.bs' -a -empty \) \) -exec rm -f {} ';'
find $RPM_BUILD_ROOT -type d -depth -exec rmdir {} 2>/dev/null ';'


%check
make test


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc Changes README TODO
%{perl_vendorlib}/*
%{_mandir}/man3/*.3*


%changelog
* Tue Mar 18 2008 Alex Lancaster <alexlan[AT]fedoraproject org> - 0.604-1
- New upstream release (0.604)

* Wed Feb 27 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0.603-4
- Rebuild for perl 5.10 (again)

* Sun Jan 20 2008 Tom "spot" Callaway <tcallawa@redhat.com> 0.603-3
- rebuild for new perl

* Thu Aug 23 2007 Alex Lancaster <alexl@users.sourceforge.net> 0.603-2
- License tag to "GPL+ or Artistic" as per new guidelines.

* Sat Aug 18 2007 Alex Lancaster <alexl@users.sourceforge.net> 0.603-1
- Update to latest upstream

* Mon Mar 26 2007 Alex Lancaster <alexl@users.sourceforge.net> 0.602-3
- Fixed %check

* Wed Mar 23 2007 Alex Lancaster <alexl@users.sourceforge.net> 0.602-2
- Update BR as per suggestions from review by Ralf Corsepius

* Wed Mar 23 2007 Alex Lancaster <alexl@users.sourceforge.net> 0.602-1
- Update to 0.602

* Wed Apr 06 2005 Hunter Matthews <thm@duke.edu> 0.531-1
- Review suggestions from José Pedro Oliveira

* Tue Mar 22 2005 Hunter Matthews <thm@duke.edu> 0.531-1
- Initial build.
