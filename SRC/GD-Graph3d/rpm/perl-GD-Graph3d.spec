# $Id: perl-GD-Graph3d.spec,v 1.4 2008-05-05 21:29:40 aps1 Exp $
# Authority: dries
# Upstream: Jeremy Wadsack <dgsupport$wadsack-allen,com>

%define perl_vendorlib %(eval "`perl -V:installvendorlib`"; echo $installvendorlib)
%define perl_vendorarch %(eval "`perl -V:installvendorarch`"; echo $installvendorarch)

%define real_name GD-Graph3d
%define debug_package %{nil}

Summary: Create 3D Graphs
Name: perl-GD-Graph3d
Version: 0.63
Release: 2.rf
License: Artistic
Group: Applications/CPAN
URL: http://search.cpan.org/dist/GD-Graph3d/

Packager: Dries Verachtert <dries@ulyssis.org>
Vendor: Dag Apt Repository, http://dag.wieers.com/apt/

Source: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

BuildArch: noarch
#BuildRequires: perl, perl(GD), perl(GD::Text), perl(GD::Graph)
#BuildRequires: perl, perl(GD), perl(GD::Text)
BuildRequires: perl
Requires: perl, perl(GD), perl(GD::Text), perl(GD::Graph)

### Obsolete to provide fedora.us compatibility
Obsoletes: perl-GDGraph3d <= %{version}

%description
With this perl module, you can create 3D graphs with GD.

%prep
%setup -n %{name}-%{version}

%build
%{__perl} Makefile.PL \
	INSTALLDIRS="vendor" \
	PREFIX="%{buildroot}%{_prefix}"
%{__make} %{?_smp_mflags}

%install
%{__rm} -rf %{buildroot}
%makeinstall

### Clean up buildroot
%{__rm} -rf %{buildroot}%{perl_archlib} \
		%{buildroot}%{perl_vendorarch}

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-, root, root, 0755)
%doc Changes
%doc %{_mandir}/man3/*
%{perl_vendorlib}/

%changelog
* Sun Oct 03 2004 Dries Verachtert <dries@ulyssis.org> - 0.63-2 - 2975/dag
- Rebuild.

* Thu Jul 22 2004 Dries Verachtert <dries@ulyssis.org> - 0.63-1
- Initial package.
