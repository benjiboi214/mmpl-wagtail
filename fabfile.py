import os
from fabric.api import cd, env, sudo, task, run, settings, get, \
    put, local
from fabric.contrib.files import exists

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
    env.hosts = ['production.bennyda.ninja']
    env.environment = 'production'
    env.user = 'root'
    env.django_user = 'admin'
    env.path = '/var/www/%(app)s/%(environment)s' % env
    env.media = '/media/%(app)s/%(environment)s' % env


@task
def development():
    """Development server settings. Must be first task!"""
    env.hosts = ['ansible.bennyda.ninja']
    env.environment = 'development'
    env.user = 'root'
    env.django_user = 'admin'
    env.path = '/var/www/%(app)s/%(environment)s' % env
    env.media = '/media/%(app)s/%(environment)s' % env


@task
def staging():
    """Staging server settings. Must be first task!"""
    env.hosts = ['staging.bennyda.ninja']
    env.environment = 'staging'
    env.user = 'root'
    env.django_user = 'admin'
    env.path = '/var/www/%(app)s/%(environment)s' % env
    env.media = '/media/%(app)s/%(environment)s' % env


@task
def toggle_maintenance():
    """Toggle the maintenance.html file on or off based on its current state"""
    require_environment()
    with cd(os.path.join(env.path, 'templates')):
        if exists('maintenance_on.html'):
            run('mv maintenance_on.html maintenance_off.html')
        elif exists('maintenance_off.html'):
            run('mv maintenance_off maintenance_on.html')


@task
def restart_nginx():
    """Restart the nginx application"""
    require_environment()
    sudo("systemctl restart nginx")


@task
def restart_uwsgi():
    """Restart the uwsgi application"""
    require_environment()
    sudo("systemctl restart uwsgi")


@task
def restart_webserver():
    """Restart the nginx and uwsgi applications"""
    require_environment()
    restart_uwsgi()
    restart_nginx()


@task
def clone_to_local_env():
    require_environment()
    source_db_name = '%(app)s_%(environment)s' % env
    destination_db_name = '%(app)s_development' % env
    tmp_dump_file = os.path.join('/tmp', source_db_name + '.sql')

    # On Remote Machine, get relevant files.
    sudo('systemctl stop uwsgi')
    sudo('sudo -Hiu postgres pg_dump -C -Fp -f %s %s' % (tmp_dump_file, source_db_name))
    sudo('systemctl start uwsgi')

    # rsync media and sql dump to local dir
    get(remote_path=tmp_dump_file, local_path='/tmp')
    get(remote_path=os.path.join(env.media, 'media'), local_path='/media/mmpl/development')

    sudo('rm %s' % tmp_dump_file)  # remove dump from source host

    # On Local Machine, import DB
    # build db from dump
    local('dropdb %s' % destination_db_name)
    local('psql -f %s' % tmp_dump_file)
    local('createdb -O %s -T %s %s' % (env['app'], source_db_name, destination_db_name))
    local('dropdb %s' % source_db_name)

    local('rm %s' % tmp_dump_file)  # remove dump from destination host
    # migrate mmpl_production to mmpl_staging


# Add a git pull task? Probably best to build another
# ansible playbook that just does github and web roles.
@task
def clone_environment(source, destination):
    """Given source and destination arguments, create a database dump and copy
    the uploaded content from the source to the destination. Best not done
    to a production database. Approach manually."""
    source, destination = get_env_values(source, destination)
    source_db_name = '%(app)s_%(environment)s' % source
    destination_db_name = '%(app)s_%(environment)s' % destination
    tmp_dump_file = os.path.join('/tmp', source_db_name + '.sql')
    tmp_media_dir = '/tmp/media'

    with settings(host_string=source['host']):
        # create dump file
        sudo('systemctl stop uwsgi')
        sudo('sudo -Hiu postgres pg_dump -C -Fp -f %s %s' % (tmp_dump_file, source_db_name))
        sudo('systemctl start uwsgi')

        # rsync media and sql dump to local dir
        get(remote_path=tmp_dump_file, local_path='/tmp')
        get(remote_path=source['media'], local_path='/tmp')

        sudo('rm %s' % tmp_dump_file)  # remove dump from source host

    with settings(host_string=destination['host']):
        # rsync media and sql dump to destination
        put(local_path=tmp_dump_file, remote_path=tmp_dump_file)
        put(local_path=tmp_media_dir, remote_path=destination['media'])

        # build db from dump
        sudo('sudo -Hiu postgres dropdb %s' % destination_db_name)
        # sudo('sudo -Hiu postgres psql %s < %s' % (destination_db_name, tmp_dump_file))
        sudo('sudo -Hiu postgres psql -f %s' % tmp_dump_file)
        sudo('sudo -Hiu postgres createdb -O %s -T %s %s' % (destination['app'], source_db_name, destination_db_name))
        sudo('sudo -Hiu postgres dropdb %s' % source_db_name)

        sudo('rm %s' % tmp_dump_file)  # remove dump from destination host
        # migrate mmpl_production to mmpl_staging

        restart_webserver()

    local('rm -rf %s' % tmp_media_dir)
    local('rm %s' % tmp_dump_file)


def get_env_values(source, destination):
    globals()[source]()
    source = {
        'app': env.app,
        'host': env.hosts[0],
        'user': env.user,
        'environment': env.environment,
        'media': os.path.join(env.media, 'media')
    }
    globals()[destination]()
    destination = {
        'app': env.app,
        'host': env.hosts[0],
        'user': env.user,
        'environment': env.environment,
        'media': env.media
    }
    return source, destination
