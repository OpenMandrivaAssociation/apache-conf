%if %mandriva_branch == Cooker
# Cooker
%define release 8
%else
# Old distros
%define subrel 1
%define release 7
%endif

Summary:	Configuration files for Apache
Name:		apache-conf
Version:	2.2.22
Release:	%release
License:	Apache License
Group:		System/Servers
URL:		http://www.mandriva.com
Source1:	httpd.init
Source2:	httpd.sysconf
Source3:	httpd.conf
Source4:	fileprotector.conf
Source5:	magic
Source6:	mime.types
Source7:	index.html
Source8:	advxsplitlogfile.pl
Source9:	advxsplitlogfile.c
Source10:	robots.txt
Source11:	00_default_vhosts.conf
Source12:	mod_ssl-gentestcrt.sh
Source13:	apache-2.0.40-testscript.pl
Source14:	http://www.mandriva.com/files/mandriva_customer_favicon.ico
Source15:	webapp.script
Requires:	lynx >= 2.8.5
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
This package contains configuration files for apache. It is necessary for
operation of the apache webserver. Having those files into a separate modules
provides better customization for OEMs and ISPs, who can modify the look and
feel of the apache webserver without having to re-compile the whole suite to
change a logo or config file.

%prep

%setup -T -c -q -n %{name}-%{version}

cp %{SOURCE1} .
cp %{SOURCE2} .
cp %{SOURCE3} .
cp %{SOURCE4} .
cp %{SOURCE5} .
cp %{SOURCE6} .
cp %{SOURCE7} .
cp %{SOURCE8} .
cp %{SOURCE9} .
cp %{SOURCE10} .
cp %{SOURCE11} .
cp %{SOURCE12} .
cp %{SOURCE13} .
cp %{SOURCE14} favicon.ico

%build
%serverbuild

gcc $CFLAGS -o advxsplitlogfile advxsplitlogfile.c

%install
rm -rf %{buildroot}

# don't fiddle with the initscript!
export DONT_GPRINTIFY=1

install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_sbindir}
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d
install -d %{buildroot}%{_sysconfdir}/httpd/conf.d
install -d %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d
install -d %{buildroot}%{_sysconfdir}/httpd/conf/vhosts.d
install -d %{buildroot}%{_sysconfdir}/httpd/conf/addon-modules
install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -d %{buildroot}%{_sysconfdir}/sysconfig

install -d %{buildroot}/var/log/httpd
install -d %{buildroot}/var/www/cgi-bin
install -d %{buildroot}/var/www/html/addon-modules
install -d %{buildroot}/var/www/icons
install -d %{buildroot}/var/www/perl

install -m0755 advxsplitlogfile %{buildroot}%{_sbindir}/advxsplitlogfile
install -m0755 advxsplitlogfile.pl %{buildroot}%{_sbindir}/advxsplitlogfile.pl
install -m0755 apache-2.0.40-testscript.pl %{buildroot}/var/www/cgi-bin/test.cgi
install -m0755 apache-2.0.40-testscript.pl %{buildroot}/var/www/perl/test.pl
install -m0755 httpd.init %{buildroot}%{_initrddir}/httpd
install -m0755 mod_ssl-gentestcrt.sh %{buildroot}%{_sbindir}/mod_ssl-gentestcrt

# make some dangling soft links 
pushd %{buildroot}%{_sysconfdir}/httpd
    ln -s ../../usr/%{_lib} %{_lib}
    ln -s ../../var/log/httpd logs
    ln -s ../../usr/%{_lib}/apache modules
    ln -s ../../usr/%{_lib}/apache-extramodules extramodules
popd

# config files
install -m0644 httpd.conf %{buildroot}%{_sysconfdir}/httpd/conf/httpd.conf
install -m0644 fileprotector.conf %{buildroot}%{_sysconfdir}/httpd/conf/fileprotector.conf
install -m0644 mime.types %{buildroot}%{_sysconfdir}/httpd/conf/mime.types
install -m0644 magic %{buildroot}%{_sysconfdir}/httpd/conf/magic
install -m0644 httpd.sysconf %{buildroot}%{_sysconfdir}/sysconfig/httpd
install -m0644 00_default_vhosts.conf %{buildroot}%{_sysconfdir}/httpd/conf/vhosts.d/00_default_vhosts.conf

