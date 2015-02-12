# You should have sphinx installed (pip install sphinx) in order to run this
# file.
cat README.rst docs/documentation.rst.dist > docs/index.rst
./bin/sphinx-build -n -a -b html docs builddocs
cd builddocs && zip -r ../builddocs.zip . -x ".*" && cd ..