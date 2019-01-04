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
          'geocoder',
          'ish_parser',
          'matplotlib',
          'numpy',
          'pandas',
          'scipy',
          'xlrd >= 0.9.0'
      ],
      zip_safe=False)



