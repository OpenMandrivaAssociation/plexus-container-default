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

%global parent plexus
%global subname container-default

Name:           plexus-container-default
Version:        1.0
Release:        0.8.a9
Summary:        Default Plexus Container
License:        ASL 2.0 and MIT
Group:          Development/Java
URL:            http://plexus.codehaus.org/
# git clone git://github.com/sonatype/plexus-containers.git
# git archive --format=tar --prefix=plexus-containers/ plexus-container-default-1.0-alpha-9-stable-1 | gzip > plexus-container-default-1.0-alpha-9-stable-1-src.tgz
Source0:        %{name}-1.0-alpha-9-stable-1-src.tgz
# test ClassicSingletonComponentManagerTest.testThreads10() fails in koji
# (dev says it fails randomly)
Patch0:         %{name}-fixed-test.patch

BuildArch:      noarch
BuildRequires:  jpackage-utils >= 0:1.6
BuildRequires:  junit
BuildRequires:  maven-surefire-provider-junit
BuildRequires:  maven
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
%setup -q -n plexus-containers
%patch0 -p1

%build
mvn-rpmbuild install javadoc:aggregate


%install
# jars
install -d -m 755 %{buildroot}%{_javadir}/%{parent}
install -pm 644 target/%{name}-%{version}-alpha-9-stable-1.jar \
  %{buildroot}%{_javadir}/%{parent}/%{subname}.jar

# poms
install -d -m 755 %{buildroot}%{_mavenpomdir}
install -pm 644 pom.xml %{buildroot}%{_mavenpomdir}/JPP.%{parent}-%{subname}.pom

# we don't provide depmap on purpose. If anyone wants to use this old
# code they should do extra work

# javadoc
install -d -m 755 %{buildroot}%{_javadocdir}/%{name}
cp -pr target/site/apidocs/* %{buildroot}%{_javadocdir}/%{name}

%pre javadoc
# workaround for rpm bug, can be removed in F-19
[ $1 -gt 1 ] && [ -L %{_javadocdir}/%{name} ] && \
rm -rf $(readlink -f %{_javadocdir}/%{name}) %{_javadocdir}/%{name} || :


%files
%{_javadir}/%{parent}
%{_mavenpomdir}/JPP.%{parent}-%{subname}.pom

%files javadoc
%{_javadocdir}/*

