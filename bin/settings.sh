#!/bin/bash
# -*- coding: utf-8 -*-
#
# This script should be sourced to use.
#
# This file is generated by cookiecutter-pygitrepo 0.0.7: https://github.com/MacHu-GWU/cookiecutter-pygitrepo/tree/0.0.7

if [ -n "${BASH_SOURCE}" ]
then
    dir_here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
else
    dir_here="$( cd "$(dirname "$0")" ; pwd -P )"
fi
dir_project_root=$(dirname "${dir_here}")

# GitHub
github_account="MacHu-GWU"
github_repo_name="superjson-project"


# Python
package_name="superjson"
py_ver_major="3"
py_ver_minor="8"
py_ver_micro="11"
use_pyenv="N" # "Y" or "N"
supported_py_versions="3.8.11" # e.g: "2.7.13 3.6.2"


#--- Doc Build
rtd_project_name="superjson"


