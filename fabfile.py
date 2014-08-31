import os
from datetime import datetime

from fabric.api import local, task, lcd
from pytz.reference import LocalTimezone


def generate_package_date():
    """
    Reads the system date and time, including the timezone and returns
    a formatted date string suitable for use in the Debian changelog file:

    Example output: Mon, 23 Dec 2013 11:41:00 +1200
    """
    today = datetime.now()
    localtime = LocalTimezone()
    date_with_timezone = today.replace(tzinfo=localtime)
    return date_with_timezone.strftime('%a, %d %b %Y %H:%M:%S %z')


def generate_debian_changelog():
    """
    We don't store the debian/changelog file in the GIT repository, but build
    it each time from the current GIT tag.
    """
    tag_version = local('git describe --tags', capture=True)
    with open('debian/changelog', 'w') as f:
        f.write('lwp ({0}) unstable; urgency=low\n\n  * LWP release {0}\n\n'.format(tag_version))
        f.write(' -- Claudio Mignanti <c.mignanti@gmail.com>  {}\n'.format(generate_package_date()))


def get_version_from_debian_changelog():
    """
    Returns the version of the latest package from the debian changelog.

    Because we build the changelog first anyway (see: create_debian_changelog),
    this should return the same version as "git describe --tags".
    """
    return local('dpkg-parsechangelog --show-field Version', capture=True)


def get_deb_architecture():
    """
    Returns the deb architecture of the local system, e.g. amd64, i386, arm
    """
    return local('dpkg --print-architecture', capture=True)


@task(alias='deb')
def debian():
    # the debian changelog is not stored on GIT and rebuilt each time
    generate_debian_changelog()
    local('dpkg-buildpackage -us -uc -b')

    # dpkgb-buildpackage places debs one folder above
    version = get_version_from_debian_changelog()
    package = 'lwp_{}_all.deb'.format(version)

    # finally, move package into gh-pages dir
    target = 'debian-testing' if 'rc' in version else 'debian'
    local('mv ../{} gh-pages/{}/'.format(package, target))
    local('rm ../lwp_*.changes')
    if (os.environ['USER'] == 'claudyus'):
        local('dpkg-sig -k 0DFD7CBB --sign builder gh-pages/{}/{}'.format(target, package))


@task
def clone():
    if not os.path.exists('gh-pages'):
        local('git clone git@github.com:claudyus/LXC-Web-Panel.git gh-pages')

    with lcd('gh-pages'):
        local('git checkout origin/gh-pages -b gh-pages || true')


@task
def site():
    clone()
    debian()
    local('make -C gh-pages/')
