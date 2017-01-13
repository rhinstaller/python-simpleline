%global srcname simpleline
%global sum A Python3 library for creating text UI

Summary: %{sum}
Name: python3-%{srcname}
Url: https://github.com/rhinstaller/python-%{srcname}
Version: 0.1
Release: 1%{?dist}
# This is a Red Hat maintained package which is specific to
# our distribution.  Thus the source is only available from
# within this srpm.
# This tarball was created from upstream git:
#   git clone https://github.com/rhinstaller/simpleline
#   cd simpleline && make archive
Source0: https://github.com/rhinstaller/python-%{srcname}/archive/%{srcname}-%{version}.tar.gz

License: GPLv2+
Group: System Environment/Libraries
BuildArch: noarch
BuildRequires: python3-devel
BuildRequires: gettext
BuildRequires: python3-setuptools
BuildRequires: intltool
BuildRequires: python3-pocketlint

Requires: rpm-python3

%{?python_provide:%python_provide python3-%{srcname}}

%description
Simpleline is a Python3 library for creating text UI.
It is designed to be used with line-based machines
and tools (e.g. serial console) so that every new line
is appended to the bottom of the screen.
Printed lines are never rewritten!

%prep
%setup -q -n %{srcname}-%{version}

%build
make

%check
make test

%install
make DESTDIR=%{buildroot} install

%find_lang python-%{srcname}

%clean
rm -rf %{buildroot}

%files -f python-%{srcname}.lang
%license COPYING
%doc ChangeLog README.md
%{python3_sitelib}/*

%changelog
* Fri Dec 16 2016 Jiri Konecny <jkonecny@redhat.com> - 0.1-1
- Initial package
