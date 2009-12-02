from __future__ import with_statement # python2.5
"""
Project root holds virtual environment
"""
from fabric.api import *

import os.path

# globals
env.project_name = 'myproject'

##
## environments
##
def init_env(current):
    """Decorator. Setup common variables.
    """
    def wrapper():
        """
        """
        env.project_local_root = os.path.dirname(os.path.realpath(__file__))

        env.hg_deploy = False
        env.virtualenv_opts = '' # --no-site-packages

        current()

        require('hosts', 'root')

        if env.hg_deploy:
            env.project_root = '%(root)s/src/%(project_name)s-project' % env 
            env.project_module_root = '%(project_root)s/%(project_name)s' % env

    return wrapper

@init_env
def localhost():
    """Use the local virtual server
    """
    env.hosts = ['localhost']
    #env.user = 'username'  # actually current shell user
    env.root = '/home/%(user)s/webapps/%(project_name)s' % env

@init_env
def staging():
    """Use staging remote server
    """
    env.hosts = ['mydevhost']
    env.user = 'username'
    env.root = '/home/%(user)s/webapps/%(project_name)s' % env
 
##
## tasks
##

## Local

## Remote
def test():
    """Run the test suite and bail out if it fails
    """
    return manage('test')

def syncdb_and_migrate():
    """Runs syncdb and migrate
    """
    output = manage('syncdb --noinput')
    # check for south message in output
    if "use ./manage.py to migrate these" in output:
        output = manage('migrate')

# bootstrap
def bootstrap():
    """Setup project's root
        - virtualenv
        - project repository
    """
    require('root', 'hg_deploy', provided_by=['localhost', 'staging'])
    require('user', 'host_string')
    require('virtualenv_opts')
    if env.hg_deploy:
        require('project_root', 'project_module_root')
    # verify required commands
    check()
    # create remote environment
    virtualenv_create_remote()
    # deploy initial release
    #deploy()

def current_release():
    """Display latest deployed release
    """
    require('hosts', 'root', provided_by=['localhost', 'staging'])
    with cd('%(root)s/releases' % env):
        run('ls -l current')

def list_releases():
    """List deployed releases
    """
    require('hosts', 'root', provided_by=['localhost', 'staging'])
    with cd('%(root)s/releases' % env):
        run('ls -l')



def deploy():
    require('hosts', 'root', provided_by=['localhost', 'staging'])
    import time
    env.release = time.strftime('%Y%m%d%H%M%S')
    env.release_root = '%(root)s/releases/%(release)s' % env

    # deploy release files env.root/releases/2009...
    deploy_release_files() # local

    #TODO: install updated apache vhost
    #TODO: copy local settings
    #TODO: copy media files (uploads)
    #TODO: backup current db

    install_release_requirements()
    symlink_current_release() # use env.release
    syncdb_and_migrate()

    restart_webserver()

    hg_tag_release() # local

def deploy_version(version):
    env.release = version
    env.release_root = '%(root)s/releases/%(release)s' % env

    #TODO: downgrade south
    # may downgrade requirements
    install_release_requirements()
    symlink_current_release()
    syncdb_and_migrate()

    restart_webserver()

def deploy_release_files():
    require('root', 'hg_deploy', 'project_local_root', provided_by=[localhost, staging])
    require('release', provided_by=['bootstrap', 'deploy'])

    if env.hg_deploy:
        hg_push_remote()
        hg_update_remote()
        hg_remote_release()
    else:
        hg_upload_release()

def install_release_requirements():
    require('release_root', provided_by=['bootstrap', 'deploy'])
    virtualenv('cd %(release_root)s && pip install -r requirements.pip' % env)

def update_release_requirements():
    require('release_root', provided_by=['bootstrap', 'deploy'])
    virtualenv('cd %(release_root)s && pip install -U -r requirements.pip' % env)

def symlink_current_release():
    require('root', provided_by=['localhost', 'staging'])
    require('release', provided_by=['bootstrap', 'deploy', 'deploy_version'])

    with cd('%(root)s/releases' % env):
        run("""
            rm -f previous;
            test -L current && mv current previous || true;
            rm -f current;
            ln -s %(release)s current;
        """ % env, pty=True)

def create_or_preserve_previous_settings():
    """
        Creates conf/local/settings.py if not exists based
        on conf/local/example/*
        Or copy from previous release
    """
    require('root', provided_by=['localhost', 'staging'])
    current_conf = '%(root)s/releases/current/%(project_name)s/conf/local' % env
    previous_conf = '%(root)s/releases/previous/%(project_name)s/conf/local' % env
    with cd(current_conf):
        run("""
            test ! -f settings.py && (
                test -f %(previous_conf)s/settings.py && (
                    cp -a %(previous_conf)s/*
                ) || (
                    cp -a example/* .
                )
            ) || true
        """ % locals())

def restart_webserver():
    pass

def rollback():
    """
    """
    require('hosts', 'root', provided_by=['localhost', 'staging'])
    with cd('%(root)s/releases' % env):
        run("""
            mv current _previous;
            mv previous current;
            mv _previous previous;
        """, pty=True)


