Summary:	Postfix Greylisting Policy Server
Name:		postgrey
Version: 	1.21
Release:	0.1
License: 	GPL
Group: 		Daemons
Source: 	http://isg.ee.ethz.ch/tools/postgrey/pub/%{name}-%{version}.tar.gz
Source1:	%{name}.sysv
Patch:		postgrey-group.patch
URL:		http://isg.ee.ethz.ch/tools/postgrey/
Buildarch:	noarch
Prereq: 	perl, perl-IO-Multiplex, perl-Net-Server, perl-BerkeleyDB
BuildArch:	noarch
BuildRoot: 	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		confdir /etc/postfix
%define		uid	95
%define		gid	95


%description
Postgrey is a Postfix policy server implementing greylisting.
When a request for delivery of a mail is received by Postfix 
via SMTP, the triplet CLIENT_IP / SENDER / RECIPIENT is built. 
If it is the first time that this triplet is seen, or if the 
triplet was first seen less than 5 minutes, then the mail gets 
rejected with a temporary error. Hopefully spammers or viruses 
will not try again later, as it is however required per RFC.
Edit your configuration files:
/etc/postfix/main.cf:
  smtpd_recipient_restrictions = ...
    check_policy_service unix:postgrey/socket, ...
or if you like to use inet sockets (modify the IP if needed):
/etc/sysconfig/postgrey:
  OPTIONS="--inet=127.0.0.1:10023"
/etc/postfix/main.cf:
  smtpd_recipient_restrictions = ...
    check_policy_service inet:127.0.0.1:10023, ...


%prep
%setup -q
%patch -p1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{rc.d/init.d,sysconfig},%{confdir},%{_sbindir}} \
	$RPM_BUILD_ROOT%{_var}/spool/postfix/%{name}

# init script:
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

install postgrey_whitelist_clients $RPM_BUILD_ROOT%{confdir}
install postgrey_whitelist_recipients $RPM_BUILD_ROOT%{confdir}
touch $RPM_BUILD_ROOT%{confdir}/postgrey_whitelist_clients.local

install postgrey $RPM_BUILD_ROOT%{_sbindir}
install contrib/postgreyreport $RPM_BUILD_ROOT%{_sbindir}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ $1 -eq 1 ]; then
	%{_sbindir}/groupadd -g %{gid} -r %{name} &>/dev/null || :
	%{_sbindir}/useradd -d %{_var}/spool/postfix/%{name} -s /sbin/nologin -u %{uid} -g %{gid} -M -r %{name} 2>/dev/null || :
fi

%post
/sbin/chkconfig --add %{name}

%preun
if [ $1 -eq 0 ]; then
        /sbin/service %{name} stop &>/dev/null || :
        /sbin/chkconfig --del %{name}
fi

%postun
if [ $1 -eq 0 ]; then
	%{_sbindir}/userdel %{name} 2>/dev/null || :
	%{_sbindir}/groupdel %{name} 2>/dev/null || :
	%{__rm} -rf %{_var}/spool/postfix/%{name}
fi


%files
%defattr(-,root,root)
%doc README Changes COPYING
%{_initrddir}/%{name}
%config(noreplace) %{confdir}/postgrey_whitelist_clients
%config(noreplace) %{confdir}/postgrey_whitelist_recipients
%config(noreplace) %{confdir}/postgrey_whitelist_clients.local
%{_sbindir}/postgrey*
%dir %attr(0711, postgrey, postgrey) %{_var}/spool/postfix/%{name}
