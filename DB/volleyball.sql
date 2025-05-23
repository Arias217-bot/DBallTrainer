-- This script was generated by the ERD tool in pgAdmin 4.
-- Please log an issue at https://github.com/pgadmin-org/pgadmin4/issues/new/choose if you find any bugs, including reproduction steps.
BEGIN;


CREATE TABLE IF NOT EXISTS public.categoria_edad
(
    id_categoria_edad integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    nombre character varying(50) COLLATE pg_catalog."default" NOT NULL,
    descripcion text COLLATE pg_catalog."default",
    CONSTRAINT categoria_edad_pkey PRIMARY KEY (id_categoria_edad)
);

CREATE TABLE IF NOT EXISTS public.categoria_sexo
(
    id_categoria_sexo integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    nombre character varying(20) COLLATE pg_catalog."default" NOT NULL,
    descripcion text COLLATE pg_catalog."default",
    CONSTRAINT categoria_sexo_pkey PRIMARY KEY (id_categoria_sexo)
);

CREATE TABLE IF NOT EXISTS public.detalle_jugada
(
    id_detalle integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    id_jugada integer NOT NULL,
    orden integer NOT NULL,
    jugador integer NOT NULL,
    zona integer NOT NULL,
    calificacion character varying(3) COLLATE pg_catalog."default",
    CONSTRAINT detalle_jugada_pkey PRIMARY KEY (id_detalle)
);

CREATE TABLE IF NOT EXISTS public.deteccion
(
    id_deteccion serial NOT NULL,
    nombre character varying(100) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT deteccion_pkey PRIMARY KEY (id_deteccion)
);

CREATE TABLE IF NOT EXISTS public.equipo
(
    id_equipo integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    nombre character varying(100) COLLATE pg_catalog."default" NOT NULL,
    id_categoria_edad integer NOT NULL,
    id_categoria_sexo integer NOT NULL,
    descripcion text COLLATE pg_catalog."default",
    CONSTRAINT equipo_pkey PRIMARY KEY (id_equipo)
);

CREATE TABLE IF NOT EXISTS public.equipo_rival
(
    nombre_equipo_rival character varying(50) COLLATE pg_catalog."default" NOT NULL,
    categoria character varying(50) COLLATE pg_catalog."default" NOT NULL,
    director character varying(50) COLLATE pg_catalog."default" NOT NULL,
    asistente character varying(50) COLLATE pg_catalog."default" NOT NULL,
    director_cedula character varying(20) COLLATE pg_catalog."default" NOT NULL,
    asistente_cedula character varying(20) COLLATE pg_catalog."default" NOT NULL,
    id_torneo integer,
    CONSTRAINT equipo_rival_pkey PRIMARY KEY (nombre_equipo_rival)
);

CREATE TABLE IF NOT EXISTS public.jugadas
(
    id_jugada integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    nombre_partido character varying(50) COLLATE pg_catalog."default" NOT NULL,
    secuencia_jugada text COLLATE pg_catalog."default",
    tiempo_inicio time without time zone NOT NULL,
    tiempo_fin time without time zone NOT NULL,
    datos_procesados json,
    CONSTRAINT jugadas_pkey PRIMARY KEY (id_jugada)
);

CREATE TABLE IF NOT EXISTS public.jugadores_rivales
(
    nombre_equipo_rival character varying(50) COLLATE pg_catalog."default" NOT NULL,
    documento character varying(20) COLLATE pg_catalog."default" NOT NULL,
    nombre character varying(100) COLLATE pg_catalog."default" NOT NULL,
    telefono character varying(15) COLLATE pg_catalog."default",
    email character varying(100) COLLATE pg_catalog."default",
    eps character varying(100) COLLATE pg_catalog."default",
    CONSTRAINT jugadores_rivales_pkey PRIMARY KEY (documento)
);

CREATE TABLE IF NOT EXISTS public.mensajes
(
    id_mensaje integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    id_equipo integer NOT NULL,
    contenido text COLLATE pg_catalog."default" NOT NULL,
    fecha_envio timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    autor character varying(100) COLLATE pg_catalog."default",
    CONSTRAINT pk_mensajes PRIMARY KEY (id_mensaje)
);

