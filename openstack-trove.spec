%global release_name juno
%global milestone 3
%global with_doc 0
%global project trove

Name:             openstack-%{project}
Version:          2014.2
Release:          0.4.b3%{?dist}
Summary:          OpenStack DBaaS (%{project})

Group:            Applications/System
License:          ASL 2.0
URL:              https://wiki.openstack.org/wiki/Trove
Source0:          https://launchpad.net/%{project}/%{release_name}/%{release_name}-%{milestone}/+download/%{project}-%{version}.b%{milestone}.tar.gz

Source1:          %{project}-dist.conf
Source2:          %{project}.logrotate
Source3:          guest_info

Source10:         %{name}-api.service
Source11:         %{name}-taskmanager.service
Source12:         %{name}-conductor.service
Source13:         %{name}-guestagent.service

Source20:         %{name}-api.init
Source21:         %{name}-taskmanager.init
Source22:         %{name}-conductor.init
Source23:         %{name}-guestagent.init
Source30:         %{name}-api.upstart
Source31:         %{name}-taskmanager.upstart
Source32:         %{name}-conductor.upstart
Source33:         %{name}-guestagent.upstart

Patch0:           version.diff
Patch1:           authtoken.diff
Patch2:           db-config.diff

Patch100:         el6-parallel-deps.diff

#
# patches_base=2014.2.b3
#

BuildArch:        noarch
BuildRequires:    intltool
%if 0%{?rhel} == 6
BuildRequires:    python-sphinx10
# These are required to build due to the requirements check added
BuildRequires:    python-paste-deploy1.5
BuildRequires:    python-routes1.12
BuildRequires:    python-sqlalchemy0.7
%endif
BuildRequires:    python-sphinx
BuildRequires:    python-setuptools
BuildRequires:    python-pbr
BuildRequires:    python-d2to1
BuildRequires:    python2-devel

Requires:         %{name}-api = %{version}-%{release}
Requires:         %{name}-taskmanager = %{version}-%{release}
Requires:         %{name}-conductor = %{version}-%{release}


%description
OpenStack DBaaS (codename %{project}) provisioning service.

%package common
Summary:          Components common to all OpenStack %{project} services
Group:            Applications/System

Requires:         python-%{project} = %{version}-%{release}

%if 0%{?rhel} == 6
Requires(post):   chkconfig
Requires(preun):  initscripts
Requires(preun):  chkconfig
%else
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd
BuildRequires:    systemd
%endif
Requires(pre):    shadow-utils

%description common
OpenStack DBaaS (codename %{project}) provisioning service.

This package contains scripts, config and dependencies shared
between all the OpenStack %{project} services.


%package api
Summary:          OpenStack %{project} API service
Group:            Applications/System

Requires:         %{name}-common = %{version}-%{release}

%description api
OpenStack DBaaS (codename %{project}) provisioning service.

This package contains the %{project} interface daemon.


%package taskmanager
Summary:          OpenStack %{project} taskmanager service
Group:            Applications/System

Requires:         %{name}-common = %{version}-%{release}

%description taskmanager
OpenStack DBaaS (codename %{project}) provisioning service.

This package contains the %{project} taskmanager service.


%package conductor
Summary:          OpenStack %{project} conductor service
Group:            Applications/System

Requires:         %{name}-common = %{version}-%{release}

%description conductor
OpenStack DBaaS (codename %{project}) provisioning service.

This package contains the %{project} conductor service.


%package guestagent
Summary:          OpenStack %{project} guest agent
Group:            Applications/System
%if 0%{?rhel}
Requires:         pexpect
%else
Requires:         python-pexpect
%endif

Requires:         %{name}-common = %{version}-%{release}

%description guestagent
OpenStack DBaaS (codename %{project}) provisioning service.

This package contains the %{project} guest agent service
that runs within the database VM instance.


%package -n       python-%{project}
Summary:          Python libraries for %{project}
Group:            Applications/System

Requires:         MySQL-python

Requires:         python-qpid
Requires:         python-kombu

Requires:         python-eventlet
Requires:         python-greenlet
Requires:         python-iso8601
Requires:         python-netaddr
Requires:         python-lxml

Requires:         python-webob >= 1.2
Requires:         python-migrate

