%define soversion 1.0.36
%define soversion_major 1

Name: libcgroup
Summary: Tools and libraries to control and monitor control groups
Group: Development/Libraries
Version: 0.36.1
Release: 6%{?dist}
License: LGPLv2+
URL: http://libcg.sourceforge.net/
Source0: http://downloads.sourceforge.net/libcg/%{name}-%{version}.tar.bz2
Source1: README.RedHat
Source2: lssubsys.1
Source3: lscgroup.1
Source4: cgdelete.1
Patch1: fedora-config.patch
Patch2: libcgroup-0.36.1-mp.patch
Patch3: libcgroup-0.36-cgget-crash.patch
Patch4: libcgroup-0.36-lscgroup.patch
Patch5: libcgroup-0.36.1-fix-initscripts.patch
Patch6: libcgroup-0.36.1-initscripts2.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: pam-devel
BuildRequires: byacc
BuildRequires: flex
BuildRequires: coreutils
Requires(post): chkconfig, /sbin/service
Requires(preun): /sbin/chkconfig

%description
Control groups infrastructure. The tools and library help manipulate, control,
administrate and monitor control groups and the associated controllers.

%package pam
Summary: A Pluggable Authentication Module for libcgroup
Group: System Environment/Base
Requires: libcgroup = %{version}-%{release}

%description pam
Linux-PAM module, which allows administrators to classify the user's login
processes to pre-configured control group.

%package devel
Summary: Development libraries to develop applications that utilize control groups
Group: Development/Libraries
Requires: libcgroup = %{version}-%{release}

%description devel
It provides API to create/delete and modify cgroup nodes. It will also in the
future allow creation of persistent configuration for control groups and
provide scripts to manage that configuration.

%prep
%setup -q
%patch1 -p1 -b .config
%patch2 -p1 -b .mp
%patch3 -p1 -b .crash
%patch4 -p1 -b .ls
%patch5 -p1 -b .lsb
%patch6 -p1 -b .rv

%build
%configure --bindir=/bin --sbindir=/sbin --libdir=%{_libdir}
cp %SOURCE2 doc/man
cp %SOURCE3 doc/man
cp %SOURCE4 doc/man
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT install

# install config files
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig
cp samples/cgred.conf $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/cgred.conf
cp samples/cgconfig.sysconfig $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/cgconfig
cp samples/cgconfig.conf $RPM_BUILD_ROOT/%{_sysconfdir}/cgconfig.conf
cp samples/cgrules.conf $RPM_BUILD_ROOT/%{_sysconfdir}/cgrules.conf

# sanitize pam module, we need only pam_cgroup.so in the right directory
mkdir -p $RPM_BUILD_ROOT/%{_lib}/security
mv -f $RPM_BUILD_ROOT/%{_libdir}/pam_cgroup.so.*.*.* $RPM_BUILD_ROOT/%{_lib}/security/pam_cgroup.so
rm -f $RPM_BUILD_ROOT/%{_libdir}/pam_cgroup*

