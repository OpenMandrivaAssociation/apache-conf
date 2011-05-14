Summary:	Configuration files for Apache
Name:		apache-conf
Version:	2.2.18
Release:	%mkrel 1
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
