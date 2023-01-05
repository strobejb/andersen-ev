from setuptools import setup

setup(
    name='andersen-ev',
    version='0.1.0',    
    description='Python package for controlling the Andersen A2 EV charger',
    url='https://github.com/strobejb/andersen-ev',
    author='James Brown',
    author_email='',    
    license='MIT',
    packages=['andersen_ev'],
    install_requires=['pycognito',
                      'botocore',
                      'gql[all]',
                      ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',  
        'Operating System :: OS Independent',        
        'Programming Language :: Python :: 3.6',
    ],
)    