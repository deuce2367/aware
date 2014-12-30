#%define __spec_install_post %{nil} 
#%define _use_internal_dependency_generator 0
%define debug_package %{nil}
#%define __find_requires %{nil}

Summary: Aware Systems Monitor (server package)
Name: aware
Version: 0
Release: 8
License: GNU
Group: Applications/System
Vendor: http://www.sourceforge.com
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Requires: perl-ZUtils-Common >= 1.44
Requires: perl-ZUtils-Aware >= 1.32
Requires: mysql-server httpd perl(GD) perl(GD::Graph) perl(GD::Graph3d) perl(GD::Text)
Requires: perl(Date::Calc) perl(Bit::Vector)
Requires: perl(Time::HiRes);
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig /sbin/service
Requires(postun): /sbin/service sed
Requires: e2fsprogs shadow-utils
Source: %{name}-%{version}.tar.gz

%description
Aware Systems Monitor server components

%package client
Summary: Aware Systems Monitor (client daemon)
Group: Applications/System
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig /sbin/service
Requires: perl(ZUtils::Common) perl(ZUtils::Aware) perl(XML::Writer) perl(GD::Graph)

%description client
The Aware client daemon

%prep

%setup -q

%build

%install
/bin/rm -rf $RPM_BUILD_ROOT/%{name}-%{version}
/bin/rm -rf %{buildroot}
/bin/mkdir -p %{buildroot}/opt/aware/
/bin/mkdir -p %{buildroot}/etc/init.d
/bin/mkdir -p %{buildroot}/etc/aware
/bin/mkdir -p %{buildroot}/etc/httpd/conf.d
/bin/mkdir -p %{buildroot}/etc/logrotate.d
/bin/mkdir -p %{buildroot}/usr/bin
/bin/cp -r $RPM_BUILD_DIR/%{name}-%{version}/* %{buildroot}/opt/aware/
/bin/cp -r $RPM_BUILD_DIR/%{name}-%{version}/web/scripts/aware_daemon %{buildroot}/etc/init.d/
/bin/cp -r $RPM_BUILD_DIR/%{name}-%{version}/web/scripts/pinger %{buildroot}/etc/init.d/
/bin/cp -r $RPM_BUILD_DIR/%{name}-%{version}/web/scripts/poller %{buildroot}/etc/init.d/
/bin/cp -r $RPM_BUILD_DIR/%{name}-%{version}/cfg/aware_httpd.conf %{buildroot}/etc/httpd/conf.d/
/bin/cp -r $RPM_BUILD_DIR/%{name}-%{version}/cfg/aware_logs.cfg %{buildroot}/etc/logrotate.d/aware
/bin/cp -r $RPM_BUILD_DIR/%{name}-%{version}/cfg/aware_client_logs.cfg %{buildroot}/etc/logrotate.d/aware_client
/bin/cp -r $RPM_BUILD_DIR/%{name}-%{version}/cfg/default.cfg %{buildroot}/etc/aware/aware.cfg
/bin/cp -r $RPM_BUILD_DIR/%{name}-%{version}/bin/* %{buildroot}/usr/bin

%clean 
/bin/rm -rf %{buildroot}

%files client
%config /etc/aware/aware.cfg
%config /etc/logrotate.d/aware_client
/etc/init.d/aware_daemon
/usr/bin/

%files
/opt/aware/bin
/opt/aware/cfg
/opt/aware/doc
/opt/aware/logs
/opt/aware/schema
/opt/aware/web
/etc/httpd/conf.d/aware_httpd.conf
/etc/init.d/pinger
/etc/init.d/poller
%config /etc/logrotate.d/aware

%pre

%post
/bin/chmod 777 /opt/aware/web/images/tmp

## somebody set up us the pinger
/sbin/chkconfig --add pinger
/sbin/chkconfig pinger on

## somebody set up us the poller
/sbin/chkconfig --add poller
/sbin/chkconfig poller on


%postun
if [ "$1" = "0" ] ; then 
    rm -rf /var/log/pinger.log*
    rm -rf /var/log/poller.log*
fi

%postun client
#if [ "$1" = "0" ] ; then
#    /sbin/service aware_daemon stop
#    /sbin/chkconfig --del aware_daemon
#    rm -rf /var/log/aware_daemon.log*
#fi

if [ "$1" = "1" ] ; then
    /sbin/service aware_daemon restart
fi


%preun client

%post client

if [ ! -f /etc/aware/hostid ] ; then
	uuidgen > /etc/aware/hostid
fi

if [ "$1" = "1" ] ; then
    ## restart the client
    /sbin/chkconfig --add aware_daemon
    /sbin/chkconfig aware_daemon on
fi

%changelog
* Tue Jul 22 2008 xxxxxx - 013
- many updates
* Fri Nov 2 2007 xxxxxx - 010
- added Makefile-driven RPM generation
- packaged for consolidator from Denver
* Sat Oct 6 2007 xxxxxx - 009
- added RRD Updates
- packaged for XXX and XXX
* Wed Jul 25 2007 xxxxxx - 009
- initial build
