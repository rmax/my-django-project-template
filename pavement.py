import os
import paver
import sys

from paver.easy import \
    options, Bunch, task, call_task, sh, needs, cmdopts, dry

options(
    bootstrap=Bunch(
        bootstrap_dir="bootstrap"
    ), virtualenv=Bunch(
        packages_to_install=["pip", "yolk"]
    )
)

@task
def bootstrap(options):
    """create virtualenv in ./bootstrap"""
    try:
        import virtualenv
    except ImportError:
        raise RuntimeError("virtualenv is needed for bootstrap")

    bdir = options.bootstrap_dir
    if not os.path.exists(bdir):
        os.makedirs(bdir)
    bscript = "bootstrap.py"

    options.virtualenv.script_name = os.path.join(options.bootstrap_dir,
            bscript)
    #options.virtualenv.no_site_packages = True
    #options.bootstrap.no_site_packages = True
    call_task('paver.virtual.bootstrap')
    sh('cd %s; %s %s' % (bdir, sys.executable, bscript))

