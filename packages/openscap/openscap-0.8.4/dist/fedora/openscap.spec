%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

Name:           openscap
Version:        0.8.4
Release:        1%{?dist}
Summary:        Set of open source libraries enabling integration of the SCAP line of standards
Group:          System Environment/Libraries
License:        LGPLv2+
URL:            http://www.open-scap.org/
Source0:        http://www.open-scap.org/download/%{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  swig libxml2-devel libxslt-devel perl-XML-Parser
BuildRequires:  rpm-devel
BuildRequires:  libgcrypt-devel
BuildRequires:  pcre-devel
BuildRequires:  libacl-devel
BuildRequires:  libselinux-devel libcap-devel
BuildRequires:  libblkid-devel
BuildRequires:  libnl-devel
Requires(post):   /sbin/ldconfig
Requires(postun): /sbin/ldconfig

%description
OpenSCAP is a set of open source libraries providing an easier path 
for integration of the SCAP line of standards. SCAP is a line of standards 
managed by NIST with the goal of providing a standard language 
for the expression of Computer Network Defense related information.

%package        devel
Summary:        Development files for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
Requires:       libxml2-devel
Requires:       pkgconfig

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%package        python
Summary:        Python bindings for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
BuildRequires:  python-devel 

%description    python
The %{name}-python package contains the bindings so that %{name}
libraries can be used by python.

%package        perl
Summary:        Perl bindings for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
BuildRequires:  perl-devel

%description    perl
The %{name}-perl package contains the bindings so that %{name}
libraries can be used by perl.


%package        utils
Summary:        Openscap utilities
Group:          Applications/System
Requires:       %{name} = %{version}-%{release}

%description    utils
The %{name}-utils package contains various utilities based on %{name} library.


%package        content
Summary:        SCAP content
Group:          Applications/System
Requires:       %{name} = %{version}-%{release}

%description    content
Example of SCAP content for Fedora. Please note that this content
is for testing purposes only.

%package        content-sectool
Summary:        Sectool content
Group:          Applications/System
Requires:       %{name} = %{version}-%{release}

%description    content-sectool
SCAP/SCE content that conforms to sectool checks.

%package        extra-probes
Summary:        SCAP probes
Group:          Applications/System
Requires:       %{name} = %{version}-%{release}
BuildRequires:  openldap-devel
BuildRequires:  GConf2-devel
#BuildRequires:  opendbx - for sql

%description    extra-probes
The %{name}-extra-probes package contains additional probes that are not
commonly used and require additional dependencies.


%prep
%setup -q

%build
%ifarch sparc64
#sparc64 need big PIE
export CFLAGS="$RPM_OPT_FLAGS -fPIE"
export LDFLAGS="-pie -Wl,-z,relro -Wl,-z,now"
%else
export CFLAGS="$RPM_OPT_FLAGS -fpie"
export LDFLAGS="-pie -Wl,-z,relro -Wl,-z,now"
%endif

%configure --enable-sce

make %{?_smp_mflags}
# Remove shebang from bash-completion script
sed -i '/^#!.*bin/,+1 d' dist/bash_completion.d/oscap

%check
#to run make check use "--with check"
%if %{?_with_check:1}%{!?_with_check:0}
make check
%endif

%install
rm -rf $RPM_BUILD_ROOT

make install INSTALL='install -p' DESTDIR=$RPM_BUILD_ROOT

# create symlinks to default content
ln -s  %{_datadir}/openscap/scap-fedora14-oval.xml $RPM_BUILD_ROOT/%{_datadir}/openscap/scap-oval.xml
ln -s  %{_datadir}/openscap/scap-fedora14-xccdf.xml $RPM_BUILD_ROOT/%{_datadir}/openscap/scap-xccdf.xml

# remove content for another OS
rm $RPM_BUILD_ROOT/%{_datadir}/openscap/scap-rhel6-oval.xml
rm $RPM_BUILD_ROOT/%{_datadir}/openscap/scap-rhel6-xccdf.xml

