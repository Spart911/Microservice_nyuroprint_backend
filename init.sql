CREATE DATABASE imagepicker;
CREATE DATABASE web_user;

-- Создаём пользователя root, если его нет
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'root') THEN
        CREATE ROLE root WITH LOGIN PASSWORD 'root';
    END IF;
END $$;

-- Даем пользователю root права на обе базы
GRANT ALL PRIVILEGES ON DATABASE imagepicker TO root;
GRANT ALL PRIVILEGES ON DATABASE web_user TO root;