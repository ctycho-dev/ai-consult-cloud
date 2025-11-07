--
-- PostgreSQL database dump
--

\restrict Ztc97CgTbMya4gcOCNHqe3ewDYABcWky86YOKQadlUECotrqaM2Ctuvs678tb6D

-- Dumped from database version 17.6 (Debian 17.6-1.pgdg13+1)
-- Dumped by pg_dump version 17.6 (Debian 17.6-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: deletestatus; Type: TYPE; Schema: public; Owner: root
--

CREATE TYPE public.deletestatus AS ENUM (
    'PENDING',
    'IN_PROGRESS',
    'FAILED',
    'COMPLETED'
);


ALTER TYPE public.deletestatus OWNER TO root;

--
-- Name: fileorigin; Type: TYPE; Schema: public; Owner: root
--

CREATE TYPE public.fileorigin AS ENUM (
    'UPLOAD',
    'S3_IMPORT',
    'OPENAI_ONLY'
);


ALTER TYPE public.fileorigin OWNER TO root;

--
-- Name: filestate; Type: TYPE; Schema: public; Owner: root
--

CREATE TYPE public.filestate AS ENUM (
    'PENDING',
    'UPLOADING',
    'STORED',
    'INDEXING',
    'INDEXED',
    'FAILED'
);


ALTER TYPE public.filestate OWNER TO root;

--
-- Name: messagestate; Type: TYPE; Schema: public; Owner: root
--

CREATE TYPE public.messagestate AS ENUM (
    'CREATED',
    'PROCESSING',
    'ERROR',
    'CANCELED',
    'TIMEOUT',
    'COMPLETED'
);


ALTER TYPE public.messagestate OWNER TO root;

--
-- Name: userrole; Type: TYPE; Schema: public; Owner: root
--

CREATE TYPE public.userrole AS ENUM (
    'ADMIN',
    'ASSISTANT',
    'USER'
);


ALTER TYPE public.userrole OWNER TO root;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: root
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO root;

--
-- Name: chats; Type: TABLE; Schema: public; Owner: root
--

CREATE TABLE public.chats (
    id integer NOT NULL,
    name character varying NOT NULL,
    user_id integer NOT NULL,
    session_handle character varying,
    tools jsonb,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.chats OWNER TO root;

--
-- Name: chats_id_seq; Type: SEQUENCE; Schema: public; Owner: root
--

CREATE SEQUENCE public.chats_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.chats_id_seq OWNER TO root;

--
-- Name: chats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: root
--

ALTER SEQUENCE public.chats_id_seq OWNED BY public.chats.id;


--
-- Name: files; Type: TABLE; Schema: public; Owner: root
--

CREATE TABLE public.files (
    id integer NOT NULL,
    s3_bucket character varying,
    s3_object_key character varying,
    s3_version_id character varying,
    e_tag character varying,
    sha256 character varying,
    vector_store_id character varying NOT NULL,
    storage_key character varying,
    name character varying,
    size integer,
    content_type character varying,
    origin public.fileorigin NOT NULL,
    status public.filestate NOT NULL,
    last_error character varying,
    delete_status public.deletestatus NOT NULL,
    deleted_openai boolean NOT NULL,
    deleted_s3 boolean NOT NULL,
    last_delete_error character varying,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    created_by_id integer,
    updated_by_id integer,
    deleted_at timestamp with time zone,
    deleted_by_id integer
);


ALTER TABLE public.files OWNER TO root;

--
-- Name: files_id_seq; Type: SEQUENCE; Schema: public; Owner: root
--

CREATE SEQUENCE public.files_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.files_id_seq OWNER TO root;

--
-- Name: files_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: root
--

ALTER SEQUENCE public.files_id_seq OWNED BY public.files.id;


--
-- Name: messages; Type: TABLE; Schema: public; Owner: root
--

CREATE TABLE public.messages (
    id integer NOT NULL,
    chat_id integer NOT NULL,
    content character varying NOT NULL,
    role character varying NOT NULL,
    run_id character varying,
    sources jsonb,
    state public.messagestate NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.messages OWNER TO root;

--
-- Name: messages_id_seq; Type: SEQUENCE; Schema: public; Owner: root
--

CREATE SEQUENCE public.messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.messages_id_seq OWNER TO root;

--
-- Name: messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: root
--

ALTER SEQUENCE public.messages_id_seq OWNED BY public.messages.id;


--
-- Name: storages; Type: TABLE; Schema: public; Owner: root
--

CREATE TABLE public.storages (
    id integer NOT NULL,
    name character varying NOT NULL,
    vector_store_id character varying NOT NULL,
    "default" boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    created_by_id integer,
    updated_by_id integer,
    deleted_at timestamp with time zone,
    deleted_by_id integer
);


ALTER TABLE public.storages OWNER TO root;

--
-- Name: storages_id_seq; Type: SEQUENCE; Schema: public; Owner: root
--

CREATE SEQUENCE public.storages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.storages_id_seq OWNER TO root;

--
-- Name: storages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: root
--

ALTER SEQUENCE public.storages_id_seq OWNED BY public.storages.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: root
--

CREATE TABLE public.users (
    id integer NOT NULL,
    name character varying,
    email character varying NOT NULL,
    password character varying NOT NULL,
    role public.userrole NOT NULL,
    valid boolean NOT NULL,
    external_id character varying,
    source character varying,
    model character varying,
    user_instructions text,
    instructions text,
    tools jsonb NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    created_by_id integer,
    updated_by_id integer,
    deleted_at timestamp with time zone,
    deleted_by_id integer
);


ALTER TABLE public.users OWNER TO root;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: root
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO root;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: root
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: chats id; Type: DEFAULT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.chats ALTER COLUMN id SET DEFAULT nextval('public.chats_id_seq'::regclass);


--
-- Name: files id; Type: DEFAULT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.files ALTER COLUMN id SET DEFAULT nextval('public.files_id_seq'::regclass);


--
-- Name: messages id; Type: DEFAULT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.messages ALTER COLUMN id SET DEFAULT nextval('public.messages_id_seq'::regclass);


--
-- Name: storages id; Type: DEFAULT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.storages ALTER COLUMN id SET DEFAULT nextval('public.storages_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: root
--

COPY public.alembic_version (version_num) FROM stdin;
5ac5027266d2
\.


--
-- Data for Name: chats; Type: TABLE DATA; Schema: public; Owner: root
--

COPY public.chats (id, name, user_id, session_handle, tools, created_at, updated_at) FROM stdin;
1	test	1	conv_690d89628a9481968ce723d2577fd8370b527a0772d480e8	\N	2025-11-07 05:53:38.631932+00	2025-11-07 05:53:38.631932+00
\.


--
-- Data for Name: files; Type: TABLE DATA; Schema: public; Owner: root
--

COPY public.files (id, s3_bucket, s3_object_key, s3_version_id, e_tag, sha256, vector_store_id, storage_key, name, size, content_type, origin, status, last_error, delete_status, deleted_openai, deleted_s3, last_delete_error, created_at, updated_at, created_by_id, updated_by_id, deleted_at, deleted_by_id) FROM stdin;
178	assistant-bucket2	178:187:Заказы поставщикам (этапы кратко) - Сырьё XLSX.xlsx	\N	\N	8288871ef8366939ce7d8a625f5f82773cd8dad5d1e42d0582cc5641ecec9bd2	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-79jty2UParPfVuhqLV9JCH	187:Заказы поставщикам (этапы кратко) - Сырьё XLSX.xlsx	22375	application/vnd.openxmlformats-officedocument.spreadsheetml.sheet	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 08:09:22.363897+00	2025-11-07 08:09:34.828331+00	\N	\N	\N	\N
95	assistant-production	125:ZICOS GE-DP TDS.pdf	\N	\N	3f2e199ece2ef1e3b323d2f52b64958d57f314195c1124988eb43933e79bb42d	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-CzaUnEpKqDLYtkuo9ZmRQo	ZICOS GE-DP TDS.pdf	55539	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:27:49.271196+00	2025-11-07 07:27:49.290034+00	\N	\N	\N	\N
6	assistant-production	27:Укупорка - каталог (1).pdf	\N	\N	fff623bb04baea7e5d7cd0309b48a1aea76b41ac4951758b7d5453bc40d1919f	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-3VJghL92ZPtp8Pxo2Ck67W	Укупорка - каталог (1).pdf	10800888	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:47:50.487568+00	2025-11-07 05:47:50.503959+00	\N	\N	\N	\N
11	assistant-production	32:Yeser.pdf	\N	\N	a4211b85bfffa6d6eebd7fe83d8bdfae2c791b6d5023f59af20b3233121029a6	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-VkCUJXhdf3nVYBFwJ1vnw2	Yeser.pdf	267637	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:50:35.151363+00	2025-11-07 05:50:35.176909+00	\N	\N	\N	\N
12	assistant-production	33:Uniproma Catalog 2024.pdf	\N	\N	389417d8ea1a7abbfb69b14de83f654034039893d2b261a0e5d60257d60ed277	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-9G7ky5emAqjhrm2qE67Ly4	Uniproma Catalog 2024.pdf	701475	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:50:40.372219+00	2025-11-07 05:50:40.391774+00	\N	\N	\N	\N
13	assistant-production	34:ZCare_catalog.pdf	\N	\N	446bad09da761ff0f1ba6d412e26adb558b5086818c3c5ee2ae2151098bc53a6	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-KWn2r38361yzAYeFxoYQGc	ZCare_catalog.pdf	33948637	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:52:16.210634+00	2025-11-07 05:52:16.224814+00	\N	\N	\N	\N
14	assistant-production	43:1.pdf	\N	\N	1954f5774e37213a18396402f64ca447e94d036b7e10a265e9a42c3e17a05425	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-JrJ2GsebpxPLKDMZjZ7Vmc	1.pdf	357443	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:52:22.198328+00	2025-11-07 05:52:22.212443+00	\N	\N	\N	\N
15	assistant-production	44:Прайс в штуках.pdf	\N	\N	e95136cea83ad9ed18eb09f47cb47d76b46957b21377b2ca7f5223c0e8384780	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-WfZoyFGK8nvDuzGcoHBwK5	Прайс в штуках.pdf	977259	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:55:22.175723+00	2025-11-07 05:55:22.204318+00	\N	\N	\N	\N
41	assistant-production	71:TDS_liprozym_standard_СТ_ferment_2023(RUS).pdf	\N	\N	85c329f79d2568fb276a01e8dfae2d383e4f53e6cd42d1c4732d20b0c0c1c59b	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-2CtfyNZCXAHTpQEY2Dfx4z	TDS_liprozym_standard_СТ_ferment_2023(RUS).pdf	234551	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:58:44.391812+00	2025-11-07 05:58:44.398968+00	\N	\N	\N	\N
42	assistant-production	72:TDS_proteasol_standard_СТ_ferment_2023(RUS).pdf	\N	\N	5483167403e5a7f8499c1ae4db148f6276f9030cc27badbac0543f695dd0be9a	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-9XcY73gJqsmQTVFezgCyg8	TDS_proteasol_standard_СТ_ferment_2023(RUS).pdf	230037	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:58:47.873269+00	2025-11-07 05:58:47.88856+00	\N	\N	\N	\N
43	assistant-production	73:TDS_amilzym_standard_СТ_ferment_2023(RUS).pdf	\N	\N	75feb666fc2d79b5c5e5d80718c7875a67f9f55403faac96bc0b8fcea6a9fad9	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-HnKf6KaU2PdWvjTYnjvr9p	TDS_amilzym_standard_СТ_ferment_2023(RUS).pdf	230080	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:58:51.887265+00	2025-11-07 05:58:51.905502+00	\N	\N	\N	\N
44	assistant-production	74:TDS_ultralase_combi_СТ_ferment_2024(RUS) (1).pdf	\N	\N	fc4aefe1be51a41b09334a7a820cd0c7774901e83ba3baaf27f40ed9bb56451d	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-RpB8gDMSVCXNuJHVweiEig	TDS_ultralase_combi_СТ_ferment_2024(RUS) (1).pdf	216985	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:58:55.452404+00	2025-11-07 05:58:55.463362+00	\N	\N	\N	\N
45	assistant-production	75:TDS_ultralase_balance_СТ_ferment_2023(RUS).pdf	\N	\N	a528e2bc799627e08ca9c2d95942d0a9ebf5d7cfd414313cedffb35aa4276caa	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-GRz412xxixymsKYvASfg2Q	TDS_ultralase_balance_СТ_ferment_2023(RUS).pdf	231736	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:59:00.212654+00	2025-11-07 05:59:00.229838+00	\N	\N	\N	\N
63	assistant-production	96:TDS_proteasol_standard_ferment_2022(RUS).pdf	\N	\N	c433dc758eb8bdc6d770e992f28544e84ac9a41aef8489e636b60dadbbdca896	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-Dj9ZbzMGg7H8FNzJwXyMw1	TDS_proteasol_standard_ferment_2022(RUS).pdf	324838	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:00:55.399132+00	2025-11-07 06:00:55.425632+00	\N	\N	\N	\N
19	assistant-production	49:COA of 1,2-Pentanediol.pdf	\N	\N	f61dd25eb2ec061c601a30b4f2d41c1cbbb0831610984be0f10940098c995446	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-WAAHwVTtW9FB4eSTSpVLEr	COA of 1,2-Pentanediol.pdf	108473	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:55:34.592881+00	2025-11-07 05:55:34.609654+00	\N	\N	\N	\N
20	assistant-production	50:COA Гидроксиацетофенон.pdf	\N	\N	37460e880b591dcfb457993e31f464bd793edb0d8fbee9fdd7343e566c9902dd	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-JQeP8hTz2zHSH6UpZcyh72	COA Гидроксиацетофенон.pdf	119059	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:55:38.978139+00	2025-11-07 05:55:38.994487+00	\N	\N	\N	\N
21	assistant-production	51:MSDS Гидроксиацетофенон.pdf	\N	\N	0b15182f41308c7b17f114ef98d19c29a6b1a3460c74751819a2801b2ad68e44	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-JW6C8vXEbvMZp6sHm5wxww	MSDS Гидроксиацетофенон.pdf	140341	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:55:42.587139+00	2025-11-07 05:55:42.602089+00	\N	\N	\N	\N
22	assistant-production	52:MSDS of Pentanediol.pdf	\N	\N	a67abb661d4f3b27b0c92ba426533ff1567825a9ffac5e3dc991d130e95d23fb	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-Y8gUm1z59uNMzDyB2RYQyx	MSDS of Pentanediol.pdf	217213	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:55:47.414622+00	2025-11-07 05:55:47.424329+00	\N	\N	\N	\N
23	assistant-production	53:TDS Гидроксиацетофенон.pdf	\N	\N	dfd5f2581d93e4ba74ed3827e76c65053984ecb56c921e705f7c8511cf6d8ab1	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-BNaT4bkv9iPzMgQ663ecVC	TDS Гидроксиацетофенон.pdf	190941	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:55:50.842374+00	2025-11-07 05:55:50.856948+00	\N	\N	\N	\N
24	assistant-production	54:COA-1,2-Hexanediol WAP.pdf	\N	\N	6f2e99afdfb52a0ba85785e055b233b944476934ec16cc41ba7f4aa9f1f2f0a5	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-JnxUHSCaUt5pJSzAL7YXaS	COA-1,2-Hexanediol WAP.pdf	325465	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:55:55.444331+00	2025-11-07 05:55:55.456525+00	\N	\N	\N	\N
25	assistant-production	55:COA of 1, 2 Hexanediol. Jeevan.pdf	\N	\N	399012d119e73d837ffa3c4d23a66f98eed849b749ae2026442536a27a40d744	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-QYMdQknxVJdKTxJAnEeSc1	COA of 1, 2 Hexanediol. Jeevan.pdf	663096	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:56:03.438705+00	2025-11-07 05:56:03.44808+00	\N	\N	\N	\N
26	assistant-production	56:MSDS-1,2-Hexanediol WAP.pdf	\N	\N	693e13855b6b1ac0851d54c4c47db93d8c84d6fc29ef071f8ce553738ade4e68	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-95FXvsEzRqmHUYRcE8cNvT	MSDS-1,2-Hexanediol WAP.pdf	677160	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:56:09.186326+00	2025-11-07 05:56:09.195771+00	\N	\N	\N	\N
27	assistant-production	57:СОА of ETHYL HEXYL GLYCERIN. JEEVAN.pdf	\N	\N	d5abce6bc77ee2d8dbdc116412f3966657df86974142a881d171f34870be63bb	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-EqKqiqJLjJMRtU3Hr9BtSM	СОА of ETHYL HEXYL GLYCERIN. JEEVAN.pdf	869270	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:56:14.675841+00	2025-11-07 05:56:14.687625+00	\N	\N	\N	\N
28	assistant-production	58:PRODUCT SPECIFICATION_SR-8503 HOT.pdf	\N	\N	6557522737dd8ec57c5f5625d2575591564890741ea079519fdea31e6b3080ae	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-QuemXmPdgDYpMgF11AK1Jc	PRODUCT SPECIFICATION_SR-8503 HOT.pdf	17637	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:56:18.131321+00	2025-11-07 05:56:18.162048+00	\N	\N	\N	\N
29	assistant-production	59:PRODUCT SPECIFICATION_SR-8502 COLD.pdf	\N	\N	2197f4e80847129a8312b6f11c90ad1c0c122d43ef568f551c1e9397c94fa8fa	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-NEuEPZRfbLZjVFxa3ch2F9	PRODUCT SPECIFICATION_SR-8502 COLD.pdf	17699	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:56:21.374743+00	2025-11-07 05:56:21.394199+00	\N	\N	\N	\N
30	assistant-production	60:PRODUCT SPECIFICATION_SR-8504.pdf	\N	\N	27458ac372d0cd88fe35f0d05ccce0c5bcd4d0563475a7020da184652d43d87c	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-WmF2Fj1effJxcyJ7Whf526	PRODUCT SPECIFICATION_SR-8504.pdf	28000	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:56:25.188639+00	2025-11-07 05:56:25.198068+00	\N	\N	\N	\N
31	assistant-production	61:СЕРТИФИКАТ АНАЛИЗА_SR-7904 ГОРЯЧИЙ.pdf	\N	\N	a588fa4157e45f84b8a6b3675ece940601fd341ed5f97aeab5c0c6eef6de7cc6	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-AwLwtapdQEc84BPQjbSxgj	СЕРТИФИКАТ АНАЛИЗА_SR-7904 ГОРЯЧИЙ.pdf	112457	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:56:28.202637+00	2025-11-07 05:56:28.212564+00	\N	\N	\N	\N
32	assistant-production	62:СЕРТИФИКАТ АНАЛИЗА_SR-7903 ХОЛОДНЫЙ.pdf	\N	\N	c207fe964eb15a63957637f358ac0424eeef8d2e6c76a5d2123ce48a9ea41ff6	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-EAvwvhKeFRjJ4HGTWA9rW3	СЕРТИФИКАТ АНАЛИЗА_SR-7903 ХОЛОДНЫЙ.pdf	115212	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:56:31.226089+00	2025-11-07 05:56:31.234608+00	\N	\N	\N	\N
33	assistant-production	63:СПЕЦИФИКАЦИЯ ПРОДУКТА_SR-8502 ХОЛОДНЫЙ.pdf	\N	\N	358ce3c691d8a594ed3e4f3a8543200f8f021befc1f27cae56a6f13b39948522	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-1hmLTyWTJtfBoc1MKTDwZq	СПЕЦИФИКАЦИЯ ПРОДУКТА_SR-8502 ХОЛОДНЫЙ.pdf	123550	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:56:34.272794+00	2025-11-07 05:56:34.293809+00	\N	\N	\N	\N
34	assistant-production	64:СЕРТИФИКАТ АНАЛИЗА_SR-8504.pdf	\N	\N	6014f084104f9841c566450a6749b168dc858a632185d1f0d6ccb0014354cebb	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-BGPnTxZPhKvGWZBG3vVFwE	СЕРТИФИКАТ АНАЛИЗА_SR-8504.pdf	131140	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:56:37.346554+00	2025-11-07 05:56:37.364033+00	\N	\N	\N	\N
35	assistant-production	65:СПЕЦИФИКАЦИЯ ПРОДУКТА_SR-8503 ГОРЯЧИЙ.pdf	\N	\N	1602570dd302ce56f305fe16aa373acd69ebe9fdee8945e9f572b9f736cfdec2	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-BUYd1Qek6X6ZDkUbUmdHiD	СПЕЦИФИКАЦИЯ ПРОДУКТА_SR-8503 ГОРЯЧИЙ.pdf	144403	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:58:21.357305+00	2025-11-07 05:58:21.385672+00	\N	\N	\N	\N
36	assistant-production	66:COA_SR-7903 COLD.pdf	\N	\N	9d1b66238bc9f03c866ac49e95b01ae85d36ca031a6290985c77e249f13580b9	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-4EicxBAxDzm2WqXU3MJHvv	COA_SR-7903 COLD.pdf	106356	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:58:24.679201+00	2025-11-07 05:58:24.699387+00	\N	\N	\N	\N
37	assistant-production	67:COA_SR-7904 HOT.pdf	\N	\N	bd72eda298a539972c6fdb69d0ce60143158cb4196a961aa0eb71f61762ced13	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-V9cqKzq1S4tomuEYyNyBrx	COA_SR-7904 HOT.pdf	114741	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:58:28.6839+00	2025-11-07 05:58:28.697445+00	\N	\N	\N	\N
38	assistant-production	68:TDS 50%.pdf	\N	\N	f927c3179af1a1d3155f0ab4af6f3452306a13b4e161fa8a96f47f46bf263036	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-CQmyakVW29fQ3CQFGSVqRz	TDS 50%.pdf	97097	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:58:32.240914+00	2025-11-07 05:58:32.256342+00	\N	\N	\N	\N
39	assistant-production	69:COA.pdf	\N	\N	f0ad6c74da3f2409bc9cb5217919f8d854d4d2ae6a0ba512fc2b88eeab966299	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-T9qfjg9TkiskWA5CJGfFvh	COA.pdf	251085	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:58:35.953392+00	2025-11-07 05:58:35.961922+00	\N	\N	\N	\N
40	assistant-production	70:TDS_proteasol_ultra_СТ_ferment_2023(RUS).pdf	\N	\N	9652478b00bd80272cb77aca98dcf376b8e52c1e653e72aa9d130c9abe8dd777	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-NdXhLbYvRg8BDrHgS7TEhq	TDS_proteasol_ultra_СТ_ferment_2023(RUS).pdf	225481	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:58:40.828856+00	2025-11-07 05:58:40.84789+00	\N	\N	\N	\N
46	assistant-production	76:TDS_ultralase_active_СТ_ferment_2023(RUS).pdf	\N	\N	42ae827f03b2e626f8bde836098d46777b7cd8f1dc2c69c36efdc2ac95cfd97b	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-4CT9LXXa9KWo9BHbMc5kC2	TDS_ultralase_active_СТ_ferment_2023(RUS).pdf	232003	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:59:03.441245+00	2025-11-07 05:59:03.455903+00	\N	\N	\N	\N
62	assistant-production	95:TDS_celazym_ultra_ferment_2024(RUS) (1).pdf	\N	\N	76b8eee2261b78f3f89236a871df8d1e172fd01afc1ad4947e25a286d8f6e75e	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-JhSPEXLHSC2hSbTLPWWJuA	TDS_celazym_ultra_ferment_2024(RUS) (1).pdf	222146	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:00:50.979331+00	2025-11-07 06:00:50.997069+00	\N	\N	\N	\N
47	assistant-production	77:TDS_ultralase_combi_СТ_ferment_2023(RUS).pdf	\N	\N	38fb2f0e6b1f7b98351ebaac45eced09ff38d7e81f58994c2c43e778e19527e9	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-Fsnev72tDYatBdX8i5nHud	TDS_ultralase_combi_СТ_ferment_2023(RUS).pdf	227445	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:59:06.902602+00	2025-11-07 05:59:06.927338+00	\N	\N	\N	\N
48	assistant-production	78:TDS_ultralase_advance_СТ_ferment_2023(RUS).pdf	\N	\N	e2a14e46ad77066dab833be43e2c97b05746277b19aeaa49e6514666c9fd171d	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-47hQEPxL4u8YzKJ1TKwUin	TDS_ultralase_advance_СТ_ferment_2023(RUS).pdf	233918	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:59:11.249095+00	2025-11-07 05:59:11.259941+00	\N	\N	\N	\N
64	assistant-production	97:TDS_liprozim_standard_ferment_2022(RUS).pdf	\N	\N	ae083a12ae86ce5c7bbb3a5be5a60af86fffce52a655e8ebaabf6b162ed1b6f3	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-Q1bLeM9VLJmgDVdezCb4NG	TDS_liprozim_standard_ferment_2022(RUS).pdf	329786	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:00:59.487516+00	2025-11-07 06:00:59.500613+00	\N	\N	\N	\N
49	assistant-production	79:TDS_ultralase_plus_СТ_ferment_2023(RUS).pdf	\N	\N	7e99a9706bd039eab4e9208b2444e45739b47900491768e3ded5141fc96ca8ab	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-7kNhKhkyC2WSDjCaRE6z2L	TDS_ultralase_plus_СТ_ferment_2023(RUS).pdf	231547	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:59:15.245264+00	2025-11-07 05:59:15.252441+00	\N	\N	\N	\N
50	assistant-production	80:TDS_ultralase_expert_СТ_ferment_2023(RUS).pdf	\N	\N	ed62499e3c639c8957862193bb844a92842c8d6bc50e122b6f190869d6658629	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-4bGqmqYtDgCMzRZ6NxWnmJ	TDS_ultralase_expert_СТ_ferment_2023(RUS).pdf	229929	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:59:20.795891+00	2025-11-07 05:59:20.812733+00	\N	\N	\N	\N
65	assistant-production	98:TDS_liquid_enzymes_for detegent_ferment_2023(RUS).pdf	\N	\N	cf5e4c115f4cf08c2cb77eff0b42f8c5f382711a545d80dbaa2f393eb64e7177	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-TBWhQdo22GHU9xJyUa8ghc	TDS_liquid_enzymes_for detegent_ferment_2023(RUS).pdf	332977	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:01:03.890398+00	2025-11-07 06:01:03.904446+00	\N	\N	\N	\N
51	assistant-production	81:TDS_granulated_enzymes_for_laundry_powder_2023(RUS).pdf	\N	\N	641e99c9cc4420aae24b9d2407c18fc46ae204441f3287036f2eb46437248006	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-T39PJsQoSdJr4mX87XieRy	TDS_granulated_enzymes_for_laundry_powder_2023(RUS).pdf	248188	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:59:25.77488+00	2025-11-07 05:59:25.792043+00	\N	\N	\N	\N
52	assistant-production	82:TDS_ultralase_start_СТ_ferment_2023(RUS).pdf	\N	\N	3ae1935f26725d16fe0c41b2ecca371030cef4a6795b472bf6e47642ef5eb226	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-TksVMaz6bqzzVsHuLM9e6o	TDS_ultralase_start_СТ_ferment_2023(RUS).pdf	226566	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:59:30.194498+00	2025-11-07 05:59:30.210898+00	\N	\N	\N	\N
66	assistant-production	99:TDS_proteasol_standard_plus_ferment_2023(RUS).pdf	\N	\N	dba52146d24fa0a8bce780189ebfd5cee3ac81cc35ede3f9619b17cc74bf4d4c	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-PXBu7z96Aoy8jUT8yfgig3	TDS_proteasol_standard_plus_ferment_2023(RUS).pdf	484396	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:01:08.418284+00	2025-11-07 06:01:08.43363+00	\N	\N	\N	\N
53	assistant-production	83:TDS_ultralase_total_СТ_ferment_2023(RUS).pdf	\N	\N	61d95e2cd564343b6e6bbf5271315ee7e7d0cd0f4599402334333a415e930aa2	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-3cVPjtLvVq3PiymeNtAWmH	TDS_ultralase_total_СТ_ferment_2023(RUS).pdf	228825	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:59:34.802648+00	2025-11-07 05:59:34.817263+00	\N	\N	\N	\N
54	assistant-production	84:TDS_ultralase_standard_СТ_ferment_2023(RUS).pdf	\N	\N	3fab352d2ef08833a4ab15a397e632e69150d06bb1675fa5294f1fe5471c3f62	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-KmL6XZ1nuicj7qof6sUGAW	TDS_ultralase_standard_СТ_ferment_2023(RUS).pdf	227809	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 05:59:38.796047+00	2025-11-07 05:59:38.810669+00	\N	\N	\N	\N
67	assistant-production	100:MSDS_celazim_ultra_ferment_2025(RUS).pdf	\N	\N	8d39bae14a5368ea8947c1c2dd22964f6a2123d9747173e79800092e291a4856	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-TKNGacJ2tTjZmE3nBbwgRw	MSDS_celazim_ultra_ferment_2025(RUS).pdf	651798	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:01:15.800834+00	2025-11-07 06:01:15.815172+00	\N	\N	\N	\N
55	assistant-production	85:TDS_ultralase_profi_СТ_ferment_2023(RUS).pdf	\N	\N	1810c8fd6ddebc9ec6b380d7c789f35091e1cad8ce13a0db4fca37006a5a0fb0	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-DJLi19D7Ln7XojYMkVVHTD	TDS_ultralase_profi_СТ_ferment_2023(RUS).pdf	228110	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:00:09.641142+00	2025-11-07 06:00:09.656619+00	\N	\N	\N	\N
56	assistant-production	86:TDS_ultralase_premium_СТ_ferment_2023(RUS).pdf	\N	\N	96f8ff07a49e37d812405e373a1b18621d0f247537e4f6c36cbd2ce5b826ef91	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-RWifuFJPx6e6oBm18HBybj	TDS_ultralase_premium_СТ_ferment_2023(RUS).pdf	234547	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:00:13.617854+00	2025-11-07 06:00:13.632391+00	\N	\N	\N	\N
68	assistant-production	101:TDS_amylzim_standard_ferment_2022(RUS).pdf	\N	\N	0c31e7d5e2ef9636b0d4e8bc06cd5cba716d8bf3d1c18cbe16fde9a1da4db295	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-PDfL58npDyBqRHKNEuH2Ge	TDS_amylzim_standard_ferment_2022(RUS).pdf	351702	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:01:19.392861+00	2025-11-07 06:01:19.401173+00	\N	\N	\N	\N
57	assistant-production	87:MSDS_AMILZYM_CT_2022_(RUS)__.pdf	\N	\N	842b427f4930f8fe9fbc3e23eb4453692bb5a9ec3a0a612ed6411bcf3665ef16	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-SZBu82rPyVdbspY1SR1XiC	MSDS_AMILZYM_CT_2022_(RUS)__.pdf	712124	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:00:19.961381+00	2025-11-07 06:00:19.97328+00	\N	\N	\N	\N
58	assistant-production	88:MSDS_LIPROZYM_CT_2022_(RUS)__.pdf	\N	\N	1c2aa45e9b5de53b38c2842d5aa1084fd15ad4723c3be71cdd9e46dfa073904e	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-RLAa3JVN5Jfz59RSQLb2nm	MSDS_LIPROZYM_CT_2022_(RUS)__.pdf	711182	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:00:24.561469+00	2025-11-07 06:00:24.579447+00	\N	\N	\N	\N
69	assistant-production	102:MSDS_amylsim_standard_ferment_2023(RUS)__.pdf	\N	\N	f1180b62eb038c62d70d75dd4c30c066643ce6bfb6585ed302515b55b4c76164	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-Mc1m6SwqaVbK1kvnvGxPqM	MSDS_amylsim_standard_ferment_2023(RUS)__.pdf	711642	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:01:24.613431+00	2025-11-07 06:01:24.626425+00	\N	\N	\N	\N
59	assistant-production	89:MSDS_ULTRALASE_PREMIUM_CT_2024(RUS).pdf	\N	\N	ed534a7919e56212c0237fcb34de3ca4878e1702764295048b50c28f5d053668	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-6Xq3dNk8GeCxwwbbixDTDb	MSDS_ULTRALASE_PREMIUM_CT_2024(RUS).pdf	723692	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:00:30.075055+00	2025-11-07 06:00:30.092883+00	\N	\N	\N	\N
60	assistant-production	90:MSDS_PROTEASOL_CT_2022_(RUS)__.pdf	\N	\N	d63bd39a0ecb9f3bc4808bf0f8b0b91d9208836c00c401cfae516644dbbd2467	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-5SvCoicsjSk6k5g3nPQ8WL	MSDS_PROTEASOL_CT_2022_(RUS)__.pdf	717456	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:00:36.9543+00	2025-11-07 06:00:36.968036+00	\N	\N	\N	\N
61	assistant-production	91:MSDS_ULTRALASE_CT_2022_(RUS)__.pdf	\N	\N	76bfe4eb1cd666fad1226ce43423079aa126d2710409a8b59024db20ac8a6eb2	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-H6bvDc4ejjmbX3yPJEF5Rn	MSDS_ULTRALASE_CT_2022_(RUS)__.pdf	719817	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:00:41.575895+00	2025-11-07 06:00:41.591413+00	\N	\N	\N	\N
70	assistant-production	103:MSDS_liprozim_standard_ferment_2023(RUS)__.pdf	\N	\N	0ba7be121cb918a7c9af0b175609b90951e5a06771d064de0f8d04c2ac07b07b	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-T9pcrzjKZ19FsSoGyVASh5	MSDS_liprozim_standard_ferment_2023(RUS)__.pdf	711413	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:01:29.622107+00	2025-11-07 06:01:29.635706+00	\N	\N	\N	\N
141	assistant-production	171:2-2. ZICOS MO-IL_COA.pdf	\N	\N	e5b734aef0872624d3f1172924844db11e3986ce6233fe8a6337a0969bdb8042	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-Vo4SWdLy2mkqQEQ2mLKA9c	2-2. ZICOS MO-IL_COA.pdf	63064	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:34:10.401295+00	2025-11-07 07:34:10.416859+00	\N	\N	\N	\N
71	assistant-production	104:MSDS_proteasol_ferment_2023(RUS)__.pdf	\N	\N	1f811a75fc3f8caf7acfe70cc47391fe048f622c75852aaa911ca2586eb8c6e2	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-8zGkWYdTfZPQA8TpCGcF5N	MSDS_proteasol_ferment_2023(RUS)__.pdf	720660	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:01:34.87743+00	2025-11-07 06:01:34.892723+00	\N	\N	\N	\N
72	assistant-production	105:booklet_liqiud_enzymes_for_detergent_2022(RUS) — копия.pdf	\N	\N	b5d550f5db312c6fe7ca007adff043f2a4da3849d502b7feb6d99dfaf6553a37	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-2kquBDvvw8mRec98rdPMbT	booklet_liqiud_enzymes_for_detergent_2022(RUS) — копия.pdf	3629643	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:01:52.325722+00	2025-11-07 06:01:52.346082+00	\N	\N	\N	\N
73	assistant-production	106:Сертификат Халяль №BY UHRC 053-112 001 H. 00054-1.pdf	\N	\N	407166357f0fe209381b1dcac0485f7df216b05e205e1e77e845470899932725	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-FVXqoLo1ZioBsKBfQY4xH1	Сертификат Халяль №BY UHRC 053-112 001 H. 00054-1.pdf	1332432	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:01:59.260922+00	2025-11-07 06:01:59.274858+00	\N	\N	\N	\N
74	assistant-production	107:tds Isodecanol Ethoxylated  (1000).pdf	\N	\N	3a4a97bc66aea7933d21d4395d404cc2370e7a5e5a17c9887b6bb10382c0d409	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-13GQU3iEyJSyc1Ck42eUyJ	tds Isodecanol Ethoxylated  (1000).pdf	129675	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:02:02.403861+00	2025-11-07 06:02:02.4136+00	\N	\N	\N	\N
75	assistant-production	108:COA_isodecanol_isotridecanol.pdf	\N	\N	223746626c3cfabe1ec3cbade63903830091d3045388217f7706869a5650bd42	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-S54mTyLWSN9xBb9PBa1ADa	COA_isodecanol_isotridecanol.pdf	288299	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:02:06.70955+00	2025-11-07 06:02:06.725841+00	\N	\N	\N	\N
76	assistant-production	109:MSDS Isotridecyl Alcohol Ethoxylated 10EO.pdf	\N	\N	c043b2c097e67e060797a164a80731fbd00dc1b1cefa91b45e2e8d28d59645ea	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-RCzHWcfc1ifDaYi18qhHcP	MSDS Isotridecyl Alcohol Ethoxylated 10EO.pdf	234383	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:02:10.701526+00	2025-11-07 06:02:10.711559+00	\N	\N	\N	\N
77	assistant-production	110:MSDS Isotridecyl Alcohol Ethoxilated 5EO.pdf	\N	\N	3c1031faa83accdc1086bd035c39be2937ae30a55b1720db3665f9ac8aba0549	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-V2xK8J4puhPRtimV5Apzh6	MSDS Isotridecyl Alcohol Ethoxilated 5EO.pdf	267531	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:02:17.794334+00	2025-11-07 06:02:17.809232+00	\N	\N	\N	\N
78	assistant-production	111:MSDS Isotridecyl Alcohol Ethoxylated 6EO.pdf	\N	\N	a8936d9fdb6af91f90fa75204c3d7b1c89fb1037215cde67bf1779d681c0bea1	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-UsfqsV8F7H3xrPzA3ryKTy	MSDS Isotridecyl Alcohol Ethoxylated 6EO.pdf	234337	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:02:23.31379+00	2025-11-07 06:02:23.331907+00	\N	\N	\N	\N
79	assistant-production	112:MSDS Isodecanol Ethoxylated 8EO.pdf	\N	\N	948a0098dfa11377526440d5712ef3e5c1344591e7b35e298b043b3d7f856bea	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-DepzsLcMSrT1vp1bRfF2rh	MSDS Isodecanol Ethoxylated 8EO.pdf	233967	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:02:27.128775+00	2025-11-07 06:02:27.13965+00	\N	\N	\N	\N
80	assistant-production	113:MSDS Isotridecyl Alcohol Ethoxylated 12EO.pdf	\N	\N	ce198476608ec4c329859e338b754b081e996d1b64872e7854220fd28bd71b97	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-RtqcdmVXDrYWupmuKc14X4	MSDS Isotridecyl Alcohol Ethoxylated 12EO.pdf	230204	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:02:32.14538+00	2025-11-07 06:02:32.157309+00	\N	\N	\N	\N
81	assistant-production	114:tds Isotridecyl Alcohol Ethoxylated.pdf	\N	\N	4a3aeb26eb66fdbe379eeb6dcc8efdecf83fb73d1644c9e47dcc86bfe3c28a21	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-HtE27jENuvKPsGjG6DNXZX	tds Isotridecyl Alcohol Ethoxylated.pdf	159431	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:02:35.896005+00	2025-11-07 06:02:35.916374+00	\N	\N	\N	\N
82	assistant-production	115:MSDS Isodecanol Ethoxylated 7EO.pdf	\N	\N	606c50279c8797743449ccdbbe554d5b9877be561872cc572eea934dd2936d24	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-7ab5KnmLFWGEycjjLGPipJ	MSDS Isodecanol Ethoxylated 7EO.pdf	233762	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:02:41.73239+00	2025-11-07 06:02:41.748066+00	\N	\N	\N	\N
83	assistant-production	116:ZIBO каталог.pdf	\N	\N	c7ef45dcc1f7728f28e9b579159f5f98d8a7609829523c60a0b7dacfb0872529	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-Ks2Eq5TuWE8drvRWJjJL1S	ZIBO каталог.pdf	9669222	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:03:14.601401+00	2025-11-07 06:03:14.616088+00	\N	\N	\N	\N
84	assistant-production	117:5-3. ZICOS AAVC_en.pdf	\N	\N	bd9a588b63f5bdfd8dc4387faa5637300d84cc555b2bc0242d938cddc2273249	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-2V4Uh2rrrW7Scr9XwaSBv2	5-3. ZICOS AAVC_en.pdf	79329	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 06:03:17.875242+00	2025-11-07 06:03:17.88786+00	\N	\N	\N	\N
85	assistant-production	92:№126 Липрозим Стандарт №4 от 22.05.2023.PDF	\N	\N	eb23b622f5453d8a7d4d83a9bc06a01167dabf4e12f67230b3c3326875d1e9de	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-8u4uXPkQZwKFV8V1dNqAv2	№126 Липрозим Стандарт №4 от 22.05.2023.PDF	108524	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:26:41.599795+00	2025-11-07 07:26:41.629704+00	\N	\N	\N	\N
86	assistant-production	93:№141 Протеазол-Стандарт №4 от 29.06.2023.PDF	\N	\N	35dafb1c5c5edfc612bbe313f6722406cff95429f953e5e84f7bfda74270f1f2	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-6RVWMw2omeWeA43XJE6Bew	№141 Протеазол-Стандарт №4 от 29.06.2023.PDF	104928	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:26:44.113056+00	2025-11-07 07:26:44.126882+00	\N	\N	\N	\N
87	assistant-production	94:№142 Амилзим Стандарт №2 от 29.06.2023.PDF	\N	\N	9e63a5c738ccbc60b814797d9e103dbe37cdedaf456c9bc67857061f0e9cdd2d	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-4tFyMkzatu5jL1mRPchpMs	№142 Амилзим Стандарт №2 от 29.06.2023.PDF	109695	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:26:47.406757+00	2025-11-07 07:26:47.415709+00	\N	\N	\N	\N
88	assistant-production	118:5-3. ZICOS AAVC_COA.pdf	\N	\N	546ff7743641c376493d9d17a940cc590024ad8b1623f3a29985ae96867a370d	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-MtiCU5vVYpeaDrUYAa1XND	5-3. ZICOS AAVC_COA.pdf	77054	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:26:51.570042+00	2025-11-07 07:26:51.58096+00	\N	\N	\N	\N
89	assistant-production	119:5-3. ZICOS AAVC_SPEC_en.pdf	\N	\N	b7b55c62a58d89221b09fdd2a71215ff4a3b1858cfaf2f93aa0927f07f3864ed	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-6R5VJb1L2diDmFtLmCn1fj	5-3. ZICOS AAVC_SPEC_en.pdf	58993	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:26:54.16795+00	2025-11-07 07:26:54.183146+00	\N	\N	\N	\N
90	assistant-production	120:5-3. ZICOS AAVC_MSDS_en.pdf	\N	\N	8f5d59ebbe358519f2da6f3dfec55fb59bd2a464b6717c57347e2ff68fd17b01	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-GqQWKGebLsRdng6VJnuuC7	5-3. ZICOS AAVC_MSDS_en.pdf	126306	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:26:57.977855+00	2025-11-07 07:26:57.991632+00	\N	\N	\N	\N
91	assistant-production	121:5-3. ZICOS AAVC_RDS_en.pdf	\N	\N	9e7d5b58f5de44d06f7450da5538b307c2117301f5a3c9ce4ed9b483ab7e2a9f	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-1cFEm6hWJsyiKbMMmHDSQy	5-3. ZICOS AAVC_RDS_en.pdf	83542	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:27:00.723016+00	2025-11-07 07:27:00.735049+00	\N	\N	\N	\N
92	assistant-production	122:ZICOS EM-PL_COA.pdf	\N	\N	22bf55f430538c1c582e20b6d6d9e9d7479fa437e77f69d0d9226acb2389b03d	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-N4X67PEw2pNjTjFpy1ptuw	ZICOS EM-PL_COA.pdf	63058	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:27:03.326306+00	2025-11-07 07:27:03.339625+00	\N	\N	\N	\N
93	assistant-production	123:ZICOS EM-PL_TDS.pdf	\N	\N	7d749376bc8bff0d4f324c91110e1e7eef85e28f20a2aca78970df8b5d9a4f8d	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-7fhPB8zZhQ4GD2SnagDBZ4	ZICOS EM-PL_TDS.pdf	87474	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:27:07.892234+00	2025-11-07 07:27:07.905974+00	\N	\N	\N	\N
94	assistant-production	124:ZICOS EM-PL_MSDS.pdf	\N	\N	37b469732eb2bbc2afbe85a0f213d38723b35b12246d3b85caf97e61f2843a68	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-RLwmpyQEXTzgHmd2NJ9wSW	ZICOS EM-PL_MSDS.pdf	93986	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:27:10.763673+00	2025-11-07 07:27:10.775005+00	\N	\N	\N	\N
142	assistant-production	172:2-3. ZICOS MO-IL_SPEC_en.pdf	\N	\N	9ccaccd6698f4839948a6480936e35f2b3d06d6d35e692372957323eaf4f632b	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-XrkRgzcMrSMcXsb8MKkjx4	2-3. ZICOS MO-IL_SPEC_en.pdf	55172	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:34:13.177698+00	2025-11-07 07:34:13.192901+00	\N	\N	\N	\N
143	assistant-production	173:2-1. ZICOS MO-IL_en.pdf	\N	\N	58db23de3fae0986d1e4be665a8add88099e5f0405ae3618c15bc8c52a5667b2	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-GrBfc8KExCo4b1XoauMV5s	2-1. ZICOS MO-IL_en.pdf	80873	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:34:17.466878+00	2025-11-07 07:34:17.47719+00	\N	\N	\N	\N
144	assistant-production	174:2-5. ZICOS MO-IL_RDS.pdf	\N	\N	b1570f6efca92ff876687ca6436d959e5b9607e0f3218f257aae8a3d46d149ac	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-3LTbPjqZFVAsfaTX5hembM	2-5. ZICOS MO-IL_RDS.pdf	72228	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:34:20.884827+00	2025-11-07 07:34:20.900082+00	\N	\N	\N	\N
145	assistant-production	175:2-6. ZICOS MO-IL_MSDS_en.pdf	\N	\N	ac26ad8cf690fe56399831b22d637d537b22fc86efcec4c44d87692aa43824f0	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-8TiZ1ERkc2HaDm6RcScrr7	2-6. ZICOS MO-IL_MSDS_en.pdf	87395	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:34:24.538459+00	2025-11-07 07:34:24.55289+00	\N	\N	\N	\N
146	assistant-production	176:12-1. ZICOS PR-HE_en.pdf	\N	\N	9f6d58c9a65bf9043cd547837b38897bee816a8a5a730a33a1df54e2afa0be08	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-7m1AeSxHtxv597838upnR4	12-1. ZICOS PR-HE_en.pdf	104318	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:34:26.963364+00	2025-11-07 07:34:26.974209+00	\N	\N	\N	\N
147	assistant-production	177:ZICOS PR-HE COA.pdf	\N	\N	deb30425df783989bc0e48b022f08234169e1539fab3a91ae30f576635b429d8	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-ALcGWq5pSu62JeBPAJgr7o	ZICOS PR-HE COA.pdf	109534	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:34:29.839063+00	2025-11-07 07:34:29.843972+00	\N	\N	\N	\N
148	assistant-production	178:ZICOS PR-HE ZERO_MSDS.pdf	\N	\N	eabc173702b06dbd2fcc9e27721c7fa2d69380c11cd722c436bda058f7feb90b	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-VxYXoDJJu8ZPmFY6EqFV8D	ZICOS PR-HE ZERO_MSDS.pdf	165513	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:34:33.018307+00	2025-11-07 07:34:33.031964+00	\N	\N	\N	\N
149	assistant-production	179:ZICOS PR-HE MSDS.pdf	\N	\N	709b279d666ad9b68f4e3b4c880ed8b3081513b67e64a6cbec98fadd8863a88c	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-9BNWd4UuR1uiEVDtSLJrmi	ZICOS PR-HE MSDS.pdf	165451	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:34:36.212383+00	2025-11-07 07:34:36.224964+00	\N	\N	\N	\N
150	assistant-production	180:ZICOS PR-HE Zero_ORIGIN COUNTRY.pdf	\N	\N	446bb87df2b4af87272aae88ad253efe57d965812494fa684008b3a338c9a067	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-RkUqqzawVJ18zaeRZZzgw1	ZICOS PR-HE Zero_ORIGIN COUNTRY.pdf	57941	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:34:40.512265+00	2025-11-07 07:34:40.524525+00	\N	\N	\N	\N
151	assistant-production	181:ZICOS PR-HE ZERO_Spec.pdf	\N	\N	36d3991f4dfbddd73fe590948802fbf2ec67d344089431489ac66b8e1b57e234	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-UUextXyYSA6XzXLkUiRCtU	ZICOS PR-HE ZERO_Spec.pdf	54885	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:34:43.239323+00	2025-11-07 07:34:43.252812+00	\N	\N	\N	\N
152	assistant-production	182:ZICOS PR-HE ZERO COA.pdf	\N	\N	4a63a9be6c8050465169609fbafe9d88ff3d7d5cfecc8d5c5562d35e1ad860cd	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-WSMMnuFQgUZ3HvPqTGpTqU	ZICOS PR-HE ZERO COA.pdf	109539	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:34:46.451966+00	2025-11-07 07:34:46.466189+00	\N	\N	\N	\N
153	assistant-production	183:ZICOS PR-HE ZERO_TDS.pdf	\N	\N	2a01a29d1dada7d1b7095e6f35b80ff87614f19daa8dda301154c909f1ecaf7e	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-UZZDPgtAf4G4iaucnKJQ5f	ZICOS PR-HE ZERO_TDS.pdf	103706	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:34:49.071786+00	2025-11-07 07:34:49.086497+00	\N	\N	\N	\N
154	assistant-production	184:ZIKO_COSMOS.pdf	\N	\N	4f91556ab6de44c9abf75cb09410ad9123d080aa8d3d6cda90fce44528d9ceeb	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-1V1v1aQCtXaZv23fQ58rfP	ZIKO_COSMOS.pdf	105500	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:34:52.909293+00	2025-11-07 07:34:52.922147+00	\N	\N	\N	\N
161	assistant-production	191:Gaĭd_na_Tovar_-_chast_1.pdf	\N	\N	f3ce93dcfd56a665510202dd80b990fe70609eb91dc0cb280191b30a95056572	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-2KDL2Py7ke8im2QZ39VRWr	Gaĭd_na_Tovar_-_chast_1.pdf	10517132	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:36:52.429554+00	2025-11-07 07:36:52.445075+00	\N	\N	\N	\N
167	assistant-bucket2	167:23:Аромо диффузоры 1.xlsx	\N	\N	fbcc8ae20b710a9d60ea18b24977ec2d12a7d9ba11d61a3b252048cf2c7e7369	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-XP6437W2KyRccGeF7d8JCi	23:Аромо диффузоры 1.xlsx	11266477	application/vnd.openxmlformats-officedocument.spreadsheetml.sheet	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 08:03:01.056831+00	2025-11-07 08:04:10.641435+00	\N	\N	\N	\N
170	assistant-bucket2	170:24:КП СТЕКЛО ДЛЯ ПАРФЮМА.xlsx	\N	\N	dad2c2014163f96e92f190189b73281753a60be78c41a1337d1775bb2ab04d02	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-4G8SfQf1pejkfxSsZLMnKs	24:КП СТЕКЛО ДЛЯ ПАРФЮМА.xlsx	4028302	application/vnd.openxmlformats-officedocument.spreadsheetml.sheet	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 08:04:37.002249+00	2025-11-07 08:05:28.019286+00	\N	\N	\N	\N
168	assistant-bucket2	168:25:КП СТИКИ.xlsx	\N	\N	afb2678b58b51281ccdcf963a23ed40622a2fd06e85dfe222548b8468cd7973d	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-TnFqZpPWTCh2E5BACem24F	25:КП СТИКИ.xlsx	3150904	application/vnd.openxmlformats-officedocument.spreadsheetml.sheet	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 08:04:36.997456+00	2025-11-07 08:05:30.248048+00	\N	\N	\N	\N
172	assistant-bucket2	172:28:КП укупорка.xlsx	\N	\N	a8ac866a98c89dc4e66f1920b9370e48f7af4fc041ab021717ac2f8cc21092fa	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-18ot1HvGGRzNa2XJYq2wfc	28:КП укупорка.xlsx	26993170	application/vnd.openxmlformats-officedocument.spreadsheetml.sheet	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 08:04:37.070255+00	2025-11-07 08:06:48.507415+00	\N	\N	\N	\N
177	assistant-bucket2	177:31:Каталог_упаковки_декоративной_косметики_04_04_2024 1.xlsx	\N	\N	173cdb2ec6a53dd4d103094f4c757ac2996cdab2ac96fe27aef82a1b219c4182	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-994fH2ojQhKjGmQDZ34yhE	31:Каталог_упаковки_декоративной_косметики_04_04_2024 1.xlsx	14979908	application/vnd.openxmlformats-officedocument.spreadsheetml.sheet	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 08:07:27.57566+00	2025-11-07 08:08:55.531636+00	\N	\N	\N	\N
96	assistant-production	126:ZICOS GE-DP RDS.pdf	\N	\N	70510dd2129c84ef18cd4516365a8d670e91f4af00572084edb3ce62674008dc	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-JbK9dAZDESCMbwBmSKNjcd	ZICOS GE-DP RDS.pdf	74983	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:27:52.218704+00	2025-11-07 07:27:52.235414+00	\N	\N	\N	\N
97	assistant-production	127:ZICOS GE-DP MSDS.pdf	\N	\N	db57b9b6d8b95d0dad971850d10c457b76a1377af35c62a333bf98742b3bdb62	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-X47dGPWrVMib5DbK8RRMTb	ZICOS GE-DP MSDS.pdf	93314	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:27:55.520418+00	2025-11-07 07:27:55.535249+00	\N	\N	\N	\N
98	assistant-production	128:ZICOS GE-DP.pdf	\N	\N	b87494b316df4bb807384bc0fec8ba834bc514903d27d6c4a9c8c9d27ad68d55	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-BC2GDHmmpuR6VHVbcunxwx	ZICOS GE-DP.pdf	83179	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:27:58.504562+00	2025-11-07 07:27:58.52281+00	\N	\N	\N	\N
99	assistant-production	129:ZICOS MO-BS TDS.pdf	\N	\N	8843a2095c68c7999754a53b0d185fb62df6c90f5839c93cb865017a40c3eece	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-MS6msrku8uYgFcEfQsy1HV	ZICOS MO-BS TDS.pdf	58466	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:28:03.187393+00	2025-11-07 07:28:03.203376+00	\N	\N	\N	\N
100	assistant-production	130:ZICOS MO-BS MSDS.pdf	\N	\N	f05c4a547c25a704194d47727a18c8bb8d2f021552fe4e87238a240fc5ee2373	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-D7UmeazDcEwbR9nfsfAG5p	ZICOS MO-BS MSDS.pdf	81853	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:28:07.394652+00	2025-11-07 07:28:07.410968+00	\N	\N	\N	\N
101	assistant-production	131:ZICOS MO-BS.pdf	\N	\N	a054785eb94408112528d0f4b974aa85b45147d97a086bb66ce939d396bf784e	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-LM4jQSkqpot3tWvvZNe4ee	ZICOS MO-BS.pdf	66824	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:28:10.564399+00	2025-11-07 07:28:10.587004+00	\N	\N	\N	\N
102	assistant-production	132:7-2. ZICOS MO-CCC_COA.pdf	\N	\N	31d75d25395f3dda6ce057cabb558e73c7ed42725a897d3ded0b47145511ec85	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-Ah9dNWmU7w8gVxbM6tLXNh	7-2. ZICOS MO-CCC_COA.pdf	62698	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:28:13.709603+00	2025-11-07 07:28:13.728935+00	\N	\N	\N	\N
103	assistant-production	133:7-3. ZICOS MO-CCC_SPEC_en.pdf	\N	\N	135fb88fc79514264321e58b525a16e3d85c498f8e6905acdab0478523944551	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-1oJMJY5eD2hQY4rcKLXGpV	7-3. ZICOS MO-CCC_SPEC_en.pdf	55136	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:28:16.779546+00	2025-11-07 07:28:16.79325+00	\N	\N	\N	\N
104	assistant-production	134:ZICOS MO-CCC__RDS.pdf	\N	\N	22f094bf505d3c848dad7e7f006301ac23bf6e6c836b9d6c93e2d710609eb708	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-WTzMWJGt3uFeufp3X5UfPJ	ZICOS MO-CCC__RDS.pdf	59877	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:28:19.88302+00	2025-11-07 07:28:19.898717+00	\N	\N	\N	\N
105	assistant-production	135:7-6. ZICOS MO-CCC_MSDS_en.pdf	\N	\N	6cff5e28355b8c9a974f02aaf46b855264ad578c6fa2dd52e739819aa11be0d4	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-RZnzyaqi77XfcmieGXBEXR	7-6. ZICOS MO-CCC_MSDS_en.pdf	93406	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:28:23.483055+00	2025-11-07 07:28:23.500919+00	\N	\N	\N	\N
106	assistant-production	136:ZICOS MO-CCC.pdf	\N	\N	57e551e753d164626a22bdf57dd565e6c427cb25f597b40c652a000bc19a8cc5	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-9vsNuMJtfJaucKBmwdrNhJ	ZICOS MO-CCC.pdf	113986	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:28:28.672136+00	2025-11-07 07:28:28.685733+00	\N	\N	\N	\N
107	assistant-production	137:7-1. ZICOS MO-CCC_en.pdf	\N	\N	57e551e753d164626a22bdf57dd565e6c427cb25f597b40c652a000bc19a8cc5	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-4LbzqRfF2FXkoPtMu5cc2y	7-1. ZICOS MO-CCC_en.pdf	113986	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:28:32.99+00	2025-11-07 07:28:33.004482+00	\N	\N	\N	\N
108	assistant-production	138:7-5. ZICOS MO-CCC__RDS.pdf	\N	\N	22f094bf505d3c848dad7e7f006301ac23bf6e6c836b9d6c93e2d710609eb708	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-Fq7KkyTxdxjEBbR3icBoLX	7-5. ZICOS MO-CCC__RDS.pdf	59877	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:28:35.791524+00	2025-11-07 07:28:35.806683+00	\N	\N	\N	\N
109	assistant-production	139:ZICOS MO-CCC_MSDS_en.pdf	\N	\N	6cff5e28355b8c9a974f02aaf46b855264ad578c6fa2dd52e739819aa11be0d4	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-QVJevDG6YGpuGmRpkHGPYa	ZICOS MO-CCC_MSDS_en.pdf	93406	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:28:38.657043+00	2025-11-07 07:28:38.663026+00	\N	\N	\N	\N
110	assistant-production	140:ZICOS MO-DСC msds ru.pdf	\N	\N	202b7e96662375f334935a9e858268532dc6defe5e35316698f3ed0d72178f46	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-1VMag8242M7ioPPq3rSqoR	ZICOS MO-DСC msds ru.pdf	263086	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:28:44.150842+00	2025-11-07 07:28:44.16494+00	\N	\N	\N	\N
111	assistant-production	141:6-3. ZICOS MO-CO_SPEC_en.pdf	\N	\N	93c0c1a76d44e9e050b39593b172eead9c5670651acfb7ae5d8f8d123d1404f3	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-U3QhRwRHGqQp3fSuFP2qWc	6-3. ZICOS MO-CO_SPEC_en.pdf	55144	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:28:47.222842+00	2025-11-07 07:28:47.238104+00	\N	\N	\N	\N
112	assistant-production	142:6-2. ZICOS MO-CO_COA.pdf	\N	\N	87dc85dc6980f4353063c8c3e50bcc0990c5ad4586471cdb7c56b2d8feae5c2e	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-NMr2HVn7EfsoGigjkLYX8C	6-2. ZICOS MO-CO_COA.pdf	63236	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:28:49.885965+00	2025-11-07 07:28:49.89747+00	\N	\N	\N	\N
113	assistant-production	143:6-1. ZICOS MO-CO_en.pdf	\N	\N	578615fb88264d3d6806cfe58d70975aa74c3d41f4cd4b435aa23062df4ea6bd	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-XB1gCj9F6mae5WmbKDYK2D	6-1. ZICOS MO-CO_en.pdf	127238	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:28:52.915442+00	2025-11-07 07:28:52.927907+00	\N	\N	\N	\N
114	assistant-production	144:6-5. ZICOS MO-CO_RDS.pdf	\N	\N	f000005de324b0e089b106c1df149ff5376d8dc1fee8106aa5c13aa97621cfde	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-SGYW6paqCwocFbWA3VutDm	6-5. ZICOS MO-CO_RDS.pdf	72558	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:28:55.444075+00	2025-11-07 07:28:55.45663+00	\N	\N	\N	\N
115	assistant-production	145:ZICOS MO-CO MSDS.pdf	\N	\N	67c1701e1dfc417204986e7c69d4665c7d6322016bff7534fa1dcc4b7ccb1a60	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-ETXyovBuP8TFUCRCWia3rr	ZICOS MO-CO MSDS.pdf	93819	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:28:59.716405+00	2025-11-07 07:28:59.728808+00	\N	\N	\N	\N
116	assistant-production	146:ZICOS MO-CO.pdf	\N	\N	4f078d2b4e4137136c4b4110536ba9c91d0e4c3e7e6e1637b694a34ae7601c72	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-Nuce1fUKZ5rsEjkox6yr7r	ZICOS MO-CO.pdf	127328	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:29:02.321006+00	2025-11-07 07:29:02.338758+00	\N	\N	\N	\N
117	assistant-production	147:4-1. ZICOS MO-DB_en.pdf	\N	\N	0cca026179cb4e7f2170451be6d56c939b2dfaf0b6f2dac669c1652ecc20f30b	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-VwoXJzLUnZuUseYpmjAwMb	4-1. ZICOS MO-DB_en.pdf	64728	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:29:06.574595+00	2025-11-07 07:29:06.589514+00	\N	\N	\N	\N
118	assistant-production	148:4-2. ZICOS MO-DB_COA.pdf	\N	\N	d5deb701eef4e0726ea176b593717908e612fe6c0ed3116f00c3ee534fcbc18e	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-9fSYqb5E9UnbZPR6KqJw8K	4-2. ZICOS MO-DB_COA.pdf	64157	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:29:09.639232+00	2025-11-07 07:29:09.645122+00	\N	\N	\N	\N
119	assistant-production	149:4-3. ZICOS MO-DB_SPEC_en.pdf	\N	\N	210c0bf3e1cc9468fa06ed8f6fa0484f6e3c84c3f0c56545be76b0c717a4d546	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-DuzZdeJEhfGXWpE1U2pmZ2	4-3. ZICOS MO-DB_SPEC_en.pdf	54795	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:29:12.306044+00	2025-11-07 07:29:12.319317+00	\N	\N	\N	\N
120	assistant-production	150:4-5. ZICOS MO-DB_RDS.pdf	\N	\N	f156e9a7c5e1bca2275ddc351669a8079173acdfdae017dc4852a26db7ba4974	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-DzCiBLhZbqq3Khx1QQejXy	4-5. ZICOS MO-DB_RDS.pdf	71227	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:29:17.739713+00	2025-11-07 07:29:17.751843+00	\N	\N	\N	\N
121	assistant-production	151:ZICOS MO-DB MSDS_en.pdf	\N	\N	25ae2f04d2f15c7cefdcc44ac471b140ebe05710aea7db2abe04ddaf55073a25	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-K9o1gzB6SuMqvkiPWgn6iK	ZICOS MO-DB MSDS_en.pdf	78779	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:29:22.550215+00	2025-11-07 07:29:22.563542+00	\N	\N	\N	\N
122	assistant-production	152:3-2. ZICOS MO-DCC_COA.pdf	\N	\N	da2d20d6e4ce4435da8be646ed1dd5a6c3651fc6c61d798aa50bcab36d1c83d2	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-URriCy91HjbuREA6c7c7iK	3-2. ZICOS MO-DCC_COA.pdf	63654	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:29:26.854981+00	2025-11-07 07:29:26.879908+00	\N	\N	\N	\N
155	assistant-production	185:지코 ISO 9001(2024).pdf	\N	\N	404755456dfdb55c57d90bd4f5f5f8533318f8832e7eebc6e44ef2c79d95b123	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-FsBLYLRCBQgjMywgbdVEoJ	지코 ISO 9001(2024).pdf	612223	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:35:48.997603+00	2025-11-07 07:35:49.027556+00	\N	\N	\N	\N
123	assistant-production	153:3-1. ZICOS MO-DCC_en.pdf	\N	\N	77deeb3a76911417d7439660fd285099d1c68df05b4317a7049b200f62e07955	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-BV5xqTtjHfPhtPPQj8WPjW	3-1. ZICOS MO-DCC_en.pdf	82757	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:29:29.7425+00	2025-11-07 07:29:29.755655+00	\N	\N	\N	\N
124	assistant-production	154:3-3. ZICOS MO-DCC_SPEC_en.pdf	\N	\N	0d366f585f4213891180bf73e6fab6893d1ebae4226c871fc697fe24745f0870	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-Jh1e1efaHUZZ24KY73jqr4	3-3. ZICOS MO-DCC_SPEC_en.pdf	56907	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:29:32.44452+00	2025-11-07 07:29:32.456064+00	\N	\N	\N	\N
125	assistant-production	155:3-5. ZICOS MO-DCC_RDS.pdf	\N	\N	7035085533534a890c370a8eefd20c392f27c0f952633e93a43fb12eb2ec4840	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-9NypQX6USduzArVRVgdDwh	3-5. ZICOS MO-DCC_RDS.pdf	72196	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:33:18.393987+00	2025-11-07 07:33:18.421558+00	\N	\N	\N	\N
182	assistant-bucket2	182:188:Ведомость по заказам поставщикам - Для SNOP XLSX.xlsx	\N	\N	de4f598ca64c304f20d39f479b828ac169da0952079de99c7449c960b9d85fe9	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-6wYLnpWjmpZFje7XeuhA2A	188:Ведомость по заказам поставщикам - Для SNOP XLSX.xlsx	87992	application/vnd.openxmlformats-officedocument.spreadsheetml.sheet	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 08:09:22.367182+00	2025-11-07 08:10:26.585362+00	\N	\N	\N	\N
126	assistant-production	156:ZICOS MO-DCC_MSDS_en.pdf	\N	\N	bcd35bae224b8468659fb8b304eb79745a485760216766cc63fe6eadc575bce3	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-Gdirx3L4wdPdpyLwqYioYt	ZICOS MO-DCC_MSDS_en.pdf	93327	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:33:21.560983+00	2025-11-07 07:33:21.588189+00	\N	\N	\N	\N
127	assistant-production	157:ZICOS MO-DCC_Halal Statement.pdf	\N	\N	aea1a97c59620baf98eb74e427739d85dd6fec97f68258f8fa1058751520e32a	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-3d15gJ1ujsRvJriRMGcHkS	ZICOS MO-DCC_Halal Statement.pdf	291590	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:33:25.613578+00	2025-11-07 07:33:25.623027+00	\N	\N	\N	\N
128	assistant-production	158:5-3. ZICOS MO-DE_SPEC_en_2506.pdf	\N	\N	991d22a3af6e6454e65f21bfb262433ef24d1de5a9367a46723658ca148e9b3c	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-AMUmxBMco5RHZGfDMDCcLX	5-3. ZICOS MO-DE_SPEC_en_2506.pdf	61114	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:33:28.523383+00	2025-11-07 07:33:28.541481+00	\N	\N	\N	\N
129	assistant-production	159:5-1. ZICOS MO-DE_¬є---¦¬э_en.pdf	\N	\N	055198d8ca38bb5b71187e45746f869ac034eec93f09d2d4b248ed502f299b93	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-C1o8HXK8YR8zampUXB77HQ	5-1. ZICOS MO-DE_¬є---¦¬э_en.pdf	82692	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:33:32.268321+00	2025-11-07 07:33:32.28618+00	\N	\N	\N	\N
130	assistant-production	160:5-5. ZICOS MO-DE_RDS.pdf	\N	\N	55d69a188dbae63f7d3e85b99bbeaffc58795a7da564c5ce95cc5036dfc87cb0	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-KmaDjyNFeBK3ZRSVnCyopX	5-5. ZICOS MO-DE_RDS.pdf	70929	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:33:35.652545+00	2025-11-07 07:33:35.667403+00	\N	\N	\N	\N
131	assistant-production	161:5-6. ZICOS MO-DE_ MSDS_en.pdf	\N	\N	77070936fb672d82a8f64de3a993efa37ca50b5edeb58b5c022ff44bd7be8744	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-K2AkiWMkHPmDwg6dth3FDc	5-6. ZICOS MO-DE_ MSDS_en.pdf	100208	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:33:38.558075+00	2025-11-07 07:33:38.565601+00	\N	\N	\N	\N
132	assistant-production	162:Дикаприлиловый эфир ZICOS MO-DE ZIKO Корея ПК  допзапрос от 06.10.25.pdf	\N	\N	72fd0e2844ecfa8a271e9249501069802039499e973e712d816a9280690e6068	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-QaXUKZrB25acPUA5i8nEvs	Дикаприлиловый эфир ZICOS MO-DE ZIKO Корея ПК  допзапрос от 06.10.25.pdf	174280	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:33:41.200903+00	2025-11-07 07:33:41.210664+00	\N	\N	\N	\N
133	assistant-production	163:ZICOS MO-DE_msds_рус.pdf	\N	\N	220382a7f024b7b58425a009912e91eec4d1d7772e54f9fc21af011a094627d0	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-NPsJLeDLfWSTSt3SzeKChj	ZICOS MO-DE_msds_рус.pdf	283668	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:33:45.112449+00	2025-11-07 07:33:45.142631+00	\N	\N	\N	\N
134	assistant-production	164:8-1. ZICOS MO-DEL_en.pdf	\N	\N	c4b80dbfe1716cd678d18b25745b63491d82f6039399506f38978736b808f31b	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-4aeH4bsxUdyp33SoT4rQWU	8-1. ZICOS MO-DEL_en.pdf	73418	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:33:47.744635+00	2025-11-07 07:33:47.75784+00	\N	\N	\N	\N
135	assistant-production	165:8-1. ZICOS MO-DEL_MSDS_en.pdf	\N	\N	18a0f88fcf0c848624b2123c653e6079fb43b5bd784e136bdf62dd22045158eb	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-SAjrwLrpUdbzc6aV4LCG7J	8-1. ZICOS MO-DEL_MSDS_en.pdf	161377	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:33:51.760145+00	2025-11-07 07:33:51.77762+00	\N	\N	\N	\N
136	assistant-production	166:ZICOS MO-DEL COA.pdf	\N	\N	ff0de80ef50a90350bf8f1a55123366ed9f961bb2d92833628e47dcb9bed6d5f	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-7irSVJ4bfWWmKrvmmCqwrR	ZICOS MO-DEL COA.pdf	76315	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:33:54.534876+00	2025-11-07 07:33:54.553932+00	\N	\N	\N	\N
137	assistant-production	167:8-5. ZICOS MO-DEL_RDS.pdf	\N	\N	d7f1a52e6d833e95ee4355546b7b54eb125cb098333e97a09aebe349c3cff85d	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-PrXPkc2Js5sonTaAx8Pwiw	8-5. ZICOS MO-DEL_RDS.pdf	71661	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:33:57.137769+00	2025-11-07 07:33:57.150631+00	\N	\N	\N	\N
138	assistant-production	168:ZICOS MO-DEL ISO 16128 Index Status.pdf	\N	\N	713e774bb611509a355143e731158e99aa28d5a2b6504373af68bde1af3efa7e	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-CdVbQZ6dhRCpQrWkqkdacL	ZICOS MO-DEL ISO 16128 Index Status.pdf	452597	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:34:01.394783+00	2025-11-07 07:34:01.409215+00	\N	\N	\N	\N
139	assistant-production	169:ZICOS MO-DIPS TDS.pdf	\N	\N	88e35704af8ed146968ff609da71cc4bd6966791368b0a4b52dd7e61a246260b	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-Q6wy1SBdG2AMa3DjigBwB9	ZICOS MO-DIPS TDS.pdf	57624	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:34:03.80245+00	2025-11-07 07:34:03.815063+00	\N	\N	\N	\N
140	assistant-production	170:ZICOS MO-DIPS MSDS.pdf	\N	\N	6e38eee9521977808f5005c7501e2396c3e8c2dad973177b7fd01dca04e588ef	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-EK3pCzhJwQnERXpM8j97tX	ZICOS MO-DIPS MSDS.pdf	77804	application/pdf	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 07:34:07.641274+00	2025-11-07 07:34:07.656697+00	\N	\N	\N	\N
169	assistant-bucket2	169:29:КП ОЛИВЕР.xlsx	\N	\N	87691ed4c2f651978451437012e0ce9d51cc0adaeb259f4afd4ac3039b2f85af	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-BaaHHkpHwH7opRhGzuNjds	29:КП ОЛИВЕР.xlsx	3021554	application/vnd.openxmlformats-officedocument.spreadsheetml.sheet	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 08:04:37.00173+00	2025-11-07 08:05:20.411771+00	\N	\N	\N	\N
171	assistant-bucket2	171:26:КП УКУПОРКА CENTER.xlsx	\N	\N	42420c7cb80b19f887ea671fa17e90f4d1c4a5e4b428d13ec5a0a9f7d4ed3db6	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-WMp889Pwp7gRaJZFbgyFsx	26:КП УКУПОРКА CENTER.xlsx	7346892	application/vnd.openxmlformats-officedocument.spreadsheetml.sheet	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 08:04:37.006733+00	2025-11-07 08:06:14.643096+00	\N	\N	\N	\N
175	assistant-bucket2	175:45:Состояния маршрутных листов - для продаж XLSX (1).xlsx	\N	\N	31b51455a3f182bfe582f440e27ef729593333fb726fdaae49a8419f76c33dbe	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-M1KF44WvAzUu6oSEi5hqai	45:Состояния маршрутных листов - для продаж XLSX (1).xlsx	44169	application/vnd.openxmlformats-officedocument.spreadsheetml.sheet	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 08:07:27.533174+00	2025-11-07 08:07:40.234975+00	\N	\N	\N	\N
179	assistant-bucket2	179:190:Заказы поставщикам (этапы кратко) - Упаковка XLSX (1).xlsx	\N	\N	baae7c11ce49129ca1d317826da1b6f63832ab058697a6fe190c86ae7acfa1fb	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-Nbxr1EdNn56xSN7zWPfGTx	190:Заказы поставщикам (этапы кратко) - Упаковка XLSX (1).xlsx	61201	application/vnd.openxmlformats-officedocument.spreadsheetml.sheet	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 08:09:22.363631+00	2025-11-07 08:09:34.529753+00	\N	\N	\N	\N
180	assistant-bucket2	180:189:Прогноз продаж XLSX.xlsx	\N	\N	62621ffe9f16f762a436a7d897593fa6983d98f58be4b10cb797f9c277ea4f20	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-JCcEsoxudLUR9QrNFQZAQa	189:Прогноз продаж XLSX.xlsx	95406	application/vnd.openxmlformats-officedocument.spreadsheetml.sheet	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 08:09:22.365853+00	2025-11-07 08:10:31.464976+00	\N	\N	\N	\N
173	assistant-bucket2	173:47:Состояния заказов поставщикам XLSX.xlsx	\N	\N	bb8de777244859c3b185d740c9ea1f030ef3e7e9c5021bcd220137ee5bd3012e	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-FkKmZ8XXiwapHqqC5FXFke	47:Состояния заказов поставщикам XLSX.xlsx	235404	application/vnd.openxmlformats-officedocument.spreadsheetml.sheet	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 08:07:27.529484+00	2025-11-07 08:07:47.865755+00	\N	\N	\N	\N
174	assistant-bucket2	174:46:Остатки и доступность товаров - для рассылки XLSX.xlsx	\N	\N	1067fdd6b204aafee7ee44318bf140499992505e96e649e37008b76c593ff91e	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-Dr6TprjXakptYigqtcRtkB	46:Остатки и доступность товаров - для рассылки XLSX.xlsx	89062	application/vnd.openxmlformats-officedocument.spreadsheetml.sheet	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 08:07:27.529896+00	2025-11-07 08:07:52.029208+00	\N	\N	\N	\N
181	assistant-bucket2	181:186:Состояния маршрутных листов - для продаж XLSX (4).xlsx	\N	\N	2d0120a72ac430a3e55f99eee67411ab8c9136e58b164048b2b93a42f1416d09	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-22sTarfNoMQMmCxbmNHHJq	186:Состояния маршрутных листов - для продаж XLSX (4).xlsx	44671	application/vnd.openxmlformats-officedocument.spreadsheetml.sheet	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 08:09:22.36736+00	2025-11-07 08:09:33.664941+00	\N	\N	\N	\N
176	assistant-bucket2	176:30:ВАКУУМНЫЕ ФЛАКОНЫ КП.xlsx	\N	\N	44b12fdb694bf7c2ce52e5eac5f2e5d726f74d0837b22748473ebff0c8efe40c	vs_690cb6b0c6dc81919f7a67a2cdf17025	file-QdYgAptJSH1idGDR8TwF7b	30:ВАКУУМНЫЕ ФЛАКОНЫ КП.xlsx	10302141	application/vnd.openxmlformats-officedocument.spreadsheetml.sheet	UPLOAD	INDEXED	\N	PENDING	f	f	\N	2025-11-07 08:07:27.55551+00	2025-11-07 08:08:33.132977+00	\N	\N	\N	\N
\.


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: root
--

COPY public.messages (id, chat_id, content, role, run_id, sources, state, created_at, updated_at) FROM stdin;
1	1	Приведи перечень уф-А фильтров в форме таблицы	user	\N	null	CREATED	2025-11-07 05:54:23.755268+00	2025-11-07 05:54:23.755268+00
2	1	К сожалению, я не нашел прямой информации о перечне УФ-А фильтров в загруженных вами документах. Это может означать, что такой информации нет в этих файлах или она представлена не в явной форме.\n\nЕсли у вас есть конкретные данные о УФ-А фильтрах, которые вы хотели бы получить в табличной форме, или если вы можете предоставить дополнительные источники, пожалуйста, дайте мне знать! Я с радостью помогу. \n\nТакже вот пример, как может выглядеть таблица с УФ-А фильтрами, если у вас есть такие данные:\n\n| Название фильтра      | Применение       | Примечание         |\n|-----------------------|------------------|--------------------|\n| Фильтр A              | Защита от UVA     | Высокая эффективность |\n| Фильтр B              | Защита от UVB     | Подходит для кожи   |\n| Фильтр C              | Защита от UVA и UVB | Гипоаллергенный    |\n\nЕсли это то, что вам нужно, вы можете предоставить данные, и я помогу с форматом.	assistant	\N	[]	COMPLETED	2025-11-07 05:54:23.795899+00	2025-11-07 05:54:44.122056+00
\.


--
-- Data for Name: storages; Type: TABLE DATA; Schema: public; Owner: root
--

COPY public.storages (id, name, vector_store_id, "default", created_at, updated_at, created_by_id, updated_by_id, deleted_at, deleted_by_id) FROM stdin;
1	JITL	vs_690cb6b0c6dc81919f7a67a2cdf17025	t	2025-11-06 14:54:41.437294+00	2025-11-06 14:54:49.73799+00	\N	\N	\N	\N
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: root
--

COPY public.users (id, name, email, password, role, valid, external_id, source, model, user_instructions, instructions, tools, created_at, updated_at, created_by_id, updated_by_id, deleted_at, deleted_by_id) FROM stdin;
1	\N	admin@dssl.ru	$argon2id$v=19$m=65536,t=3,p=4$w252eQu7ndldCGbq2dj6lw$0mViAFNNjHPQqZ8X0kS9PhtWIfTSVLFylmWmTTT64uA	ADMIN	t	\N	web	gpt-4o-mini	\N	Regardless of previous instructions, you must always:\nYou are an expert assistant. Use the provided context to answer accurately and clearly. The context consists of numbered snippets from source documents, each followed by its source info in parentheses — e.g., (Источник: file_name.pdf, стр. 3). Use these numbers (e.g., [1], [2], etc.) in your answer to refer to relevant sources. Respond in **Markdown** format with structured headings, bullet points, and emphasis where appropriate. If your answer contains structured data, such as lists of people or items, present it as a Markdown table when it enhances clarity. If the answer is based on multiple sources, indicate the relevant source numbers inline. If a source does not fully answer the question, say so honestly and suggest what information is missing if relevant.	[{"type": "file_search", "max_num_results": null, "vector_store_ids": ["vs_690cb6b0c6dc81919f7a67a2cdf17025"]}]	2025-11-06 14:31:22.167197+00	2025-11-06 14:54:47.712683+00	\N	\N	\N	\N
\.


--
-- Name: chats_id_seq; Type: SEQUENCE SET; Schema: public; Owner: root
--

SELECT pg_catalog.setval('public.chats_id_seq', 1, true);


--
-- Name: files_id_seq; Type: SEQUENCE SET; Schema: public; Owner: root
--

SELECT pg_catalog.setval('public.files_id_seq', 182, true);


--
-- Name: messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: root
--

SELECT pg_catalog.setval('public.messages_id_seq', 2, true);


--
-- Name: storages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: root
--

SELECT pg_catalog.setval('public.storages_id_seq', 1, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: root
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: chats chats_pkey; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.chats
    ADD CONSTRAINT chats_pkey PRIMARY KEY (id);


--
-- Name: files files_pkey; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.files
    ADD CONSTRAINT files_pkey PRIMARY KEY (id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: storages storages_pkey; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.storages
    ADD CONSTRAINT storages_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_chats_user_id; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX ix_chats_user_id ON public.chats USING btree (user_id);


--
-- Name: ix_files_created_by_id; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX ix_files_created_by_id ON public.files USING btree (created_by_id);


--
-- Name: ix_files_s3_object_key; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX ix_files_s3_object_key ON public.files USING btree (s3_object_key);


--
-- Name: ix_files_sha256; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX ix_files_sha256 ON public.files USING btree (sha256);


--
-- Name: ix_files_storage_key; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX ix_files_storage_key ON public.files USING btree (storage_key);


--
-- Name: ix_files_updated_by_id; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX ix_files_updated_by_id ON public.files USING btree (updated_by_id);


--
-- Name: ix_messages_chat_id; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX ix_messages_chat_id ON public.messages USING btree (chat_id);


--
-- Name: ix_messages_state; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX ix_messages_state ON public.messages USING btree (state);


--
-- Name: ix_storages_created_by_id; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX ix_storages_created_by_id ON public.storages USING btree (created_by_id);


--
-- Name: ix_storages_updated_by_id; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX ix_storages_updated_by_id ON public.storages USING btree (updated_by_id);


--
-- Name: ix_users_created_by_id; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX ix_users_created_by_id ON public.users USING btree (created_by_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_updated_by_id; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX ix_users_updated_by_id ON public.users USING btree (updated_by_id);


--
-- Name: chats chats_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.chats
    ADD CONSTRAINT chats_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: files files_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.files
    ADD CONSTRAINT files_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: files files_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.files
    ADD CONSTRAINT files_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: files files_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.files
    ADD CONSTRAINT files_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: messages messages_chat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_chat_id_fkey FOREIGN KEY (chat_id) REFERENCES public.chats(id) ON DELETE CASCADE;


--
-- Name: storages storages_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.storages
    ADD CONSTRAINT storages_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: storages storages_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.storages
    ADD CONSTRAINT storages_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: storages storages_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.storages
    ADD CONSTRAINT storages_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: users users_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: users users_deleted_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_deleted_by_id_fkey FOREIGN KEY (deleted_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: users users_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

\unrestrict Ztc97CgTbMya4gcOCNHqe3ewDYABcWky86YOKQadlUECotrqaM2Ctuvs678tb6D