#install misc documentation and logos
install -m0644 index.html %{buildroot}/var/www/html/
install -m0644 favicon.ico %{buildroot}/var/www/html/
install -m0644 robots.txt %{buildroot}/var/www/html/

# nuke any mandrake button
rm -f %{buildroot}/var/www/icons/mandrake.png
rm -f %{buildroot}/var/www/icons/medbutton.png

cat > HOWTO_get_modules.html << EOF
<p>* For a fresh list of available modules for apache2, please visit <a href=http://nux.se/apache/>nux.se</a>.</p>
EOF
install -m0644 HOWTO_get_modules.html %{buildroot}/var/www/html/addon-modules/

cat > %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d/addon-modules.conf << EOF
<Directory "/var/www/html/addon-modules">
    Options Indexes MultiViews FollowSymlinks
    AllowOverride None
    Order deny,allow
    Deny from all
    Allow from 127.0.0.1
    ErrorDocument 403 "This directory can only be viewed from localhost."
</Directory>
EOF

# install log rotation stuff
cat > %{buildroot}%{_sysconfdir}/logrotate.d/httpd << EOF
/var/log/httpd/*_log /var/log/httpd/apache_runtime_status /var/log/httpd/ssl_mutex {
    rotate 5
    monthly
    missingok
    notifempty
    nocompress
    prerotate
	%{_initrddir}/httpd closelogs > /dev/null 2>&1 || :
    endscript
    postrotate
	%{_initrddir}/httpd closelogs > /dev/null 2>&1 || :
    endscript
}
EOF

# rpm filetriggers
install -d -m 755 %{buildroot}%{_localstatedir}/lib/rpm/filetriggers
cat > %buildroot%{_localstatedir}/lib/rpm/filetriggers/webapp.filter << EOF
^./etc/httpd/conf/webapps.d/.*\.conf$
EOF
install -m 755 %{SOURCE15} \
    %{buildroot}%{_localstatedir}/lib/rpm/filetriggers/webapp.script

%pre
%_pre_useradd apache /var/www /bin/sh

%post
%_post_service httpd

%preun
%_preun_service httpd

%postun
%_postun_userdel apache

%clean
rm -rf %{buildroot}

%files 
%defattr(-,root,root)
%attr(0755,root,root) %{_initrddir}/httpd
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/httpd
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/httpd

%dir %{_sysconfdir}/httpd
%dir %{_sysconfdir}/httpd/conf
%dir %{_sysconfdir}/httpd/conf/addon-modules
%dir %{_sysconfdir}/httpd/conf/webapps.d
%dir %{_sysconfdir}/httpd/conf/vhosts.d
%dir %{_sysconfdir}/httpd/conf.d
%dir %{_sysconfdir}/httpd/modules.d

%dir %{_sysconfdir}/httpd/%{_lib}
%dir %{_sysconfdir}/httpd/logs
%dir %{_sysconfdir}/httpd/modules
%dir %{_sysconfdir}/httpd/extramodules

%attr(0755,apache,apache) %dir /var/www
%attr(0755,root,root) %dir /var/www/html

%dir /var/log/httpd
%dir /var/www/cgi-bin
%dir /var/www/html/addon-modules
%dir /var/www/icons
%dir /var/www/perl

%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/conf/httpd.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/conf/fileprotector.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/conf/mime.types
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/conf/magic
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/conf/webapps.d/addon-modules.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/conf/vhosts.d/00_default_vhosts.conf

%attr(0755,root,root) /var/www/cgi-bin/*
%attr(0755,root,root) /var/www/perl/*
/var/www/html/addon-modules/*

%attr(0644,root,root) %config(noreplace) /var/www/html/favicon.ico
%attr(0644,root,root) %config(noreplace) /var/www/html/index.html
%attr(0644,root,root) %config(noreplace) /var/www/html/robots.txt
%attr(0755,root,root) %{_sbindir}/*
%{_localstatedir}/lib/rpm/filetriggers/webapp.*


%changelog
* Wed Feb 01 2012 Oden Eriksson <oeriksson@mandriva.com> 2.2.22-0.1
- built for updates

* Wed Feb 01 2012 Oden Eriksson <oeriksson@mandriva.com> 2.2.22-1mdv2012.0
+ Revision: 770385
- make it backportable

* Sun Jan 29 2012 Oden Eriksson <oeriksson@mandriva.com> 2.2.22-0.0.1
+ Revision: 769606
- 2.2.22 (pre-release)
- sync some config changes with default

* Wed Sep 14 2011 Oden Eriksson <oeriksson@mandriva.com> 2.2.21-1
+ Revision: 699746
- 2.2.21

* Thu Sep 01 2011 Oden Eriksson <oeriksson@mandriva.com> 2.2.20-1
+ Revision: 697665
- 2.2.20

* Tue Jun 14 2011 Oden Eriksson <oeriksson@mandriva.com> 2.2.19-1
+ Revision: 684990
- bump release

* Sat May 21 2011 Oden Eriksson <oeriksson@mandriva.com> 2.2.19-0
+ Revision: 676777
- 2.2.19 (pre-release)

* Sat May 14 2011 Oden Eriksson <oeriksson@mandriva.com> 2.2.18-1
+ Revision: 674417
- 2.2.18

* Mon May 02 2011 Oden Eriksson <oeriksson@mandriva.com> 2.2.17-2
+ Revision: 662768
- mass rebuild

* Sun Oct 17 2010 Oden Eriksson <oeriksson@mandriva.com> 2.2.17-1mdv2011.0
+ Revision: 586222
- 2.2.17

* Sun Jul 25 2010 Funda Wang <fwang@mandriva.org> 2.2.16-1mdv2011.0
+ Revision: 559479
- 2.2.16

* Sat Mar 06 2010 Oden Eriksson <oeriksson@mandriva.com> 2.2.15-1mdv2010.1
+ Revision: 515157
- 2.2.15 (official)

* Tue Mar 02 2010 Oden Eriksson <oeriksson@mandriva.com> 2.2.15-0.0mdv2010.1
+ Revision: 513531
- 2.2.15 (pre-release)

* Sun Jan 03 2010 Guillaume Rousse <guillomovitch@mandriva.org> 2.2.14-4mdv2010.1
+ Revision: 486068
- install rpm filetriggers for handling webapps configuration

* Tue Dec 22 2009 Oden Eriksson <oeriksson@mandriva.com> 2.2.14-3mdv2010.1
+ Revision: 481383
- added more graceful handling of the httpd server in the initscript

* Sun Nov 15 2009 Oden Eriksson <oeriksson@mandriva.com> 2.2.14-2mdv2010.1
+ Revision: 466259
- fix CVE-2009-2823

* Sun Oct 04 2009 Oden Eriksson <oeriksson@mandriva.com> 2.2.14-1mdv2010.0
+ Revision: 453380
- 2.2.14 was silently released 23-Sep-2009

* Fri Oct 02 2009 Oden Eriksson <oeriksson@mandriva.com> 2.2.14-0.2mdv2010.0
+ Revision: 452665
- fix #53887 (obsolete favicon.ico file in Apache default www pages)

* Sun Sep 27 2009 Oden Eriksson <oeriksson@mandriva.com> 2.2.14-0.1mdv2010.0
+ Revision: 449728
- 2.2.14 (non official release)

* Mon Aug 10 2009 Oden Eriksson <oeriksson@mandriva.com> 2.2.13-1mdv2010.0
+ Revision: 414340
- 2.2.13 (official)

* Thu Aug 06 2009 Oden Eriksson <oeriksson@mandriva.com> 2.2.13-0.1mdv2010.0
+ Revision: 410967
- 2.2.13
- get rid of old cruft like the advx crap

* Thu Jul 23 2009 Oden Eriksson <oeriksson@mandriva.com> 2.2.12-1mdv2010.0
+ Revision: 399052
- update the source as well
- 2.2.12

* Wed Apr 15 2009 Oden Eriksson <oeriksson@mandriva.com> 2.2.11-5mdv2009.1
+ Revision: 367507
- workaround #47992 (apache does not start "occasionally")

* Mon Mar 09 2009 Oden Eriksson <oeriksson@mandriva.com> 2.2.11-4mdv2009.1
+ Revision: 353267
- added logic to make it possible to set limits from the init
  script in an attempt to address #30849 and similar problems
- sync with fedora

* Sun Mar 08 2009 Oden Eriksson <oeriksson@mandriva.com> 2.2.11-3mdv2009.1
+ Revision: 352907
- rebuild

* Sat Feb 07 2009 Oden Eriksson <oeriksson@mandriva.com> 2.2.11-2mdv2009.1
+ Revision: 338393
- added logic to easy debugging with gdb in the initscript

* Tue Dec 16 2008 Oden Eriksson <oeriksson@mandriva.com> 2.2.11-1mdv2009.1
+ Revision: 314830
- 2.2.11

* Sat Dec 06 2008 Oden Eriksson <oeriksson@mandriva.com> 2.2.11-0.1mdv2009.1
+ Revision: 311440
- 2.2.11

* Mon Oct 13 2008 Oden Eriksson <oeriksson@mandriva.com> 2.2.10-1mdv2009.1
+ Revision: 293149
- 2.2.10

* Sat Jul 26 2008 Oden Eriksson <oeriksson@mandriva.com> 2.2.9-2mdv2009.0
+ Revision: 250119
- re-implement the peruser mpm (requested by Denis Philippov <den-is@mezon.ru>)

* Fri Jun 13 2008 Oden Eriksson <oeriksson@mandriva.com> 2.2.9-1mdv2009.0
+ Revision: 218816
- build release

* Wed Jun 11 2008 Oden Eriksson <oeriksson@mandriva.com> 2.2.9-0.1mdv2009.0
+ Revision: 218146
- sync with 2.2.9

* Sun May 18 2008 Oden Eriksson <oeriksson@mandriva.com> 2.2.8-5mdv2009.0
+ Revision: 208683
- removed old cruft in the init script
- rebuild

* Fri Mar 07 2008 Oden Eriksson <oeriksson@mandriva.com> 2.2.8-3mdv2008.1
+ Revision: 181422
- fix the initscript

* Mon Feb 11 2008 Oden Eriksson <oeriksson@mandriva.com> 2.2.8-2mdv2008.1
+ Revision: 165132
- rebuild
- added Charset=UTF-8 as default IndexOptions (requested by rapsys)

* Fri Jan 18 2008 Oden Eriksson <oeriksson@mandriva.com> 2.2.8-1mdv2008.1
+ Revision: 154624
- 2.2.8 (official release)

* Thu Jan 10 2008 Oden Eriksson <oeriksson@mandriva.com> 2.2.8-0.1mdv2008.1
+ Revision: 147737
- 2.2.8

* Sat Jan 05 2008 Oden Eriksson <oeriksson@mandriva.com> 2.2.7-0.1mdv2008.1
+ Revision: 145813
- revert changes to the initscript, it's not backportable
- sync with 2.2.7

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Tue Nov 20 2007 Oden Eriksson <oeriksson@mandriva.com> 2.2.6-2mdv2008.1
+ Revision: 110771
- handle stop, reload, restart better
- handle stop, restart better
- added some svn props

* Fri Sep 07 2007 Oden Eriksson <oeriksson@mandriva.com> 2.2.6-1mdv2008.0
+ Revision: 82041
- 2.2.6 (release)

* Wed Sep 05 2007 Oden Eriksson <oeriksson@mandriva.com> 2.2.6-0.1mdv2008.0
+ Revision: 79886
- 2.2.6
- use the vanilla mime.types file from 2.2.6

* Sat Aug 11 2007 Oden Eriksson <oeriksson@mandriva.com> 2.2.5-0.1mdv2008.0
+ Revision: 61965
- sync with 2.2.5 (only in mime.types)

* Mon Jul 23 2007 Oden Eriksson <oeriksson@mandriva.com> 2.2.4-8mdv2008.0
+ Revision: 54692
- the advxsplitlogfile-DIET binary is now named just advxsplitlogfile and
  not built against dietlibc, fixes #26851
- don't start apache per default, this conforms to the 2008 specifications

* Sun Jun 24 2007 Oden Eriksson <oeriksson@mandriva.com> 2.2.4-7mdv2008.0
+ Revision: 43746
- fix #31562

* Sun Jun 24 2007 Oden Eriksson <oeriksson@mandriva.com> 2.2.4-6mdv2008.0
+ Revision: 43624
- ThreadStackSize was set too low on x86_64, it's now increased to 65536

* Thu Jun 07 2007 Oden Eriksson <oeriksson@mandriva.com> 2.2.4-5mdv2008.0
+ Revision: 36709
- fix a small bug in the initscript when using a different mpm
- added the itk config

  + Guillaume Rousse <guillomovitch@mandriva.org>
    - no need to explicitely restart httpd in %%post, rpm macro already handles it
    - no more certwatch reference


* Sat Mar 10 2007 Oden Eriksson <oeriksson@mandriva.com> 2.2.4-4mdv2007.1
+ Revision: 140574
- rebuild

* Tue Feb 27 2007 Oden Eriksson <oeriksson@mandriva.com> 2.2.4-3mdv2007.1
+ Revision: 126596
- fix release
-  general cleanups

* Tue Feb 27 2007 Oden Eriksson <oeriksson@mandriva.com> 2.2.4-2mdv2007.1
+ Revision: 126360
- handle start/stop in a better fashion

* Thu Jan 25 2007 Oden Eriksson <oeriksson@mandriva.com> 2.2.4-1mdv2007.1
+ Revision: 113433
- cosmetic 2.2.4 version
- fix #28404 (2.0 compat)

* Sun Nov 05 2006 Oden Eriksson <oeriksson@mandriva.com> 2.2.3-5mdv2007.1
+ Revision: 76720
- send USR1 instead of HUP when rotating logs (Olivier Thauvin)
- rebuild
- rebuild
- comment the first CustomLog line (thanks pterjan!)
- Import apache-conf

* Wed Sep 13 2006 Oden Eriksson <oeriksson@mandriva.com> 2.2.3-3mdv2007.0
- fix #25259 (thanks guillomovitch!)

* Tue Aug 01 2006 Oden Eriksson <oeriksson@mandriva.com> 2.2.3-2mdk
- fix #20257

* Sat Jul 29 2006 Oden Eriksson <oeriksson@mandriva.com> 2.2.3-1mdk
- 2.2.3

* Sat May 27 2006 Oden Eriksson <oeriksson@mandriva.com> 2.2.2-4mdk
- be more gentle while nuking the env in the initscript (#21727)

* Mon May 01 2006 Oden Eriksson <oeriksson@mandriva.com> 2.2.2-3mdk
- fix the config (S3)

* Mon May 01 2006 Oden Eriksson <oeriksson@mandriva.com> 2.2.2-2mdk
- broke out the bundled dbd modules (S3)

* Tue Apr 25 2006 Oden Eriksson <oeriksson@mandriva.com> 2.2.2-1mdk
- 2.2.2
- fix the initscript again and #21821

* Wed Feb 22 2006 Oden Eriksson <oeriksson@mandriva.com> 2.2.0-8mdk
- fix the initscript again
- added default vhosts config (by popular request)
- added mod_ssl-gentestcrt (by popular request)

* Tue Feb 07 2006 Oden Eriksson <oeriksson@mandriva.com> 2.2.0-7mdk
- fix the initscript and config (S1,S2,S3)

* Fri Jan 06 2006 Oden Eriksson <oeriksson@mandriva.com> 2.2.0-6mdk
- fix one typo (guillomovitch)

* Sat Dec 31 2005 Oden Eriksson <oeriksson@mandriva.com> 2.2.0-5mdk
- fix promo icons

* Tue Dec 20 2005 Oden Eriksson <oeriksson@mandriva.com> 2.2.0-4mdk
- don't use the daemon function in the initscript (S1) as it hides
  the ssl/nss pass phraze prompt

* Sat Dec 17 2005 Oden Eriksson <oeriksson@mandriva.com> 2.2.0-3mdk
- make the apache 2.0 config startup error more verbose
- fix the addon-modules.conf file
- adjust the logrotate script (large file support)

* Tue Dec 13 2005 Oden Eriksson <oeriksson@mandriva.com> 2.2.0-2mdk
- prevent startup if apache 2.0 config directives are found, these
  can pose a security threat (please do read README.urpmi)
- updated the httpd.conf file with missing/new entries
- updated the README.urpmi file to reflect certain changes

* Mon Dec 12 2005 Oden Eriksson <oeriksson@mandriva.com> 2.2.0-1mdk
- sync with the 2.2.0 conf

* Thu Nov 03 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.55-4mdk
- make the logrotate script less verbose (rgs)

* Sun Oct 30 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.55-3mdk
- rebuilt to provide a -debug package too

* Sat Oct 15 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.55-2mdk
- actually add mod_echo here too (S1)

* Sat Oct 15 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.55-1mdk
- sync with apache-2.0.55 (S1)

* Thu Aug 11 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54-12mdk
- fix #17406

* Wed Aug 10 2005 Andreas Hasenack <andreas@mandriva.com> 2.0.54-11mdk
- fixed env cleaning in the init script with other terminals (like
  inside a screen)

* Sun Jul 31 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54-10mdk
- fixed the APACHEPROXIED stuff in %%pre (again)
- fix changelog mismatch

* Sat Jul 30 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54-9mdk
- added another work around for a rpm bug

* Sat Jul 30 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54-8mdk
- added a work around for a rpm bug, "Requires(foo,bar)" don't work
- fixed the APACHEPROXIED stuff in %%pre

* Tue Jul 12 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54-7mdk
- fix #16303 and #16769

* Fri Jul 01 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54-6mdk
- fix another glitch in the sysv script

* Fri Jul 01 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54-5mdk
- fix a glitch in the sysv script

* Thu Jun 09 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54-4mdk
- move away presumptive old httpd.conf file in %%pre
- shorten the list of log files to rotate by using a wildcard
- added the old config files and instructions how to easier
  determine possible changes the user might have done

* Mon Jun 06 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54-3mdk
- provide correct info about .htaccess files in README.urpmi
- move php specific directives to their respective mod_php packages

* Sun Jun 05 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54-2mdk
- the mod_userdir module now is an external sub package. if you
  need it just install it. (urpmi apache-mod_userdir)

* Sat May 28 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54-1mdk
- major cleanups
- all old files now lives in the apache-conf-2.0.54 tar ball
- no more commonhttpd.conf file, this file is now merged into the 
  httpd.conf file
- fix #15561
- the mime.types file has been touched
- .htaccess files are no longer considered per default (speed, security)
- ~/username is no longer activated per default (security)
- use new rpm-4.4.x pre,post magic

* Thu Mar 31 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53-5mdk
- use the %%mkrel macro
- remove the metuxmpm stuff

* Thu Mar 10 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53-4mdk
- fix %%post and %%postun to prevent double restarts
- own directories (#14418)
- misc spec file and rpmlint fixes

* Fri Feb 18 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53-3mdk
- spec file cleanups, remove the ADVX-build stuff

* Fri Feb 11 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53-2mdk
- added means to secure sensible data (S101)

* Mon Feb 07 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53-1mdk
- added the new dumpio module to the config
- merge changes from the httpd2-VANILLA.conf file

* Fri Jan 21 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.52-7mdk
- set TMP and TMPDIR to /tmp

* Tue Jan 11 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.52-6mdk
- Mandrake Linux/Mandrakelinux, spotted by "Zeb"

* Mon Jan 10 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.52-5mdk
- handle mod_perl2 access from the apache2-mod_perl config

* Fri Nov 19 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.52-4mdk
- build the dietized binay
- added forgotten and new stuff in the httpd2*.conf files
- various small fixes here and there
- added the robots.txt file after looking at the suse stuff...
- misc spec file fixes

* Mon Oct 18 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.52-3mdk
- make use of the new %%{_sysconfdir}/sysconfig/httpd file

* Thu Oct 14 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.52-2mdk
- make the sysv script spit out those -D variables if wanted

* Wed Sep 29 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.52-1mdk
- 2.0.52

* Fri Sep 17 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.51-1mdk
- 2.0.51

* Fri Aug 27 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.50-4mdk
- reverse an gprintified mistake in the past (S0)

* Wed Jul 14 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.50-3mdk
- let the apache user own some of its directories (fixes #6014)

* Mon Jul 12 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.50-2mdk
- provide the actual directory too, duh! (Michael Reinsch)

* Mon Jul 12 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.50-1mdk
- remove redundant provides
- use new webapps policy

* Fri Jun 11 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.49-4mdk
- yet again a funnier initscript...

* Fri Jun 11 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.49-3mdk
- fixed S0 again

* Thu Jun 10 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.49-2mdk
- fixed S0 so that the semkill stuff has to be initiated manually
- added/prepared for the new mod_log_forensic module

* Sun May 16 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.49-1mdk
- 2.0.49

* Sun May 16 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.48-3mdk
- fix S0; bugzilla #5629, #9101, #9107, #9167 and anthill #489, #490, #599
- logrotate if size is above 2GB; anthill #689

* Wed Mar 17 2004 Frederic Lepied <flepied@mandrakesoft.com> 2.0.48-2mdk
- added extramodules to file list
- added MIME types for urpmi and urpmi-media
- fixed MIME type for rpm
- added MIME types for OOo (bug #6113)

