from distutils.core import setup, Extension

hello_world_module = Extension('calculations',
                           sources = ['calc_price_module.c'])

setup(name = 'calculations module',
      version = '1.0',
      description = 'Python Package with C Extension for price calculation',
      ext_modules = [hello_world_module],
      url='http://noneyet.com',
      author='Joshua Schmid',
      author_email='jaiks at posteo dot de')
