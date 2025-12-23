#!/usr/bin/env python3
"""
Lambda deployment package creator using uv.
"""

import argparse
import logging
import os
import site
import sys
import shutil
import zipfile
from pathlib import Path


def create_deployment_package(venv_path=None, out_zip=None, dry_run=False, exclude_pkgs=None):
    """Create a Lambda deployment package with dependencies from uv.

    Args:
        venv_path (str|Path): Optional path to virtualenv root. If None, tries VIRTUAL_ENV or sys.executable.
        out_zip (str|Path): Output path for the zip file. Defaults to ./lambda_function.zip
        dry_run (bool): If True, show what would be included but don't create zip.
        exclude_pkgs (list): List of top-level package names to exclude from copying (e.g., boto3).
    """

    logger = logging.getLogger(__name__)

    # Paths
    current_dir = Path(__file__).parent
    build_dir = current_dir / 'build'
    package_dir = build_dir / 'package'
    zip_path = Path(out_zip) if out_zip else current_dir / 'lambda_function.zip'

    # Resolve virtualenv site-packages robustly
    site_packages = None
    if venv_path:
        venv_root = Path(venv_path)
    else:
        # Prefer VIRTUAL_ENV environment variable
        venv_root = Path(os.getenv('VIRTUAL_ENV') or '')
        if not venv_root.exists():
            # Fallback to deriving from sys.executable
            # Typical venv layout: <venv>/bin/python (Unix) or <venv>/Scripts/python.exe (Windows)
            venv_root = Path(sys.executable).parents[1]

    # Candidate site-packages locations
    candidates = []
    # Common *nix path
    candidates.append(venv_root / 'lib')
    # Common Windows path
    candidates.append(venv_root / 'Lib')
    # Try python's site module as a fallback
    for sp in site.getsitepackages() if hasattr(site, 'getsitepackages') else []:
        candidates.append(Path(sp))

    for base in candidates:
        try:
            for path in base.rglob('site-packages'):
                site_packages = path
                break
        except Exception:
            continue
        if site_packages:
            break

    if not site_packages or not site_packages.exists():
        logger.error("Could not find site-packages. Provide --venv or ensure the venv is activated and contains installed dependencies.")
        sys.exit(1)

    logger.info(f"Copying dependencies from {site_packages}...")

    # Clean up previous builds
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if zip_path.exists():
        os.remove(zip_path)

    # Create build directory
    package_dir.mkdir(parents=True, exist_ok=True)

    # Default exclusions
    if exclude_pkgs is None:
        exclude_pkgs = ['boto3', 'botocore', 's3transfer']

    # Copy all dependencies to package directory
    for item in site_packages.iterdir():
        name = item.name
        # Skip dist-info and caches
        if name.endswith('.dist-info') or name == '__pycache__':
            continue
        # Skip excluded top-level packages
        if any(name == pkg or name.startswith(pkg + '-') for pkg in exclude_pkgs):
            logger.debug(f"Skipping excluded package: {name}")
            continue
        try:
            if item.is_dir():
                shutil.copytree(item, package_dir / name, dirs_exist_ok=True)
            else:
                shutil.copy2(item, package_dir)
        except Exception as e:
            logger.warning(f"Failed to copy {name}: {e}")
    
    # Copy Lambda function code
    logger.info("Copying Lambda function code...")

    # Copy S3 Vectors Lambda handlers
    handlers = []
    if (current_dir / 'ingest_s3vectors.py').exists():
        handlers.append('ingest_s3vectors.py')
        shutil.copy(current_dir / 'ingest_s3vectors.py', package_dir)
    if (current_dir / 'search_s3vectors.py').exists():
        handlers.append('search_s3vectors.py')
        shutil.copy(current_dir / 'search_s3vectors.py', package_dir)

    if dry_run:
        # Show a summary of what would be included
        included = [p.name for p in package_dir.iterdir()]
        print("Dry run - package would include the following top-level entries:")
        for name in sorted(included):
            print(f" - {name}")
        # Clean up build dir
        shutil.rmtree(build_dir)
        return "dry-run"

    # Create ZIP file
    logger.info("Creating deployment package...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            # Skip __pycache__ directories
            dirs[:] = [d for d in dirs if d != '__pycache__']
            for file in files:
                if file.endswith('.pyc'):
                    continue
                file_path = Path(root) / file
                arcname = file_path.relative_to(package_dir)
                zipf.write(file_path, arcname)

    # Clean up build directory
    shutil.rmtree(build_dir)

    # Get file size
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    logger.info(f"\n✅ Deployment package created: {zip_path}")
    logger.info(f"   Size: {size_mb:.2f} MB")

    if size_mb > 50:
        logger.warning("Package exceeds 50MB. Consider using Lambda Layers.")

    return str(zip_path)


def _parse_args():
    parser = argparse.ArgumentParser(description='Create a Lambda deployment package')
    parser.add_argument('--venv', help='Path to virtualenv root (optional)')
    parser.add_argument('--out', help='Output zip file path (optional)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be included without creating the zip')
    parser.add_argument('--exclude', help='Comma-separated package names to exclude (default: boto3,botocore,s3transfer)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format='%(levelname)s: %(message)s')
    exclude = args.exclude.split(',') if args.exclude else None
    pkg = create_deployment_package(venv_path=args.venv, out_zip=args.out, dry_run=args.dry_run, exclude_pkgs=exclude)
    if pkg == 'dry-run':
        print('Dry run completed.')
    else:
        print(f'Deployment package: {pkg}')