# bash-completion script
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/bash_completion.d
install -pm 644 dist/bash_completion.d/oscap $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d/oscap

find $RPM_BUILD_ROOT -name '*.la' -exec rm -f {} ';'

%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%doc AUTHORS COPYING ChangeLog NEWS README
%{_libdir}/*.so.*
%{_libexecdir}/openscap/probe_dnscache
%{_libexecdir}/openscap/probe_environmentvariable
%{_libexecdir}/openscap/probe_environmentvariable58
%{_libexecdir}/openscap/probe_family
%{_libexecdir}/openscap/probe_file
%{_libexecdir}/openscap/probe_fileextendedattribute
%{_libexecdir}/openscap/probe_filehash
%{_libexecdir}/openscap/probe_filehash58
%{_libexecdir}/openscap/probe_iflisteners
%{_libexecdir}/openscap/probe_inetlisteningservers
%{_libexecdir}/openscap/probe_interface
%{_libexecdir}/openscap/probe_partition
%{_libexecdir}/openscap/probe_password
%{_libexecdir}/openscap/probe_process
%{_libexecdir}/openscap/probe_process58
%{_libexecdir}/openscap/probe_routingtable
%{_libexecdir}/openscap/probe_rpminfo
%{_libexecdir}/openscap/probe_rpmverify
%{_libexecdir}/openscap/probe_rpmverifyfile
%{_libexecdir}/openscap/probe_runlevel
%{_libexecdir}/openscap/probe_selinuxboolean
%{_libexecdir}/openscap/probe_selinuxsecuritycontext
%{_libexecdir}/openscap/probe_shadow
%{_libexecdir}/openscap/probe_sysctl
%{_libexecdir}/openscap/probe_system_info
%{_libexecdir}/openscap/probe_textfilecontent
%{_libexecdir}/openscap/probe_textfilecontent54
%{_libexecdir}/openscap/probe_uname
%{_libexecdir}/openscap/probe_variable
%{_libexecdir}/openscap/probe_xinetd
%{_libexecdir}/openscap/probe_xmlfilecontent
%dir %{_datadir}/openscap
%dir %{_datadir}/openscap/schemas
%dir %{_datadir}/openscap/xsl
%{_datadir}/openscap/schemas/*
%{_datadir}/openscap/xsl/*

%files python
%defattr(-,root,root,-)
%{python_sitearch}/*

%files perl
%defattr(-,root,root,-)
%{perl_vendorarch}/*
%{perl_vendorlib}/*

%files devel
%defattr(-,root,root,-)
%doc docs/{html,examples}/
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc

%files utils
%defattr(-,root,root,-)
%doc docs/oscap-scan.cron
%{_mandir}/man8/*
%{_bindir}/*
%{_sysconfdir}/bash_completion.d

%files content
%defattr(-,root,root,-)
%{_datadir}/openscap/scap-oval.xml
%{_datadir}/openscap/scap-xccdf.xml
%{_datadir}/openscap/scap-fedora14-oval.xml
%{_datadir}/openscap/scap-fedora14-xccdf.xml

%files content-sectool
%defattr(-,root,root,-)
%{_datadir}/openscap/sectool-sce

%files extra-probes
%{_libexecdir}/openscap/probe_ldap57
%{_libexecdir}/openscap/probe_gconf

%changelog
* Tue Aug 07 2012 Petr Lautrbach <plautrba@redhat.com> 0.8.4-1
- upgrade

* Mon Jul 30 2012 Petr Lautrbach <plautrba@redhat.com> 0.8.3-1
- upgrade

* Wed Mar 28 2012 Petr Lautrbach <plautrba@redhat.com> 0.8.2-1
- upgrade

* Tue Feb 21 2012 Peter Vrabec <pvrabec@redhat.com> 0.8.1-1
- upgrade
