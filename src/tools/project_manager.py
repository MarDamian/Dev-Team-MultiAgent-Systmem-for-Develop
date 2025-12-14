"""
Módulo de Gestión de Proyectos

Este módulo proporciona funcionalidades para gestionar proyectos de desarrollo
de forma aislada, con IDs únicos, metadata y estructura de carpetas organizada.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# Directorio base para todos los proyectos
PROJECTS_BASE_DIR = "outputs"

# Variable global para el proyecto activo
_active_project_id: Optional[str] = None


class ProjectManager:
    """Gestor centralizado de proyectos de desarrollo."""
    
    def __init__(self, base_dir: str = PROJECTS_BASE_DIR):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
    
    def create_project(
        self, 
        name: str, 
        plan_type: str,
        technologies: Dict[str, str],
        description: str = ""
    ) -> str:
        """
        Crea un nuevo proyecto con estructura de carpetas y metadata.
        
        Args:
            name: Nombre descriptivo del proyecto
            plan_type: Tipo de plan ('frontend-only', 'backend-only', 'database-only', 'fullstack')
            technologies: Dict con tecnologías por capa (ej: {'backend': 'Python Flask', 'frontend': 'HTML/CSS/JS'})
            description: Descripción opcional del proyecto
            
        Returns:
            ID único del proyecto creado
        """
        project_id = self._generate_project_id()
        project_path = self._get_project_path(project_id)
        
        # Crear estructura de carpetas
        os.makedirs(project_path, exist_ok=True)
        os.makedirs(os.path.join(project_path, "contracts"), exist_ok=True)
        
        # Crear carpetas según el tipo de plan
        if plan_type in ['backend-only', 'fullstack']:
            os.makedirs(os.path.join(project_path, "backend"), exist_ok=True)
        if plan_type in ['frontend-only', 'fullstack']:
            os.makedirs(os.path.join(project_path, "frontend"), exist_ok=True)
        if plan_type in ['database-only', 'fullstack', 'backend-only']:
            os.makedirs(os.path.join(project_path, "database"), exist_ok=True)
        
        # Crear metadata
        metadata = {
            "project_id": project_id,
            "name": name,
            "description": description,
            "plan_type": plan_type,
            "technologies": technologies,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        # Guardar metadata
        self._save_metadata(project_id, metadata)
        
        print(f"✅ Proyecto creado: {name} (ID: {project_id})")
        print(f"   Tipo: {plan_type}")
        print(f"   Ruta: {project_path}")
        
        return project_id
    
    def get_project_path(self, project_id: str, subfolder: str = "") -> str:
        """
        Obtiene la ruta completa de un proyecto o subcarpeta.
        
        Args:
            project_id: ID del proyecto
            subfolder: Subcarpeta opcional ('backend', 'frontend', 'database', 'contracts')
            
        Returns:
            Ruta completa al proyecto o subcarpeta
        """
        base_path = self._get_project_path(project_id)
        
        if subfolder:
            return os.path.join(base_path, subfolder)
        
        return base_path
    
    def get_project_metadata(self, project_id: str) -> Optional[Dict]:
        """
        Obtiene la metadata de un proyecto.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Diccionario con metadata o None si no existe
        """
        metadata_path = os.path.join(self._get_project_path(project_id), "metadata.json")
        
        if not os.path.exists(metadata_path):
            print(f"⚠️ No se encontró metadata para el proyecto {project_id}")
            return None
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error al leer metadata del proyecto {project_id}: {e}")
            return None
    
    def update_project_metadata(self, project_id: str, updates: Dict) -> bool:
        """
        Actualiza la metadata de un proyecto.
        
        Args:
            project_id: ID del proyecto
            updates: Diccionario con campos a actualizar
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        metadata = self.get_project_metadata(project_id)
        
        if not metadata:
            return False
        
        # Actualizar campos
        metadata.update(updates)
        metadata["updated_at"] = datetime.now().isoformat()
        
        # Guardar
        return self._save_metadata(project_id, metadata)
    
    def list_projects(self) -> List[Dict]:
        """
        Lista todos los proyectos existentes.
        
        Returns:
            Lista de diccionarios con metadata de cada proyecto
        """
        projects = []
        
        if not os.path.exists(self.base_dir):
            return projects
        
        for item in os.listdir(self.base_dir):
            item_path = os.path.join(self.base_dir, item)
            if os.path.isdir(item_path):
                metadata = self.get_project_metadata(item)
                if metadata:
                    projects.append(metadata)
        
        # Ordenar por fecha de creación (más reciente primero)
        projects.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return projects
    
    def set_active_project(self, project_id: str) -> bool:
        """
        Establece el proyecto activo globalmente.
        
        Args:
            project_id: ID del proyecto a activar
            
        Returns:
            True si se activó correctamente, False si no existe
        """
        global _active_project_id
        
        if not os.path.exists(self._get_project_path(project_id)):
            print(f"❌ El proyecto {project_id} no existe")
            return False
        
        _active_project_id = project_id
        print(f"✅ Proyecto activo: {project_id}")
        return True
    
    def get_active_project_id(self) -> Optional[str]:
        """
        Obtiene el ID del proyecto activo.
        
        Returns:
            ID del proyecto activo o None
        """
        return _active_project_id
    
    def project_exists(self, project_id: str) -> bool:
        """
        Verifica si un proyecto existe.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            True si existe, False en caso contrario
        """
        return os.path.exists(self._get_project_path(project_id))
    
    # --- Métodos privados ---
    
    def _generate_project_id(self) -> str:
        """Genera un ID único para el proyecto."""
        return f"project_{uuid.uuid4().hex[:12]}"
    
    def _get_project_path(self, project_id: str) -> str:
        """Obtiene la ruta base de un proyecto."""
        return os.path.join(self.base_dir, project_id)
    
    def _save_metadata(self, project_id: str, metadata: Dict) -> bool:
        """Guarda la metadata de un proyecto."""
        metadata_path = os.path.join(self._get_project_path(project_id), "metadata.json")
        
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error al guardar metadata: {e}")
            return False


