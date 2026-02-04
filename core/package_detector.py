"""
Package Detector
Phase 23.5: Security Hardening

Detects when LLM suggests package installations in generated code.
Scans code for import statements and pip install suggestions.
"""

import re
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)


class PackageSource(Enum):
    """Source where package was detected."""
    IMPORT = "import"
    FROM_IMPORT = "from_import"
    PIP_INSTALL = "pip_install"
    REQUIREMENTS_TXT = "requirements_txt"


@dataclass
class PackageReference:
    """Reference to a package found in code."""
    name: str
    source: PackageSource
    line_number: int
    context: str  # Line of code where found
    requires_approval: bool = True  # Will be set based on allowlist


class PackageDetector:
    """
    Detect when LLM suggests package installations in code.
    
    Scans code for:
    - import statements (import package_name)
    - from imports (from package_name import ...)
    - pip install suggestions in comments/docstrings
    - requirements.txt references
    """
    
    # Python standard library modules (always safe, no approval needed)
    # This is a subset - full list would be ~200+ modules
    STDLIB_MODULES = {
        'os', 'sys', 'json', 're', 'datetime', 'pathlib', 'typing',
        'collections', 'itertools', 'functools', 'asyncio', 'logging',
        'math', 'random', 'string', 'urllib', 'http', 'html', 'xml',
        'csv', 'sqlite3', 'hashlib', 'base64', 'uuid', 'time', 'calendar',
        'copy', 'pickle', 'io', 'tempfile', 'shutil', 'glob', 'fnmatch',
        'statistics', 'decimal', 'fractions', 'array', 'bisect', 'heapq',
        'queue', 'threading', 'multiprocessing', 'concurrent', 'subprocess',
        'socket', 'ssl', 'email', 'mimetypes', 'zipfile', 'tarfile',
        'gzip', 'bz2', 'lzma', 'zlib', 'codecs', 'unicodedata', 'locale',
        'gettext', 'argparse', 'getopt', 'readline', 'rlcompleter',
        'cmd', 'shlex', 'configparser', 'netrc', 'xdrlib', 'plistlib',
        'secrets', 'hashlib', 'hmac', 'secrets', 'doctest', 'unittest',
        'pdb', 'profile', 'pstats', 'trace', 'tracemalloc', 'gc', 'inspect',
        'site', 'sysconfig', 'builtins', '__builtin__', '__main__', 'warnings',
        'contextlib', 'abc', 'atexit', 'traceback', 'future_builtins',
        'imp', 'importlib', 'pkgutil', 'modulefinder', 'runpy', 'parser',
        'ast', 'symtable', 'symbol', 'token', 'tokenize', 'keyword', 'tabnanny',
        'py_compile', 'compileall', 'dis', 'pickletools', 'formatter',
        'msilib', 'msvcrt', 'winreg', 'winsound', 'posix', 'pwd', 'spwd',
        'grp', 'crypt', 'termios', 'tty', 'pty', 'fcntl', 'pipes', 'resource',
        'nis', 'syslog', 'dbm', 'gdbm', 'dbm.ndbm', 'dbm.gnu', 'dbm.dumb',
        'sqlite3', 'zlib', 'gzip', 'bz2', 'lzma', 'zipfile', 'tarfile',
        'csv', 'configparser', 'netrc', 'xdrlib', 'plistlib', 'logging',
        'getopt', 'argparse', 'getpass', 'curses', 'platform', 'errno',
        'ctypes', 'struct', 'codecs', 'encodings', 'unicodedata', 'stringprep',
        'readline', 'rlcompleter', 'cmd', 'shlex', 'configparser', 'netrc',
        'xdrlib', 'plistlib', 'secrets', 'hashlib', 'hmac', 'secrets',
        'doctest', 'unittest', 'pdb', 'profile', 'pstats', 'trace',
        'tracemalloc', 'gc', 'inspect', 'site', 'sysconfig', 'builtins',
        '__builtin__', '__main__', 'warnings', 'contextlib', 'abc', 'atexit',
        'traceback', 'future_builtins', 'imp', 'importlib', 'pkgutil',
        'modulefinder', 'runpy', 'parser', 'ast', 'symtable', 'symbol',
        'token', 'tokenize', 'keyword', 'tabnanny', 'py_compile', 'compileall',
        'dis', 'pickletools', 'formatter'
    }
    
    def __init__(self, allowlist_path: Optional[Path] = None):
        """
        Initialize package detector with allowlist.
        
        Args:
            allowlist_path: Path to approved_packages.yaml (defaults to config/approved_packages.yaml)
        """
        self.allowlist_path = allowlist_path or self._find_allowlist()
        self.approved_packages: Set[str] = set()
        self.blocked_packages: Set[str] = set()
        self._load_allowlist()
    
    def _find_allowlist(self) -> Path:
        """Find approved packages allowlist file."""
        locations = [
            Path.cwd() / "config" / "approved_packages.yaml",
            Path(__file__).parent.parent / "config" / "approved_packages.yaml",
            Path.home() / ".polly" / "approved_packages.yaml"
        ]
        
        for loc in locations:
            if loc.exists():
                return loc
        
        # Return default location even if doesn't exist
        return Path(__file__).parent.parent / "config" / "approved_packages.yaml"
    
    def _load_allowlist(self) -> None:
        """Load approved and blocked packages from allowlist file."""
        if not self.allowlist_path or not self.allowlist_path.exists():
            logger.warning(f"Package allowlist not found at {self.allowlist_path}. Using defaults.")
            # Use some common safe packages as defaults
            self.approved_packages = {
                'numpy', 'pandas', 'matplotlib', 'scikit-learn', 'scipy',
                'requests', 'httpx', 'aiohttp', 'flask', 'fastapi',
                'pytest', 'unittest', 'black', 'ruff', 'mypy'
            }
            return
        
        try:
            with open(self.allowlist_path) as f:
                config = yaml.safe_load(f) or {}
            
            # Load approved packages
            approved = config.get("approved_packages", [])
            self.approved_packages = set(pkg.lower() for pkg in approved)
            
            # Load blocked packages
            blocked = config.get("blocked_packages", [])
            self.blocked_packages = set(pkg.lower() for pkg in blocked)
            
            # Stdlib is always approved (add to approved set)
            stdlib = config.get("stdlib_modules", [])
            self.approved_packages.update(pkg.lower() for pkg in stdlib)
            
            logger.info(f"Loaded {len(self.approved_packages)} approved packages, {len(self.blocked_packages)} blocked packages")
        except Exception as e:
            logger.error(f"Failed to load package allowlist: {e}")
            # Use defaults
            self.approved_packages = {'numpy', 'pandas', 'requests', 'pytest'}
    
    def scan_code(self, code: str) -> List[PackageReference]:
        """
        Scan code for package references.
        
        Detects:
        - import package_name
        - from package_name import ...
        - pip install package_name (in comments/docstrings)
        - requirements.txt references
        
        Args:
            code: Python code to scan
            
        Returns:
            List of PackageReference objects for packages that need approval
        """
        packages = []
        lines = code.split('\n')
        
        # Pattern for import statements: import package_name
        import_pattern = re.compile(r'^\s*import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)')
        
        # Pattern for from imports: from package_name import ...
        from_import_pattern = re.compile(r'^\s*from\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import')
        
        # Pattern for pip install in comments/docstrings
        pip_install_pattern = re.compile(r'pip\s+install\s+([a-zA-Z0-9_-]+)', re.IGNORECASE)
        
        # Pattern for requirements.txt style
        requirements_pattern = re.compile(r'^([a-zA-Z0-9_-]+)(?:[<>=!]+.*)?$')
        
        for line_num, line in enumerate(lines, start=1):
            # Check for import statements
            import_match = import_pattern.match(line)
            if import_match:
                package_name = import_match.group(1).split('.')[0]  # Get top-level package
                if not self._is_stdlib(package_name):
                    packages.append(PackageReference(
                        name=package_name,
                        source=PackageSource.IMPORT,
                        line_number=line_num,
                        context=line.strip(),
                        requires_approval=not self._is_approved(package_name)
                    ))
            
            # Check for from imports
            from_match = from_import_pattern.match(line)
            if from_match:
                package_name = from_match.group(1).split('.')[0]  # Get top-level package
                if not self._is_stdlib(package_name):
                    packages.append(PackageReference(
                        name=package_name,
                        source=PackageSource.FROM_IMPORT,
                        line_number=line_num,
                        context=line.strip(),
                        requires_approval=not self._is_approved(package_name)
                    ))
            
            # Check for pip install in comments/docstrings
            pip_matches = pip_install_pattern.findall(line)
            for package_name in pip_matches:
                if not self._is_stdlib(package_name):
                    packages.append(PackageReference(
                        name=package_name,
                        source=PackageSource.PIP_INSTALL,
                        line_number=line_num,
                        context=line.strip(),
                        requires_approval=not self._is_approved(package_name)
                    ))
        
        # Remove duplicates (same package found multiple times)
        seen = set()
        unique_packages = []
        for pkg in packages:
            key = (pkg.name.lower(), pkg.source)
            if key not in seen:
                seen.add(key)
                unique_packages.append(pkg)
        
        # Filter to only packages that require approval
        unapproved = [pkg for pkg in unique_packages if pkg.requires_approval]
        
        if unapproved:
            logger.info(f"Found {len(unapproved)} unapproved packages in code: {[p.name for p in unapproved]}")
        
        return unapproved
    
    def _is_stdlib(self, package_name: str) -> bool:
        """Check if package is Python standard library."""
        return package_name.lower() in self.STDLIB_MODULES
    
    def _is_approved(self, package_name: str) -> bool:
        """Check if package is in approved allowlist."""
        return package_name.lower() in self.approved_packages
    
    def _is_blocked(self, package_name: str) -> bool:
        """Check if package is explicitly blocked."""
        return package_name.lower() in self.blocked_packages
    
    def requires_approval(self, packages: List[PackageReference]) -> bool:
        """Check if any packages need user approval."""
        return len([p for p in packages if p.requires_approval]) > 0
    
    def get_unapproved_packages(self, packages: List[PackageReference]) -> List[str]:
        """Get list of unapproved package names."""
        return [p.name for p in packages if p.requires_approval]


# Global package detector instance
_package_detector: Optional[PackageDetector] = None


def get_package_detector() -> PackageDetector:
    """Get global package detector instance."""
    global _package_detector
    if _package_detector is None:
        _package_detector = PackageDetector()
    return _package_detector
