# TODO
# - build fails as internal kernel headers are used like:
#include "dm.h"
#include "dm-io.h"
#include "dm-bio-list.h"
#include "kcopyd.h"
#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose build (V=1)

%if %{without kernel}
%undefine	with_dist_kernel
%endif

#
# main package.
#
%define		_rel	0.1
Summary:	DM-Cache: A Generic drivers-level Disk Cache
Name:		dmcache
Version:	0.1
Release:	%{_rel}
License:	GPL
Group:		Base/Kernel
# http://www.acis.ufl.edu/~ming/dmcache/patch-2.6.21
Patch0:		linux-%{name}.patch
URL:		http://www.acis.ufl.edu/~ming/dmcache/index.html
BuildRequires:	patchutils
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.20.2}
BuildRequires:	rpmbuild(macros) >= 1.379
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Dm-cache provides a generic drivers-level disk cache for storage
networking. It is built upon the Linux device-mapper, a generic drivers
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
filterdiff -x '*/Kconfig' -x '*/Makefile' %{PATCH0} | %{__patch} -p1
# prepare makefile:
cat > drivers/md/Makefile << EOF

obj-m += dm-cache.o

# XXX
CFLAGS += -I$(pwd)/../linux-2.6.22/drivers/md
EOF

%build
%if %{with userspace}
%endif

%if %{with kernel}
%build_kernel_modules -C drivers/md -m dm-cache
%endif

%install
rm -rf $RPM_BUILD_ROOT
%if %{with userspace}
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
%endif
