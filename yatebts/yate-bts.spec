# to add a distro release tag run rpmbuild --define 'dist value'
# to add a revision tag run rpmbuild --define 'revision value'
# to create a debug info package run rpmbuild --define 'debuginfo 1'
# to suppress auto dependencies run rpmbuild --define 'nodeps 1'

%{!?dist:%define dist %{nil}}
%{!?revision:%define revision %{nil}}
%{?nodeps:%define no_auto_deps 1}

%{!?debuginfo:%define debuginfo %{nil}}
%if "%{debuginfo}"
%define stripped debug
%else
%define stripped strip
%define debug_package ${nil}
%endif

%if "%{revision}" == "svn"
%define revision 570svn
%endif

%if "%{dist}" == ""
%define dist %{?distsuffix:%distsuffix}%{?product_version:%product_version}
%endif
%if "%{dist}" == ""
%define dist %(test -f /etc/mageia-release && echo mga)
%endif
%if "%{dist}" == ""
%define dist %(test -f /etc/mandriva-release && echo mdv)
%endif
%if "%{dist}" == ""
%define dist %(test -f /etc/mandrake-release && echo mdk)
%endif
%if "%{dist}" == ""
%define dist %(test -f /etc/fedora-release && echo fc)
%endif
%if "%{dist}" == ""
%define dist %(grep -q ^CentOS /etc/issue && echo centos)
%endif
%if "%{dist}" == ""
%define dist %(test -f /etc/redhat-release && echo rh)
%endif
%if "%{dist}" == ""
%define dist %(test -f /etc/SuSE-release && echo suse)
%endif
%if "%{dist}" == "none"
%define dist %{nil}
%endif

Summary:	GSM BTS based on Yet Another Telephony Engine
Name:		yate-bts
Version: 	5.0.1
Release:	devel%{revision}1%{dist}
License:	GPL
Packager:	Paul Chitescu <paulc@null.ro>
Source:		http://yatebts.com/%{name}-%{version}-devel1.tar.gz
Group:		Applications/Communications
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root
URL:		http://yatebts.com/
BuildRequires:	gcc-c++
BuildRequires:	yate-devel >= 5.5.1
Requires:	yate = 5.5.1
Requires:	yate-gsm = 5.5.1
Requires:	yate-radio = 5.5.1
Conflicts:	yate-bts-transceiver

%define prefix	/usr
%define moddir	%{_libdir}/yate/server
%define btsdir	%{moddir}/bts


%description
Yate is a telephony engine designed to implement PBX and IVR solutions
for small to large scale projects.
This module implements a 2G GSM BTS for Yate.
At least one Yate radio device package must also be installed.

