%global selinuxtype targeted
%global selinux_policyver 3.14.3-22
%global modulename python3-validity

%global pypi_name validity
%define _unitdir %{_exec_prefix}/lib/systemd/system

Name:           python-%{pypi_name}
Version:        0.18
Release:        1%{?dist}
Summary:        Validity fingerprint sensor driver

License:        MIT
URL:            https://github.com/bmanuel/%{name}
Source0:        %{name}-%{version}.tar.xz
BuildArch:      noarch

Requires:       selinux-policy >= %{selinux_policyver}
BuildRequires:  selinux-policy
BuildRequires:  selinux-policy-devel
BuildRequires:  selinux-policy-%{selinuxtype}
# must be in copr builds
BuildRequires:  systemd-rpm-macros
Requires(post): selinux-policy-base >= %{selinux_policyver}

%description
Validity fingerprint sensor driver.


%package -n python3-%{pypi_name}
Summary:        %{summary}

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  policycoreutils
BuildRequires:  checkpolicy
BuildRequires:  bzip2
Requires:       policycoreutils
Requires:       innoextract
Requires:       open-fprintd
%{?python_provide:%python_provide python3-%{pypi_name}}

%description -n python3-%{pypi_name}
Validity fingerprint sensor driver.

%prep
%autosetup -n %{name}-%{version} -p1

%build
%py3_build

cd selinux
checkmodule -M -m -o python3-validity.mod python3-validity.te
semodule_package -o python3-validity.pp -m python3-validity.mod
bzip2 python3-validity.pp
cd ..

%pre
%selinux_relabel_pre -s %{selinuxtype}

%install
%py3_install

install -d -m 0700 %{buildroot}%{_sysconfdir}/python-validity
install -d -m 0755 %{buildroot}%{_unitdir}/
install -d -m 0755 %{buildroot}%{_prefix}/lib/udev/rules.d
install -d -m 0755 %{buildroot}%{_datadir}/selinux/packages

install -m 0600 etc/python-validity/dbus-service.yaml %{buildroot}%{_sysconfdir}/python-validity/
install -m 0644 debian/python3-validity.service %{buildroot}%{_unitdir}/
install -m 0644 debian/python3-validity-restart-after-resume.service %{buildroot}%{_unitdir}/
install -m 0644 debian/python3-validity.udev %{buildroot}%{_prefix}/lib/udev/rules.d/40-python3-validity.udev
install -m 0644 selinux/python3-validity.pp.bz2 %{buildroot}%{_datadir}/selinux/packages/

%post -n python3-%{pypi_name}
%selinux_modules_install -s %{selinuxtype} %{_datadir}/selinux/packages/%{modulename}.pp.bz2
validity-sensors-firmware || true
systemctl daemon-reload
udevadm control --reload-rules 
udevadm trigger
%systemd_post python3-validity.service python3-validity-restart-after-resume.service

%preun -n python3-%{pypi_name}
%systemd_preun python3-validity.service python3-validity-restart-after-resume.service

%postun -n python3-%{pypi_name}
%systemd_postun_with_restart python3-validity.service python3-validity-restart-after-resume.service
if [ $1 -eq 0 ]; then
    %selinux_modules_uninstall -s %{selinuxtype} %{modulename}
fi

%posttrans
%selinux_relabel_post -s %{selinuxtype}

%files -n python3-%{pypi_name}
%doc README.md
%license LICENSE
%config(noreplace) %{_sysconfdir}/python-validity/dbus-service.yaml
%{_prefix}/lib/systemd/system/python3-validity.service
%{_prefix}/lib/systemd/system/python3-validity-restart-after-resume.service
%{_prefix}/lib/udev/rules.d/40-python3-validity.udev
%{python3_sitelib}/validitysensor/
%{python3_sitelib}/python_%{pypi_name}-%{version}-py*.egg-info/
%{_bindir}/validity-led-dance
%{_bindir}/validity-sensors-firmware
%{_exec_prefix}/lib/%{name}/dbus-service
%{_datadir}/dbus-1/system.d/io.github.uunicorn.Fprint.conf
%{_datadir}/%{name}/
%{_datadir}/selinux/packages/python3-validity.pp.bz2

%changelog
* Sun Oct 22 2023 Benjamin Manuel <ben@benmanuel.com> 0.18-1
- Get copr release working 

* Sun Oct 22 2023 Benjamin Manuel <ben@benmanuel.com>
- 

* Sun Oct 22 2023 Benjamin Manuel <ben@benmanuel.com> 0.16-1
- 

* Sat Oct 21 2023 Benjamin Manuel <ben@benmanuel.com> 0.17-1
- new package built with tito

* Sat Oct 21 2023 Benjamin Manuel <ben@benmanuel.com> - 0.16-1
Update to latest commit to allow Silverblue insallation
