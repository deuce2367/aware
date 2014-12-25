# $Id: perl-GD.spec,v 1.3 2008-05-05 21:29:40 aps1 Exp $
# Authority: dag

%{?dist: %{expand: %%define %dist 1}}

%{!?dist:%define _with_modxorg 1}
%{?fc7:  %define _with_modxorg 1}
%{?el5:  %define _with_modxorg 1}
%{?fc6:  %define _with_modxorg 1}
%{?fc5:  %define _with_modxorg 1}

%define perl_vendorlib %(eval "`perl -V:installvendorlib`"; echo $installvendorlib)
%define perl_vendorarch %(eval "`perl -V:installvendorarch`"; echo $installvendorarch)

%define real_name GD
%define debug_package %{nil}

Summary: GD Perl interface to the GD Graphics Library
Name: perl-GD
Version: 2.30
Release: 2.2.rf
License: LGPL
Group: Applications/CPAN
URL: http://search.cpan.org/dist/GD/

Packager: Dag Wieers <dag@wieers.com>
Vendor: Dag Apt Repository, http://dag.wieers.com/apt/

Source: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

BuildRequires: perl >= 0:5.8.0, gd-devel >= 2.0.12, libpng-devel, zlib-devel
BuildRequires: freetype-devel, libjpeg-devel
#%{?_with_modxorg:BuildRequires: xorg-x11-devel}
#%{!?_with_modxorg:BuildRequires: XFree86-devel}
Requires: perl >= 0:5.8.0

%description
perl-GD is a Perl interface to the gd graphics library. GD allows you
to create color drawings using a large number of graphics primitives,
and emit the drawings as PNG files.

%prep
#%setup -n %{real_name}-%{version}
%setup -n %{name}-%{version}

%build
CFLAGS="%{optflags}" %{__perl} Makefile.PL \
	-options "JPEG,FT,XPM,PNG,GIF" \
	-lib_gd_path "%{_libdir}" \
	-lib_ft_path "%{_libdir}" \
	-lib_png_path "%{_libdir}" \
	-lib_jpeg_path "%{_libdir}" \
	-lib_xpm_path "%{_libdir}" \
	-lib_zlib_path "%{_libdir}" \
	PREFIX="%{buildroot}%{_prefix}" \
	INSTALLDIRS="vendor"
%{__make} %{?_smp_mflags} \
	OPTIMIZE="%{optflags}"

%install
%{__rm} -rf %{buildroot}
%makeinstall

### Clean up buildroot
#%{__rm} -rf %{buildroot}%{perl_archlib} %{buildroot}%{perl_vendorarch}/auto/*{,/*{,/*}}/.packlist
#find %{buildroot} -name "*.pod" | xargs -r sed -i 's:'%{buildroot}'::g' 
%{__rm} -rf %{buildroot}%{perl_vendorarch}/auto/*{,/*{,/*}}/.packlist
find %{buildroot} -name "*.pod" | xargs -r /bin/rm

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-, root, root, 0755)
%doc ChangeLog MANIFEST README
%doc %{_mandir}/man?/*
%{perl_vendorarch}/GD.pm
%{perl_vendorarch}/GD/
%{perl_vendorarch}/auto/GD/
%{perl_vendorarch}/qd.pl
%{_bindir}/bdf2gdfont.pl

%changelog
* Sat Apr 08 2006 Dries Verachtert <dries@ulyssis.org> - 2.30-2.2 - 4308+/dries
- Rebuild for Fedora Core 5.

* Sun Dec 25 2005 Dag Wieers <dag@wieers.com> - 2.30-2
- Added PNG support. (Why was it gone ?)

* Sat Nov  5 2005 Dries Verachtert <dries@ulyssis.org> - 2.30-1
- Updated to release 2.30.

* Wed Jan 19 2005 Dag Wieers <dag@wieers.com> - 2.16-1
- Updated to release 2.16.

* Thu Feb 19 2004 Dag Wieers <dag@wieers.com> - 2.11-0
- Initial package. (using DAR)
