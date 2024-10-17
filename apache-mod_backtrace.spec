Summary:	Collects backtraces when a child process crashes
Name:		apache-mod_backtrace
Version:	0
Release:	17
Group:		System/Servers
License:	Apache License
Group:		System/Servers
URL:		https://www.apache.org
# http://www.apache.org/~trawick/mod_backtrace.c
Source0: 	mod_backtrace.c.bz2
Source1: 	test_char.h.bz2
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache-base >= 2.2.0
Requires(pre):	apache-modules >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache-base >= 2.2.0
Requires:	apache-modules >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0

%description
mod_backtrace is an experimental module for Apache httpd 2.x which
collects backtraces when a child process crashes. Currently it is
implemented only on Linux and FreeBSD, but other platforms could be
supported in the future. You should verify that it works reasonably
on your system before putting it in production.

It implements a fatal exception hook that will be called when a child
process crashes. In the exception hook it uses system library routines
to obtain information about the call stack, and it writes the call
stack to a log file or the web server error log. The backtrace is a
critical piece of information when determining the failing software
component that caused the crash.  Note that the backtrace written by
mod_backtrace may not have as much information as a debugger can
display from a core dump.

%prep

%setup -c -T

bzcat %{SOURCE0} > mod_backtrace.c
bzcat %{SOURCE1} > test_char.h

%build

%{_bindir}/apxs `apr-1-config --includes` -c mod_backtrace.c

%install

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d
install -d %{buildroot}/var/log/httpd

install -m0755 .libs/mod_backtrace.so %{buildroot}%{_libdir}/apache-extramodules/

# fix the mod_backtrace.conf
cat << EOF > %{buildroot}/%{_sysconfdir}/httpd/modules.d/ZZ90_mod_backtrace.conf
<IfDefine HAVE_BACKTRACE>
  <IfModule !mod_backtrace.so.c>
    LoadModule backtrace_module		extramodules/mod_backtrace.so
  </IfModule>
</IfDefine>

<IfModule mod_backtrace.c>
    EnableExceptionHook On
    BacktraceLog logs/backtrace_log
</IfModule>
EOF

touch %{buildroot}/var/log/httpd/backtrace_log

%post
%create_ghostfile /var/log/httpd/backtrace_log apache apache 0644
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
        %{_initrddir}/httpd restart 1>&2
    fi
fi

%clean


%files
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/ZZ90_mod_backtrace.conf
%attr(0755,root,root) %{_libdir}/apache-extramodules/mod_backtrace.so
%attr(0644,apache,apache) %ghost /var/log/httpd/backtrace_log


%changelog
* Sat Feb 11 2012 Oden Eriksson <oeriksson@mandriva.com> 0-16mdv2012.0
+ Revision: 772595
- rebuild

* Tue May 24 2011 Oden Eriksson <oeriksson@mandriva.com> 0-15
+ Revision: 678281
- mass rebuild

* Sun Oct 24 2010 Oden Eriksson <oeriksson@mandriva.com> 0-14mdv2011.0
+ Revision: 587939
- rebuild

* Mon Mar 08 2010 Oden Eriksson <oeriksson@mandriva.com> 0-13mdv2010.1
+ Revision: 516067
- rebuilt for apache-2.2.15

* Sat Aug 01 2009 Oden Eriksson <oeriksson@mandriva.com> 0-12mdv2010.0
+ Revision: 406551
- rebuild

* Tue Jan 06 2009 Oden Eriksson <oeriksson@mandriva.com> 0-11mdv2009.1
+ Revision: 325636
- rebuild

* Mon Jul 14 2008 Oden Eriksson <oeriksson@mandriva.com> 0-10mdv2009.0
+ Revision: 234781
- rebuild

* Thu Jun 05 2008 Oden Eriksson <oeriksson@mandriva.com> 0-9mdv2009.0
+ Revision: 215547
- fix rebuild

* Fri Mar 07 2008 Oden Eriksson <oeriksson@mandriva.com> 0-8mdv2008.1
+ Revision: 181704
- rebuild

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Sat Sep 08 2007 Oden Eriksson <oeriksson@mandriva.com> 0-7mdv2008.0
+ Revision: 82534
- rebuild

* Sat Aug 18 2007 Oden Eriksson <oeriksson@mandriva.com> 0-6mdv2008.0
+ Revision: 65629
- rebuild


* Sat Mar 10 2007 Oden Eriksson <oeriksson@mandriva.com> 0-5mdv2007.1
+ Revision: 140649
- rebuild

* Thu Nov 09 2006 Oden Eriksson <oeriksson@mandriva.com> 0-4mdv2007.1
+ Revision: 79353
- Import apache-mod_backtrace

* Wed Aug 23 2006 Oden Eriksson <oeriksson@mandriva.com> 0-4mdv2007.0
- use correct apr-1-config

* Mon Aug 07 2006 Oden Eriksson <oeriksson@mandriva.com> 0-3mdv2007.0
- rebuild

* Wed Dec 14 2005 Oden Eriksson <oeriksson@mandriva.com> 0-2mdk
- rebuilt against apache-2.2.0

* Sun Nov 06 2005 Oden Eriksson <oeriksson@mandriva.com> 0-1mdk
- initial Mandriva package

