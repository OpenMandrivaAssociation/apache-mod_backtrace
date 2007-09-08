Summary:	Collects backtraces when a child process crashes
Name:		apache-mod_backtrace
Version:	0
Release:	%mkrel 7
Group:		System/Servers
License:	Apache License
Group:		System/Servers
URL:		http://www.apache.org
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
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

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

%{_sbindir}/apxs `apr-1-config --includes` -c mod_backtrace.c

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot} 

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
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot} 


%files
%defattr(-,root,root)
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/ZZ90_mod_backtrace.conf
%attr(0755,root,root) %{_libdir}/apache-extramodules/mod_backtrace.so
%attr(0644,apache,apache) %ghost /var/log/httpd/backtrace_log
