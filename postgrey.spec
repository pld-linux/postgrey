%include	/usr/lib/rpm/macros.perl
Summary:	Postfix Greylisting Policy Server
Name:		postgrey
Version: 	1.21
Release:	0.4
License: 	GPL v2
Group: 		Daemons
Source0: 	http://isg.ee.ethz.ch/tools/postgrey/pub/%{name}-%{version}.tar.gz
# Source0-md5:	1274e073be5178445e0892a9dcc6fe98
Source1:	%{name}.init
Patch0:		%{name}-group.patch
Patch1:		%{name}-postfix_dir.patch
URL:		http://isg.ee.ethz.ch/tools/postgrey/
Buildarch:	noarch
BuildRequires:	rpm-perlprov
Requires:	postfix
BuildArch:	noarch
BuildRoot: 	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		confdir /etc/mail

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
%patch0 -p1
%patch1 -p1

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
%groupadd -g 155 postgrey
%useradd -u 155 -d %{_var}/spool/postfix/%{name} -s /sbin/false -c "Postfix Greylisting Policy" -g postgrey postgrey

%post
/sbin/chkconfig --add %{name}

%preun
if [ $1 -eq 0 ]; then
	if [ -f /var/lock/subsys/%{name} ]; then
		/etc/rc.d/init.d/%{name} stop >&2
	fi
        /sbin/chkconfig --del %{name}
fi

%postun
if [ $1 -eq 0 ]; then
	%userremove postgrey
	%groupremove postgrey
	# should be done?:
	rm -rf %{_var}/spool/postfix/%{name}
fi

%files
%defattr(644,root,root,755)
%doc README Changes
%config(noreplace) %verify(not md5 mtime size) %{confdir}/postgrey_whitelist_clients
%config(noreplace) %verify(not md5 mtime size) %{confdir}/postgrey_whitelist_recipients
%config(noreplace) %verify(not md5 mtime size) %{confdir}/postgrey_whitelist_clients.local
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(755,root,root) %{_sbindir}/postgrey*
%dir %attr(0711, postgrey, postgrey) %{_var}/spool/postfix/%{name}
