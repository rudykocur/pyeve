__author__ = 'Rudy'

from setuptools import setup

setup(
    name='PyEve',
    version='0.1.0',
    author='Rudykocur',
    author_email='grzegorz.przydryga@gmail.com',
    packages=['pyeve', 'pyeve.eveapi'],
    # scripts=['bin/stowe-towels.py','bin/wash-towels.py'],
    # url='http://pypi.python.org/pypi/TowelStuff/',
    # license='LICENSE.txt',
    description='Lorem ipsum ...',
    # long_description=open('README.txt').read(),
    install_requires=[
        # "Django >= 1.1.1",
        # "caldav == 0.1.4",
        'Werkzeug',
        'Breve',
        'WTForms',
        'sqlalchemy',
        'alembic',
        'pyyaml'
    ],
    entry_points={
        'UIModules': [
            'profile = pyeve.www.pages.profile:ProfileModule',
            'skills = pyeve.www.pages.skills:SkillsModule',
            'scanning = pyeve.www.pages.scanning:ScanningModule',
        ]
    }
)