#!/usr/bin/env python

from setuptools import setup, find_packages


__author__ = 'Hardy.zheng'
__version = '0.1'

setup(
    name='cdsagent',
    version=__version,
    description='cdsagent ',
    author='hardy.Zheng',
    author_email='wei.zheng@yun-idc.com',
    install_requires=[
        'eventlet>=0.13.0',
        'PasteDeploy>=1.5.0',
        'six>=1.7.0',
        # 'pysphere>=0.5',
        'stevedore>=0.14',
        'jsonschema>=2.0.0,<3.0.0',
        'jsonpath-rw>=1.2.0,<2.0',
        'anyjson>=0.3.3'],
    packages=find_packages(),
    entry_points={
        'instance_create': [
            'create = cdsagent.instance:InstanceCreate'],
        'instance_delete': [
            'delete = cdsagent.instance:InstanceDelete'],
        'watch_dog': [
            'watch = cdsagent.instance:InstanceWatchDog'],
        },
    scripts=['cds-agent'],
    namespace_packages=['cdsagent'],
    include_package_data=True,
    )
