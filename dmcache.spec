# TODO
# - make it use kernel headers, not -source
#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose build (V=1)

%if %{without kernel}
%undefine	with_dist_kernel
%endif

%define		_rel	0.1
Summary:	DM-Cache: A Generic Block-level Disk Cache
Name:		dmcache
Version:	0.1
Release:	%{_rel}
License:	GPL
Group:		Base/Kernel
Source0:	http://www.acis.ufl.edu/~ming/dmcache/dmc-setup.pl
# Source0-md5:	f9a214936265781d30a11fbc1d6c0878
Patch0:		linux-%{name}.patch
URL:		http://www.acis.ufl.edu/~ming/dmcache/index.html
BuildRequires:	patchutils
%if %{with kernel}
%if %{with dist_kernel}
BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.20.2
BuildRequires:	kernel%{_alt_kernel}-source >= 3:2.6.20.2
%endif
BuildRequires:	rpmbuild(macros) >= 1.379
%endif
%{?with_userspace:BuildRequires:	perl-tools-pod}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Dm-cache provides a generic block-level disk cache for storage
networking. It is built upon the Linux device-mapper, a generic block
device virtualization infrastructure. It can be transparently plugged
into a client of any storage system, including SAN, iSCSI and AoE, and
supports dynamic customization for policy-guided optimizations.
Experimental evaluation based on file system benchmarks and typical
applications show that dm-cache can significantly improve the
performance and scalability of a storage system by orders of
magnitude.

%package -n kernel%{_alt_kernel}-drivers-dmcache
Summary:	Linux driver for dmcache
Summary(pl.UTF-8):	Sterownik dla Linuksa do dmcache
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):	%releq_kernel
%endif

%description -n kernel%{_alt_kernel}-drivers-dmcache
This is driver for dmcache for Linux.

This package contains Linux module.

%description -n kernel%{_alt_kernel}-drivers-dmcache -l pl.UTF-8
Sterownik dla Linuksa do dmcache.

Ten pakiet zawiera moduł jądra Linuksa.

%prep
%setup -qcT
install %{SOURCE0} .
filterdiff -x '*/Kconfig' -x '*/Makefile' %{PATCH0} | %{__patch} -p1
# prepare makefile:
cat > drivers/md/Makefile << EOF
obj-m += dm-cache.o

EXTRA_CFLAGS="-I%{_kernelsrcdir}/drivers/md"
EOF

%build
%if %{with userspace}
pod2man dmc-setup.pl > dmc-setup.1
%endif

%if %{with kernel}
%build_kernel_modules -C drivers/md -m dm-cache
%endif

%install
rm -rf $RPM_BUILD_ROOT
%if %{with userspace}
install -d $RPM_BUILD_ROOT{%{_sbindir},%{_mandir}/man1}
install dmc-setup.pl $RPM_BUILD_ROOT%{_sbindir}/dmc-setup
install dmc-setup.1 $RPM_BUILD_ROOT%{_mandir}/man1
%endif

%if %{with kernel}
%install_kernel_modules -m drivers/md/dm-cache -d kernel/drivers/md
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel%{_alt_kernel}-drivers-dmcache
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-drivers-dmcache
%depmod %{_kernel_ver}

%if %{with kernel}
%files -n kernel%{_alt_kernel}-drivers-dmcache
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/drivers/md/*.ko*
%endif

%if %{with userspace}
%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/dmc-setup
%{_mandir}/man1/dmc-setup.1*
%endif
