# Open edX Plugin Examples

[![Source code](https://img.shields.io/static/v1?logo=github&label=Git&style=flat-square&color=brightgreen&message=Source%20code)](https://github.com/cookiecutter-openedx/cookiecutter-openedx-plugin)
[![Forums](https://img.shields.io/static/v1?logo=discourse&label=Forums&style=flat-square&color=000000&message=discuss.openedx.org)](https://discuss.openedx.org/tag/cookiecutter)
[![Documentation](https://img.shields.io/static/v1?&label=Documentation&style=flat-square&color=000000&message=Documentation)](https://github.com/cookiecutter-openedx/cookiecutter-openedx-plugin)
[![PyPI releases](https://img.shields.io/pypi/v/cookiecutter-openedx-plugin?logo=python&logoColor=white)](https://pypi.org/project/cookiecutter-openedx-plugin)
[![AGPL License](https://img.shields.io/github/license/overhangio/tutor.svg?style=flat-square)](https://www.gnu.org/licenses/agpl-3.0.en.html)
[![hack.d Lawrence McDaniel](https://img.shields.io/badge/hack.d-Lawrence%20McDaniel-orange.svg)](https://lawrencemcdaniel.com)

An open edx plugin that implements customizations for deployment to Kubernetes. Currently only implements a custom Badges backend that works with Amazon S3 Django storages backend.

## Getting Started

### Install using Tutor

See [Installing extra xblocks and requirements](https://docs.tutor.overhang.io/configuration.html)

```bash
tutor config save       # to ensure that tutor's root folder system has been created
echo "git+https://github.com/cookiecutter-openedx/cookiecutter-openedx-plugin.git" >> "$(tutor config printroot)/env/build/openedx/requirements/private.txt"
cat "$(tutor config printroot)/env/build/openedx/requirements/private.txt"
tutor images build openedx
tutor local quickstart

# you'll also need to run this on your very first install
# -----------------------------------------------------------------------------

# run migrations
tutor local run lms ./manage.py lms makemigrations
tutor local run lms ./manage.py lms migrate
tutor local run cms ./manage.py cms makemigrations
tutor local run cms ./manage.py cms migrate
```

### Documentation

Documentation is available here: [Documentation](https://github.com/cookiecutter-openedx/cookiecutter-openedx-plugin)

### Support

To get community support, go to the official Open edX discussion forum: [https://discuss.openedx.org](https://discuss.openedx.org).

### Contributing

We welcome contributions! cookiecutter-openedx-plugin is part of the [cookiecutter-openedx](https://github.com/cookiecutter-openedx) project. Pull requests are welcome in all repos belonging to this organization. You can also contact [Lawrence McDaniel](https://lawrencemcdaniel.com/contact) directly.

### Getting Started With Local development

* Use the same virtual environment that you use for edx-platform
* Ensure that your Python interpreter to 3.8x
* install black: <https://pypi.org/project/black/>
* install flake8: <https://flake8.pycqa.org/en/latest/>
* install flake8-coding: <https://pypi.org/project/flake8-coding/>

```bash
# Run these from within your edx-platform virtual environment
python3 -m venv venv
source venv/bin/activate

cd /path/to/edx-platform
pip install -r requirements/edx/base.txt
pip install -r requirements/edx/coverage.txt
pip install -r requirements/edx/development.txt
pip install -r requirements/edx/pip-tools.txt
pip install -r requirements/edx/testing.txt
pip install -r requirements/edx/doc.txt
pip install -r requirements/edx/paver.txt

pip install pre-commit black flake8
pre-commit install
```

#### Local development good practices

* run `black` on modified code before committing.
* run `flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics`
* run `flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics`
* run `pre-commit run --all-files` before pushing. see: <https://pre-commit.com/>

#### edx-platform dependencies

To avoid freaky version conflicts in prod it's a good idea to install all of the edx-platform requirements to your local dev virtual environment.

* requirements/edx/base.txt
* requirements/edx/develop.txt,
* requirements/edx/testing.txt

At a minimum this will give you the full benefit of your IDE's linter.
