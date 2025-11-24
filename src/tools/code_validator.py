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
                request_schema = contract.get("request_schema", {})
                response_schema = contract.get("response_schema", {})
                status_codes = contract.get("status_codes", [])
                
                # Buscar definición del endpoint en el código
                endpoint_found = endpoint.replace('/', '') in code or endpoint in code
                
                if not endpoint_found:
                    result["errors"].append(
                        f"❌ Endpoint {method} {endpoint} NO implementado"
                    )
                    result["valid"] = False
                    continue
                
                # Validar schema de request
                if request_schema:
                    for field in request_schema.keys():
                        if field not in code:
                            result["warnings"].append(
                                f"⚠️ Campo '{field}' del request schema de {endpoint} no encontrado en código"
                            )
                
                # Validar schema de response
                if response_schema:
                    # Si es un dict, validar campos
                    if isinstance(response_schema, dict):
                        for field in response_schema.keys():
                            if field not in code:
                                result["errors"].append(
                                    f"❌ Campo '{field}' del response schema de {endpoint} NO encontrado en código"
                                )
                                result["valid"] = False
                
                # Validar códigos de estado
                if status_codes:
                    for status_code in status_codes:
                        if str(status_code) not in code:
                            result["warnings"].append(
                                f"⚠️ Código de estado {status_code} para {endpoint} no encontrado explícitamente"
                            )
        
        elif code_type == "frontend":
            # Verificar que se consuman los endpoints
            for contract in api_contracts:
                endpoint = contract["endpoint"]
                method = contract["method"]
                request_schema = contract.get("request_schema", {})
                response_schema = contract.get("response_schema", {})
                
                # Buscar uso del endpoint en el código
                if endpoint not in code:
                    result["errors"].append(
                        f"❌ Endpoint {endpoint} NO consumido en frontend"
                    )
                    result["valid"] = False
                    continue
                
                # Validar que se envíen los campos del request
                if request_schema:
                    for field in request_schema.keys():
                        if field not in code:
                            result["errors"].append(
                                f"❌ Campo '{field}' del request NO enviado a {endpoint}"
                            )
                            result["valid"] = False
                
                # Validar que se procesen los campos del response
                if response_schema:
                    if isinstance(response_schema, dict):
                        for field in response_schema.keys():
                            if field not in code:
                                result["warnings"].append(
                                    f"⚠️ Campo '{field}' del response de {endpoint} no procesado en frontend"
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
    
    def validate_project_contracts(self, project_id: str) -> Dict[str, any]:
        """
        Valida que todo el código del proyecto cumpla con los contratos definidos.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Dict con resultados de validación de contratos
        """
        results = {
            "overall_valid": True,
            "backend_validation": {},
            "frontend_validation": {},
            "summary": {
                "total_violations": 0,
                "critical_violations": 0,
                "warnings": 0
            }
        }
        
        project_path = get_project_path(project_id)
        
        if not os.path.exists(project_path):
            results["overall_valid"] = False
            results["error"] = f"El proyecto {project_id} no existe"
            return results
        
        # Validar backend
        backend_path = os.path.join(project_path, "backend")
        if os.path.exists(backend_path):
            backend_code = ""
            for root, dirs, files in os.walk(backend_path):
                for file in files:
                    if file.endswith('.py'):
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                backend_code += f.read() + "\n"
                        except:
                            pass
            
            if backend_code:
                results["backend_validation"] = self.validate_api_contracts(
                    project_id, backend_code, "backend"
                )
                
                if not results["backend_validation"]["valid"]:
                    results["overall_valid"] = False
                
                results["summary"]["critical_violations"] += len(results["backend_validation"].get("errors", []))
                results["summary"]["warnings"] += len(results["backend_validation"].get("warnings", []))
        
        # Validar frontend
        frontend_path = os.path.join(project_path, "frontend")
        if os.path.exists(frontend_path):
            frontend_code = ""
            for root, dirs, files in os.walk(frontend_path):
                for file in files:
                    if file.endswith(('.js', '.html')):
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                frontend_code += f.read() + "\n"
                        except:
                            pass
            
            if frontend_code:
                results["frontend_validation"] = self.validate_api_contracts(
                    project_id, frontend_code, "frontend"
                )
                
                if not results["frontend_validation"]["valid"]:
                    results["overall_valid"] = False
                
                results["summary"]["critical_violations"] += len(results["frontend_validation"].get("errors", []))
                results["summary"]["warnings"] += len(results["frontend_validation"].get("warnings", []))
        
        results["summary"]["total_violations"] = (
            results["summary"]["critical_violations"] + 
            results["summary"]["warnings"]
        )
        
        return results
    
    def format_contract_validation_report(self, validation_results: Dict) -> str:
        """
        Formatea los resultados de validación de contratos en un reporte legible.
        
        Args:
            validation_results: Resultados de validate_project_contracts()
            
        Returns:
            String con reporte formateado
        """
        lines = []
        lines.append("=" * 60)
        lines.append("REPORTE DE VALIDACIÓN DE CONTRATOS")
        lines.append("=" * 60)
        
        summary = validation_results.get("summary", {})
        lines.append(f"\n📊 Resumen:")
        lines.append(f"   Total de violaciones: {summary.get('total_violations', 0)}")
        lines.append(f"   ❌ Violaciones críticas: {summary.get('critical_violations', 0)}")
        lines.append(f"   ⚠️  Advertencias: {summary.get('warnings', 0)}")
        
        if validation_results.get("overall_valid"):
            lines.append(f"\n✅ VALIDACIÓN DE CONTRATOS: APROBADA")
        else:
            lines.append(f"\n❌ VALIDACIÓN DE CONTRATOS: RECHAZADA")
        
        # Backend
        backend = validation_results.get("backend_validation", {})
        if backend:
            lines.append(f"\n⚙️ Backend:")
            if backend.get("errors"):
                for error in backend["errors"]:
                    lines.append(f"   {error}")
            if backend.get("warnings"):
                for warning in backend["warnings"]:
                    lines.append(f"   {warning}")
        
        # Frontend
        frontend = validation_results.get("frontend_validation", {})
        if frontend:
            lines.append(f"\n🎨 Frontend:")
            if frontend.get("errors"):
                for error in frontend["errors"]:
                    lines.append(f"   {error}")
            if frontend.get("warnings"):
                for warning in frontend["warnings"]:
                    lines.append(f"   {warning}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)
    
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
