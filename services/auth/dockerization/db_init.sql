DO
$$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'auth') THEN
        CREATE USER auth WITH PASSWORD 'bbYZEq8q7PadE9pr3bmZoa5SYag92fU99ndKjg' CREATEDB;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'auth') THEN
        CREATE DATABASE auth WITH OWNER = auth;
    END IF;
END
$$;