import os
from fabric.api import cd, env, sudo, settings, task, local, run
from fabric.contrib.files import exists
from fabric.contrib.project import rsync_project


# TODO::
#
# 1. Permissions/Groups for uwsgi/nginx/django
# 2. Better base directory for django projects (not Home dir)
#
# These todo's really are for puppet

def require_environment():
    """
    Helper method to ensure that tasks aren't run in development
    """
    if not hasattr(env, 'environment'):
        raise NotImplementedError(
            'An environment task like @production must be the first task')


@task
def production():
    """Production server settings. Must be first task!"""
    env.environment = 'production'
    env.user = 'root'
    env.app = 'mmpl'
    env.path = '/var/www/%(app)s/%(environment)s' % env
    env.media = '/media/%(app)s/%(environment)s' % env


@task
def setup_server():
    require_environment()

    # setup media/static directories
    sudo('mkdir -p %(media)s' % env)
    with cd(env.media):
        sudo('mkdir -p {static,media}')

    # setup webapp directory and virtualenv
    sudo('mkdir -p %(path)s' % env)
    with cd(env.path):
        sudo('pip install virtualenv pip --upgrade')
        if not exists('venv'):
            sudo('virtualenv -p python venv')


@task
def deploy():
    """Deploy the application, install requirements, collect static, compress, and migrate"""
    require_environment()

    with cd(env.path):
        sudo('rm -rf deploysite')
        rsync_project(
            local_dir='site/',
            remote_dir='/tmp/%(environment)s' % env,
            exclude=['.tox/', '.tests/', 'media/'])
        sudo('mv /tmp/%(environment)s deploysite' % env)
        # should also remove cache files/dirs
        sudo('venv/bin/pip install -r deploysite/requirements.txt --upgrade')
        with cd(os.path.join(env.path, 'deploysite')):
            sudo('../venv/bin/python manage.py createcachetable')
            sudo('../venv/bin/python manage.py collectstatic --noinput')
            # sudo('../venv/bin/python manage.py compress')
            sudo('../venv/bin/python manage.py migrate --noinput')
        sudo('rm -rf rollbacksite')
        if exists('site'):
            sudo('mv site rollbacksite')
        sudo('mv deploysite site')
        sudo('chown -R nginx:nginx *')
        # reload_uwsgi()


@task
def rollback():
    """
    Rolls back to last known state. Multiple rollbacks simply toggles.
    We intentionally do not call migrate -- reverse migrations must be
    done by hand.
    """
    require_environment()

    with cd(env.path):
        sudo('mv rollbacksite deploysite')
        with cd(os.path.join(env.path, 'deploysite')):
            sudo('../venv/bin/python manage.py collectstatic --noinput', user='nginx', group='nginx')
            sudo('../venv/bin/python manage.py compress', user='nginx', group='nginx')
        sudo('mv site rollbacksite')
        sudo('mv deploysite site')
        sudo('chown -R nginx:nginx *')
        reload_uwsgi()


@task
def reload_nginx():
    """Reloads or starts the nginx service"""
    require_environment()

    with settings(warn_only=True):
        # we check status because calling reload
        # on a stopped instance returns 0 :(
        result = sudo('/sbin/service nginx status')
        if result.return_code == 0:
            sudo('/sbin/service nginx reload')
        else:
            sudo('/sbin/service nginx restart')


@task
def reload_uwsgi():
    """Reloads or starts the uwsgi emperor service"""
    require_environment()

    with settings(warn_only=True):
        result = sudo('/sbin/initctl reload peppermint_%(environment)s' % env)
        if result.return_code != 0:
            sudo('/sbin/initctl start peppermint_%(environment)s' % env)


@task
def live_reload_static():
    """Runs static file compression and collectstatic"""
    require_environment()
    with cd(os.path.join(env.path, 'site')):
        sudo('../venv/bin/python manage.py collectstatic --noinput', user='nginx', group='nginx')
        sudo('../venv/bin/python manage.py compress', user='nginx', group='nginx')
    reload_nginx()
