# import os.path

from setuptools import setup, find_packages


setup(
    name='sql2xls_task',
    description='sql2xls_task sql to cls',
    long_description='readme',
    version="0.0.1",
    # use_scm_version={
    #     'version_scheme': 'post-release',
    #     'local_scheme': 'dirty-tag'
    # },
    url='',
    author='ppolxda',
    author_email='',
    classifiers=[],
    keywords='report_task',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    setup_requires=[
        'tenacity >= 4.7.0',
    ],
    install_requires=(
        'sqlalchemy >= 1.3.15',
        'pymysql >= 0.9.3',
        'psycopg2-binary >= 2.8.4',
        'minio >= 2.8.4',
        'xlwt >= 1.3.0',
        'redis >= 3.4.1',
        'sanic >= 19.12.2',
        'aiohttp >= 3.6.2',
    ),
    extras_require={':python_version >= "2.6"': ['argparse']},
    zip_safe=False,
    entry_points={
        # 'console_scripts': ['report_task = report_task.worker:main']
    }
)