%if 0%{?rhel} == 6
Requires:         python-sqlalchemy0.7
Requires:         python-paste-deploy1.5
Requires:         python-routes1.12
Requires:         python-argparse
%else
Requires:         python-sqlalchemy
Requires:         python-paste-deploy
Requires:         python-routes
%endif

Requires:         python-troveclient
Requires:         python-novaclient
Requires:         python-cinderclient
Requires:         python-heatclient
Requires:         python-swiftclient
Requires:         python-keystoneclient >= 0.4.1

Requires:         python-oslo-config >= 1:1.2.1
Requires:         python-jsonschema
Requires:         python-babel
Requires:         python-jinja2

Requires:         python-httplib2
Requires:         python-passlib


%description -n   python-%{project}
OpenStack DBaaS (codename %{project}) provisioning service.

This package contains the %{project} python library.

%if 0%{?with_doc}
%package doc
Summary:          Documentation for OpenStack %{project}
Group:            Documentation


%description      doc
OpenStack DBaaS (codename %{project}) provisioning service.

This package contains documentation files for %{project}.
%endif

%prep
%setup -q -n %{project}-%{version}

%patch0 -p1
%patch1 -p1
%patch2 -p1

%if 0%{?rhel} == 6
%patch100 -p1
%endif

# Avoid non-executable-script rpmlint while maintaining timestamps
find %{project} -name \*.py |
while read source; do
  if head -n1 "$source" | grep -F '/usr/bin/env'; then
    touch --ref="$source" "$source".ts
    sed -i '/\/usr\/bin\/env python/{d;q}' "$source"
    touch --ref="$source".ts "$source"
    rm "$source".ts
  fi
done

sed -i 's/REDHATVERSION/%{version}/; s/REDHATRELEASE/%{release}/' %{project}/version.py

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
rm -rf {test-,}requirements.txt

%build
%{__python} setup.py build

# Programmatically update defaults in sample config
# which is installed at /etc/trove/trove.conf

#  First we ensure all values are commented in appropriate format.
#  Since icehouse, there was an uncommented keystone_authtoken section
#  at the end of the file which mimics but also conflicted with our
#  distro editing that had been done for many releases.
sed -i '/^[^#[]/{s/^/#/; s/ //g}; /^#[^ ]/s/ = /=/' etc/%{project}/%{project}.conf.sample

#  TODO: Make this more robust
#  Note it only edits the first occurance, so assumes a section ordering in sample
#  and also doesn't support multi-valued variables like dhcpbridge_flagfile.
while read name eq value; do
  test "$name" && test "$value" || continue
  sed -i "0,/^# *$name=/{s!^# *$name=.*!#$name=$value!}" etc/%{project}/%{project}.conf.sample
done < %{SOURCE1}

%install
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

# docs generation requires everything to be installed first
export PYTHONPATH="$( pwd ):$PYTHONPATH"

%if 0%{?with_doc}
pushd doc

SPHINX_DEBUG=1 sphinx-build -b html source build/html
# Fix hidden-file-or-dir warnings
rm -fr build/html/.doctrees build/html/.buildinfo

