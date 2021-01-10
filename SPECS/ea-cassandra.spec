%define		debug_package %{nil}
%define         installdir /opt/cassandra
%define         rpm_user cassandra
%define         rpm_grp cassandra
%define         _rpmfilename %%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm
%define		ver 3.11.6


Name:     	ea-cassandra-%{major_version}
Version:	%{Version}
Release:	%{BUILD_NUMBER}
Summary:	EA Cassandra 
License:	ASL 2.0
Group:		Software/EADPDBA
Source0:	apache-cassandra-%{Version}-bin.tar.gz
AutoReqProv:	no
Prefix: 	/opt/cassandra/product

%define     	install_path %{prefix}/%{major_version}-%{Version}

%description
EA Cassandra

%prep
%setup -q -n apache-cassandra-%{Version} -a0

%install
DEST_PATH=%{buildroot}%{install_path}
rm -rf %{buildroot}
mkdir -p %{buildroot}%{install_path}

cp -rp apache-cassandra-%{Version}/* ${DEST_PATH}/
mv ../../SOURCES/metrics-graphite-3.1.4.jar ${DEST_PATH}/lib/
mv ../../SOURCES/cassandra.yaml ${DEST_PATH}/conf/
mv ../../SOURCES/metrics-reporter.yaml ${DEST_PATH}/conf/
mv ../../SOURCES/jvm.options ${DEST_PATH}/conf/
mv ../../SOURCES/cassandra-rackdc.properties ${DEST_PATH}/conf/
mv ../../SOURCES/cassandra-env.sh ${DEST_PATH}/conf/
mv ../../SOURCES/commitlog_archiving.properties ${DEST_PATH}/conf/
mv ../../SOURCES/logback.xml ${DEST_PATH}/conf/
mv ../../ic-sstable-tools.jar ${DEST_PATH}/lib/
mv ../../cassandra-lucene-index-plugin-3.11.3.0.jar ${DEST_PATH}/lib/
find ${DEST_PATH}/conf/ -type f -exec chmod 644 {} \;

#mv ${DEST_PATH}/conf/cassandra.yaml ${DEST_PATH}/conf/cassandra.yaml.orig
#mv ${DEST_PATH}/conf/jvm.options ${DEST_PATH}/conf/jvm.options.orig
#mv ${DEST_PATH}/conf/commitlog_archiving.properties ${DEST_PATH}/conf/commitlog_archiving.properties.orig



%pre
### Check for folder structure
for x in /cassandralog /cassandradata /cassandracommitlog /cassandrabackup ; do
  if [ ! -d ${x} ]; then
    echo "${x} folder is missing"
    exit 1
  fi 
done


getent group %{rpm_grp} > /dev/null 2> /dev/null
if [ $? -ne 0 ] ; then
        groupadd %{rpm_grp} || %nnmmsg Unexpected error adding group "%{rpm_grp}". Aborting install process.
fi


getent passwd %{rpm_user} > /dev/null 2> /dev/null
if [ $? -ne 0 ] ; then
  useradd -r -d /home/%{rpm_user} -c "%{rpm_user}" -g %{rpm_grp} %{rpm_user} || \
    %nnmmsg Unexpected error adding user "%{rpm_user}". Aborting install process.
fi

### Stop service if Running
if [ -e /etc/init.d/cassandra ] || [ -e /usr/lib/systemd/system/cassandra.service ]; then
  /sbin/service cassandra status &> /dev/null
  if [ $? -eq 0 ]; then
    /sbin/service cassandra stop
  fi 
fi


%post
# Get version of current install - before removing softlink
curver=`readlink /opt/cassandra/product/cassandra | awk -F '/' '{print $5}' | awk -F '.' '{print $1}'`
# Get version of new RPM install


### Check Major version
if [ -e /opt/cassandra/product/cassandra/conf/cassandra.yaml ]; then
  cp /opt/cassandra/product/cassandra/conf/cassandra.yaml %{install_path}/conf/
  chown %{rpm_user}:%{rpm_grp} %{install_path}/conf/cassandra.yaml
  if [ $major_version  -eq 3 ] && [ $curver -lt $major_version ] ; then
    echo "Upgrading file"
    echo "hints_directory: /cassandradata/hints" >> %{install_path}/conf/cassandra.yaml
    sed -i 's/memtable_allocation_type: heap_buffers/memtable_allocation_type: offheap_objects/' %{install_path}/conf/cassandra.yaml
  fi
fi


### Delete initial symlink
if [ -h /opt/cassandra/product/cassandra ]; then
  rm -f /opt/cassandra/product/cassandra
fi

ln -s %{install_path} /opt/cassandra/product/cassandra
#ln -s /cassandralog /opt/cassandra/product/cassandra/logs

chown -R cassandra:cassandra /opt/cassandra

## Start service
if [ ! -h /opt/cassandra/product/cassandra ]; then
  echo "failed to create symlink"
  exit 1 
fi

/sbin/service cassandra start

%files 
%defattr(-, cassandra, cassandra, -)
%{prefix}/*


%changelog
* Thu Jul 02 2020 pdutt <pdutt@contractor.ea.com> - 1.3
- Updated  to  latest  Avilable  Version
* Wed Jun 19 2019 pdutt  <pdutt@contractor.ea.com> - 1.2
- Updated  to  latest  Avilable  Version
* Wed Oct 26 2016 jgammelgaard <jgammelgaar@ea.com> - 1.1
- Updates to make it build via Jenkins
* Tue Oct 18 2016 lthompson <lthompson@ea.com> - 1.0
- initial creation
