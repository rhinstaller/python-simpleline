%global srcname simpleline

Summary: A python library for text UI framework
Name: python-simpleline
Url: https://github.com/rhinstaller/python-%{srcname}
Version: 0.1
Release: 1%{?dist}
# This is a Red Hat maintained package which is specific to
# our distribution.  Thus the source is only available from
# within this srpm.
# This tarball was created from upstream git:
#   git clone https://github.com/rhinstaller/simpleline
#   cd simpleline && make archive
Source0: https://github.com/rhinstaller/python-simpleline/archive/%{name}-%{version}.tar.gz

License: GPLv2+
Group: System Environment/Libraries
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: python3-devel
BuildRequires: gettext
BuildRequires: python3-setuptools
BuildRequires: intltool
BuildRequires: python3-pocketlint

Requires: rpm-python3
Requires: python3-meh

%{?python_provide:%python_provide python3-%{srcname}}

%description
The simpleline package is a python library for creating simpleline but powerful
text UI.

%prep
%setup -q

%build
make

%check
make test

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install

%find_lang %{name}

%clean
rm -rf %{buildroot}

%files -f %{name}.lang
%defattr(-,root,root,-)
%license COPYING
%doc ChangeLog README
%{python3_sitelib}/*

%changelog
* Fri Dec 16 2016 Jiri Konecny <jkonecny@redhat.com> - 0.1-1
- Initial package
