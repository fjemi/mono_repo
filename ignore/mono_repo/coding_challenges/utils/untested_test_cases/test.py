from shared.get_module_at_path import app as get_module_at_path


path = '/home/femij/mono_repo/coding_challenges/utils/untested_test_cases/app.py'
module = get_module_at_path.main(path)
print(dir(module._object))

print(locals().keys())



from importlib.util import spec_from_loader, module_from_spec
from importlib.machinery import SourceFileLoader 
from os import path

file_path = '/home/femij/mono_repo/coding_challenges/utils/untested_test_cases/test_resources/arithmetic.py'
file_name = path.basename(file_path)
file_name = file_name.replace('.py', '')
file_directory = path.dirname(file_path)
folder_name = path.basename(file_directory)
module_name = f'{folder_name}_{file_name}'

spec = spec_from_loader(module_name, SourceFileLoader(module_name, file_path))
mod = module_from_spec(spec)
spec.loader.exec_module(mod)

globals()[module_name] = mod
print(locals().keys())
print(test_resources_arithmetic.use_add(1, 1))