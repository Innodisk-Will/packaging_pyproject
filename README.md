# release-py-project
package python API to dynamic shared objects

# Topic
* [Build the shared object from the python API (demo).](#Build-the-shared-object-from-the-python-API-(demo).)
* [Compress whole python project](#Compress-whole-python-project)

# Feature
1. Package the project to a new one but will not confuse the original one.
2. The user could use the generated project in the same way as the python module, but could not see any details.
3. Delete `pycache` and exclude `__init__.py` in order to generate a more concise structure.
4. Backup the source file automatically ( the default is `./backup` ).
# Prerequirement
```bash
apt-get update && apt-get install zip -y
pip3 install Cython
```

# Build the shared object.
* Place this repo next to the target project.
    ```bash
    $ ls .. | grep -e demo -e release
    demo
    release-pyproject
    ```
* Build the shared object from the python API (demo).
    > The python API with shared objects ( out ) will be generated after this command and backup the original one into ./backup folder.
    ```bash
    $ python3 setup.py build_ext --inplace --src ../demo --dst ./out --backup ./backup
    ```

    ```bash
    $ tree
    .
    |-- LICENSE
    |-- README.md
    |-- backup
    |   `-- demo_backup_220311-1317
    |       |-- __init__.py
    |       |-- bar
    |       |   |-- __init__.py
    |       |   |-- barbar
    |       |   |   |-- __init__.py
    |       |   |   `-- print_me.py
    |       |   `-- print_me.py
    |       `-- foo
    |           |-- __init__.py
    |           `-- print_me.py
    |-- out
    |   |-- __init__.py
    |   |-- bar
    |   |   |-- __init__.py
    |   |   |-- barbar
    |   |   |   |-- __init__.py
    |   |   |   `-- print_me.so
    |   |   `-- print_me.so
    |   `-- foo
    |       |-- __init__.py
    |       `-- print_me.so
    |-- release.sh
    `-- setup.py

    9 directories, 18 files
    ```
# Compress whole python project
* Check file structure  
    ```bash
    $ ls
    LICENSE  README.md  release.sh  setup.py
* Release python project.
    > The release version will be generated at `output` folder.
    1. Build the shared objects from python.
    2. Remove `.c`, `build`, `.py`, `.pyc`, `pycache`.
    3. Compress to a `.zip` file.
    ```
    $ ./release.sh -r ../demo -a ../demo -e "data;.git;.gitignore"

    $ ls
    LICENSE  README.md  output release.sh  setup.py
    
    $ tree ./output/
    ./output/
    |-- demo
    |   |-- __init__.py
    |   |-- bar
    |   |   |-- __init__.py
    |   |   |-- barbar
    |   |   |   |-- __init__.py
    |   |   |   `-- print_me.so
    |   |   `-- print_me.so
    |   `-- foo
    |       |-- __init__.py
    |       `-- print_me.so
    `-- demo_release_220311-0522.zip

    4 directories, 8 files
    ```

# Help
* `setup.py`
    ```bash
    $ python setup.py -h
    #-----------------------------------------------------------------
    $ python setup.py build_ext --inplace --src <the_source_path> [Options]

    [Options]
    --dst       if not provide the destination path, will backup and replace the original one.
    --backup    if you want backup the original file, you can setup the backup path.
    --build     change the path of build folder, the default is './build'
    ```
* `release.sh`
    ```bash
    $ ./release.sh -h
    #-----------------------------------------------------------------
    Package whole project and replace the python api to shared object

    $ ./release.sh [OPTION]

    [OPTION]
    -r  the root to the project
    -a  the path of the python API in target project which will be converted to dynamic shared objects.
    -z  compress the release project, default is True
    -e  exclude files, like "data;.git;.gitignore"
    ```

# Feature
[　] Distribute a Python package with a compiled dynamic shared library.