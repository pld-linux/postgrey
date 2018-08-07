%include	/usr/lib/rpm/macros.perl
Summary:	Postfix Greylisting Policy Server
Summary(pl.UTF-8):	Serwer do polityki "szarych list" dla Postfiksa
Name:		postgrey
Version:	1.37
Release:	2
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://postgrey.schweikert.ch/pub/%{name}-%{version}.tar.gz
# Source0-md5:	2ef30f42ad84f00caf41c49b593b8e2a
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	http://www.lipek.pl/postgrey_clients_dump
# Source3-md5:	155b88f2781b03535bfa2797cda28e52
Patch0:		%{name}-group.patch
Patch1:		%{name}-postfix_dir.patch
Patch2:		disable-transaction-logic
URL:		http://postgrey.schweikert.ch/
BuildRequires:	rpm-perlprov
BuildRequires:	rpmbuild(macros) >= 1.268
Requires:	perl-IO-Multiplex
Requires:	postfix
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir /etc/mail

%description
Postgrey is a Postfix policy server implementing greylisting. When a
request for delivery of a mail is received by Postfix via SMTP, the
triplet CLIENT_IP / SENDER / RECIPIENT is built. If it is the first
time that this triplet is seen, or if the triplet was first seen less
than 5 minutes, then the mail gets rejected with a temporary error.
Hopefully spammers or viruses will not try again later, as it is
however required per RFC.

Edit your configuration files:
%{_sysconfdir}/main.cf:
  smtpd_recipient_restrictions = ...
    check_policy_service unix:postgrey/socket, ...
or if you like to use inet sockets (modify the IP if needed):
/etc/sysconfig/postgrey:
  OPTIONS="--inet=127.0.0.1:10023"
%{_sysconfdir}/main.cf:
  smtpd_recipient_restrictions = ...
    check_policy_service inet:127.0.0.1:10023, ...

%description -l pl.UTF-8
Postgrey to serwer polityki dla Postfiksa implementujący "szare
listy". Kiedy Postfix otrzymuje po SMTP żądanie dostarczenia poczty,
tworzony jest triplet IP_KLIENTA / NADAWCA / ADRESAT. Jeśli dany
triplet jest widziany po raz pierwszy lub był widziany po raz pierwszy
mniej niż 5 minut temu, poczta jest odrzucana z tymczasowym błędem.
Można mieć nadzieję, że spamerzy i wirusy nie będą próbować ponownie,
co jest jednak wymagane przez RFC.

Aby użyć tego programu należy zmodyfikować pliki konfiguracyjne:
%{_sysconfdir}/main.cf:
  smtpd_recipient_restrictions = ...
    check_policy_service unix:postgrey/socket, ...
lub jeśli chcemy używać gniazd inet (w razie potrzeby zmienić IP):
/etc/sysconfig/postgrey:
  OPTIONS="--inet=127.0.0.1:10023"
%{_sysconfdir}/main.cf:
  smtpd_recipient_restrictions = ...
    check_policy_service inet:127.0.0.1:10023, ...

%prep
%setup -q
%patch0 -p1
%patch1 -p0
%patch2 -p1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{rc.d/init.d,sysconfig},%{_sysconfdir},%{_sbindir}} \
	$RPM_BUILD_ROOT%{_var}/spool/postfix/%{name}

# init script:
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}

install postgrey_whitelist_clients $RPM_BUILD_ROOT%{_sysconfdir}
install postgrey_whitelist_recipients $RPM_BUILD_ROOT%{_sysconfdir}
touch $RPM_BUILD_ROOT%{_sysconfdir}/postgrey_whitelist_clients.local

install postgrey %{SOURCE3} contrib/postgreyreport $RPM_BUILD_ROOT%{_sbindir}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 155 postgrey
%useradd -u 155 -d %{_var}/spool/postfix/%{name} -s /sbin/false -c "Postfix Greylisting Policy" -g postgrey postgrey

%post
/sbin/chkconfig --add %{name}
%service %{name} restart

%preun
if [ "$1" = 0 ]; then
	%service %{name} stop
	/sbin/chkconfig --del %{name}
fi

%postun
if [ "$1" = 0 ]; then
	%userremove postgrey
	%groupremove postgrey
	# should be done?:
	rm -rf %{_var}/spool/postfix/%{name}
fi

%files
%defattr(644,root,root,755)
%doc README Changes
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/postgrey_whitelist_clients
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/postgrey_whitelist_recipients
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/postgrey_whitelist_clients.local
%attr(640,root,postgrey) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(755,root,root) %{_sbindir}/postgrey*
%dir %attr(711,postgrey,postgrey) %{_var}/spool/postfix/%{name}
