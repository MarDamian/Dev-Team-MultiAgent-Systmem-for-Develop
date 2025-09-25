-- Deshabilitar temporalmente la verificación de claves foráneas si fuera necesario para el DROP,
-- aunque en PostgreSQL CASCADE es suficiente para un orden inverso de DROP.
-- SET session_replication_role = 'replica'; -- Esto es más para replicación, no para DROP.
-- Simplemente el orden inverso es la mejor práctica.

-- Eliminar tablas en orden inverso de dependencia para evitar problemas de restricciones de clave foránea.
DROP TABLE IF EXISTS Daily_Activities CASCADE;
DROP TABLE IF EXISTS Task_Assignments CASCADE;
DROP TABLE IF EXISTS Project_Resources CASCADE;
DROP TABLE IF EXISTS Issues CASCADE;
DROP TABLE IF EXISTS Budgets CASCADE;
DROP TABLE IF EXISTS Milestones CASCADE;
DROP TABLE IF EXISTS Tasks CASCADE;
DROP TABLE IF EXISTS Projects CASCADE;
DROP TABLE IF EXISTS Resources CASCADE;
DROP TABLE IF EXISTS Employees CASCADE;
DROP TABLE IF EXISTS Clients CASCADE;

-- Crear una función para actualizar automáticamente la columna 'updated_at'
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 1. Tabla Clientes (Clients)
CREATE TABLE Clients (
    client_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    contact_person VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TRIGGER update_clients_updated_at
BEFORE UPDATE ON Clients
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- 2. Tabla Empleados (Employees)
CREATE TABLE Employees (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(50),
    role VARCHAR(100),
    hire_date DATE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TRIGGER update_employees_updated_at
BEFORE UPDATE ON Employees
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- 3. Tabla Proyectos (Projects)
CREATE TABLE Projects (
    project_id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES Clients(client_id),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    start_date DATE NOT NULL,
    estimated_end_date DATE,
    actual_end_date DATE,
    status VARCHAR(50) DEFAULT 'Activo' CHECK (status IN ('Activo', 'Completado', 'Pausado', 'Cancelado')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TRIGGER update_projects_updated_at
BEFORE UPDATE ON Projects
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- 4. Tabla Tareas (Tasks)
CREATE TABLE Tasks (
    task_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES Projects(project_id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    due_date DATE,
    status VARCHAR(50) DEFAULT 'Pendiente' CHECK (status IN ('Pendiente', 'En Progreso', 'Completada', 'Bloqueada', 'Cancelada')),
    priority VARCHAR(50) DEFAULT 'Media' CHECK (priority IN ('Alta', 'Media', 'Baja')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TRIGGER update_tasks_updated_at
BEFORE UPDATE ON Tasks
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- 5. Tabla Hitos (Milestones)
CREATE TABLE Milestones (
    milestone_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES Projects(project_id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    due_date DATE NOT NULL,
    completed_date DATE,
    status VARCHAR(50) DEFAULT 'Pendiente' CHECK (status IN ('Pendiente', 'Alcanzado', 'Retrasado', 'Cancelado')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TRIGGER update_milestones_updated_at
BEFORE UPDATE ON Milestones
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- 6. Tabla Recursos (Resources)
CREATE TABLE Resources (
    resource_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    type VARCHAR(100) NOT NULL CHECK (type IN ('Software', 'Hardware', 'Personal', 'Material', 'Servicio', 'Licencia')),
    description TEXT,
    quantity INTEGER DEFAULT 1 CHECK (quantity >= 0),
    unit_cost NUMERIC(10, 2) DEFAULT 0.00 CHECK (unit_cost >= 0),
    available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TRIGGER update_resources_updated_at
BEFORE UPDATE ON Resources
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- 7. Tabla Presupuestos (Budgets)
-- Permite múltiples entradas de presupuesto por proyecto para diferentes categorías/ítems
CREATE TABLE Budgets (
    budget_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES Projects(project_id),
    description TEXT,
    amount_allocated NUMERIC(12, 2) NOT NULL CHECK (amount_allocated >= 0),
    amount_spent NUMERIC(12, 2) DEFAULT 0.00 CHECK (amount_spent >= 0),
    currency VARCHAR(3) DEFAULT 'USD',
    budget_date DATE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TRIGGER update_budgets_updated_at
BEFORE UPDATE ON Budgets
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- 8. Tabla Problemas/Incidencias (Issues)
CREATE TABLE Issues (
    issue_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES Projects(project_id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    reported_by_employee_id INTEGER REFERENCES Employees(employee_id),
    reported_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'Abierto' CHECK (status IN ('Abierto', 'En Revisión', 'Resuelto', 'Cerrado', 'Duplicado')),
    resolution_description TEXT,
    resolved_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TRIGGER update_issues_updated_at
BEFORE UPDATE ON Issues
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- 9. Tabla Actividades Diarias (Daily_Activities)
CREATE TABLE Daily_Activities (
    activity_id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES Employees(employee_id),
    project_id INTEGER NOT NULL REFERENCES Projects(project_id),
    task_id INTEGER REFERENCES Tasks(task_id), -- Opcional, puede ser NULL si la actividad no está ligada a una tarea específica
    description TEXT NOT NULL,
    activity_date DATE DEFAULT NOW(),
    hours_spent NUMERIC(4, 2) NOT NULL CHECK (hours_spent > 0 AND hours_spent <= 24), -- Horas dedicadas en un día, entre 0 y 24
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TRIGGER update_daily_activities_updated_at
BEFORE UPDATE ON Daily_Activities
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Tablas de unión para relaciones N:M

-- 10. Tabla Asignaciones de Tareas (Task_Assignments) - Relación N:M entre Tareas y Empleados
CREATE TABLE Task_Assignments (
    assignment_id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES Tasks(task_id) ON DELETE CASCADE,
    employee_id INTEGER NOT NULL REFERENCES Employees(employee_id) ON DELETE CASCADE,
    assigned_date DATE DEFAULT NOW(),
    role_in_task VARCHAR(100), -- Ej. 'Desarrollador Líder', 'Tester'
    hours_estimated NUMERIC(6, 2) CHECK (hours_estimated >= 0),
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(task_id, employee_id) -- Un empleado solo puede ser asignado a una tarea específica una vez
);

CREATE TRIGGER update_task_assignments_updated_at
BEFORE UPDATE ON Task_Assignments
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- 11. Tabla Recursos del Proyecto (Project_Resources) - Relación N:M entre Proyectos y Recursos
CREATE TABLE Project_Resources (
    project_resource_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES Projects(project_id) ON DELETE CASCADE,
    resource_id INTEGER NOT NULL REFERENCES Resources(resource_id) ON DELETE CASCADE,
    quantity_used INTEGER DEFAULT 1 CHECK (quantity_used > 0),
    cost_associated NUMERIC(12, 2) CHECK (cost_associated >= 0), -- Costo asociado a este uso específico del recurso en este proyecto
    assigned_date DATE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(project_id, resource_id) -- Un recurso específico solo puede ser asignado a un proyecto una vez (su cantidad puede ser actualizada)
);

CREATE TRIGGER update_project_resources_updated_at
BEFORE UPDATE ON Project_Resources
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();