# Instancia global del gestor de proyectos
project_manager = ProjectManager()


# --- Funciones de conveniencia para uso directo ---

def create_project(name: str, plan_type: str, technologies: Dict[str, str], description: str = "") -> str:
    """Crea un nuevo proyecto. Ver ProjectManager.create_project()"""
    return project_manager.create_project(name, plan_type, technologies, description)


def get_project_path(project_id: str, subfolder: str = "") -> str:
    """Obtiene la ruta de un proyecto. Ver ProjectManager.get_project_path()"""
    return project_manager.get_project_path(project_id, subfolder)


def get_active_project_path(subfolder: str = "") -> Optional[str]:
    """
    Obtiene la ruta del proyecto activo.
    
    Args:
        subfolder: Subcarpeta opcional
        
    Returns:
        Ruta del proyecto activo o None si no hay proyecto activo
    """
    project_id = project_manager.get_active_project_id()
    if not project_id:
        return None
    return project_manager.get_project_path(project_id, subfolder)


def set_active_project(project_id: str) -> bool:
    """Establece el proyecto activo. Ver ProjectManager.set_active_project()"""
    return project_manager.set_active_project(project_id)


def get_active_project_id() -> Optional[str]:
    """Obtiene el ID del proyecto activo."""
    return project_manager.get_active_project_id()


def list_projects() -> List[Dict]:
    """Lista todos los proyectos. Ver ProjectManager.list_projects()"""
    return project_manager.list_projects()


def get_project_metadata(project_id: str) -> Optional[Dict]:
    """Obtiene metadata de un proyecto. Ver ProjectManager.get_project_metadata()"""
    return project_manager.get_project_metadata(project_id)


def ensure_project_folders(project_id: str, folders: List[str]) -> bool:
    """
    Asegura que las carpetas especificadas existan en el proyecto.
    Útil para crear carpetas dinámicamente si no fueron creadas inicialmente.
    
    Args:
        project_id: ID del proyecto
        folders: Lista de carpetas a crear (ej: ['frontend', 'backend', 'database'])
        
    Returns:
        True si todas las carpetas se crearon/verificaron correctamente
    """
    try:
        project_path = project_manager.get_project_path(project_id)
        
        if not project_path or not os.path.exists(project_path):
            print(f"❌ El proyecto {project_id} no existe")
            return False
        
        for folder in folders:
            folder_path = os.path.join(project_path, folder)
            os.makedirs(folder_path, exist_ok=True)
            print(f"✓ Carpeta asegurada: {folder_path}")
        
        return True
    except Exception as e:
        print(f"❌ Error al crear carpetas del proyecto: {e}")
        return False

