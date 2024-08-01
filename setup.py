from setuptools import setup, find_packages

setup(
    name='sri_xml_bot',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'altgraph==0.17.4',
        'et-xmlfile==1.1.0',
        'importlib-metadata==6.7.0',  # Considera actualizar a la última versión si es posible
        'openpyxl==3.1.1',
        'packaging==24.0',
        'pefile==2023.2.7',
        'pyinstaller==5.13.2',
        'pywin32-ctypes==0.2.2',
        'setuptools==68.0.0',  # Considera actualizar a la última versión si es posible
        'typing-extensions==4.7.1',
        'wheel==0.41.0',  # Considera actualizar a la última versión si es posible
        'zipp==3.15.0',  # Considera actualizar a la última versión si es posible
    ],
    entry_points={
        'console_scripts': [
            'sri_xml_bot=sri_xml_bot.main:main',  # Asegúrate de que 'main' sea la función de entrada correcta
        ],
    },
)

#pyinstaller main.spec