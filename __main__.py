import argparse
import datetime
import importlib
import os
import shutil

from dis_report import generate_report_html

_DATE_FORMAT = '%Y_%m_%d_%H_%M_%S'
_DIRECTORY_NAME = f'report_{datetime.datetime.strftime(datetime.datetime.now(), _DATE_FORMAT)}'
_STYLESHEET_PATH = os.path.join(os.path.split(__file__)[0], 'style.css')

parser = argparse.ArgumentParser(description='Generate python bytecode object disassembly report as a HTML document.')
parser.add_argument('module', help='Module from which to retrieve desired object')
parser.add_argument('object_name', help='Name of the object from which to retrieve CodeObject')
parser.add_argument('-o', help='Output filename', default='report.html', required=False)

args = parser.parse_args()
mod = importlib.import_module(args.module)
obj = getattr(mod, args.object_name, None)
if obj is None:
    raise RuntimeError(f'Object with name {args.object_name} not found.')
code = getattr(obj, '__code__', None)
if code is None:
    raise RuntimeError(f'Provided object has no "__code__" attribute.')

result_dir = os.path.join(os.getcwd(), _DIRECTORY_NAME)
os.mkdir(result_dir)
with open(os.path.join(result_dir, args.o), 'w+') as f:
    f.write(generate_report_html(code))

shutil.copy(_STYLESHEET_PATH, result_dir)
