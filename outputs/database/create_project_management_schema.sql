-- Desactivar verificaciones de claves foráneas temporalmente si fuera necesario para DROP TABLE,
-- pero para un script de creación limpia, no es estrictamente necesario.
-- SET session_replication_role = 'replica';

-- Eliminar tablas existentes en orden inverso de dependencia para evitar errores de FK
DROP TABLE IF EXISTS Project_Resources CASCADE;
DROP TABLE IF EXISTS Task_Assignments CASCADE;
DROP TABLE IF EXISTS Daily_Activities CASCADE;
DROP TABLE IF EXISTS Issues CASCADE;
DROP TABLE IF EXISTS Budgets CASCADE;
DROP TABLE IF EXISTS Milestones CASCADE;
DROP TABLE IF EXISTS Tasks CASCADE;
DROP TABLE IF EXISTS Projects CASCADE;
DROP TABLE IF EXISTS Resources CASCADE;
DROP TABLE IF EXISTS Employees CASCADE;
DROP TABLE IF EXISTS Clients CASCADE;

-- Tabla para Clientes
CREATE TABLE IF NOT EXISTS Clients (
    client_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    contact_person VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    phone_number VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para Empleados
CREATE TABLE IF NOT EXISTS Employees (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(100),
    email VARCHAR(255) NOT NULL UNIQUE,
    phone_number VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para Recursos
CREATE TABLE IF NOT EXISTS Resources (
    resource_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    type VARCHAR(100), -- e.g., 'Software', 'Hardware', 'Personal', 'Material'
    quantity INTEGER DEFAULT 1 CHECK (quantity >= 0),
    cost_per_unit NUMERIC(10, 2) DEFAULT 0.00 CHECK (cost_per_unit >= 0),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para Proyectos
CREATE TABLE IF NOT EXISTS Projects (
    project_id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES Clients(client_id) ON DELETE RESTRICT, -- No se puede eliminar un cliente si tiene proyectos asociados
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    start_date DATE NOT NULL,
    estimated_end_date DATE,
    real_end_date DATE,
    status VARCHAR(50) DEFAULT 'Activo' CHECK (status IN ('Activo', 'Completado', 'Pausado', 'Cancelado', 'Pendiente')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para Tareas
CREATE TABLE IF NOT EXISTS Tasks (
    task_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES Projects(project_id) ON DELETE CASCADE, -- Si se elimina un proyecto, sus tareas también
    name VARCHAR(255) NOT NULL,
    description TEXT,
    due_date DATE,
    status VARCHAR(50) DEFAULT 'Pendiente' CHECK (status IN ('Pendiente', 'En Progreso', 'Completada', 'Bloqueada', 'Revisión')),
    priority VARCHAR(50) DEFAULT 'Media' CHECK (priority IN ('Alta', 'Media', 'Baja')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para Hitos
CREATE TABLE IF NOT EXISTS Milestones (
    milestone_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES Projects(project_id) ON DELETE CASCADE, -- Si se elimina un proyecto, sus hitos también
    name VARCHAR(255) NOT NULL,
    description TEXT,
    due_date DATE NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para Presupuestos (permitiendo múltiples partidas presupuestarias por proyecto)
CREATE TABLE IF NOT EXISTS Budgets (
    budget_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES Projects(project_id) ON DELETE CASCADE, -- Si se elimina un proyecto, sus presupuestos también
    description TEXT NOT NULL,
    amount_allocated NUMERIC(12, 2) NOT NULL CHECK (amount_allocated >= 0),
    amount_spent NUMERIC(12, 2) DEFAULT 0.00 CHECK (amount_spent >= 0),
    currency VARCHAR(3) DEFAULT 'USD', -- e.g., 'USD', 'EUR', 'GBP'
    budget_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para Problemas/Incidencias
CREATE TABLE IF NOT EXISTS Issues (
    issue_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES Projects(project_id) ON DELETE CASCADE, -- Si se elimina un proyecto, sus problemas también
    reported_by_employee_id INTEGER REFERENCES Employees(employee_id) ON DELETE SET NULL, -- Si el empleado se elimina, el campo se pone a NULL
    resolved_by_employee_id INTEGER REFERENCES Employees(employee_id) ON DELETE SET NULL,
    description TEXT NOT NULL,
    reported_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'Abierto' CHECK (status IN ('Abierto', 'En Revisión', 'Resuelto', 'Cerrado', 'Rechazado')),
    priority VARCHAR(50) DEFAULT 'Media' CHECK (priority IN ('Alta', 'Media', 'Baja')),
    solution TEXT,
    resolution_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para Actividades Diarias
CREATE TABLE IF NOT EXISTS Daily_Activities (
    activity_id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES Employees(employee_id) ON DELETE RESTRICT, -- No se puede eliminar un empleado si tiene actividades registradas
    project_id INTEGER NOT NULL REFERENCES Projects(project_id) ON DELETE CASCADE, -- Si se elimina un proyecto, sus actividades también
    task_id INTEGER REFERENCES Tasks(task_id) ON DELETE SET NULL, -- Opcional: si la tarea se elimina, la actividad puede seguir siendo relevante
    description TEXT NOT NULL,
    activity_date DATE DEFAULT CURRENT_DATE NOT NULL,
    hours_spent NUMERIC(4, 2) NOT NULL CHECK (hours_spent > 0 AND hours_spent <= 24),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de unión para Tareas y Empleados (N:M)
CREATE TABLE IF NOT EXISTS Task_Assignments (
    task_id INTEGER NOT NULL REFERENCES Tasks(task_id) ON DELETE CASCADE, -- Si la tarea se elimina, la asignación también
    employee_id INTEGER NOT NULL REFERENCES Employees(employee_id) ON DELETE CASCADE, -- Si el empleado se elimina, la asignación también
    assigned_date DATE DEFAULT CURRENT_DATE,
    role_in_task VARCHAR(100), -- e.g., 'Responsable', 'Colaborador', 'Revisor'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (task_id, employee_id)
);

-- Tabla de unión para Proyectos y Recursos (N:M)
CREATE TABLE IF NOT EXISTS Project_Resources (
    project_id INTEGER NOT NULL REFERENCES Projects(project_id) ON DELETE CASCADE, -- Si el proyecto se elimina, el uso del recurso también
    resource_id INTEGER NOT NULL REFERENCES Resources(resource_id) ON DELETE RESTRICT, -- No se puede eliminar un recurso si está asignado a un proyecto
    quantity_used INTEGER NOT NULL DEFAULT 1 CHECK (quantity_used > 0),
    cost_associated NUMERIC(12, 2) DEFAULT 0.00 CHECK (cost_associated >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project_id, resource_id)
);

-- Índices para mejorar el rendimiento de las consultas
CREATE INDEX IF NOT EXISTS idx_projects_client_id ON Projects (client_id);
CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON Tasks (project_id);
CREATE INDEX IF NOT EXISTS idx_milestones_project_id ON Milestones (project_id);
CREATE INDEX IF NOT EXISTS idx_budgets_project_id ON Budgets (project_id);
CREATE INDEX IF NOT EXISTS idx_issues_project_id ON Issues (project_id);
CREATE INDEX IF NOT EXISTS idx_issues_reported_by_employee_id ON Issues (reported_by_employee_id);
CREATE INDEX IF NOT EXISTS idx_daily_activities_employee_id ON Daily_Activities (employee_id);
CREATE INDEX IF NOT EXISTS idx_daily_activities_project_id ON Daily_Activities (project_id);
CREATE INDEX IF NOT EXISTS idx_daily_activities_task_id ON Daily_Activities (task_id);
CREATE INDEX IF NOT EXISTS idx_task_assignments_employee_id ON Task_Assignments (employee_id);
CREATE INDEX IF NOT EXISTS idx_project_resources_resource_id ON Project_Resources (resource_id);


-- Función y Trigger para actualizar automáticamente la columna 'updated_at'
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar triggers a las tablas con columna 'updated_at'
DO $$
DECLARE
    t_name TEXT;
BEGIN
    FOR t_name IN (SELECT table_name FROM information_schema.columns WHERE column_name = 'updated_at' AND table_schema = current_schema())
    LOOP
        EXECUTE format('
            CREATE OR REPLACE TRIGGER %I_updated_at_trigger
            BEFORE UPDATE ON %I
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        ', t_name, t_name);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- SET session_replication_role = 'origin'; -- Reactivar verificaciones de claves foráneas