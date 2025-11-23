"""
Módulo de Gestión de Contratos de Interfaz

Este módulo proporciona funcionalidades para definir, almacenar y validar
contratos de interfaz entre diferentes capas de la aplicación (frontend, backend, database).
"""

import os
import json
from typing import Dict, List, Optional, Any
from .project_manager import get_project_path, get_active_project_id


class ContractManager:
    """Gestor de contratos de interfaz para proyectos."""
    
    def __init__(self):
        pass
    
    def define_api_contract(
        self,
        project_id: str,
        endpoint: str,
        method: str,
        request_schema: Dict[str, str],
        response_schema: Dict[str, str],
        status_codes: List[int],
        description: str = ""
    ) -> bool:
        """
        Define un contrato de API REST.
        
        Args:
            project_id: ID del proyecto
            endpoint: Ruta del endpoint (ej: '/api/users')
            method: Método HTTP (GET, POST, PUT, DELETE)
            request_schema: Schema del request body (dict con nombre_campo: tipo)
            response_schema: Schema de la respuesta (dict con nombre_campo: tipo)
            status_codes: Lista de códigos de estado posibles
            description: Descripción opcional del endpoint
            
        Returns:
            True si se guardó correctamente
        """
        contract = {
            "type": "api",
            "endpoint": endpoint,
            "method": method.upper(),
            "description": description,
            "request_schema": request_schema,
            "response_schema": response_schema,
            "status_codes": status_codes
        }
        
        return self._add_contract(project_id, "api_contracts", contract)
    
    def define_data_contract(
        self,
        project_id: str,
        model_name: str,
        fields: Dict[str, Dict[str, Any]],
        description: str = ""
    ) -> bool:
        """
        Define un contrato de modelo de datos.
        
        Args:
            project_id: ID del proyecto
            model_name: Nombre del modelo (ej: 'User', 'Product')
            fields: Dict con definición de campos
                   Ejemplo: {
                       "id": {"type": "integer", "primary_key": True},
                       "username": {"type": "string", "max_length": 50, "unique": True}
                   }
            description: Descripción opcional del modelo
            
        Returns:
            True si se guardó correctamente
        """
        contract = {
            "type": "data",
            "model_name": model_name,
            "description": description,
            "fields": fields
        }
        
        return self._add_contract(project_id, "data_contracts", contract)
    
    def get_api_contracts(self, project_id: str) -> List[Dict]:
        """
        Obtiene todos los contratos de API de un proyecto.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Lista de contratos de API
        """
        return self._get_contracts(project_id, "api_contracts")
    
    def get_data_contracts(self, project_id: str) -> List[Dict]:
        """
        Obtiene todos los contratos de datos de un proyecto.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Lista de contratos de datos
        """
        return self._get_contracts(project_id, "data_contracts")
    
    def get_all_contracts(self, project_id: str) -> Dict[str, List[Dict]]:
        """
        Obtiene todos los contratos de un proyecto.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Dict con 'api_contracts' y 'data_contracts'
        """
        return {
            "api_contracts": self.get_api_contracts(project_id),
            "data_contracts": self.get_data_contracts(project_id)
        }
    
    def validate_api_usage(
        self,
        project_id: str,
        endpoint: str,
        method: str,
        request_data: Dict
    ) -> Dict[str, Any]:
        """
        Valida que el uso de una API cumpla con el contrato definido.
        
        Args:
            project_id: ID del proyecto
            endpoint: Endpoint usado
            method: Método HTTP usado
            request_data: Datos enviados en el request
            
        Returns:
            Dict con resultado de validación:
            {
                "valid": bool,
                "errors": List[str],
                "warnings": List[str]
            }
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Buscar el contrato correspondiente
        api_contracts = self.get_api_contracts(project_id)
        contract = None
        
        for c in api_contracts:
            if c["endpoint"] == endpoint and c["method"] == method.upper():
                contract = c
                break
        
        if not contract:
            result["valid"] = False
            result["errors"].append(f"No se encontró contrato para {method} {endpoint}")
            return result
        
        # Validar request schema
        request_schema = contract.get("request_schema", {})
        
        for field, field_type in request_schema.items():
            if field not in request_data:
                result["valid"] = False
                result["errors"].append(f"Falta el campo requerido: {field}")
            else:
                # Validación básica de tipo
                actual_type = type(request_data[field]).__name__
                if not self._types_match(actual_type, field_type):
                    result["warnings"].append(
                        f"El campo '{field}' debería ser {field_type}, pero es {actual_type}"
                    )
        
        # Verificar campos extra
        for field in request_data:
            if field not in request_schema:
                result["warnings"].append(f"Campo no definido en contrato: {field}")
        
        return result
    
    def format_contracts_for_prompt(self, project_id: str, contract_type: str = "all") -> str:
        """
        Formatea los contratos en un string legible para incluir en prompts de LLM.
        
        Args:
            project_id: ID del proyecto
            contract_type: 'api', 'data', o 'all'
            
        Returns:
            String formateado con los contratos
        """
        output_parts = []
        
        if contract_type in ["api", "all"]:
            api_contracts = self.get_api_contracts(project_id)
            if api_contracts:
                output_parts.append("=== CONTRATOS DE API ===\n")
                for contract in api_contracts:
                    output_parts.append(f"\n**Endpoint:** {contract['method']} {contract['endpoint']}")
                    if contract.get('description'):
                        output_parts.append(f"**Descripción:** {contract['description']}")
                    output_parts.append(f"**Request Schema:**")
                    output_parts.append(json.dumps(contract['request_schema'], indent=2))
                    output_parts.append(f"**Response Schema:**")
                    output_parts.append(json.dumps(contract['response_schema'], indent=2))
                    output_parts.append(f"**Status Codes:** {contract['status_codes']}\n")
        
        if contract_type in ["data", "all"]:
            data_contracts = self.get_data_contracts(project_id)
            if data_contracts:
                output_parts.append("\n=== CONTRATOS DE DATOS ===\n")
                for contract in data_contracts:
                    output_parts.append(f"\n**Modelo:** {contract['model_name']}")
                    if contract.get('description'):
                        output_parts.append(f"**Descripción:** {contract['description']}")
                    output_parts.append(f"**Campos:**")
                    output_parts.append(json.dumps(contract['fields'], indent=2))
                    output_parts.append("")
        
        return "\n".join(output_parts)
    
    # --- Métodos privados ---
    
    def _add_contract(self, project_id: str, contract_type: str, contract: Dict) -> bool:
        """Añade un contrato al archivo correspondiente."""
        contracts_path = self._get_contracts_path(project_id, contract_type)
        
        # Leer contratos existentes
        existing_contracts = []
        if os.path.exists(contracts_path):
            try:
                with open(contracts_path, 'r', encoding='utf-8') as f:
                    existing_contracts = json.load(f)
            except Exception as e:
                print(f"⚠️ Error al leer contratos existentes: {e}")
        
        # Añadir nuevo contrato
        existing_contracts.append(contract)
        
        # Guardar
        try:
            with open(contracts_path, 'w', encoding='utf-8') as f:
                json.dump(existing_contracts, f, indent=2, ensure_ascii=False)
            print(f"✅ Contrato añadido: {contract_type}")
            return True
        except Exception as e:
            print(f"❌ Error al guardar contrato: {e}")
            return False
    
    def _get_contracts(self, project_id: str, contract_type: str) -> List[Dict]:
        """Obtiene contratos de un tipo específico."""
        contracts_path = self._get_contracts_path(project_id, contract_type)
        
        if not os.path.exists(contracts_path):
            return []
        
        try:
            with open(contracts_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error al leer contratos: {e}")
            return []
    
    def _get_contracts_path(self, project_id: str, contract_type: str) -> str:
        """Obtiene la ruta del archivo de contratos."""
        contracts_dir = get_project_path(project_id, "contracts")
        return os.path.join(contracts_dir, f"{contract_type}.json")
    
    def _types_match(self, actual_type: str, expected_type: str) -> bool:
        """Verifica si dos tipos coinciden (validación básica)."""
        type_mapping = {
            "str": ["string", "text"],
            "int": ["integer", "int", "number"],
            "float": ["float", "decimal", "number"],
            "bool": ["boolean", "bool"],
            "dict": ["object", "dict", "json"],
            "list": ["array", "list"]
        }
        
        expected_variants = type_mapping.get(actual_type, [actual_type])
        return expected_type.lower() in expected_variants


# Instancia global del gestor de contratos
contract_manager = ContractManager()


# --- Funciones de conveniencia ---

def define_api_contract(
    project_id: str,
    endpoint: str,
    method: str,
    request_schema: Dict[str, str],
    response_schema: Dict[str, str],
    status_codes: List[int],
    description: str = ""
) -> bool:
    """Define un contrato de API. Ver ContractManager.define_api_contract()"""
    return contract_manager.define_api_contract(
        project_id, endpoint, method, request_schema, 
        response_schema, status_codes, description
    )


def define_data_contract(
    project_id: str,
    model_name: str,
    fields: Dict[str, Dict[str, Any]],
    description: str = ""
) -> bool:
    """Define un contrato de datos. Ver ContractManager.define_data_contract()"""
    return contract_manager.define_data_contract(project_id, model_name, fields, description)


def get_contracts_for_prompt(project_id: str, contract_type: str = "all") -> str:
    """Formatea contratos para prompts. Ver ContractManager.format_contracts_for_prompt()"""
    return contract_manager.format_contracts_for_prompt(project_id, contract_type)


def get_all_contracts(project_id: str) -> Dict[str, List[Dict]]:
    """Obtiene todos los contratos. Ver ContractManager.get_all_contracts()"""
    return contract_manager.get_all_contracts(project_id)