def prepare_debian():
    """Prepare debian/ubuntu target system for installation
    """
    require('hosts')

    # check internet access
    run('ping -c 1 -W 3 peak.telecommunity.com')

    # install required debian packages
    packages = 'python python-dev tar gzip wget'
    sudo('packages="%s" aptitude -y install $packages' % packages)

    # install latest setuptools for python
    sudo("""
    which easy_install \
        || (wget http://peak.telecommunity.com/dist/ez_setup.py \
            && python ez_setup.py \
            && rm ez_setup.py)
    """)

    # install latest mercurial
    sudo('which hg || easy_install mercurial')
    # install virtual env & pip
    sudo('which pip || easy_install pip')
    sudo('which virtualenv || pip install virtualenv')
    sudo('which paver || pip install paver')

def prepare_local_py():
    require('hosts')

    #TODO: python, local easy_install
    # install latest mercurial
    run('which hg || easy_install mercurial')
    # install virtual env & pip
    run('which pip || easy_install pip')
    run('which virtualenv || pip install virtualenv')

# helpers
def check():
    """Checks whether we can deploy
    """
    require('hosts', 'hg_deploy', provided_by=['localhost', 'staging'])

    local("echo checking needed commands...")

    run('which python')
    run('which gzip')
    run('which tar')
    run('which sudo')
    run('which chown')
    run('which chmod')
    run('which wget')
    run('which echo')
    if env.hg_deploy:
        run('which hg')
    # add extra needed commands here

def manage(cmd, **kwargs):
    """Runs project's manage.py
    """
    require('root', provided_by=['localhost', 'staging'])

    with cd('%(root)s/releases/current/%(project_name)s' % env):
        result = virtualenv('python bin/manage.py %s' % cmd, **kwargs)
    return result

def purge_project_env():
    require('root', 'host_string')
    ret = prompt('Are you sure to delete %(root)s on %(host_string)s? (yes/no):' % env)
    if ret == 'yes':
        return run('rm -fR %(root)s' % env)

def virtualenv(cmd, **kwargs):
    """Runs commands within project's virtual environment
    """
    require('root', provided_by=['localhost', 'staging'])
    defaults = {
        'pty': True,
    }
    defaults.update(kwargs)
    return run('source %s/bin/activate && %s' % (env.root, cmd), **defaults)

def invoke(cmd):
    return run(cmd)

# virtualenv
def virtualenv_create_remote():
    require('root', 'virtualenv_opts', 'hg_deploy')

    output = run('test -d %s && echo exists || echo not-exists' % env.root, pty=True)
    if output == 'exists':
        abort('Root directory already exists: %s' % env.root)

    run('mkdir -p %s' % env.root)
    with cd(env.root):
        output = run('virtualenv %s .' % env.virtualenv_opts, pty=True)
        # default dirs
        run('mkdir -p src releases')

    if env.hg_deploy:
        # prepare hg repo for push
        hg_init_remote()

    return output

def create_manage_symlink():
    #@@@ use release current
    require('root', 'project_module_root')
    origin = '%(project_module_root)s/bin/manage.py' % env
    symlink = '%(root)s/bin/manage.py' % env
    output = run('test -f %s && echo exists || echo not-exists' % origin, pty=True)
    if output != 'exists':
        abort('Symlink origin does not exists %s' % origin)
    return run('ln -s %s %s' % (origin, symlink))

def restart_webserver():
    pass

# hg
def hg_ssh_path():
    require('user', 'host_string', 'project_root')
    return 'ssh://%(user)s@%(host_string)s/%(project_root)s' % env

def hg_clone_remote():
    require('project_local_root')
    with cd(env.project_local_root):
        output = local('hg clone . %s' % hg_ssh_path())
    return output

def hg_push_remote():
    require('project_local_root')
    with cd(env.project_local_root):
        output = local('hg push %s' % hg_ssh_path())
    return output

def hg_update_remote():
    require('project_root')
    with cd(env.project_root):
        output = run('hg update')
    return output

def hg_init_remote():
    require('project_root')
    return run("""
        mkdir -p %(project_root)s;
        cd %(project_root)s && hg init .
    """ % env, shell=False)

def hg_tag_release():
    require('hosts', 'root', 'project_local_root', provided_by=[localhost, staging])
    require('release', provided_by=[bootstrap, deploy])

    with cd(env.project_local_root):
        local('hg tag --local deploy%(release)s' % env)

def hg_upload_release():
    require('hosts', 'root', 'project_local_root', provided_by=[localhost, staging])
    require('release', provided_by=[bootstrap, deploy])

    # create an archive using rev of working dir
    with cd(env.project_local_root):
        local("""
            mkdir -p dists;
            hg archive --type tgz dists/%(release)s.tgz
        """ % env)
    local_archive = '%(project_local_root)s/dists/%(release)s.tgz' % env
    # upload release tar
    put(local_archive, '%(root)s/releases/%(release)s.tgz' % env)
    # unpack release files
    run('cd %(root)s/releases && tar zxf %(release)s.tgz' % env)
    # remove release tar
    run('rm -f %(root)s/releases/%(release)s.tgz' % env)


def hg_remote_release():
    require('hosts', 'root', 'project_root', provided_by=[localhost, staging])
    require('release', provided_by=[bootstrap, deploy])

    release_archive = '%(root)s/releases/%(release)s' % env

    with cd(env.project_root):
        # create files archive
        run('hg archive --type files %s' % release_archive)


### Try to use local defined envinronments
try:
    fabfile_local = os.path.join(
                        os.path.dirname(os.path.realpath(__file__)),
                        'fabfile_local.py')
    execfile(fabfile_local, globals(), locals())
except IOError:
    pass


