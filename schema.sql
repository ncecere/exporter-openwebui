-- DROP SCHEMA public;

CREATE SCHEMA public AUTHORIZATION pg_database_owner;

-- DROP SEQUENCE public.config_id_seq;

CREATE SEQUENCE public.config_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE public.document_id_seq;

CREATE SEQUENCE public.document_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE public.migratehistory_id_seq;

CREATE SEQUENCE public.migratehistory_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;
-- DROP SEQUENCE public.prompt_id_seq;

CREATE SEQUENCE public.prompt_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;-- public.alembic_version definition

-- Drop table

-- DROP TABLE public.alembic_version;

CREATE TABLE public.alembic_version (
	version_num varchar(32) NOT NULL,
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);


-- public.auth definition

-- Drop table

-- DROP TABLE public.auth;

CREATE TABLE public.auth (
	id varchar(255) NOT NULL,
	email varchar(255) NOT NULL,
	"password" text NOT NULL,
	active bool NOT NULL
);
CREATE UNIQUE INDEX auth_id ON public.auth USING btree (id);


-- public.chat definition

-- Drop table

-- DROP TABLE public.chat;

CREATE TABLE public.chat (
	id varchar(255) NOT NULL,
	user_id varchar(255) NOT NULL,
	title text NOT NULL,
	share_id varchar(255) NULL,
	archived bool NOT NULL,
	created_at int8 NOT NULL,
	updated_at int8 NOT NULL,
	chat json NULL,
	pinned bool NULL,
	meta json DEFAULT '{}'::json NOT NULL,
	folder_id text NULL
);
CREATE UNIQUE INDEX chat_id ON public.chat USING btree (id);
CREATE UNIQUE INDEX chat_share_id ON public.chat USING btree (share_id);


-- public.chatidtag definition

-- Drop table

-- DROP TABLE public.chatidtag;

CREATE TABLE public.chatidtag (
	id varchar(255) NOT NULL,
	tag_name varchar(255) NOT NULL,
	chat_id varchar(255) NOT NULL,
	user_id varchar(255) NOT NULL,
	"timestamp" int8 NOT NULL
);
CREATE UNIQUE INDEX chatidtag_id ON public.chatidtag USING btree (id);


-- public.config definition

-- Drop table

-- DROP TABLE public.config;

CREATE TABLE public.config (
	id serial4 NOT NULL,
	"data" json NOT NULL,
	"version" int4 NOT NULL,
	created_at timestamp DEFAULT now() NOT NULL,
	updated_at timestamp DEFAULT now() NULL,
	CONSTRAINT config_pkey PRIMARY KEY (id)
);


-- public."document" definition

-- Drop table

-- DROP TABLE public."document";

CREATE TABLE public."document" (
	id serial4 NOT NULL,
	collection_name varchar(255) NOT NULL,
	"name" varchar(255) NOT NULL,
	title text NOT NULL,
	filename text NOT NULL,
	"content" text NULL,
	user_id varchar(255) NOT NULL,
	"timestamp" int8 NOT NULL,
	CONSTRAINT document_pkey PRIMARY KEY (id)
);
CREATE UNIQUE INDEX document_collection_name ON public.document USING btree (collection_name);
CREATE UNIQUE INDEX document_name ON public.document USING btree (name);


-- public.feedback definition

-- Drop table

-- DROP TABLE public.feedback;

CREATE TABLE public.feedback (
	id text NOT NULL,
	user_id text NULL,
	"version" int8 NULL,
	"type" text NULL,
	"data" json NULL,
	meta json NULL,
	"snapshot" json NULL,
	created_at int8 NOT NULL,
	updated_at int8 NOT NULL,
	CONSTRAINT feedback_pkey PRIMARY KEY (id)
);


-- public.file definition

-- Drop table

-- DROP TABLE public.file;

CREATE TABLE public.file (
	id text NOT NULL,
	user_id text NOT NULL,
	filename text NOT NULL,
	meta json NULL,
	created_at int8 NOT NULL,
	hash text NULL,
	"data" json NULL,
	updated_at int8 NULL,
	"path" text NULL
);
CREATE UNIQUE INDEX file_id ON public.file USING btree (id);


-- public.folder definition

-- Drop table

-- DROP TABLE public.folder;

CREATE TABLE public.folder (
	id text NOT NULL,
	parent_id text NULL,
	user_id text NOT NULL,
	"name" text NOT NULL,
	items json NULL,
	meta json NULL,
	is_expanded bool NOT NULL,
	created_at int8 NOT NULL,
	updated_at int8 NOT NULL,
	CONSTRAINT folder_pkey PRIMARY KEY (id, user_id)
);


-- public."function" definition

-- Drop table

-- DROP TABLE public."function";

