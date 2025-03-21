from setuptools import setup, find_packages

description = 'Pacote com objetos que serão utilizados para criação de sistemas automatizados dentro da empresa JauPesca'

setup(
    name='base_jp_lab',
    version='0.1.0',
    description=description,
    author='Bruno Lallo, Marcelo de Paula',
    author_email='brunolallo8@gmail.com, marcelodepaula.dev@gmai.com',
    packages=find_packages(),
    install_requires=[
        "requests==2.32.3", "selenium==4.24.0", "gspread==6.1.4", "oauth2client==4.1.3", "pandas==2.2.3", "mysql-connector==2.2.9", "cryptography==43.0.3", "grequests==0.7.0"
        ],
    license='MIT'
)