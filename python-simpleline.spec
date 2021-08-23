%global srcname simpleline

Name: python-%{srcname}
Summary: A Python library for creating text UI
Url: https://github.com/rhinstaller/python-%{srcname}
Version: 1.8.1
Release: 1%{?dist}
# This tarball was created from upstream git:
#   git clone https://github.com/rhinstaller/python-simpleline
#   cd python-simpleline && make archive
Source0: https://github.com/rhinstaller/python-%{srcname}/releases/download/%{version}/%{srcname}-%{version}.tar.gz

License: LGPLv3+
BuildArch: noarch
BuildRequires: make
BuildRequires: python3-devel
BuildRequires: gettext
BuildRequires: python3-setuptools
BuildRequires: intltool
BuildRequires: python3-gobject-base

%description
Simpleline is a Python library for creating text UI.
It is designed to be used with line-based machines
and tools (e.g. serial console) so that every new line
is appended to the bottom of the screen.
Printed lines are never rewritten!


%package -n python3-%{srcname}
Summary: A Python3 library for creating text UI
Requires: rpm-python3

%{?python_provide:%python_provide python3-%{srcname}}

%description -n python3-%{srcname}
Simpleline is a Python3 library for creating text UI.
It is designed to be used with line-based machines
and tools (e.g. serial console) so that every new line
is appended to the bottom of the screen.
Printed lines are never rewritten!

%prep
%setup -q -n %{srcname}-%{version}

%build
%make_build

%install
make DESTDIR=%{buildroot} install
%find_lang python-%{srcname}

%check
make test


%files -n python3-%{srcname} -f python-%{srcname}.lang
%license LICENSE.md
%doc ChangeLog README.md
%{python3_sitelib}/*

%changelog
