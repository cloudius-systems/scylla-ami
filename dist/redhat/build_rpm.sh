#!/bin/bash -e

PRODUCT=scylla

. /etc/os-release

is_redhat_variant() {
    [ -f /etc/redhat-release ]
}
pkg_install() {
    if is_redhat_variant; then
        sudo yum install -y $1
    else
        echo "Requires to install following command: $1"
        exit 1
    fi
}

if [ ! -e dist/redhat/build_rpm.sh ]; then
    echo "run build_rpm.sh in top of scylla-ami dir"
    exit 1
fi

if [ "$(arch)" != "x86_64" ]; then
    echo "Unsupported architecture: $(arch)"
    exit 1
fi

if [ ! -f /usr/bin/rpmbuild ]; then
    pkg_install rpm-build
fi
if [ ! -f /usr/bin/git ]; then
    pkg_install git
fi

VERSION=$(./SCYLLA-VERSION-GEN)
SCYLLA_VERSION=$(cat build/SCYLLA-VERSION-FILE)
SCYLLA_RELEASE=$(cat build/SCYLLA-RELEASE-FILE)

RPMBUILD=$(readlink -f build/)
mkdir -p $RPMBUILD/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}

git archive --format=tar --prefix=$PRODUCT-ami-$SCYLLA_VERSION/ HEAD -o $RPMBUILD/SOURCES/$PRODUCT-ami-$VERSION.tar

parameters=(
    -D"version $SCYLLA_VERSION"
    -D"release $SCYLLA_RELEASE"
    -D"product $PRODUCT"
    -D"${PRODUCT/-/_} 1"
)

rpmbuild "${parameters[@]}" -ba --define '_binary_payload w2.xzdio' --define "_topdir $RPMBUILD" $RPMBUILD/SPECS/scylla-ami.spec
