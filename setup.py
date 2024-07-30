from setuptools import setup, find_packages

setup(
    name='sri_xml_bot',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # Lista de dependencias, por ejemplo:
        # 'numpy',
    ],
    entry_points={
        'console_scripts': [
            'sri_xml_bot=sri_xml_bot.main:main',
        ],
    },
)
