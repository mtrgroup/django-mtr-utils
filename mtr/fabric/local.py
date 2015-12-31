from fabric.api import local, task


@task
def clear():
    """Delete unnecessary and cached files"""

    local(
        "find . -name '~*' -or -name '*.pyo' -or -name '*.pyc' "
        "-or -name '__pycache__' -or -name 'Thubms.db' "
        "| xargs -I {} rm -vrf '{}'")


@task
def subl():
    """Start Sublime editor"""

    local('subl project.sublime-project')
