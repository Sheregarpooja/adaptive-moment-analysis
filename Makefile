# Makefile - CLI shortcuts for build and dev workflow

# Setup environment and build extension
setup:
	@bash setup.sh

# Setup and run unit tests
all:
	@bash setup.sh --test

# Build only the C++ extension
build:
	@python setup.py build_ext --inplace

# Retune the algorithm threshold
retune:
	@source venv/bin/activate && python main.py --retune

# Clean all build artifacts
clean:
	@rm -rf build dist __pycache__ .pytest_cache *.so .momentcore_build_cache momentcore.so venv
	@find . -name "*.pyc" -delete
