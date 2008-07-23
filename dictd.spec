%define version 1.10.1
%define release %mkrel 8

# NEC Socks V5 support
%define enable_socks 0
%{?_with_plf: %global enable_socks 1}

Summary:	Client/server software implementing the Dictionary Server Protocol
Name:		dictd
Version:	%{version}
Release:	%{release}
License:	GPL
Group:		Text tools
URL:		http://www.dict.org/
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

Source0:	http://internap.dl.sourceforge.net/sourceforge/dict/%name-%version.tar.bz2
Source1:	%{name}.init
Source2:	%{name}.sysconfig
#(neoclust) Add a configuration file to allow dictd as a xinetd service provided by Eric Pielbug  ( piel@lifl.fr )
Source3:	%name
Source4:	update-%{name}.conf

# (Abel) Add missing include when compiling sample plugins
Patch0:		%{name}-1.9.7-missing-header.patch


Requires:	%{name}-server = %version-%release
Requires:	%{name}-client = %version-%release
Requires:	%{name}-utils = %version-%release

BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	groff-for-man
BuildRequires:	libtool-devel
BuildRequires:	zlib-devel
%if %enable_socks
BuildRequires:	socks5-devel
%endif

%description 
The DICT Protocol, described in RFC 2229 is a TCP transaction based
query/response protocol that allows a client to access dictionary
definitions from a set of natural language dictionary databases.

This package contains documentation about DICT.

Build Options:
--with plf		compile with Socks V5 support

%package	utils
Summary:	Dictionary management/maintenance utilities
Group:		Text tools

%description	utils
The DICT Protocol, described in RFC 2229 is a TCP transaction based
query/response protocol that allows a client to access dictionary
definitions from a set of natural language dictionary databases.

This package contains various utilities handling file format used by
dictd, such as dict file (de)compression.

%package	client
Summary:	Command line software accessing Dictionary Server Protocol
Group:		Text tools

%description	client
The DICT Protocol, described in RFC 2229 is a TCP transaction based
query/response protocol that allows a client to access dictionary
definitions from a set of natural language dictionary databases.

This packages contains dict(1) which can access DICT servers from the
command line.

%package	server
Summary:	Server software implementing the Dictionary Server Protocol
Group:		System/Servers
Requires(post):	rpm-helper
Requires(preun):	rpm-helper
Requires:	dictd-dictionaries >= 0.1.0-11, dictd-dictionary >= 0.1.0-11
Conflicts:	dictd-dictionaries <= 0.1.0-10, dictd-dictionary <= 0.1.0-10

%description	server
The DICT Protocol, described in RFC 2229 is a TCP transaction based
query/response protocol that allows a client to access dictionary
definitions from a set of natural language dictionary databases.

This packages contains dictd(8) which is a server supporting the DICT
protocol.

%package	static-devel
Summary:	Development related file for DICT plugins
Group:		Development/C

%description	static-devel
This package contains various development related files from dict.
You need to install this package if you want to develop or compile
anything that has dict plugin support. 

%prep
%setup -q 
%patch0 -p1 -b .include

sed -i 's/\(CFLAGS=.*$\)/\1 -fPIC/' libmaa/Makefile.in

perl -pi -e 's!/usr/lib/dict!%{_datadir}/dict!g' dictd.conf example.conf

%build
# Plugins are install in $libexecdir
%define _libexecdir %{_libdir}/%{name}

%configure2_5x \
%if %enable_socks
	--with-nec-socks \
%endif
	--with-cflags="$RPM_OPT_FLAGS" \
	--datadir=%{_datadir}/dict

# Do NOT use %make here!  Compiliation *WILL* fail!
make

%install
rm -rf %{buildroot}
%makeinstall_std install.samples

# dict client config
mkdir -p %{buildroot}%{_sysconfdir}
cat > %{buildroot}%{_sysconfdir}/dict.conf << _EOF_
# pager less
# server test.dict.org
# server dict.dom.ain { port 2628 user joe mysecretpasswd }
server localhost
_EOF_
chmod 644 %{buildroot}%{_sysconfdir}/dict.conf

# server initscript
mkdir -p %{buildroot}%{_initrddir}
install -m 755 %{SOURCE1} %{buildroot}%{_initrddir}/%{name}-server

#
mkdir %{buildroot}%{_sysconfdir}/xinetd.d/
cp %{SOURCE3} %{buildroot}%{_sysconfdir}/xinetd.d/


mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
install -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/%{name}

# owns /etc/dictd.conf
echo > %{buildroot}%{_sysconfdir}/dictd.conf
mkdir -p %{buildroot}%{_sysconfdir}/dictd.conf.d
cp -a %{SOURCE4} %{buildroot}%{_sbindir}

# Multiarch Files
%if %mdkversion >= 1020
%multiarch_binaries %{buildroot}%{_bindir}/dictdplugin-config
%endif

%clean
rm -rf %{buildroot}

%post server
%{_sbindir}/update-dictd.conf
%_post_service %{name}-server

%preun server
%_preun_service %{name}-server

%files

%files utils
%defattr(-,root,root)
%doc ANNOUNCE COPYING INSTALL README TODO
%{_mandir}/man1/dictfmt*
%{_mandir}/man1/dictunformat.*
%{_mandir}/man1/dictzip.*
%{_mandir}/man1/colorit.*
%{_mandir}/man1/dictl.*

%{_bindir}/dictfmt*
%{_bindir}/dictunformat
%{_bindir}/dictzip
%{_bindir}/colorit
%{_bindir}/dictl

%files server
%defattr(-,root,root)
%doc dictd.conf example.conf example?.conf example.site example_*.conf
%doc doc/rfc2229.txt doc/security.doc
%doc ANNOUNCE COPYING INSTALL README TODO
%{_initrddir}/%{name}-server
%dir %{_sysconfdir}/dictd.conf.d
%config(noreplace) %{_sysconfdir}/dictd.conf
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%config(noreplace) %{_sysconfdir}/xinetd.d/dictd

%{_sbindir}/*
%{_libdir}/%{name}
%{_datadir}/dict/*
%{_mandir}/man8/*

%files client
%defattr(-,root,root)
%doc example.dictrc
%config(noreplace) %{_sysconfdir}/dict.conf
%{_bindir}/dict
%{_mandir}/man1/dict.*

%files static-devel
%defattr(-,root,root)
%doc ChangeLog
%{_bindir}/dictdplugin-config
%if %mdkversion >= 1020
%multiarch %{multiarch_bindir}/dictdplugin-config
%endif
%{_includedir}/dictdplugin.h


