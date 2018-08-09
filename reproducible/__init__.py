__version__ = '0.2.3'

from .reproducible import Context

# Create one instance and export its methods as module-level functions,
# similarly to the `random` standart module.
_context = Context(repo_path=None)

reset            = _context.reset
data             = _context.data

function_args    = _context.function_args

add_repo         = _context.add_repo
add_file         = _context.add_file
add_data         = _context.add_data
add_random_state = _context.add_random_state

json                = _context.json
yaml                = _context.yaml
requirements        = _context.requirements
export_json         = _context.export_json
export_yaml         = _context.export_yaml
export_requirements = _context.export_requirements

git_info         = _context.git_info
git_dirty        = _context.git_dirty


# Deprecated, will be removed in a future version
save_json        = _context.save_json
save_yaml        = _context.save_yaml
