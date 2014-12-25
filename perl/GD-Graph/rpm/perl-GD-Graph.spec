# $Id: perl-GD-Graph.spec,v 1.1 2008-05-04 13:57:28 aps1 Exp $
# Authority: dag

%define perl_vendorlib %(eval "`perl -V:installvendorlib`"; echo $installvendorlib)
%define perl_vendorarch %(eval "`perl -V:installvendorarch`"; echo $installvendorarch)

%define real_name GDGraph
%define debug_package %{nil}

Summary: Graph plotting module for Perl
Name: perl-GD-Graph
Version: 1.43
Release: 1.rf
License: LGPL
Group: Applications/CPAN
URL: http://search.cpan.org/dist/GDGraph/

Packager: Dag Wieers <dag@wieers.com>
Vendor: Dag Apt Repository, http://dag.wieers.com/apt/

Source: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

BuildArch: noarch
BuildRequires: perl >= 0:5.8.0
Requires: perl >= 0:5.8.0

%description
Graph plotting module for Perl.

%prep
%setup -n %{name}-%{version}

%build
%{__perl} Makefile.PL PREFIX="%{buildroot}%{_prefix}" INSTALLDIRS="vendor"
%{__make} %{?_smp_mflags}

%install
%{__rm} -rf %{buildroot}
%makeinstall

### Clean up buildroot
%{__rm} -rf %{buildroot}%{perl_archlib} %{buildroot}%{perl_vendorarch}

%clean 
%{__rm} -rf %{buildroot}

%files
%defattr(-, root, root, 0755)
%doc CHANGES MANIFEST README
%doc %{_mandir}/man3/*
%dir %{perl_vendorlib}/GD/
%{perl_vendorlib}/GD/Graph/
%{perl_vendorlib}/GD/Graph.pm

%changelog
* Sat Apr 02 2005 Dag Wieers <dag@wieers.com> - 1.43-1 - 2984+/dag
- Cosmetic cleanup.
- Fixed BuildArch, now noarch.

* Mon Mar 15 2004 Dag Wieers <dag@wieers.com> - 1.43-0
- Initial package. (using DAR)
