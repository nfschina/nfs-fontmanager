Name:           nfs-fontmanager
Version:        1.0.11
Release:        2
Summary:        manager fonts

License:        GPL
URL:            http://www.nfschina.com/
Source0:        nfs-fontmanager-1.0.11.tar.gz


#add patch
Patch0:    FollowSystemPath.patch

#BuildRequires:  

Requires:       python3-pandas
Requires:       qt5-qtbase-devel
Requires:       qt5-qtbase
Requires:       python3-qt5-base
Requires:       python3-pyqt5-sip

%define debug_package %{nil}

%description
nfs-fontmanager is the system fonts manager and install or uninstall or check.

%prep
%setup -q
%patch0 -p1

%build

%install
#mkdir -p %{buildroot}/usr/bin
#mkdir -p %{buildroot}/usr/share/nfs-fontmanager
#%define _unpackaged_files_terminate_build 0
#cp -a %_builddir/nfs-fontmanager-1.0.11/* %{buildroot}/
install -d $RPM_BUILD_ROOT/
cp -a * $RPM_BUILD_ROOT/

%clean
rm -rf %{buildroot}

%files

/usr/bin/*
/usr/share/*

%post

%preun


%changelog
* Wed Jul 22 2020 hanxf <hanxiaofeng@cpu-os.ac.cn> - 1.0.11-2
- 字体安装、卸载路径跟随服务器系统默认路径
- FollowSystemPath.patch
* Fri Jul 17 2020 hanxf <hanxiaofeng@cpu-os.ac.cn> - 1.0.11
- First: fontmanager source code.


