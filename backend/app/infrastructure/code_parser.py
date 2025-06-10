import ast
from typing import Dict, Any, List
import re

class CodeParser:
    def parse_code(self, repo_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parsea el código del repositorio y extrae información relevante.
        """
        parsed_data = {
            "files": [],
            "functions": [],
            "classes": [],
            "imports": [],
            "structure": {}
        }

        for item in repo_content["contents"]:
            if item["type"] == "file":
                file_data = self._parse_file(item)
                if file_data:
                    parsed_data["files"].append(file_data)
                    parsed_data["functions"].extend(file_data.get("functions", []))
                    parsed_data["classes"].extend(file_data.get("classes", []))
                    parsed_data["imports"].extend(file_data.get("imports", []))

        return parsed_data

    def _parse_file(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parsea un archivo individual y extrae su estructura.
        """
        if not file_data["name"].endswith((".py", ".js", ".ts")):
            return None

        content = file_data.get("content", "")
        if not content:
            return None

        parsed = {
            "name": file_data["name"],
            "path": file_data["path"],
            "functions": [],
            "classes": [],
            "imports": []
        }

        if file_data["name"].endswith(".py"):
            return self._parse_python_file(content, parsed)
        else:
            return self._parse_js_file(content, parsed)

    def _parse_python_file(self, content: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parsea un archivo Python usando ast.
        """
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    parsed["functions"].append({
                        "name": node.name,
                        "docstring": ast.get_docstring(node),
                        "args": [arg.arg for arg in node.args.args],
                        "returns": self._get_return_type(node)
                    })
                elif isinstance(node, ast.ClassDef):
                    parsed["classes"].append({
                        "name": node.name,
                        "docstring": ast.get_docstring(node),
                        "methods": [
                            {
                                "name": method.name,
                                "docstring": ast.get_docstring(method),
                                "args": [arg.arg for arg in method.args.args]
                            }
                            for method in node.body
                            if isinstance(method, ast.FunctionDef)
                        ]
                    })
                elif isinstance(node, ast.Import):
                    parsed["imports"].extend([name.name for name in node.names])
                elif isinstance(node, ast.ImportFrom):
                    parsed["imports"].extend([f"{node.module}.{name.name}" for name in node.names])

        except Exception as e:
            print(f"Error parsing Python file: {e}")
            return None

        return parsed

    def _parse_js_file(self, content: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parsea un archivo JavaScript/TypeScript usando expresiones regulares.
        """
        # Extraer funciones
        function_pattern = r"function\s+(\w+)\s*\(([^)]*)\)\s*{([^}]*)}"
        functions = re.finditer(function_pattern, content)
        
        for func in functions:
            name, args, body = func.groups()
            parsed["functions"].append({
                "name": name,
                "args": [arg.strip() for arg in args.split(",") if arg.strip()],
                "body": body.strip()
            })

        # Extraer clases
        class_pattern = r"class\s+(\w+)\s*{([^}]*)}"
        classes = re.finditer(class_pattern, content)
        
        for cls in classes:
            name, body = cls.groups()
            parsed["classes"].append({
                "name": name,
                "methods": self._extract_js_methods(body)
            })

        # Extraer imports
        import_pattern = r"import\s+(?:{[^}]*}|\*\s+as\s+\w+|\w+)\s+from\s+['\"]([^'\"]+)['\"]"
        imports = re.finditer(import_pattern, content)
        parsed["imports"].extend([imp.group(1) for imp in imports])

        return parsed

    def _extract_js_methods(self, class_body: str) -> List[Dict[str, Any]]:
        """
        Extrae métodos de una clase JavaScript.
        """
        method_pattern = r"(\w+)\s*\(([^)]*)\)\s*{([^}]*)}"
        methods = re.finditer(method_pattern, class_body)
        
        return [{
            "name": method.group(1),
            "args": [arg.strip() for arg in method.group(2).split(",") if arg.strip()],
            "body": method.group(3).strip()
        } for method in methods]

    def _get_return_type(self, node: ast.FunctionDef) -> str:
        """
        Extrae el tipo de retorno de una función Python.
        """
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            elif isinstance(node.returns, ast.Subscript):
                return f"{node.returns.value.id}[{node.returns.slice.value.id}]"
        return None 