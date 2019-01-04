from setuptools import setup

setup(name='CERC_BEE_Tool',
      version='0.1',
      description='Building targeting tool',
      url='http://github.com/',
      author='Han Li and Ahmed Bekhit',
      author_email='hanli@lbl.gov',
      license='MIT',
      packages=[],
      install_requires=[
          'geocoder>=1.38.1',
          'ish_parser>=0.0.22',
          'numpy>=1.14.2',
          'pandas>=0.22.0',
          'scipy>=1.0.0',
          'xlrd>= 0.9.0'
      ],
      zip_safe=False)