CREATE TABLE public."function" (
	id text NOT NULL,
	user_id text NOT NULL,
	"name" text NOT NULL,
	"type" text NOT NULL,
	"content" text NOT NULL,
	meta text NOT NULL,
	created_at int8 NOT NULL,
	updated_at int8 NOT NULL,
	valves text NULL,
	is_active bool NOT NULL,
	is_global bool NOT NULL
);
CREATE UNIQUE INDEX function_id ON public.function USING btree (id);


-- public."group" definition

-- Drop table

-- DROP TABLE public."group";

CREATE TABLE public."group" (
	id text NOT NULL,
	user_id text NULL,
	"name" text NULL,
	description text NULL,
	"data" json NULL,
	meta json NULL,
	permissions json NULL,
	user_ids json NULL,
	created_at int8 NULL,
	updated_at int8 NULL,
	CONSTRAINT group_pkey PRIMARY KEY (id)
);


-- public.knowledge definition

-- Drop table

-- DROP TABLE public.knowledge;

CREATE TABLE public.knowledge (
	id text NOT NULL,
	user_id text NOT NULL,
	"name" text NOT NULL,
	description text NULL,
	"data" json NULL,
	meta json NULL,
	created_at int8 NOT NULL,
	updated_at int8 NULL,
	access_control json NULL,
	CONSTRAINT knowledge_pkey PRIMARY KEY (id)
);


-- public.memory definition

-- Drop table

-- DROP TABLE public.memory;

CREATE TABLE public.memory (
	id varchar(255) NOT NULL,
	user_id varchar(255) NOT NULL,
	"content" text NOT NULL,
	updated_at int8 NOT NULL,
	created_at int8 NOT NULL
);
CREATE UNIQUE INDEX memory_id ON public.memory USING btree (id);


-- public.migratehistory definition

-- Drop table

-- DROP TABLE public.migratehistory;

CREATE TABLE public.migratehistory (
	id serial4 NOT NULL,
	"name" varchar(255) NOT NULL,
	migrated_at timestamp NOT NULL,
	CONSTRAINT migratehistory_pkey PRIMARY KEY (id)
);


-- public.model definition

-- Drop table

-- DROP TABLE public.model;

CREATE TABLE public.model (
	id text NOT NULL,
	user_id text NOT NULL,
	base_model_id text NULL,
	"name" text NOT NULL,
	meta text NOT NULL,
	params text NOT NULL,
	created_at int8 NOT NULL,
	updated_at int8 NOT NULL,
	access_control json NULL,
	is_active bool DEFAULT true NOT NULL
);
CREATE UNIQUE INDEX model_id ON public.model USING btree (id);


-- public.prompt definition

-- Drop table

-- DROP TABLE public.prompt;

CREATE TABLE public.prompt (
	id serial4 NOT NULL,
	command varchar(255) NOT NULL,
	user_id varchar(255) NOT NULL,
	title text NOT NULL,
	"content" text NOT NULL,
	"timestamp" int8 NOT NULL,
	access_control json NULL,
	CONSTRAINT prompt_pkey PRIMARY KEY (id)
);
CREATE UNIQUE INDEX prompt_command ON public.prompt USING btree (command);


-- public.tag definition

-- Drop table

-- DROP TABLE public.tag;

CREATE TABLE public.tag (
	id varchar(255) NOT NULL,
	"name" varchar(255) NOT NULL,
	user_id varchar(255) NOT NULL,
	meta json NULL,
	CONSTRAINT pk_id_user_id PRIMARY KEY (id, user_id)
);


-- public.tool definition

-- Drop table

-- DROP TABLE public.tool;

CREATE TABLE public.tool (
	id text NOT NULL,
	user_id text NOT NULL,
	"name" text NOT NULL,
	"content" text NOT NULL,
	specs text NOT NULL,
	meta text NOT NULL,
	created_at int8 NOT NULL,
	updated_at int8 NOT NULL,
	valves text NULL,
	access_control json NULL
);
CREATE UNIQUE INDEX tool_id ON public.tool USING btree (id);


-- public."user" definition

-- Drop table

-- DROP TABLE public."user";

CREATE TABLE public."user" (
	id varchar(255) NOT NULL,
	"name" varchar(255) NOT NULL,
	email varchar(255) NOT NULL,
	"role" varchar(255) NOT NULL,
	profile_image_url text NOT NULL,
	api_key varchar(255) NULL,
	created_at int8 NOT NULL,
	updated_at int8 NOT NULL,
	last_active_at int8 NOT NULL,
	settings text NULL,
	info text NULL,
	oauth_sub text NULL
);
CREATE UNIQUE INDEX user_api_key ON public."user" USING btree (api_key);
CREATE UNIQUE INDEX user_id ON public."user" USING btree (id);
CREATE UNIQUE INDEX user_oauth_sub ON public."user" USING btree (oauth_sub);