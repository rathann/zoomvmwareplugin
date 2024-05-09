%define _enable_debug_packages %{nil}
%define debug_package          %{nil}
%global _build_id_links alldebug

%bcond_without bundled_qt5
%global bundled_qt_version 5.15.11

%global vdi_version 5.14.15

Summary: Zoom thin client plugin for VMware Horizon
Name: zoomvmwareplugin
Version: %{vdi_version}.24580
Release: 1
URL: https://support.zoom.us/hc/en-us/articles/360031096531-Getting-Started-with-VDI
Source0: https://cdn.zoom.us/prod/vdi/%{version}/zoomvmwareplugin-centos_%{vdi_version}.rpm#/%{name}-%{version}.x86_64.rpm
License: Zoom
ExclusiveArch: x86_64
BuildRequires: chrpath
BuildRequires: crudini
BuildRequires: execstack
Requires: fdk-aac
Requires: libmpg123.so.0()(64bit)
Requires: libturbojpeg.so.0()(64bit)
Requires: vmware-horizon-client-pcoip
Provides: bundled(ffmpeg) = 4.2.7
Provides: bundled(libicu) = 56.1
Provides: bundled(openvino)
%if %{with bundled_qt5}
Provides: bundled(qt5-qtbase) = %{bundled_qt_version}
Provides: bundled(qt5-qtbase-gui) = %{bundled_qt_version}
Provides: bundled(qt5-qtimageformats) = %{bundled_qt_version}
Provides: bundled(qt5-qtquickcontrols) = %{bundled_qt_version}
Provides: bundled(qt5-qtquickcontrols2) = %{bundled_qt_version}
Provides: bundled(qt5-qtremoteobjects) = %{bundled_qt_version}
Provides: bundled(qt5-qtscript) = %{bundled_qt_version}
Provides: bundled(qt5-qtx11extras) = %{bundled_qt_version}

# Qt5 cannot be unbundled as the application uses private APIs
%global __requires_exclude ^lib\(avcodec\|avformat\|avutil\|swresample\|icu\(data\|i18n\|uc\)\|Qt5\(3D\(Animation\|Core\|Input\|Logic\|Quick\|QuickScene2D\|Render\)\|Bodymovin\|Concurrent\|Core\|DBus\|EglFSDeviceIntegration\|EglFsKmsSupport\|Gamepad\|Gui\|Multimedia\|Network\|Qml\|Quick\|RemoteObjects\|Script\|Sql\|Svg\|WaylandClient\|Widgets\|X11Extras\|XcbQpa\|XmlPatterns\)\|vdpservice\)
%else
%global __requires_exclude ^lib\(avcodec\|avformat\|avutil\|swresample\|icu\(data\|i18n\|uc\)\|vdpservice\)
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
find Qt/qml -type f -name qmldir -o -name *.qml | xargs chmod -x

chmod +x \
  libclDNN64.so \
  libmkldnn.so \
  libquazip.so \

execstack -c aomhost
for f in \
  zoom \
  libdvf.so \
  libquazip.so \
  Qt/lib/libicu{data,i18n,uc}.so.56 \
; do chrpath -d $f ; done
rm -r \
%if ! %{with bundled_qt5}
  Qt \
  libquazip.so \
  qt.conf \
%endif
  libfdkaac2.so \
  libmpg123.so \
  libOpenCL.so.1 \
  libturbojpeg.so* \
  getbssid.sh \

crudini --set qt.conf Paths Prefix %{_libdir}/%{name}
popd

pushd etc/zoomvdi
for i in PATH LD_LIBRARY_PATH ; do
    crudini --set ZoomMedia.ini ENV ${i} %{_libdir}/%{name}
done
crudini --set ZoomMedia.ini OS OS_DISTRO fedora
crudini --set ZoomMedia.ini FEATURE SMARTVB 1
popd

%build

%install
install -dm755 %{buildroot}{/etc/zoomvdi,%{_libdir}/%{name},/usr/lib}
install -pm644 etc/zoomvdi/ZoomMedia.ini %{buildroot}/etc/zoomvdi
cp -pr usr/lib/%{name} %{buildroot}%{_libdir}
cp -pr usr/lib/vmware %{buildroot}/usr/lib

ln -s ../fdk-aac/libfdk-aac.so.2 %{buildroot}%{_libdir}/%{name}/libfdkaac2.so
ln -s ../libmpg123.so.0 %{buildroot}%{_libdir}/%{name}/libmpg123.so
ln -s ../libturbojpeg.so.0 %{buildroot}%{_libdir}/%{name}/libturbojpeg.so
ln -s ../../bin/true %{buildroot}%{_libdir}/%{name}/getbssid.sh

%files
/etc/zoomvdi/ZoomMedia.ini
%{_libdir}/%{name}
/usr/lib/vmware/view/vdpService/libZoomMediaVmware.so

%changelog
* Thu May 09 2024 Dominik Mierzejewski <dominik@greysector.net> 5.14.15.24580-1
- update to VDI release 5.14.15
- update bundled components
- filter out bundled FFmpeg from Requires:

* Thu Oct 12 2023 Dominik Mierzejewski <dominik@greysector.net> 5.14.11.23790-1
- update to VDI release 5.14.11

* Tue May 23 2023 Dominik Mierzejewski <dominik@greysector.net> 5.13.1.22610-1
- update to VDI release 5.13.1

* Wed Nov 02 2022 Dominik Mierzejewski <dominik@greysector.net> 5.11.9.21750-1
- update to VDI release 5.11.9
- update Source URL

* Mon Nov 22 2021 Dominik Mierzejewski <rpm@greysector.net> 5.7.8.20826-1
- update to VDI release 5.7.8

* Mon Oct 25 2021 Dominik Mierzejewski <rpm@greysector.net> 5.7.6.20822-1
- update to VDI release 5.7.6
- unbundle OpenCL
- fix some file permissions

* Mon Oct 25 2021 Dominik Mierzejewski <rpm@greysector.net> 5.7.5.20811-1
- update to VDI release 5.7.5

* Wed Sep 15 2021 Dominik Mierzejewski <rpm@greysector.net> 5.7.0.20703-1
- update to VDI release 5.7.0

* Thu Jun 24 2021 Dominik Mierzejewski <rpm@greysector.net> 5.5.12716.0227-1
- update to 5.5.12716.0227 (VDI Release 5.5.4)
- drop faac
- certificates seem to be built into the binary now
- unbundle fdk-aac

* Mon Oct 05 2020 Dominik Mierzejewski <rpm@greysector.net> 5.2.470858.0930-1
- update to 5.2.470858.0930 (VDI release 3.1.3)

* Mon Sep 28 2020 Dominik Mierzejewski <rpm@greysector.net> 5.2.456413.0902-1
- initial build
- unbundle faac, mpg123 and turbojpeg
