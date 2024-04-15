import sys
import os
sys.path.append(os.path.abspath('../..'))
# sys.path.insert(0, os.path.abspath('../..'))
# sys.path.append(os.path.abspath('../..'))
# sys.path.append(os.path.abspath('../..'))
# sys.path.append(os.path.abspath('../..'))
# sys.path.insert(0, os.path.abspath(os.path.join("..", "..")))

project = 'Contact management Application'
copyright = '2024, Serhii Rusetskyi'
author = 'Serhii Rusetskyi'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'nature'
html_static_path = ['_static']
