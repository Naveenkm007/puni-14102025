from setuptools import setup, find_packages

setup(
    name="personal-task-planner-bot",
    version="1.0.0",
    description="A personal task planner bot with Notion integration",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "flask>=2.3.2",
        "langchain>=0.0.207",
        "openai>=0.27.8",
        "requests>=2.31.0",
        "schedule>=1.2.0",
    ],
    entry_points={
        'console_scripts': [
            'task-planner=api:main',
        ],
    },
    python_requires=">=3.8",
)