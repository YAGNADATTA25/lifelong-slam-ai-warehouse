import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'overhead_slam_simulation'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Include all launch files from the launch directory:
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        # Include all world files from the worlds directory:
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.world')),
        # Include config files:
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('lib', package_name), glob('scripts/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='yagnadatta',
    maintainer_email='your_email@domain.com',
    description='Overhead SLAM Simulation Package',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'auto_map = overhead_slam_simulation.auto_map:main',
        ],
    },
)