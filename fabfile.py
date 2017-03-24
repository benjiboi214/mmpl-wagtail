import os
from fabric.api import cd, env, sudo, task
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
def development():
    """Production server settings. Must be first task!"""
    env.environment = 'development'
    env.user = 'root'
    env.app = 'mmpl'
    env.path = '/var/www/%(app)s/%(environment)s' % env
    env.media = '/media/%(app)s/%(environment)s' % env


@task
def deploy():
    """Deploy the application, install requirements,
    collect static, compress, and migrate"""
    require_environment()

    with cd(env.path):
        sudo('rm -rf deploysite')
        rsync_project(
            local_dir='site/',
            remote_dir='/tmp/%(environment)s' % env,
            exclude=['.tox/', '.tests/', 'media/', '.db.sqlite3'])
        sudo('mv /tmp/%(environment)s deploysite' % env)
        # should also remove cache files/dirs
        sudo('venv/bin/pip install -r deploysite/requirements.txt --upgrade')
        with cd(os.path.join(env.path, 'deploysite')):
            sudo('../venv/bin/python manage.py createcachetable')
            sudo('../venv/bin/python manage.py collectstatic --noinput')
            # sudo('../venv/bin/python manage.py compress')
            # sudo('../venv/bin/python manage.py makemigrations --noinput')
            sudo('../venv/bin/python manage.py migrate --noinput')
        sudo('rm -rf rollbacksite')
        if exists('site'):
            sudo('mv site rollbacksite')
        sudo('mv deploysite site')
        sudo('chown -R nginx:nginx *')
        sudo('cp site/uwsgi/%(environment)s.ini /etc/uwsgi/vassals/%(environment)s.ini' % env)


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
            sudo('../venv/bin/python manage.py collectstatic --noinput')
            sudo('../venv/bin/python manage.py compress')
        sudo('mv site rollbacksite')
        sudo('mv deploysite site')
        sudo('chown -R nginx:nginx *')
