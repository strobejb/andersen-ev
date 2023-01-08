from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='andersen-ev',
    version='0.1.1',    
    description='Python package for controlling the Andersen A2 EV charger',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/strobejb/andersen-ev',
    author='James Brown',
    author_email='',    
    license='MIT',
    packages=['andersen_ev'],
    include_package_data=True,
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