from setuptools import setup

setup(
    name='aak_integration',
    version='0.1',
    decription='integration til serviceplatformen',
    author='Heini Leander Ovason',
    author_email='heini@magenta.dk',
    license="MPL 2.0",
    packages=['serviceplatformen_cpr', 'serviceplatformen_cvr'],
    zip_safe=False,
    install_requires=[
        'aak-integration==0.1',
        'appdirs==1.4.3',
        'cached-property==1.3.1',
        'certifi==2017.7.27.1',
        'chardet==3.0.4',
        'click==6.7',
        'defusedxml==0.5.0',
        'idna==2.6',
        'isodate==0.5.4',
        'Jinja2==2.9.6',
        'jinja2-cli==0.6.0',
        'lxml==4.0.0',
        'MarkupSafe==1.0',
        'python-dotenv==0.7.1',
        'pytz==2017.2',
        'requests==2.18.4',
        'requests-toolbelt==0.8.0',
        'six==1.11.0',
        'urllib3==1.22',
        'xmltodict==0.11.0',
        'zeep==2.4.0'
    ]
)