# move the libraries  to /
mkdir -p $RPM_BUILD_ROOT/%{_lib}
mv -f $RPM_BUILD_ROOT/%{_libdir}/libcgroup.so.%{soversion} $RPM_BUILD_ROOT/%{_lib}
rm -f $RPM_BUILD_ROOT/%{_libdir}/libcgroup.so.%{soversion_major}
ln -sf libcgroup.so.%{soversion} $RPM_BUILD_ROOT/%{_lib}/libcgroup.so.%{soversion_major}
ln -sf ../../%{_lib}/libcgroup.so.%{soversion} $RPM_BUILD_ROOT/%{_libdir}/libcgroup.so
rm -f $RPM_BUILD_ROOT/%{_libdir}/*.la

# pre-create /cgroup directory
mkdir $RPM_BUILD_ROOT/cgroup

# install README.RedHat
cp %SOURCE1 .

%clean
rm -rf $RPM_BUILD_ROOT


%post 
/sbin/ldconfig
/sbin/chkconfig --add cgred
/sbin/chkconfig --add cgconfig

%preun
if [ $1 = 0 ]; then
    /sbin/service cgred stop > /dev/null 2>&1 || :
    /sbin/service cgconfig stop > /dev/null 2>&1 || :
    /sbin/chkconfig --del cgconfig
    /sbin/chkconfig --del cgred
fi

%postun -p /sbin/ldconfig

%files 
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/sysconfig/cgconfig
%config(noreplace) %{_sysconfdir}/sysconfig/cgred.conf
%config(noreplace) %{_sysconfdir}/cgconfig.conf
%config(noreplace) %{_sysconfdir}/cgrules.conf
/%{_lib}/libcgroup.so.*
/bin/cgexec
/bin/cgclassify
/bin/cgcreate
/bin/cgget
/bin/cgset
/bin/cgdelete
/bin/lscgroup
/bin/lssubsys
/sbin/cgconfigparser
/sbin/cgrulesengd
/sbin/cgclear
%attr(0644, root, root) %{_mandir}/man1/cgclassify.1*
%attr(0644, root, root) %{_mandir}/man1/cgclear.1*
%attr(0644, root, root) %{_mandir}/man1/cgcreate.1*
%attr(0644, root, root) %{_mandir}/man1/cgdelete.1*
%attr(0644, root, root) %{_mandir}/man1/cgexec.1*
%attr(0644, root, root) %{_mandir}/man1/cgget.1*
%attr(0644, root, root) %{_mandir}/man1/cgset.1*
%attr(0644, root, root) %{_mandir}/man1/lscgroup.1*
%attr(0644, root, root) %{_mandir}/man1/lssubsys.1*
%attr(0644, root, root) %{_mandir}/man5/cgconfig.conf.5*
%attr(0644, root, root) %{_mandir}/man5/cgred.conf.5*
%attr(0644, root, root) %{_mandir}/man5/cgrules.conf.5*
%attr(0644, root, root) %{_mandir}/man8//cgconfigparser.8*
%attr(0644, root, root) %{_mandir}/man8//cgrulesengd.8*
%attr(0755,root,root) %{_initrddir}/cgconfig
%attr(0755,root,root) %{_initrddir}/cgred
%doc COPYING INSTALL README_daemon README.RedHat
%attr(0755,root,root) %dir /cgroup

%files pam
%defattr(-,root,root,-)
%attr(0755,root,root) /%{_lib}/security/pam_cgroup.so

%files devel
%defattr(-,root,root,-)
%{_includedir}/libcgroup.h
%{_includedir}/libcgroup/*
%{_libdir}/libcgroup.*
%{_libdir}/pkgconfig/libcgroup.pc
%doc COPYING INSTALL 


%changelog
* Wed Jul 14 2010 Ivana Hutarova Varekova <varekova@redhat.com> 0.36-6
- Resolves: #609816
  serivces of libcgroup not LSB-compliant

* Tue Jun 29 2010 Jan Safranek <jsafrane@redhat.com> 0.36-5
- Relax the dependency on redhat-lsb package (#607537)
- Fix installation of -devel libraries (#607538)

* Tue Jun 15 2010 Jan Safranek <jsafrane@redhat.com> 0.36-4
- Fix libcgroup.so link to the right soname (#599367)
- Fix segmentation fault in cgget tool (#601071)
- Fix lscgroup commandline parsing (#601095)

* Tue Jun  1 2010 Ivana Hutarova Varekova <varekova@redhat.com> 0.36-3
- Related: #594249
  add three man pages

* Wed May 26 2010 Ivana Hutarova Varekova <varekova@redhat.com> 0.36-2
- Resolves: #594249
  add three man pages

* Tue May 25 2010 Jan Safranek <jsafrane@redhat.com> 0.36-1
- Updated to 0.36.1 (#594703)

* Thu Apr 22 2010 Ivana Hutarova Varekova <varekova@redhat.com> 0.35-3
- Resolves: #584681
  fix man-pages problem

* Wed Apr 14 2010 Jan Safranek <jsafrane@redhat.com> 0.35-2
- Fix parsing of command line options on ppc (#581044)

* Tue Mar  9 2010 Jan Safranek <jsafrane@redhat.com> 0.35-1
- Update to 0.35.1
- Separate pam module to its own subpackage

* Mon Jan 18 2010 Jan Safranek <jsafrane@redhat.com> - 0.34-4
- Added README.RedHat to describe libcgroup integration into initscripts

* Mon Dec 21 2009 Jan Safranek <jsafrane@redhat.com> - 0.34-3
- Change the default configuration to mount everything to /cgroup

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 0.34-2.1
- Rebuilt for RHEL 6

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.34-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jul  7 2009 Jan Safranek <jsafrane@redhat.com> 0.34-1
- Update to 0.34
* Mon Mar 09 2009 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.33-3
- Add a workaround for rt cgroup controller.
* Mon Mar 09 2009 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.33-2
- Change the cgconfig script to start earlier
- Move the binaries to /bin and /sbin
* Mon Mar 02 2009 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.33-1
- Update to latest upstream
* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> 0.32.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Jan 05 2009 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.32.2-3
- Fix redhat-lsb dependency
* Mon Dec 29 2008 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.32.2-2
- Fix build dependencies
* Mon Dec 29 2008 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.32.2-1
- Update to latest upstream
* Thu Oct 23 2008 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.32.1-1
* Tue Feb 24 2009 Balbir Singh <balbir@linux.vnet.ibm.com> 0.33-1
- Update to 0.33, spec file changes to add Makefiles and pam_cgroup module
* Fri Oct 10 2008 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.32-1
- Update to latest upstream
* Thu Sep 11 2008 Dhaval Giani <dhaval@linux-vnet.ibm.com> 0.31-1
- Update to latest upstream
* Sat Aug 2 2008 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.1c-3
- Change release to fix broken upgrade path
* Wed Jun 11 2008 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.1c-1
- Update to latest upstream version
* Tue Jun 3 2008 Balbir Singh <balbir@linux.vnet.ibm.com> 0.1b-3
- Add post and postun. Also fix Requires for devel to depend on base n-v-r
* Sat May 31 2008 Balbir Singh <balbir@linux.vnet.ibm.com> 0.1b-2
- Fix makeinstall, Source0 and URL (review comments from Tom)
* Mon May 26 2008 Balbir Singh <balbir@linux.vnet.ibm.com> 0.1b-1
- Add a generatable spec file
* Tue May 20 2008 Balbir Singh <balbir@linux.vnet.ibm.com> 0.1-1
- Get the spec file to work
* Tue May 20 2008 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.01-1
- The first version of libcg