# Create dir link to avoid a sphinx-build exception
mkdir -p build/man/.doctrees/
ln -s .  build/man/.doctrees/man
SPHINX_DEBUG=1 sphinx-build -b man -c source source/man build/man
mkdir -p %{buildroot}%{_mandir}/man1
install -p -D -m 644 build/man/*.1 %{buildroot}%{_mandir}/man1/

popd
%endif

# Setup directories
%if 0%{?rhel} != 6
install -d -m 755 %{buildroot}%{_unitdir}
%endif
install -d -m 755 %{buildroot}%{_datadir}/%{project}
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{project}
install -d -m 755 %{buildroot}%{_localstatedir}/log/%{project}

# Install config files
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_datadir}/%{project}/%{project}-dist.conf
install -p -D -m 644 etc/%{project}/api-paste.ini %{buildroot}%{_datadir}/%{project}/%{project}-dist-paste.ini
install -d -m 755 %{buildroot}%{_sysconfdir}/%{project}
install -p -D -m 640 etc/%{project}/%{project}.conf.sample %{buildroot}%{_sysconfdir}/%{project}/%{project}.conf
install -p -D -m 640 etc/%{project}/trove-taskmanager.conf.sample %{buildroot}%{_sysconfdir}/%{project}/trove-taskmanager.conf
install -p -D -m 640 etc/%{project}/trove-conductor.conf.sample %{buildroot}%{_sysconfdir}/%{project}/trove-conductor.conf
install -p -D -m 640 etc/%{project}/trove-guestagent.conf.sample %{buildroot}%{_sysconfdir}/%{project}/trove-guestagent.conf
install -p -D -m 640 %{SOURCE3} %{buildroot}%{_sysconfdir}/%{project}/guest_info

# Install initscripts
%if 0%{?rhel} == 6
install -p -D -m 755 %{SOURCE20} %{buildroot}%{_initrddir}/%{name}-api
install -p -D -m 755 %{SOURCE21} %{buildroot}%{_initrddir}/%{name}-taskmanager
install -p -D -m 755 %{SOURCE22} %{buildroot}%{_initrddir}/%{name}-conductor
install -p -D -m 755 %{SOURCE23} %{buildroot}%{_initrddir}/%{name}-guestagent
install -p -m 755 %{SOURCE30} %{SOURCE31} %{SOURCE32} %{SOURCE33} %{buildroot}%{_datadir}/%{project}
%else
install -p -m 644 %{SOURCE10} %{SOURCE11} %{SOURCE12} %{SOURCE13} %{buildroot}%{_unitdir}
%endif

# Install logrotate
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

# Install pid directory
install -d -m 755 %{buildroot}%{_localstatedir}/run/%{project}

# Remove unneeded in production stuff
rm -fr %{buildroot}%{_bindir}/trove-fake-mode
rm -fr %{buildroot}%{python_sitelib}/%{project}/tests/
rm -fr %{buildroot}%{python_sitelib}/run_tests.*

%pre common
# Origin: http://fedoraproject.org/wiki/Packaging:UsersAndGroups#Dynamic_allocation
USERNAME=%{project}
GROUPNAME=$USERNAME
HOMEDIR=%{_sharedstatedir}/$USERNAME
getent group $GROUPNAME >/dev/null || groupadd -r $GROUPNAME
getent passwd $USERNAME >/dev/null || \
  useradd -r -g $GROUPNAME -G $GROUPNAME -d $HOMEDIR -s /sbin/nologin \
    -c "$USERNAME Daemons" $USERNAME
exit 0

%if 0%{?rhel} == 6
%post api
/sbin/chkconfig --add %{name}-api
%post taskmanager
/sbin/chkconfig --add %{name}-taskmanager
%post conductor
/sbin/chkconfig --add %{name}-conductor
%post guestagent
/sbin/chkconfig --add %{name}-guestagent

%preun api
if [ $1 = 0 ] ; then
  /sbin/service %{name}-api stop >/dev/null 2>&1
  /sbin/chkconfig --del %{name}-api
fi
%preun taskmanager
if [ $1 = 0 ] ; then
  /sbin/service %{name}-taskmanager stop >/dev/null 2>&1
  /sbin/chkconfig --del %{name}-taskmanager
fi
%preun conductor
if [ $1 = 0 ] ; then
  /sbin/service %{name}-conductor stop >/dev/null 2>&1
  /sbin/chkconfig --del %{name}-conductor
fi
%preun guestagent
if [ $1 = 0 ] ; then
  /sbin/service %{name}-guestagent stop >/dev/null 2>&1
  /sbin/chkconfig --del %{name}-guestagent
fi

%postun api
if [ $1 -ge 1 ] ; then
  # Package upgrade, not uninstall
  /sbin/service %{name}-api condrestart > /dev/null 2>&1 || :
fi
%postun taskmanager
if [ $1 -ge 1 ] ; then
  # Package upgrade, not uninstall
  /sbin/service %{name}-taskmanager condrestart > /dev/null 2>&1 || :
fi
%postun conductor
if [ $1 -ge 1 ] ; then
  # Package upgrade, not uninstall
  /sbin/service %{name}-conductor condrestart > /dev/null 2>&1 || :
fi
%postun guestagent
if [ $1 -ge 1 ] ; then
  # Package upgrade, not uninstall
  /sbin/service %{name}-guestagent condrestart > /dev/null 2>&1 || :
fi

%else

%post api
%systemd_post openstack-trove-api.service
%post taskmanager
%systemd_post openstack-trove-taskmanager.service
%post conductor
%systemd_post openstack-trove-conductor.service
%post guestagent
%systemd_post openstack-trove-guestagent.service

%preun api
%systemd_preun openstack-trove-api.service
%preun taskmanager
%systemd_preun openstack-trove-taskmanager.service
%preun conductor
%systemd_preun openstack-trove-conductor.service
%preun guestagent
%systemd_preun openstack-trove-guestagent.service

%postun api
%systemd_postun_with_restart openstack-trove-api.service
%postun taskmanager
%systemd_postun_with_restart openstack-trove-taskmanager.service
%postun conductor
%systemd_postun_with_restart openstack-trove-conductor.service
%postun guestagent
%systemd_postun_with_restart openstack-trove-guestagent.service
%endif

%files
%doc LICENSE

%files common
%doc LICENSE
%dir %{_sysconfdir}/%{project}
%config(noreplace) %attr(0640, root, %{project}) %{_sysconfdir}/%{project}/%{project}.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}

%dir %attr(0755, %{project}, root) %{_localstatedir}/log/%{project}
%dir %attr(0755, %{project}, root) %{_localstatedir}/run/%{project}

%{_bindir}/%{project}-manage
%{_bindir}/trove-mgmt-taskmanager

%{_datarootdir}/%{project}

%defattr(-, %{project}, %{project}, -)
%dir %{_sharedstatedir}/%{project}

%files api
%{_bindir}/%{project}-api
%if 0%{?rhel} == 6
%{_initrddir}/%{name}-api
%{_datadir}/%{project}/%{name}-api.upstart
%else
%{_unitdir}/%{name}-api.service
%endif

%files taskmanager
%{_bindir}/%{project}-taskmanager
%if 0%{?rhel} == 6
%{_initrddir}/%{name}-taskmanager
%{_datadir}/%{project}/%{name}-taskmanager.upstart
%else
%{_unitdir}/%{name}-taskmanager.service
%endif
%config(noreplace) %attr(0640, root, %{project}) %{_sysconfdir}/%{project}/%{project}-taskmanager.conf

%files conductor
%{_bindir}/%{project}-conductor
%if 0%{?rhel} == 6
%{_initrddir}/%{name}-conductor
%{_datadir}/%{project}/%{name}-conductor.upstart
%else
%{_unitdir}/%{name}-conductor.service
%endif
%config(noreplace) %attr(0640, root, %{project}) %{_sysconfdir}/%{project}/%{project}-conductor.conf

%files guestagent
%{_bindir}/%{project}-guestagent
%if 0%{?rhel} == 6
%{_initrddir}/%{name}-guestagent
%{_datadir}/%{project}/%{name}-guestagent.upstart
%else
%{_unitdir}/%{name}-guestagent.service
%endif
%config(noreplace) %attr(0640, root, %{project}) %{_sysconfdir}/%{project}/%{project}-guestagent.conf
%config(noreplace) %attr(0640, root, %{project}) %{_sysconfdir}/%{project}/guest_info

%files -n python-%{project}
%defattr(-,root,root,-)
%doc LICENSE
%{python_sitelib}/%{project}
%{python_sitelib}/%{project}-%{version}*.egg-info

%if 0%{?with_doc}
%files doc
%doc LICENSE doc/build/html
%endif

%changelog
* Thu Sep 18 2014 Haikel Guemar <hguemar@fedoraproject.org> 2014.2-0.4.b3
- Update to upstream 2014.2.b3

* Tue Jun 24 2014 Pádraig Brady <pbrady@redhat.com> - 2014.1-6
- Use more up to date build dependencies for systemd

* Mon Jun 16 2014 Pádraig Brady <pbrady@redhat.com> - 2014.1-4
- Have guestagent reference /etc/guest_info
- Require correct version of python-oslo-config

* Wed May 21 2014 Pádraig Brady <pbrady@redhat.com> - 2014.1-3
- Tweaks for fedora review

* Sun Apr 27 2014 Pádraig Brady <pbrady@redhat.com> - 2014.1-2
- Have guestagent reference /etc/guest-info

* Fri Apr 18 2014 Pádraig Brady <pbrady@redhat.com> - 2014.1-1
- Update to Icehouse release

* Mon Apr 07 2014 Pádraig Brady <pbrady@redhat.com> - 2014.1-0.1.rc1
- Initial release
