# Contenido para: src/agents/frontend_developer.py

from src.model import advanced_llm
from src.tools.code_extractor import extract_and_save_code
from src.tools.contract_manager import get_contracts_for_prompt
from src.tools.project_manager import get_active_project_id

def frontend_developer_node(state: dict) -> dict:
    """
    Agente que genera el código de la aplicación frontend en la tecnología especificada.
    Utiliza el plan, la tarea específica, el diseño UI/UX y los contratos de API del backend.
    """
    print("---AGENTE: DESARROLLADOR FRONTEND---")
    
    plan = state.get("dev_plan")
    if not plan or not plan.get("frontend_task"):
        print("Advertencia: No se encontró un plan de frontend válido. Omitiendo nodo.")
        return {}

    # --- Recopilación de contexto ---
    frontend_tech = plan.get("frontend_tech", "HTML, CSS y JavaScript")
    task = plan.get("frontend_task")
    backend_port = plan.get("backend_port", 5000)  # Puerto por defecto
    feedback = state.get("review_feedback")
    ui_ux_spec = state.get("ui_ux_spec", "No se proporcionó especificación de UI/UX. Crea una interfaz limpia y moderna.")
    
    # Obtener contratos del proyecto activo
    project_id = get_active_project_id()
    contracts_text = ""
    if project_id:
        # Solo obtener contratos de API para el frontend
        contracts_text = get_contracts_for_prompt(project_id, "api")
        if contracts_text:
            print(f"✅ Contratos de API cargados para desarrollo frontend")
    
    prompt_additions = ""
    # Si hay feedback, incluir código existente
    if feedback:
        existing_frontend_code = state.get("frontend_code", {})
        existing_code_prompt = ""
        if isinstance(existing_frontend_code, dict):
            full_existing_code = []
            for filename, code in existing_frontend_code.items():
                full_existing_code.append(f"--- {filename} ---\n{code}")
            
            existing_code_prompt = "\n\n".join(full_existing_code)

        prompt_additions = f"""
        **Feedback de la Revisión Anterior (Debes Corregirlo):**
        ---
        {feedback}
        ---
        **CÓDIGO EXISTENTE (MODIFICA ESTE CÓDIGO):**
        ```
        {existing_code_prompt}
        ```
         **Modifica o Genera unicamente los archivos que se te piden en el Feedback. 
         No modifiques todo el codigo solo las funcionalidades que se te piden en el feedback.
         Lo demas mantenerlo igual.**
        """

    # --- Construcción del Prompt ---
    prompt = f"""
Eres un desarrollador frontend senior de élite especializado en {frontend_tech}.
Tu código es conocido por ser limpio, accesible, responsive y seguir las mejores prácticas modernas de UI/UX.

**TU MISIÓN:**
Generar código frontend completo, production-ready, funcional y profesional que implemente EXACTAMENTE los requisitos especificados.

TAREA ESPECÍFICA ASIGNADA
{task}

CONTRATOS DE API DEL BACKEND (CONSUMIR EXACTAMENTE)

{contracts_text}

**CONFIGURACIÓN DE CONEXIÓN BACKEND:**
- Puerto del backend: {backend_port}
- Define en JavaScript: `const BASE_URL = 'http://localhost:{backend_port}';`
- Usa esta constante en TODAS las llamadas fetch/axios

ESPECIFICACIÓN DE UI/UX

{ui_ux_spec}

{prompt_additions}

 REQUISITOS TÉCNICOS CRÍTICOS (OBLIGATORIOS)

**1. ESTRUCTURA HTML SEMÁNTICA:**
   ✓ Tags semánticos (<header>, <nav>, <main>, <section>, <article>, <footer>)
   ✓ Estructura lógica y jerárquica
   ✓ IDs únicos y clases reutilizables con nombres descriptivos
   ✓ Atributos alt en TODAS las imágenes
   ✓ Labels asociados a TODOS los inputs (for + id)
   ✓ ARIA attributes para accesibilidad donde sean necesarios

**2. CSS MODERNO Y RESPONSIVE:**
   ✓ Mobile-first design (media queries de menor a mayor)
   ✓ Flexbox/Grid para layouts modernos
   ✓ Variables CSS para colores, espaciados y tipografía
   ✓ Nomenclatura BEM o consistente
   ✓ Responsive en móvil (320px), tablet (768px) y desktop (1024px+)
   ✓ Transiciones suaves en interacciones (hover, focus, active)
   ✓ Estados de hover/focus/active claramente visibles
   ✓ Contraste adecuado (WCAG AA mínimo)

**3. JAVASCRIPT PROFESIONAL:**
   ✓ Código modular y organizado (funciones específicas, no monolíticas)
   ✓ Event listeners con delegación si hay elementos dinámicos
   ✓ Async/await para llamadas fetch (NO callbacks anidados)
   ✓ Manejo de errores en TODAS las llamadas async
   ✓ Validación de formularios antes de enviar
   ✓ Feedback visual en TODAS las acciones (loading, success, error)
   ✓ Sanitización de inputs (prevenir XSS)
   ✓ LocalStorage/SessionStorage usado correctamente si es necesario
   ✓ Comentarios JSDoc en funciones complejas

**4. INTEGRACIÓN CON BACKEND (CRÍTICO):**
   ✓ URLs construidas dinámicamente con BASE_URL
   ✓ Headers correctos en fetch (Content-Type: application/json)
   ✓ Body JSON.stringify para POST/PUT/PATCH
   ✓ Verificación de response.ok antes de parsear
   ✓ Manejo de TODOS los códigos de estado (200, 201, 400, 401, 404, 500)
   ✓ Tokens/credenciales manejados de forma segura
   ✓ Logout limpia sesión y storage

**5. EXPERIENCIA DE USUARIO:**
   ✓ Loading spinners durante operaciones async
   ✓ Mensajes de error claros y útiles (no técnicos)
   ✓ Confirmaciones antes de acciones destructivas
   ✓ Formularios reseteados después de submit exitoso
   ✓ Deshabilitar botones durante procesamiento (evitar doble submit)
   ✓ Scroll suave y natural
   ✓ Focus visible en navegación por teclado

**6. PERFORMANCE:**
   ✓ Imágenes optimizadas (webp, lazy loading si aplica)
   ✓ CSS y JS minificados (comentario sobre build si aplica)
   ✓ Evitar reflows innecesarios (leer DOM, luego escribir)
   ✓ Debounce en inputs de búsqueda
   ✓ Event listeners removidos si se crean dinámicamente

**7. SEGURIDAD:**
   ✓ NO almacenar contraseñas en localStorage/sessionStorage
   ✓ Sanitización de contenido insertado dinámicamente (textContent vs innerHTML)
   ✓ HTTPS en producción (comentario si es relevante)
   ✓ CORS configurado correctamente en backend

FORMATO DE SALIDA (ESTRICTAMENTE OBLIGATORIO)

**Genera el código en bloques separados usando EXACTAMENTE este formato:**

1. **HTML** (index.html):
   `<!--- index.html_CODE_START --->`
   [código HTML completo]
   `<!--- index.html_CODE_END --->`

2. **CSS** (style.css o styles.css):
   `/* --- style.css_CODE_START --- */`
   [código CSS completo]
   `/* --- style.css_CODE_END --- */`

3. **JAVASCRIPT** (script.js o app.js):
   `// --- script.js_CODE_START ---`
   [código JavaScript completo]
   `// --- script.js_CODE_END ---`

**REGLAS DE ORO:**
- ❌ NO añadas explicaciones fuera de los bloques de código
- ❌ NO uses markdown para código (solo los delimitadores especificados)
- ✅ Código completo y funcional, listo para abrir en navegador
- ✅ Links a archivos CSS y JS correctos en HTML
- ✅ Implementación EXACTA de los contratos de API

CHECKLIST FINAL ANTES DE GENERAR

Verifica mentalmente:
□ ¿Consumí TODOS los endpoints de los contratos?
□ ¿BASE_URL configurado correctamente?
□ ¿HTML es semántico y accesible?
□ ¿CSS es responsive (móvil, tablet, desktop)?
□ ¿Manejé TODOS los estados (loading, success, error)?
□ ¿Validé formularios antes de enviar?
□ ¿Hay feedback visual en todas las acciones?
□ ¿El código es limpio y comentado donde es necesario?

**AHORA GENERA EL CÓDIGO FRONTEND COMPLETO Y PROFESIONAL.**
    """
    
    response = advanced_llm.invoke(prompt)
    full_code = response.content

    print("\n--- SALIDA COMPLETA DEL LLM (PARA DEPURACIÓN) ---\n")
    print(full_code)
    print("\n--- FIN DE LA SALIDA DE DEPURACIÓN ---\n")

    extracted_code_dict = extract_and_save_code(full_code, default_folder="frontend")
    
    return {
        "frontend_code": extracted_code_dict,
        "last_code_generated": "frontend",
        "review_feedback": None,
        "supervisor_iterations": state.get("supervisor_iterations")+1
    }
