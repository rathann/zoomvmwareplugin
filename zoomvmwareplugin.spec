%define _enable_debug_packages %{nil}
%define debug_package          %{nil}
%global _build_id_links alldebug

%bcond_without bundled_qt5
%global bundled_qt_version 5.9.9

%global vdi_version 3.1.1

Summary: Zoom thin client plugin for VMware Horizon
Name: zoomvmwareplugin
Version: 5.2.456413.0902
Release: 1
URL: https://support.zoom.us/hc/en-us/articles/360031096531-Getting-Started-with-VDI
Source0: https://zoom.us/download/vdi/%{vdi_version}/zoomvmwareplugin-centos_64.rpm#/%{name}-%{version}.x86_64.rpm
License: Zoom
ExclusiveArch: x86_64
BuildRequires: chrpath
BuildRequires: crudini
BuildRequires: execstack
Requires: ca-certificates
Requires: libfaac.so.0()(64bit)
Requires: libmpg123.so.0()(64bit)
Requires: libturbojpeg.so.0()(64bit)
Requires: vmware-horizon-client-pcoip
Provides: bundled(libicu) = 56.1
%if %{with bundled_qt5}
Provides: bundled(qt5-qtbase) = %{bundled_qt_version}
Provides: bundled(qt5-qtbase-gui) = %{bundled_qt_version}
Provides: bundled(qt5-qtimageformats) = %{bundled_qt_version}
Provides: bundled(qt5-qtquickcontrols) = %{bundled_qt_version}
Provides: bundled(qt5-qtquickcontrols2) = %{bundled_qt_version}
Provides: bundled(qt5-qtscript) = %{bundled_qt_version}

# Qt5 cannot be unbundled as the application uses private APIs
%global __requires_exclude ^lib\(icu\(data\|i18n\|uc\)\|Qt5\(Core\|DBus\|Gui\|Network\|Qml\|Quick\|Script\|Svg\|Widgets\|XcbQpa\)\|vdpservice\)
%else
%global __requires_exclude ^lib\(icu\(data\|i18n\|uc\)\|vdpservice\)
%endif
%global __provides_exclude_from ^(%{_libdir}/%{name}|/usr/lib/vmware)

%description
Zoom, the cloud meeting company, unifies cloud video conferencing, simple online
meetings, and group messaging into one easy-to-use platform. Our solution offers
the best video, audio, and screen-sharing experience across Zoom Rooms, Windows
Mac, Linux, iOS, Android, and H.323/SIP room systems.

This package contains the thin client plugin for VMware Horizon.

%prep
%setup -qcT
rpm2cpio %{S:0} | \
    cpio --extract --make-directories --no-absolute-filenames --preserve-modification-time

pushd usr/lib/%{name}
chmod -x \
  *.pcm \
  *.pem \
  Qt*/{qmldir,*/*.qml} \

execstack -c zoom
chrpath -d zoom
rm -r \
%if ! %{with bundled_qt5}
  audio \
  egldeviceintegrations \
  generic \
  iconengines \
  imageformats \
  libQt5* \
  platforminputcontexts \
  platforms \
  platformthemes \
  Qt{,GraphicalEffects,Qml,Quick{,.2}} \
  qtdiag \
  xcbglintegrations \
%endif
  libfaac1.so \
  libmpg123.so \
  libturbojpeg.so* \
  getbssid.sh \
  zcacert.pem \

crudini --set qt.conf Paths Prefix %{_libdir}/%{name}
popd

pushd etc/vmware
for i in PATH LD_LIBRARY_PATH ; do
    crudini --set ZoomMediaVmware.ini ENV ${i} %{_libdir}/%{name}
done
crudini --set ZoomMediaVmware.ini OS OS_DISTRO fedora
popd

%build

%install
install -dm755 %{buildroot}{/etc/vmware,%{_libdir}/%{name},/usr/lib}
install -pm644 etc/vmware/ZoomMediaVmware.ini %{buildroot}/etc/vmware
cp -pr usr/lib/%{name} %{buildroot}%{_libdir}
cp -pr usr/lib/vmware %{buildroot}/usr/lib

ln -s ../libfaac.so.0 %{buildroot}%{_libdir}/%{name}/libfaac1.so
ln -s ../libmpg123.so.0 %{buildroot}%{_libdir}/%{name}/libmpg123.so
ln -s ../libturbojpeg.so.0 %{buildroot}%{_libdir}/%{name}/libturbojpeg.so
ln -s ../../bin/true %{buildroot}%{_libdir}/%{name}/getbssid.sh
ln -s ../../../etc/pki/tls/certs/ca-bundle.crt %{buildroot}%{_libdir}/%{name}/zcacert.pem

%files
/etc/vmware/ZoomMediaVmware.ini
%{_libdir}/%{name}
/usr/lib/vmware/view/vdpService/libZoomMediaVmware.so

%changelog
* Mon Sep 28 2020 Dominik Mierzejewski <rpm@greysector.net> 5.2.456413.0902-1
- initial build
- unbundle faac, mpg123 and turbojpeg
