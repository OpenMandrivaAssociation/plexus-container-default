# Copyright (c) 2000-2005, JPackage Project
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

# We don't want to use maven
%define _without_maven 1

# If you don't want to build with maven, and use straight ant instead,
# give rpmbuild option '--without maven'

%define with_maven %{!?_without_maven:1}%{?_without_maven:0}
%define without_maven %{?_without_maven:1}%{!?_without_maven:0}

Name:           plexus-container-default
Version:        1.0
Release:        0.4.a8.1.2
Summary:        Default Plexus Container
License:        ASL 2.0 and MIT
Group:          Development/Java
URL:            http://plexus.codehaus.org/
# svn export  \
#     svn://svn.plexus.codehaus.org/plexus/tags/plexus-container-default-1.0-alpha-8 plexus-container-default-1.0-alpha-8
# tar cjf plexus-container-default-1.0-alpha-8-src.tar.bz2 \
#   plexus-container-default-1.0-alpha-8
Source0:        %{name}-1.0-alpha-8-src.tar.bz2
# This was generated by an maven download and hand-tuned
Source1:        %{name}-1.0-build.xml
Source2:        %{name}-1.0-project.xml

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  jpackage-utils >= 0:1.6
BuildRequires:  ant >= 0:1.6
BuildRequires:  ant-nodeps
BuildRequires:  junit
%if %{with_maven}
BuildRequires:  maven
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
cp %{SOURCE1} build.xml
cp %{SOURCE2} project.xml

%build
%if %{with_maven}
mkdir -p .maven/repository/maven/jars
build-jar-repository .maven/repository/maven/jars \
maven-jelly-tags

mkdir -p .maven/repository/JPP/jars
build-jar-repository -s -p .maven/repository/JPP/jars \
classworlds plexus/utils

export MAVEN_HOME_LOCAL=$(pwd)/.maven
maven \
        -Dmaven.repo.remote=file:/usr/share/maven-1.0/repository \
        -Dmaven.home.local=$MAVEN_HOME_LOCAL \
        jar:install javadoc

%else
mkdir -p target/lib
build-jar-repository -s -p target/lib \
classworlds \
plexus/utils \
junit

ant jar javadoc
%endif


%install
rm -rf $RPM_BUILD_ROOT
# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}/plexus
install -pm 644 target/%{name}-%{version}-alpha-8.jar \
  $RPM_BUILD_ROOT%{_javadir}/plexus/container-default-%{version}.jar
(cd $RPM_BUILD_ROOT%{_javadir}/plexus && \
 for jar in *-%{version}*; do \
     ln -sf ${jar} `echo $jar| sed  "s|-%{version}||g"`; \
 done \
)

# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr target/docs/apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name}


%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{_javadir}/*

%files javadoc
%defattr(-,root,root,-)
%doc %{_javadocdir}/*