%files
%defattr(-, root, root)
%docdir %{_defaultdocdir}/%{name}-%{version}
%doc %{_defaultdocdir}/%{name}-%{version}/*
%dir %{btsdir}
%{moddir}/*.yate
%{btsdir}/mbts
%config(noreplace) %{_sysconfdir}/yate/ybts.conf

%post
if grep -q '^ *Radio.C0 *= *[0-9]' %{_sysconfdir}/yate/ybts.conf 2>/dev/null; then
    if [ -s /usr/lib/systemd/system/yate.service ]; then
        systemctl condrestart yate.service
    else
        if [ -s /etc/init.d/yate ]; then
            service yate condrestart
        fi
    fi
fi

%postun
if [ -s /usr/lib/systemd/system/yate.service ]; then
    systemctl condrestart yate.service
else
    if [ -s /etc/init.d/yate ]; then
        service yate condrestart
    fi
fi


%package nib
Summary:	GSM Network In a Box based on Yate-BTS
Group:		Applications/Communications
Requires:	%{name} = %{version}-%{release}
Requires:	yate-scripts = 5.5.1
Requires:	apache-mod_php
Requires(post):	gawk
Suggests:	pysim

%description nib
Scripts and support executables that implement a GSM Network In a Box.

%files nib
%defattr(-, root, root)
%dir %{_datadir}/yate/nib_web
%{_datadir}/yate/scripts/gsm_auth.sh
%{_datadir}/yate/scripts/do_*
%{_datadir}/yate/scripts/nib.js
%{_datadir}/yate/scripts/welcome.js
%{_datadir}/yate/scripts/custom_sms.js
%{_datadir}/yate/sounds/*
%{_datadir}/yate/nib_web/*
/var/www/html/nib
%config(noreplace) %{_datadir}/yate/nib_web/.htaccess
%config(noreplace) %{_datadir}/yate/nib_web/config.php
%config(noreplace) %{_sysconfdir}/yate/subscribers.conf

%post nib
sed -i 's/^ *\(roaming\|nib\) *=.*$/;; \0/' %{_sysconfdir}/yate/javascript.conf
if ! grep -q '; Installed by yate-bts-nib' %{_sysconfdir}/yate/javascript.conf 2>/dev/null; then
    if grep -q '^ *\[general\]' %{_sysconfdir}/yate/javascript.conf 2>/dev/null; then
	awk '/^ *\[/{sect=0}
	/^ *\[general\]/{sect=1}
	/^ *routing *=/{if(sect==2)sect=3}
	{if(sect==3){print ";; " $0;sect=2} else print;
	 if(sect==1){print "; Installed by yate-bts-nib, do not remove this comment line\nrouting=welcome.js\n";sect=2}
	}' <%{_sysconfdir}/yate/javascript.conf >%{_sysconfdir}/yate/javascript.conf.tmp
	mv -f %{_sysconfdir}/yate/javascript.conf.tmp %{_sysconfdir}/yate/javascript.conf
    else
	cat <<-EOF >>%{_sysconfdir}/yate/javascript.conf
	[general]
	; Installed by yate-bts-nib, do not remove this comment line
	routing=welcome.js

	EOF
    fi
fi
if ! grep -q '^ *mode *=' %{_sysconfdir}/yate/ybts.conf 2>/dev/null; then
    if grep -q '^ *\[ybts\]' %{_sysconfdir}/yate/ybts.conf 2>/dev/null; then
	awk '/^ *\[/{sect=0}
	/^ *\[ybts\]/{sect=1}
	/^ *mode *=/{if(sect==2)sect=3}
	{if(sect==3){print ";; " $0;sect=2} else print;
	 if(sect==1){print "; Installed by yate-bts-nib, do not remove this comment line\nmode=nib\n";sect=2}
	}' <%{_sysconfdir}/yate/ybts.conf >%{_sysconfdir}/yate/ybts.conf.tmp
	mv -f %{_sysconfdir}/yate/ybts.conf.tmp %{_sysconfdir}/yate/ybts.conf
    fi
fi
if ! grep -q '; Installed by yate-bts-nib' %{_sysconfdir}/yate/extmodule.conf 2>/dev/null; then
    if grep -q '^ *\[scripts\]' %{_sysconfdir}/yate/extmodule.conf 2>/dev/null; then
	awk '/^ *\[/{sect=0}
	/^ *\[scripts\]/{sect=1}
	/^ *gsm_auth\.sh/{if(sect==2)sect=3}
	{if(sect==3){print ";; " $0;sect=2} else print;
	 if(sect==1){print "; Installed by yate-bts-nib, do not remove this comment line\ngsm_auth.sh\n";sect=2}
	}' <%{_sysconfdir}/yate/extmodule.conf >%{_sysconfdir}/yate/extmodule.conf.tmp
	mv -f %{_sysconfdir}/yate/extmodule.conf.tmp %{_sysconfdir}/yate/extmodule.conf
    else
	cat <<-EOF >>%{_sysconfdir}/yate/extmodule.conf
	[scripts]
	; Installed by yate-bts-nib, do not remove this comment line
	gsm_auth.sh

	EOF
    fi
fi
chgrp -R apache %{_sysconfdir}/yate
chmod -R g+rw %{_sysconfdir}/yate


%package roaming
Summary:	SIP based GSM roaming support for Yate-BTS
Group:		Applications/Communications
Requires:	%{name} = %{version}-%{release}
Requires:	yate-scripts = 5.5.1
Requires(post):	gawk

%description roaming
Scripts that implement SIP registration from YateBTS to a remote OpenVoLTE server.

%files roaming
%defattr(-, root, root)
%{_datadir}/yate/scripts/roaming.js
%{_datadir}/yate/scripts/handover.js
%{_datadir}/yate/scripts/lib_str_util.js

%post roaming
sed -i 's/^ *\(roaming\|nib\) *=.*$/;; \0/' %{_sysconfdir}/yate/javascript.conf
if ! grep -q '^ *mode *=' %{_sysconfdir}/yate/ybts.conf 2>/dev/null; then
    if grep -q '^ *\[ybts\]' %{_sysconfdir}/yate/ybts.conf 2>/dev/null; then
	awk '/^ *\[/{sect=0}
	/^ *\[ybts\]/{sect=1}
	/^ *mode *=/{if(sect==2)sect=3}
	{if(sect==3){print ";; " $0;sect=2} else print;
	 if(sect==1){print "; Installed by yate-bts-roaming, do not remove this comment line\nmode=roaming\n";sect=2}
	}' <%{_sysconfdir}/yate/ybts.conf >%{_sysconfdir}/yate/ybts.conf.tmp
	mv -f %{_sysconfdir}/yate/ybts.conf.tmp %{_sysconfdir}/yate/ybts.conf
    fi
fi
if ! grep -q '; Installed by yate-bts-roaming +handover' %{_sysconfdir}/yate/ysipchan.conf 2>/dev/null; then
    mv -f -n %{_sysconfdir}/yate/ysipchan.conf %{_sysconfdir}/yate/ysipchan.conf.rpmold
    cat <<-EOF >%{_sysconfdir}/yate/ysipchan.conf
	; Installed by yate-bts-roaming +handover, do not remove this comment line

	[general]
	lazy100=yes
	transfer=no
	privacy=yes
	generate=yes
	rtp_start=yes
	auth_foreign=yes
	autochangeparty=yes
	update_target=yes
	body_encoding=hex
	async_generic=yes
	sip_req_trans_count=5
	useragent=YateBTS/5.0.1

	[codecs]
	default=disable
	gsm=enable

	[message]
	enable=yes
	auth_required=false

	[options]
	enable=no

	[methods]
	options=no
	info=no

	EOF
fi


%prep
%setup -q -n %{name}

%define local_find_requires %{_builddir}/%{name}/local-find-requires
#
%{__cat} <<EOF >%{local_find_requires}
#! /bin/sh
grep -v '\.yate$' | %{__find_requires} | grep -v '^\(perl\|pear\)'
exit 0
EOF
#
chmod +x %{local_find_requires}
%define __find_requires %{local_find_requires}

%if "%{no_auto_deps}" == "1"
%define local_find_provides %{_builddir}/%{name}/local-find-provides
#
%{__cat} <<EOF >%{local_find_provides}
#! /bin/sh
%{__find_provides} | grep -v '\.yate$'
exit 0
EOF
#
chmod +x %{local_find_provides}
%define _use_internal_dependency_generator 0
%define __find_provides %{local_find_provides}
%define __perl_requires /bin/true
%endif

%build
./configure --prefix=%{prefix} --sysconfdir=/etc --mandir=%{prefix}/share/man
make %{stripped}

%install
make install DESTDIR=%{buildroot}
mkdir -p %{buildroot}/var/www/html
ln -sf %{_datadir}/yate/nib_web %{buildroot}/var/www/html/nib

%clean
rm -rf %{buildroot}

%changelog
* Mon Aug 24 2015 Paul Chitescu <paulc@null.ro>
- Removed hardware support subpackages

* Thu Apr 24 2014 Paul Chitescu <paulc@null.ro>
- Added bladerf subpackage

* Mon Mar 17 2014 Paul Chitescu <paulc@null.ro>
- Added NIB Web interface files

* Mon Dec 09 2013 Paul Chitescu <paulc@null.ro>
- Created specfile
