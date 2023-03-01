import sys, os, glob, shutil
from distutils.core import setup
from datetime import datetime, timezone, timedelta
from os import walk
from os.path import join

EXCLUDE_CFILE="YOLO/darknet"
IGNORE_PATTERNS='*.xmodel'

# we'd better have Cython installed, or it's a no-go
try:
    from Cython.Distutils import build_ext
    from Cython.Build import cythonize
except:
    print("You don't seem to have Cython installed. Please get a")
    print("copy from www.cython.org and install it")
    sys.exit(1)

def get_time(zone='+8'):
    # 設定為 +8 時區
    tz = timezone(timedelta(hours=zone))
    # 取得現在時間、指定時區、轉為 ISO 格式
    datetime.now(tz).isoformat()
    return datetime.now(tz).strftime("%y%m%d-%H%M")

# get custom argument: if no key return None , if no value return default
def get_args(args:list, key:str, default:str=None):
    if key in args:
        idx = args.index(key)
        try:
            val = args[int(idx)+1]           # get value of argument
            [ sys.argv.remove(i) for i in [key, val] ] # remove argument or setup will get error
            return os.path.abspath(val)
        except Exception as e:
            if default:
                return default        
            else:
                raise Exception('Could not find the value of argument ({})'.format(key))
    else:
        return default

# print help
def helper():
    info = [
        "$ python setup.py build_ext --inplace --src <the_source_path> [Options]",
        "",
        "[Options]",
        "--dst       if not provide the destination path, will backup and replace the original one.",
        "--backup    if you want backup the original file, you can setup the backup path.",
        "--build     change the path of build folder, the default is './build'",
        "--exclude   Exclude file or folder, fill relative path in exclude.txt",
        "--delete    Delete file or folder, fill relative path in delete.txt",
        "" ]
    [print(i) for i in info]
    sys.exit(1)

# setup basic variable
args = sys.argv

# show helper 
if not (('build_ext' in args) and ('--inplace' in args) and ('--src' in args)) or (('--help' in args) and ('-h' in args)): helper()

# ------------------------------------------------------------------------------------------------------------------------------
# parse custom variable
print('parse custom option')
src_path = get_args(args, '--src') 
dst_path = get_args(args, '--dst', src_path)                   
backup_path = get_args(args, '--backup') 
exclude_txt = get_args(args, '--exclude') 
delete_txt = get_args(args, '--delete') 
build_path = os.path.normpath(get_args(args, '--build', './build') )

# if the source is exists, clear pycahe folder
if not os.path.exists(src_path):
    raise Exception('Could not find the source path ({})'.format(src_path))                
else:
    print('clear pycache')
    [ shutil.rmtree(f) for f in glob.glob(f"{src_path}/**/__pycache__", recursive=True) ] 

# backup the old one with time if the source path is same with the destination path or the backup option is enable
if (src_path==dst_path or backup_path):
    print('backup the original file, because the original path and the destination path is the same.')
    backup_path = './backup' if backup_path==None else backup_path
    if not os.path.exists(backup_path): os.makedirs(backup_path)
    shutil.copytree(src_path, os.path.join(backup_path, "{}_backup_{}".format(os.path.basename(src_path), get_time(+8) )))
    
# create a temp_dst for setup.py if the source path is not same with the destination path
temp_dst = os.path.join( os.getcwd(), '{}'.format(os.path.basename(dst_path)) )

if src_path != temp_dst:
    shutil.copytree(src_path, temp_dst, ignore=shutil.ignore_patterns(IGNORE_PATTERNS))
    print('create a temp_dst ({})'.format(temp_dst))

# Delete file in temp_dst
if delete_txt != None:
    with open(delete_txt) as f:
        contents = f.readlines()
        contents = [temp_dst + "/" +value.split("\n")[0].split("./")[1] for value in contents]
    for de in contents:
        if os.path.exists(de):
            print("Remove file:({})".format(de))
            os.remove(de)
            
# distutils
# cpature all python files but exclude __init__.py
print('start package')
extensions = [ f for f in glob.glob(f"{temp_dst}/**/*.py", recursive=True) if not ("__init__" in f) ]

# Exclude file
if exclude_txt != None:
    with open(exclude_txt) as f:
        contents = f.readlines()
        contents = [temp_dst + "/" +value.split("\n")[0].split("./")[1] for value in contents]
    folder_list = [ ed for ed in contents if os.path.isdir(ed)]
    if len(folder_list) > 0:
        for path in folder_list:
            for root, dirs, files in walk(path):
                for f in files:
                    fullpath = join(root, f)
                    contents.append(fullpath)
    for ed in contents:
        extensions = [ val for val in extensions if not (ed in val)]

setup(
    name=temp_dst,
    ext_modules=cythonize(extensions),
    cmdclass = {'build_ext': build_ext},
    build_dir=build_path
)

# remove build and `.py`
[ os.remove(f) for f in extensions ]
[ os.remove(f) for f in glob.glob(f"{temp_dst}/**/*.c", recursive=True) if not (EXCLUDE_CFILE in f)]

# remove the platform information from shared objects name 
print('renaming ...')
for f in glob.glob(f"{temp_dst}/**/*.so", recursive=True):
    trg_f = "{}.so".format(f.split('.cpython')[0]) if '.cpython' in f else f
    os.rename(f, trg_f)
    print(os.path.basename(f), " -> ", os.path.basename(trg_f))

# overwrite
if dst_path != temp_dst:
    if os.path.exists(dst_path):
        shutil.rmtree(dst_path)
    shutil.move(temp_dst, dst_path)

# remove something like build folder
[ shutil.rmtree(path) for path in [build_path] if os.path.exists(path) ]