from setuptools import setup

setup(name='better',
      version='0.1',
      description='Building Efficiency Targeting Tool for Energy Retrofits',
      url='https://github.com/LBNL-JCI-ICF/better',
      author='Han Li and Ahmed Bekhit',
      author_email='hanli@lbl.gov',
      license='LBNL Modified BSD',
      packages=['better'],
      entry_points={"console_scripts": ["better=better.cli:cli"]},
      install_requires=[
          'geocoder>=1.38.1',
          'ish_parser>=0.0.22',
          'numpy>=1.14.2',
          'pandas>=0.22.0',
          'scipy>=1.0.0',
          'xlrd>= 0.9.0',
          'click>= 6.7'
      ],
      zip_safe=False)