CREATE TABLE IF NOT EXISTS public.modalidad
(
    id_modalidad serial NOT NULL,
    nombre character varying(100) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT modalidad_pkey PRIMARY KEY (id_modalidad)
);

CREATE TABLE IF NOT EXISTS public.partido
(
    nombre_partido character varying(50) COLLATE pg_catalog."default" NOT NULL,
    id_torneo integer NOT NULL,
    nombre_equipo_rival character varying(50) COLLATE pg_catalog."default" NOT NULL,
    fecha timestamp without time zone NOT NULL,
    lugar character varying(100) COLLATE pg_catalog."default",
    marcador_local integer NOT NULL,
    marcador_rival integer NOT NULL,
    video_url character varying(255) COLLATE pg_catalog."default",
    observaciones text COLLATE pg_catalog."default",
    CONSTRAINT partido_pkey PRIMARY KEY (nombre_partido)
);

CREATE TABLE IF NOT EXISTS public.posicion
(
    id_posicion integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    nombre character varying(20) COLLATE pg_catalog."default" NOT NULL,
    descripcion text COLLATE pg_catalog."default",
    CONSTRAINT posicion_pkey PRIMARY KEY (id_posicion)
);

CREATE TABLE IF NOT EXISTS public.rol
(
    id_rol integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    nombre character varying(20) COLLATE pg_catalog."default" NOT NULL,
    descripcion text COLLATE pg_catalog."default",
    CONSTRAINT rol_pkey PRIMARY KEY (id_rol)
);

CREATE TABLE IF NOT EXISTS public.tipo_usuario
(
    id_tipo_usuario integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    nombre character varying(50) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT tipo_usuario_pkey PRIMARY KEY (id_tipo_usuario)
);

CREATE TABLE IF NOT EXISTS public.torneo
(
    id_torneo integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    nombre_torneo character varying(50) COLLATE pg_catalog."default" NOT NULL,
    id_equipo integer NOT NULL,
    descripcion text COLLATE pg_catalog."default",
    CONSTRAINT torneo_pkey PRIMARY KEY (id_torneo),
    CONSTRAINT uq_torneo_nombre UNIQUE (nombre_torneo)
);

CREATE TABLE IF NOT EXISTS public.usuario
(
    documento character varying(20) COLLATE pg_catalog."default" NOT NULL,
    nombre character varying(100) COLLATE pg_catalog."default" NOT NULL,
    password character varying(255) COLLATE pg_catalog."default" NOT NULL,
    fecha_nacimiento date,
    sexo character varying(20) COLLATE pg_catalog."default" NOT NULL,
    telefono character varying(15) COLLATE pg_catalog."default",
    direccion character varying(255) COLLATE pg_catalog."default",
    email character varying(100) COLLATE pg_catalog."default",
    experiencia text COLLATE pg_catalog."default",
    foto_url character varying(255) COLLATE pg_catalog."default",
    id_tipo_usuario integer,
    peso numeric(5, 2),
    altura numeric(5, 2),
    CONSTRAINT usuario_pkey PRIMARY KEY (documento),
    CONSTRAINT usuario_email_key UNIQUE (email)
);

CREATE TABLE IF NOT EXISTS public.usuario_equipo
(
    id_usuario_equipo integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    documento character varying(20) COLLATE pg_catalog."default" NOT NULL,
    id_equipo integer NOT NULL,
    id_rol integer NOT NULL,
    id_posicion integer NOT NULL,
    numero integer,
    CONSTRAINT usuario_equipo_pkey PRIMARY KEY (id_usuario_equipo)
);

CREATE TABLE IF NOT EXISTS public.videos
(
    id_video serial NOT NULL,
    nombre character varying(255) COLLATE pg_catalog."default" NOT NULL,
    url character varying(255) COLLATE pg_catalog."default" NOT NULL,
    documento_usuario character varying(20) COLLATE pg_catalog."default" NOT NULL,
    id_modalidad integer,
    id_deteccion integer,
    resultados_analisis jsonb,
    reporte_generado boolean DEFAULT false,
    url_procesado character varying(255) COLLATE pg_catalog."default",
    CONSTRAINT videos_pkey PRIMARY KEY (id_video)
);

