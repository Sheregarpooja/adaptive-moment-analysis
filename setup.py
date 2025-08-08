import os
import hashlib
import glob
import shutil
from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

# -----------------------------------------------------------------------------
# Build Info:
# - Uses Pybind11 to build C++ extension "momentcore"
# - Caches build using file hash of source code and environment
# - Adds OpenMP support (set OMP_NUM_THREADS=X to tune thread count)
# -----------------------------------------------------------------------------

# List C++ source files (excluding headers)
source_files = [
    "bindings/bindings.cpp",
    "src/moments_pebay.cpp",
    "src/moments_twopass.cpp",
]

# Header file to track for rebuild
header_file = "src/moments.hpp"
build_cache_file = ".momentcore_build_cache"

def compute_source_hash(files_to_hash):
    """
    Generate a hash based on source files + OS + architecture + venv.
    Used to detect if rebuild is needed.
    """
    h = hashlib.sha256()
    for filepath in files_to_hash:
        with open(filepath, "rb") as f:
            h.update(f.read())
    h.update(os.uname().machine.encode())
    h.update(os.uname().sysname.encode())
    h.update(os.uname().version.encode())
    h.update(os.getenv("VIRTUAL_ENV", "").encode())
    return h.hexdigest()

# Determine if rebuild is needed
rebuild_required = True
current_hash = compute_source_hash(source_files + [header_file])

if os.path.exists(build_cache_file):
    with open(build_cache_file, "r") as f:
        if f.read().strip() == current_hash:
            rebuild_required = False

print("Rebuilding momentcore..." if rebuild_required else "No changes detected. Using cached build.")

# Extension module definition
ext_modules = [
    Pybind11Extension("momentcore", sources=source_files, cxx_std=17)
] if rebuild_required else []

# Setup config
setup(
    name="momentcore",
    version="0.1",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)

# Save hash and link .so file
if rebuild_required:
    with open(build_cache_file, "w") as f:
        f.write(current_hash)

    for sofile in glob.glob("momentcore*.so"):
        if sofile != "momentcore.so":
            try:
                if os.path.exists("momentcore.so"):
                    os.remove("momentcore.so")
                os.symlink(sofile, "momentcore.so")
                print(f"Linked {sofile} → momentcore.so")
            except Exception:
                shutil.copy(sofile, "momentcore.so")
                print(f"Copied {sofile} → momentcore.so")
            break
