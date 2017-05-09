import os
from fabric.api import cd, env, sudo, task, shell_env, run
from fabric.contrib.files import exists
from fabric.contrib.project import rsync_project

# TODO::
#
# 1. Permissions/Groups for uwsgi/nginx/django
# 2. Better base directory for django projects (not Home dir)
#
# These todo's really are for puppet

env.app = 'mmpl'


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
    env.hosts = ['ansible.bennyda.ninja']
    env.environment = 'production'
    env.user = 'root'
    env.django_user = 'admin'
    env.path = '/var/www/%(app)s/%(environment)s' % env
    env.media = '/media/%(app)s/%(environment)s' % env


@task
def development():
    """Production server settings. Must be first task!"""
    env.hosts = ['ansible.bennyda.ninja']
    env.environment = 'development'
    env.user = 'root'
    env.django_user = 'admin'
    env.path = '/var/www/%(app)s/%(environment)s' % env
    env.media = '/media/%(app)s/%(environment)s' % env


@task
def staging():
    """Production server settings. Must be first task!"""
    env.hosts = ['ansible.bennyda.ninja']
    env.environment = 'staging'
    env.user = 'root'
    env.django_user = 'admin'
    env.path = '/var/www/%(app)s/%(environment)s' % env
    env.media = '/media/%(app)s/%(environment)s' % env


@task
def toggle_maintenance():
    require_environment()
    with cd(os.path.join(env.path, 'templates')):
        if exists('maintenance_on.html'):
            run('mv maintenance_on.html maintenance_off.html')
        elif exists('maintenance_off.html'):
            run('mv maintenance_off maintenance_on.html')


@task
def restart_nginx():
    require_environment()
    sudo("systemctl restart nginx")


@task
def restart_uwsgi():
    require_environment()
    sudo("systemctl restart uwsgi")


@task
def restart_webserver():
    require_environment()
    restart_uwsgi()
    restart_nginx()


@task
def clone_environment():
    # copy postgres db from one env to another
    require_environment()
