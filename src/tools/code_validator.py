"""
Módulo de Validación de Código

Este módulo proporciona funcionalidades para validar código generado,
incluyendo sintaxis, imports, contratos de interfaz y ejecución básica.
"""

import os
import ast
import json
import subprocess
import tempfile
from typing import Dict, List, Optional, Tuple
from .contract_manager import contract_manager
from .project_manager import get_project_path


class CodeValidator:
    """Validador de código generado."""
    
    def __init__(self):
        pass
    
    def validate_python_syntax(self, code: str) -> Dict[str, any]:
        """
        Valida la sintaxis de código Python.
        
        Args:
            code: Código Python a validar
            
        Returns:
            Dict con resultado: {"valid": bool, "errors": List[str]}
        """
        result = {"valid": True, "errors": []}
        
        try:
            ast.parse(code)
        except SyntaxError as e:
            result["valid"] = False
            result["errors"].append(f"Error de sintaxis en línea {e.lineno}: {e.msg}")
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Error al parsear código: {str(e)}")
        
        return result
    
    def validate_javascript_syntax(self, code: str) -> Dict[str, any]:
        """
        Valida la sintaxis de código JavaScript (requiere Node.js instalado).
        
        Args:
            code: Código JavaScript a validar
            
        Returns:
            Dict con resultado: {"valid": bool, "errors": List[str]}
        """
        result = {"valid": True, "errors": [], "warnings": []}
        
        # Verificar si Node.js está disponible
        try:
            subprocess.run(
                ["node", "--version"],
                capture_output=True,
                timeout=2
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            result["warnings"].append("Node.js no está instalado, no se puede validar sintaxis JavaScript")
            return result
        
        # Crear archivo temporal y validar
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_file = f.name
            
            # Intentar parsear con Node.js
            proc = subprocess.run(
                ["node", "--check", temp_file],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if proc.returncode != 0:
                result["valid"] = False
                result["errors"].append(f"Error de sintaxis JavaScript: {proc.stderr}")
            
            # Limpiar archivo temporal
            os.unlink(temp_file)
            
        except Exception as e:
            result["warnings"].append(f"No se pudo validar sintaxis JavaScript: {str(e)}")
        
        return result
    
    def validate_html_syntax(self, code: str) -> Dict[str, any]:
        """
        Valida la sintaxis básica de HTML.
        
        Args:
            code: Código HTML a validar
            
        Returns:
            Dict con resultado: {"valid": bool, "errors": List[str], "warnings": List[str]}
        """
        result = {"valid": True, "errors": [], "warnings": []}
        
        # Validaciones básicas
        if not code.strip():
            result["valid"] = False
            result["errors"].append("El código HTML está vacío")
            return result
        
        # Verificar etiquetas básicas
        if "<!DOCTYPE" not in code and "<html" not in code:
            result["warnings"].append("Falta declaración DOCTYPE o etiqueta <html>")
        
        # Verificar balance de etiquetas comunes
        common_tags = ["html", "head", "body", "div", "script", "style"]
        for tag in common_tags:
            open_count = code.count(f"<{tag}")
            close_count = code.count(f"</{tag}>")
            if open_count != close_count:
                result["warnings"].append(f"Posible desbalance en etiquetas <{tag}>: {open_count} aperturas, {close_count} cierres")
        
        return result
    
    def validate_file_syntax(self, filepath: str) -> Dict[str, any]:
        """
        Valida la sintaxis de un archivo según su extensión.
        
        Args:
            filepath: Ruta al archivo
            
        Returns:
            Dict con resultado de validación
        """
        if not os.path.exists(filepath):
            return {"valid": False, "errors": [f"El archivo {filepath} no existe"]}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            return {"valid": False, "errors": [f"Error al leer archivo: {str(e)}"]}
        
        # Determinar tipo de archivo
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext == '.py':
            return self.validate_python_syntax(code)
        elif ext in ['.js', '.mjs']:
            return self.validate_javascript_syntax(code)
        elif ext in ['.html', '.htm']:
            return self.validate_html_syntax(code)
        else:
            return {"valid": True, "warnings": [f"No hay validador para archivos {ext}"]}
    
    def validate_python_imports(self, code: str) -> Dict[str, any]:
        """
        Valida que los imports de Python sean válidos.
        
        Args:
            code: Código Python
            
        Returns:
            Dict con resultado: {"valid": bool, "missing_imports": List[str], "errors": List[str]}
        """
        result = {"valid": True, "missing_imports": [], "errors": []}
        
        try:
            tree = ast.parse(code)
        except:
            result["valid"] = False
            result["errors"].append("No se pudo parsear el código para validar imports")
            return result
        
        # Extraer imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module.split('.')[0])
        
        # Verificar si los módulos están disponibles
        for module in set(imports):
            try:
                __import__(module)
            except ImportError:
                result["missing_imports"].append(module)
        
        if result["missing_imports"]:
            result["valid"] = False
        
        return result
    
    def validate_api_contracts(self, project_id: str, code: str, code_type: str) -> Dict[str, any]:
        """
        Valida que el código cumpla con los contratos de API definidos.
        
        Args:
            project_id: ID del proyecto
            code: Código a validar
            code_type: Tipo de código ('frontend' o 'backend')
            
        Returns:
            Dict con resultado de validación
        """
        result = {"valid": True, "errors": [], "warnings": []}
        
        # Obtener contratos de API
        api_contracts = contract_manager.get_api_contracts(project_id)
        
        if not api_contracts:
            result["warnings"].append("No hay contratos de API definidos para validar")
            return result
        
        # Validar según el tipo de código
        if code_type == "backend":
            # Verificar que los endpoints estén definidos
            for contract in api_contracts:
                endpoint = contract["endpoint"]
                method = contract["method"]
                
                # Buscar definición del endpoint en el código (búsqueda simple)
                if endpoint.replace('/', '') not in code and endpoint not in code:
                    result["warnings"].append(
                        f"No se encontró implementación del endpoint {method} {endpoint}"
                    )
        
        elif code_type == "frontend":
            # Verificar que se consuman los endpoints
            for contract in api_contracts:
                endpoint = contract["endpoint"]
                
                # Buscar uso del endpoint en el código
                if endpoint not in code:
                    result["warnings"].append(
                        f"El endpoint {endpoint} no parece ser usado en el frontend"
                    )
        
        return result
    
    def validate_project_code(self, project_id: str) -> Dict[str, any]:
        """
        Valida todo el código de un proyecto.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Dict con resultados de validación por archivo
        """
        results = {
            "overall_valid": True,
            "files": {},
            "summary": {
                "total_files": 0,
                "valid_files": 0,
                "files_with_errors": 0,
                "files_with_warnings": 0
            }
        }
        
        project_path = get_project_path(project_id)
        
        if not os.path.exists(project_path):
            results["overall_valid"] = False
            results["error"] = f"El proyecto {project_id} no existe"
            return results
        
        # Recorrer archivos del proyecto
        for root, dirs, files in os.walk(project_path):
            # Ignorar carpeta de contratos
            if "contracts" in root:
                continue
            
            for file in files:
                if file.endswith(('.py', '.js', '.html', '.htm')):
                    filepath = os.path.join(root, file)
                    relative_path = os.path.relpath(filepath, project_path)
                    
                    # Validar sintaxis
                    validation_result = self.validate_file_syntax(filepath)
                    results["files"][relative_path] = validation_result
                    
                    results["summary"]["total_files"] += 1
                    
                    if validation_result["valid"]:
                        results["summary"]["valid_files"] += 1
                    else:
                        results["summary"]["files_with_errors"] += 1
                        results["overall_valid"] = False
                    
                    if validation_result.get("warnings"):
                        results["summary"]["files_with_warnings"] += 1
        
        return results
    
    def format_validation_report(self, validation_results: Dict) -> str:
        """
        Formatea los resultados de validación en un reporte legible.
        
        Args:
            validation_results: Resultados de validate_project_code()
            
        Returns:
            String con reporte formateado
        """
        lines = []
        lines.append("=" * 60)
        lines.append("REPORTE DE VALIDACIÓN DE CÓDIGO")
        lines.append("=" * 60)
        
        summary = validation_results.get("summary", {})
        lines.append(f"\n📊 Resumen:")
        lines.append(f"   Total de archivos: {summary.get('total_files', 0)}")
        lines.append(f"   ✅ Archivos válidos: {summary.get('valid_files', 0)}")
        lines.append(f"   ❌ Archivos con errores: {summary.get('files_with_errors', 0)}")
        lines.append(f"   ⚠️  Archivos con advertencias: {summary.get('files_with_warnings', 0)}")
        
        if validation_results.get("overall_valid"):
            lines.append(f"\n✅ VALIDACIÓN GENERAL: APROBADA")
        else:
            lines.append(f"\n❌ VALIDACIÓN GENERAL: RECHAZADA")
        
        # Detalles por archivo
        files = validation_results.get("files", {})
        if files:
            lines.append(f"\n📄 Detalles por archivo:")
            for filepath, result in files.items():
                status = "✅" if result["valid"] else "❌"
                lines.append(f"\n{status} {filepath}")
                
                if result.get("errors"):
                    for error in result["errors"]:
                        lines.append(f"   ❌ {error}")
                
                if result.get("warnings"):
                    for warning in result["warnings"]:
                        lines.append(f"   ⚠️  {warning}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)


# Instancia global del validador
code_validator = CodeValidator()


# --- Funciones de conveniencia ---

def validate_syntax(code: str, language: str) -> Dict[str, any]:
    """
    Valida sintaxis de código.
    
    Args:
        code: Código a validar
        language: Lenguaje ('python', 'javascript', 'html')
    """
    if language == 'python':
        return code_validator.validate_python_syntax(code)
    elif language == 'javascript':
        return code_validator.validate_javascript_syntax(code)
    elif language == 'html':
        return code_validator.validate_html_syntax(code)
    else:
        return {"valid": True, "warnings": [f"No hay validador para {language}"]}


def validate_project(project_id: str) -> Dict[str, any]:
    """Valida todo el código de un proyecto."""
    return code_validator.validate_project_code(project_id)


def get_validation_report(project_id: str) -> str:
    """Obtiene un reporte de validación formateado."""
    results = code_validator.validate_project_code(project_id)
    return code_validator.format_validation_report(results)