ALTER TABLE IF EXISTS public.detalle_jugada
    ADD CONSTRAINT fk_detalle_jugada_jugada FOREIGN KEY (id_jugada)
    REFERENCES public.jugadas (id_jugada) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE CASCADE;


ALTER TABLE IF EXISTS public.equipo
    ADD CONSTRAINT fk_equipo_categoria_edad FOREIGN KEY (id_categoria_edad)
    REFERENCES public.categoria_edad (id_categoria_edad) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE CASCADE;


ALTER TABLE IF EXISTS public.equipo
    ADD CONSTRAINT fk_equipo_categoria_sexo FOREIGN KEY (id_categoria_sexo)
    REFERENCES public.categoria_sexo (id_categoria_sexo) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE CASCADE;


ALTER TABLE IF EXISTS public.equipo_rival
    ADD CONSTRAINT fk_equipo_rival_torneo FOREIGN KEY (id_torneo)
    REFERENCES public.torneo (id_torneo) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE CASCADE;


ALTER TABLE IF EXISTS public.jugadas
    ADD CONSTRAINT fk_jugadas_partido FOREIGN KEY (nombre_partido)
    REFERENCES public.partido (nombre_partido) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE CASCADE;


ALTER TABLE IF EXISTS public.jugadores_rivales
    ADD CONSTRAINT fk_jugadores_rivales_equipo_rival FOREIGN KEY (nombre_equipo_rival)
    REFERENCES public.equipo_rival (nombre_equipo_rival) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE CASCADE;


ALTER TABLE IF EXISTS public.mensajes
    ADD CONSTRAINT fk_mensajes_equipo FOREIGN KEY (id_equipo)
    REFERENCES public.equipo (id_equipo) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE CASCADE;


ALTER TABLE IF EXISTS public.partido
    ADD CONSTRAINT fk_partido_equipo_rival FOREIGN KEY (nombre_equipo_rival)
    REFERENCES public.equipo_rival (nombre_equipo_rival) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE CASCADE;


ALTER TABLE IF EXISTS public.partido
    ADD CONSTRAINT fk_partido_torneo FOREIGN KEY (id_torneo)
    REFERENCES public.torneo (id_torneo) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE CASCADE;


ALTER TABLE IF EXISTS public.torneo
    ADD CONSTRAINT fk_torneo_equipo FOREIGN KEY (id_equipo)
    REFERENCES public.equipo (id_equipo) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE CASCADE;


ALTER TABLE IF EXISTS public.usuario
    ADD CONSTRAINT fk_usuario_tipo_usuario FOREIGN KEY (id_tipo_usuario)
    REFERENCES public.tipo_usuario (id_tipo_usuario) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE CASCADE;


ALTER TABLE IF EXISTS public.usuario_equipo
    ADD CONSTRAINT fk_usuario_equipo_equipo FOREIGN KEY (id_equipo)
    REFERENCES public.equipo (id_equipo) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE CASCADE;


ALTER TABLE IF EXISTS public.usuario_equipo
    ADD CONSTRAINT fk_usuario_equipo_posicion FOREIGN KEY (id_posicion)
    REFERENCES public.posicion (id_posicion) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE CASCADE;


ALTER TABLE IF EXISTS public.usuario_equipo
    ADD CONSTRAINT fk_usuario_equipo_rol FOREIGN KEY (id_rol)
    REFERENCES public.rol (id_rol) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE CASCADE;


ALTER TABLE IF EXISTS public.usuario_equipo
    ADD CONSTRAINT fk_usuario_equipo_usuario FOREIGN KEY (documento)
    REFERENCES public.usuario (documento) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE CASCADE;


ALTER TABLE IF EXISTS public.videos
    ADD CONSTRAINT fk_usuario FOREIGN KEY (documento_usuario)
    REFERENCES public.usuario (documento) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE CASCADE;


ALTER TABLE IF EXISTS public.videos
    ADD CONSTRAINT fk_videos_deteccion FOREIGN KEY (id_deteccion)
    REFERENCES public.deteccion (id_deteccion) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE SET NULL;


ALTER TABLE IF EXISTS public.videos
    ADD CONSTRAINT fk_videos_modalidad FOREIGN KEY (id_modalidad)
    REFERENCES public.modalidad (id_modalidad) MATCH SIMPLE
    ON UPDATE CASCADE
    ON DELETE SET NULL;

END;