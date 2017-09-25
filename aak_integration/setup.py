from setuptools import setup

setup(name='aak_integration',
      version='0.1',
      decription='integration til serviceplatformen',
      author='Heini Leander Ovason',
      author_email='heini@magenta.dk',
      license="MPL 2.0",
      packages=['serviceplatformen_cpr',],
      install_requires= [
          'certifi==2017.7.27.1',
          'chardet==3.0.4',
          'click==6.7',
          'idna==2.6',
          'Jinja2==2.9.6',
          'jinja2-cli==0.6.0',
          'MarkupSafe==1.0',
          'python-dotenv==0.7.1',
          'requests==2.18.4',
          'urllib3==1.22',
          'xmltodict==0.11.0'
      ],
      zip_safe=False)


