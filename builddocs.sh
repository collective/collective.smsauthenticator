# You should have sphinx installed (pip install sphinx) in order to run this file.
cp README.rst docs/index.rst
#cat README.rst docs/documentation.rst.distrib > docs/index.rst
sphinx-build -n -a -b html docs builddocs
cd builddocs && zip -r ../builddocs.zip . -x ".*" && cd ..