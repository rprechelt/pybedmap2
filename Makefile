##
# ##
# bedmap2
#
# @file
# @version 0.0.1

# find python3
PYTHON=`/usr/bin/which python3`

# our testing targets
.PHONY: tests flake black isort all

all: mypy isort black flake tests

tests:
	${PYTHON} -m pytest --cov=bedmap2 tests

flake:
	${PYTHON} -m flake8 bedmap2

black:
	${PYTHON} -m black -t py37 bedmap2
	${PYTHON} -m black -t py37 tests

isort:
	${PYTHON} -m isort --atomic -rc -y bedmap2
	${PYTHON} -m isort --atomic -rc -y tests

mypy:
	${PYTHON} -m mypy bedmap2

# end
