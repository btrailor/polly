"""
Code Pattern Extractor
Uses AST parsing to detect patterns in code

This module analyzes code to discover:
- Common imports and libraries used
- Class structures and inheritance patterns
- Function signatures and decorators
- Error handling patterns
- Async/await usage
- Framework-specific patterns
"""

import ast
import re
from typing import List, Dict
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class CodePatternExtractor:
    """Extract patterns from code using AST parsing and regex."""
    
    def extract_from_python(self, code: str) -> List[Dict]:
        """
        Extract patterns from Python code.
        
        Patterns detected:
        - Common imports
        - Class structures
        - Function signatures
        - Decorator usage
        - Error handling patterns
        - Async patterns
        """
        patterns = []
        
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            logger.warning(f"Failed to parse Python code: {e}")
            return patterns
        
        # Extract imports
        imports = []
        from_imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for alias in node.names:
                        from_imports.append(f"{node.module}.{alias.name}")
        
        all_imports = imports + from_imports
        
        if all_imports:
            import_counter = Counter(all_imports)
            patterns.append({
                'type': 'imports',
                'pattern': 'Common imports',
                'details': import_counter.most_common(10)
            })
        
        # Extract class patterns
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        if classes:
            # Detect inheritance patterns
            base_classes = []
            for cls in classes:
                for base in cls.bases:
                    if isinstance(base, ast.Name):
                        base_classes.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        base_classes.append(f"{base.value.id}.{base.attr}" if isinstance(base.value, ast.Name) else base.attr)
            
            if base_classes:
                base_counter = Counter(base_classes)
                patterns.append({
                    'type': 'inheritance',
                    'pattern': 'Class inheritance',
                    'details': base_counter.most_common(5)
                })
            
            # Detect class decorator patterns
            class_decorators = []
            for cls in classes:
                for dec in cls.decorator_list:
                    if isinstance(dec, ast.Name):
                        class_decorators.append(dec.id)
                    elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name):
                        class_decorators.append(dec.func.id)
            
            if class_decorators:
                dec_counter = Counter(class_decorators)
                patterns.append({
                    'type': 'decorators',
                    'pattern': 'Class decorators',
                    'details': dec_counter.most_common(5)
                })
        
        # Extract function patterns
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        async_functions = [node for node in ast.walk(tree) if isinstance(node, ast.AsyncFunctionDef)]
        
        if functions or async_functions:
            # Detect async functions
            if async_functions:
                patterns.append({
                    'type': 'async',
                    'pattern': 'Async functions',
                    'count': len(async_functions),
                    'names': [f.name for f in async_functions[:5]]
                })
            
            # Detect function decorators
            func_decorators = []
            for func in functions + async_functions:
                for dec in func.decorator_list:
                    if isinstance(dec, ast.Name):
                        func_decorators.append(dec.id)
                    elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name):
                        func_decorators.append(dec.func.id)
            
            if func_decorators:
                dec_counter = Counter(func_decorators)
                patterns.append({
                    'type': 'decorators',
                    'pattern': 'Function decorators',
                    'details': dec_counter.most_common(5)
                })
        
        # Detect try/except patterns
        try_blocks = [node for node in ast.walk(tree) if isinstance(node, ast.Try)]
        
        if try_blocks:
            exception_types = []
            for try_block in try_blocks:
                for handler in try_block.handlers:
                    if handler.type:
                        if isinstance(handler.type, ast.Name):
                            exception_types.append(handler.type.id)
                        elif isinstance(handler.type, ast.Tuple):
                            for exc in handler.type.elts:
                                if isinstance(exc, ast.Name):
                                    exception_types.append(exc.id)
            
            if exception_types:
                exc_counter = Counter(exception_types)
                patterns.append({
                    'type': 'error_handling',
                    'pattern': 'Exception handling',
                    'details': exc_counter.most_common(5),
                    'try_blocks': len(try_blocks)
                })
        
        # Detect context managers (with statements)
        with_stmts = [node for node in ast.walk(tree) if isinstance(node, ast.With)]
        
        if with_stmts:
            patterns.append({
                'type': 'context_managers',
                'pattern': 'Context managers (with statements)',
                'count': len(with_stmts)
            })
        
        # Detect comprehensions
        list_comps = [node for node in ast.walk(tree) if isinstance(node, ast.ListComp)]
        dict_comps = [node for node in ast.walk(tree) if isinstance(node, ast.DictComp)]
        
        if list_comps or dict_comps:
            patterns.append({
                'type': 'comprehensions',
                'pattern': 'List/Dict comprehensions',
                'list_comps': len(list_comps),
                'dict_comps': len(dict_comps)
            })
        
        return patterns
    
    def extract_from_javascript(self, code: str) -> List[Dict]:
        """
        Extract patterns from JavaScript code using regex.
        
        Patterns detected:
        - Framework usage (React, Vue, etc.)
        - Async/await patterns
        - Arrow functions
        - Promise usage
        - Common imports
        """
        patterns = []
        
        # Detect React patterns
        if re.search(r"import\s+React|from\s+['\"]react['\"]|from\s+['\"]@react", code):
            patterns.append({
                'type': 'framework',
                'pattern': 'React',
                'indicators': []
            })
            
            # Detect React hooks
            hooks = re.findall(r'\b(use[A-Z]\w+)\s*\(', code)
            if hooks:
                hook_counter = Counter(hooks)
                patterns.append({
                    'type': 'react_hooks',
                    'pattern': 'React Hooks',
                    'details': hook_counter.most_common(5)
                })
            
            # Detect JSX usage
            if re.search(r'<[A-Z]\w+|<[a-z]+[\s>]', code):
                patterns.append({
                    'type': 'jsx',
                    'pattern': 'JSX syntax'
                })
        
        # Detect Vue patterns
        if re.search(r"from\s+['\"]vue['\"]|@vue/", code):
            patterns.append({
                'type': 'framework',
                'pattern': 'Vue'
            })
        
        # Detect async/await
        async_funcs = re.findall(r'async\s+(?:function|[a-zA-Z_$][\w$]*\s*=)', code)
        await_calls = re.findall(r'\bawait\s+', code)
        
        if async_funcs or await_calls:
            patterns.append({
                'type': 'async',
                'pattern': 'Async/await',
                'async_functions': len(async_funcs),
                'await_calls': len(await_calls)
            })
        
        # Detect arrow functions
        arrow_funcs = len(re.findall(r'=>', code))
        if arrow_funcs > 0:
            patterns.append({
                'type': 'style',
                'pattern': 'Arrow functions',
                'count': arrow_funcs
            })
        
        # Detect Promise usage
        if re.search(r'\.then\(|\.catch\(|new\s+Promise\(', code):
            then_count = len(re.findall(r'\.then\(', code))
            catch_count = len(re.findall(r'\.catch\(', code))
            patterns.append({
                'type': 'async',
                'pattern': 'Promises',
                'then_calls': then_count,
                'catch_calls': catch_count
            })
        
        # Detect common imports
        import_matches = re.findall(r"import\s+.+\s+from\s+['\"]([^'\"]+)['\"]", code)
        if import_matches:
            import_counter = Counter(import_matches)
            patterns.append({
                'type': 'imports',
                'pattern': 'Common imports',
                'details': import_counter.most_common(10)
            })
        
        # Detect TypeScript patterns
        if re.search(r':\s*(?:string|number|boolean|any|void|never)\b', code) or \
           re.search(r'interface\s+\w+|type\s+\w+\s*=', code):
            patterns.append({
                'type': 'language',
                'pattern': 'TypeScript'
            })
        
        # Detect class-based components
        class_components = re.findall(r'class\s+(\w+)\s+extends\s+(?:React\.)?Component', code)
        if class_components:
            patterns.append({
                'type': 'react_class',
                'pattern': 'Class-based React components',
                'count': len(class_components)
            })
        
        # Detect functional components
        func_components = re.findall(r'(?:function|const)\s+([A-Z]\w+)\s*(?:=\s*)?(?:\([^)]*\))?\s*(?:=>)?\s*{', code)
        if func_components:
            patterns.append({
                'type': 'react_functional',
                'pattern': 'Functional components',
                'count': len(func_components)
            })
        
        return patterns
    
    def extract_patterns(self, code: str, language: str = None) -> List[Dict]:
        """
        Extract patterns from code, auto-detecting language if not specified.
        
        Args:
            code: The source code to analyze
            language: Optional language hint ('python', 'javascript', 'typescript')
        
        Returns:
            List of detected patterns
        """
        if not code or not code.strip():
            return []
        
        # Auto-detect language if not specified
        if language is None:
            # Simple heuristics
            if 'def ' in code or 'import ' in code and ':' in code:
                language = 'python'
            elif 'function ' in code or 'const ' in code or '=>' in code:
                language = 'javascript'
        
        if language == 'python':
            return self.extract_from_python(code)
        elif language in ('javascript', 'typescript', 'jsx', 'tsx'):
            return self.extract_from_javascript(code)
        else:
            logger.warning(f"Unknown language: {language}")
            return []
