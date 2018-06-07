__version__ = '0.1.0'

from .reproducible import Context

# Create one instance and export its methods as module-level functions,
# similarly to the `random` standart module.
_context = Context(repo_path=None)

add_repo         = _context.add_repo
add_file         = _context.add_file
add_data     = _context.add_data
add_random_state = _context.add_random_state

save_json        = _context.save_json
save_yaml        = _context.save_yaml

git_info         = _context.git_info
git_dirty        = _context.git_dirty
