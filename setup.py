from setuptools import setup, find_packages

setup(name='diagnose',
      version='1',
      description='Diagnostic Tests for SD2 Experiments',
      url='',
      author='Anastasia Deckard & Tessa Johnson',
      author_email='anastasia.deckard@geomdata.com & tessa.johnson@geomdata.com',
      license='MIT',
      packages=find_packages('src'),
      package_dir={'':'src'},
      zip_safe=False)
