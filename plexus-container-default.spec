# Copyright (c) 2000-2007, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# If you don't want to build with maven, and use straight ant instead,
# give rpmbuild option '--without maven'

%define with_maven 0

%define gcj_support 1

%define parent plexus
%define subname container-default

Name:           plexus-container-default
Version:        1.0
Release:        %mkrel 0.1.a8.3.0.2
Epoch:          0
Summary:        Default Plexus Container
License:        Apache License
Group:          Development/Java
URL:            http://plexus.codehaus.org/
Source0:        plexus-container-default-1.0-alpha-8-src.tar.gz
# svn export svn://svn.plexus.codehaus.org/plexus/scm/tags/plexus-container-default-1.0-alpha-8/
Source1:        plexus-container-default-1.0-build.xml
Source2:        plexus-container-default-1.0-project.xml
Source3:        plexus-container-default-settings.xml
Source4:        plexus-container-default-1.0-jpp-depmap.xml


BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%if %{gcj_support}
BuildRequires:  java-gcj-compat-devel
%else
BuildArch:      noarch
BuildRequires:  java-devel
%endif
BuildRequires:  java-rpmbuild >= 0:1.7.2
BuildRequires:  ant >= 0:1.6
BuildRequires:  ant-nodeps
BuildRequires:  junit
%if %{with_maven}
BuildRequires:  maven2 >= 2.0.4
BuildRequires:  maven2-plugin-compiler
BuildRequires:  maven2-plugin-install
BuildRequires:  maven2-plugin-jar
BuildRequires:  maven2-plugin-javadoc
BuildRequires:  maven2-plugin-resources
BuildRequires:  maven2-plugin-surefire
BuildRequires:  maven2-plugin-release
%endif
BuildRequires:  classworlds >= 0:1.1
BuildRequires:  plexus-utils 
Requires:  classworlds >= 0:1.1
Requires:  plexus-utils 

%description
The Plexus project seeks to create end-to-end developer tools for 
writing applications. At the core is the container, which can be 
embedded or for a full scale application server. There are many 
reusable components for hibernate, form processing, jndi, i18n, 
velocity, etc. Plexus also includes an application server which 
is like a J2EE application server, without all the baggage.


%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description javadoc
Javadoc for %{name}.


%prep
%setup -q -n plexus-container-default-1.0-alpha-8
for j in $(find . -name "*.jar"); do
        mv $j $j.no
done
cp %{SOURCE1} build.xml
cp %{SOURCE2} project.xml
cp %{SOURCE3} settings.xml

%build
sed -i -e "s|<url>__JPP_URL_PLACEHOLDER__</url>|<url>file://`pwd`/.m2/repository</url>|g" settings.xml
sed -i -e "s|<url>__JAVADIR_PLACEHOLDER__</url>|<url>file://`pwd`/external_repo</url>|g" settings.xml
sed -i -e "s|<url>__MAVENREPO_DIR_PLACEHOLDER__</url>|<url>file://`pwd`/.m2/repository</url>|g" settings.xml
sed -i -e "s|<url>__MAVENDIR_PLUGIN_PLACEHOLDER__</url>|<url>file:///usr/share/maven2/plugins</url>|g" settings.xml
sed -i -e "s|<url>__ECLIPSEDIR_PLUGIN_PLACEHOLDER__</url>|<url>file:///usr/share/eclipse/plugins</url>|g" settings.xml

export MAVEN_REPO_LOCAL=$(pwd)/.m2/repository
mkdir -p $MAVEN_REPO_LOCAL

mkdir external_repo
ln -s %{_javadir} external_repo/JPP

%if %{with_maven}
    mvn-jpp \
        -e \
        -s $(pwd)/settings.xml \
        -Dmaven2.jpp.depmap.file=%{SOURCE4} \
        -Dmaven.repo.local=$MAVEN_REPO_LOCAL \
        -Dmaven.test.skip=true \
        install javadoc:javadoc

%else
mkdir -p target/lib
build-jar-repository -s -p target/lib \
classworlds \
plexus/utils \
junit

%{ant} jar javadoc
%endif


%install
rm -rf $RPM_BUILD_ROOT
# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}/plexus
install -pm 644 target/%{name}-%{version}-alpha-8.jar \
  $RPM_BUILD_ROOT%{_javadir}/plexus/container-default-%{version}.jar
%add_to_maven_depmap org.codehaus.plexus %{name} %{version} JPP/%{parent} %{subname}
(cd $RPM_BUILD_ROOT%{_javadir}/plexus && \
 for jar in *-%{version}*; do \
     ln -sf ${jar} `echo $jar| sed  "s|-%{version}||g"`; \
 done \
)

# poms
%if %{with_maven}
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/maven2/poms
install -pm 644 pom.xml \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP.%{parent}-%{subname}.pom
%endif

# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr target/site/apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name}

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
%update_maven_depmap
%if %{gcj_support}
%{update_gcjdb}
%endif

%postun
%update_maven_depmap
%if %{gcj_support}
%{clean_gcjdb}
%endif

%files
%defattr(0644,root,root,0755)
%{_javadir}/*
%if %{with_maven}
%{_datadir}/maven2/poms/*
%endif
%{_mavendepmapfragdir}
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/*
%endif

%files javadoc
%defattr(-,root,root,-)
%doc %{_javadocdir}/*


%changelog
* Wed Jan 02 2008 Olivier Blin <oblin@mandriva.com> 0:1.0-0.1.a8.3.0.2mdv2009.0
+ Revision: 140733
- restore BuildRoot

  + Thierry Vignaud <tvignaud@mandriva.com>
    - kill re-definition of %%buildroot on Pixel's request

* Sun Dec 16 2007 Anssi Hannula <anssi@mandriva.org> 0:1.0-0.1.a8.3.0.2mdv2008.1
+ Revision: 121004
- buildrequire java-rpmbuild, i.e. build with icedtea on x86(_64)

* Thu Dec 13 2007 Alexander Kurtakov <akurtakov@mandriva.org> 0:1.0-0.1.a8.3.0.1mdv2008.1
+ Revision: 119384
- skip tests
- add maven2-plugin-release BR
- add maven poms and depmaps (jpp sync)

* Sat Sep 15 2007 Anssi Hannula <anssi@mandriva.org> 0:1.0-0.1.a8.1.1.2mdv2008.0
+ Revision: 87308
- rebuild to filter out autorequires of GCJ AOT objects
- remove unnecessary Requires(post) on java-gcj-compat

* Wed Jul 04 2007 David Walluck <walluck@mandriva.org> 0:1.0-0.1.a8.1.1.1mdv2008.0
+ Revision: 47854
- Import plexus-container-default



* Fri Mar 09 2007 Deepak Bhole <dbhole@redhat.com> 0:1.0-0.1.a8.1jpp.1
- From Andrew Overholt:
  - Remove javadoc symlinking
  - Remove Vendor and Distribution
  - Remove section free
  - Change Release to be 0.Z.tag.Xjpp.Y%%{?dist}
  - Use Fedora BuildRoot
  - Don't use maven

* Wed Jan 11 2006 Fernando Nasser <fnasser@redhat.com> - 0:1.0-0.a8.2jpp
- First JPP 1.7 build
                                                                                
* Mon Nov 07 2005 Ralph Apel <r.apel at r-apel.de> - 0:1.0-0.a8.1jpp
- First JPackage build
