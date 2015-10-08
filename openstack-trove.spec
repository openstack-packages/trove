%global release_name liberty
%global project trove
%global milestone .0rc2
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%global with_doc 0

Name:             openstack-%{project}
Epoch:            1
Version:          4.0.0
Release:          0.1%{?milestone}%{?dist}
Summary:          OpenStack DBaaS (%{project})

License:          ASL 2.0
URL:              https://wiki.openstack.org/wiki/Trove
Source0:          https://launchpad.net/%{project}/%{release_name}/%{release_name}-rc2/+download/%{project}-%{upstream_version}.tar.gz

Source1:          %{project}-dist.conf
Source2:          %{project}.logrotate
Source3:          guest_info

Source10:         %{name}-api.service
Source11:         %{name}-taskmanager.service
Source12:         %{name}-conductor.service
Source13:         %{name}-guestagent.service

BuildArch:        noarch
BuildRequires:    python2-devel
BuildRequires:    python-setuptools
BuildRequires:    python-pbr
BuildRequires:    python-d2to1
BuildRequires:    python-sphinx
BuildRequires:    intltool

Requires:         %{name}-api = %{epoch}:%{version}-%{release}
Requires:         %{name}-taskmanager = %{epoch}:%{version}-%{release}
Requires:         %{name}-conductor = %{epoch}:%{version}-%{release}


%description
OpenStack DBaaS (codename %{project}) provisioning service.

%package common
Summary:          Components common to all OpenStack %{project} services

Requires:         python-%{project} = %{epoch}:%{version}-%{release}

Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd
BuildRequires:    systemd

Requires(pre):    shadow-utils
Requires:         python-pbr

%description common
OpenStack DBaaS (codename %{project}) provisioning service.

This package contains scripts, config and dependencies shared
between all the OpenStack %{project} services.


%package api
Summary:          OpenStack %{project} API service
Requires:         %{name}-common = %{epoch}:%{version}-%{release}

%description api
OpenStack DBaaS (codename %{project}) provisioning service.

This package contains the %{project} interface daemon.


%package taskmanager
Summary:          OpenStack %{project} taskmanager service
Requires:         %{name}-common = %{epoch}:%{version}-%{release}

%description taskmanager
OpenStack DBaaS (codename %{project}) provisioning service.

This package contains the %{project} taskmanager service.


%package conductor
Summary:          OpenStack %{project} conductor service
Requires:         %{name}-common = %{epoch}:%{version}-%{release}

%description conductor
OpenStack DBaaS (codename %{project}) provisioning service.

This package contains the %{project} conductor service.


%package guestagent
Summary:          OpenStack %{project} guest agent
%if 0%{?rhel}
Requires:         pexpect
%else
Requires:         python-pexpect
%endif
Requires:         python-netifaces

Requires:         %{name}-common = %{epoch}:%{version}-%{release}

%description guestagent
OpenStack DBaaS (codename %{project}) provisioning service.

This package contains the %{project} guest agent service
that runs within the database VM instance.


%package -n       python-%{project}
Summary:          Python libraries for %{project}

Requires:         MySQL-python

Requires:         python-kombu

Requires:         python-eventlet
Requires:         python-iso8601
Requires:         python-netaddr
Requires:         python-lxml
Requires:         python-six
Requires:         python-stevedore

Requires:         python-webob >= 1.2
Requires:         python-migrate

Requires:         python-sqlalchemy
Requires:         python-paste
Requires:         python-paste-deploy
Requires:         python-routes

Requires:         python-troveclient
Requires:         python-novaclient
Requires:         python-cinderclient
Requires:         python-heatclient
Requires:         python-swiftclient
Requires:         python-keystoneclient >= 0.4.1
Requires:         python-keystonemiddleware
Requires:         python-designateclient
Requires:         python-neutronclient

Requires:         python-oslo-config >= 1:1.2.1
Requires:         python-oslo-concurrency
Requires:         python-oslo-messaging
Requires:         python-oslo-context
Requires:         python-oslo-i18n
Requires:         python-oslo-serialization
Requires:         python-oslo-service
Requires:         python-oslo-utils
Requires:         python-oslo-log

Requires:         python-osprofiler
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


%description      doc
OpenStack DBaaS (codename %{project}) provisioning service.

This package contains documentation files for %{project}.
%endif

%prep
%autosetup -n %{project}-%{upstream_version} -S git

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

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
rm -rf {test-,}requirements.txt

%build
%{__python2} setup.py build

%install
%{__python2} setup.py install -O1 --skip-build --root %{buildroot}

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
install -d -m 750 %{buildroot}%{_localstatedir}/log/%{project}

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


%files
%license LICENSE

%files common
%license LICENSE
%dir %{_sysconfdir}/%{project}
%config(noreplace) %attr(0640, root, %{project}) %{_sysconfdir}/%{project}/%{project}.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}

%dir %attr(0750, %{project}, root) %{_localstatedir}/log/%{project}
%dir %attr(0755, %{project}, root) %{_localstatedir}/run/%{project}

%{_bindir}/%{project}-manage
%{_bindir}/trove-mgmt-taskmanager

%{_datarootdir}/%{project}

%defattr(-, %{project}, %{project}, -)
%dir %{_sharedstatedir}/%{project}

%files api
%{_bindir}/%{project}-api
%{_unitdir}/%{name}-api.service

%files taskmanager
%{_bindir}/%{project}-taskmanager
%{_unitdir}/%{name}-taskmanager.service
%config(noreplace) %attr(0640, root, %{project}) %{_sysconfdir}/%{project}/%{project}-taskmanager.conf

%files conductor
%{_bindir}/%{project}-conductor
%{_unitdir}/%{name}-conductor.service
%config(noreplace) %attr(0640, root, %{project}) %{_sysconfdir}/%{project}/%{project}-conductor.conf

%files guestagent
%{_bindir}/%{project}-guestagent
%{_unitdir}/%{name}-guestagent.service
%config(noreplace) %attr(0640, root, %{project}) %{_sysconfdir}/%{project}/%{project}-guestagent.conf
%config(noreplace) %attr(0640, root, %{project}) %{_sysconfdir}/%{project}/guest_info

%files -n python-%{project}
%license LICENSE
%{python_sitelib}/%{project}
%{python_sitelib}/%{project}-%{version}*.egg-info

%if 0%{?with_doc}
%files doc
%license LICENSE
%doc doc/build/html
%endif

%changelog
* Thu Oct 08 2015 Victoria Martinez de la Cruz <vkmc@fedoraproject.org> - 1:4.0.0-0.1.0rc2
- Update to upstream 4.0.0.0rc2

* Tue Oct 06 2015 Victoria Martinez de la Cruz <vkmc@fedoraproject.org> - 1:4.0.0-0.1.0rc1
- Update to upstream 4.0.0.0rc1
