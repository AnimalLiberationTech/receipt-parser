--
-- PostgreSQL database dump
--
-- Dumped from database version 9.6.21
-- Dumped by pg_dump version 11.11 (Debian 11.11-0+deb10u1)

--
-- Name: moderator_task; Type: TABLE;
--
CREATE TABLE moderator_task (
    id integer NOT NULL,
    barcode text,
    task_type smallint NOT NULL,
    task_source_user_id uuid NOT NULL,
    text_from_user text,
    creation_time bigint NOT NULL,
    assignee uuid,
    assign_time bigint,
    resolution_time bigint,
    "osmId" text,
    rejected_assignees_list text,
    lang text,
    resolver uuid,
    resolver_action text,
    news_piece_id integer
);

--
-- Name: moderator_task_id_seq; Type: SEQUENCE;
--
CREATE SEQUENCE moderator_task_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: news_piece_product_at_shop; Type: TABLE;
--
CREATE TABLE news_piece_product_at_shop (
    id integer NOT NULL,
    news_piece_id integer NOT NULL,
    barcode text NOT NULL,
    shop_uid text NOT NULL
);

--
-- Name: news_piece_product_at_shop_id_seq; Type: SEQUENCE;
--
CREATE SEQUENCE news_piece_product_at_shop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: news_piece_table; Type: TABLE;
--
CREATE TABLE news_piece_table (
    id integer NOT NULL,
    lat double precision NOT NULL,
    lon double precision NOT NULL,
    creator_user_id uuid NOT NULL,
    creation_time bigint NOT NULL,
    type smallint NOT NULL,
    deleted boolean DEFAULT false NOT NULL
);

--
-- Name: news_piece_table_id_seq; Type: SEQUENCE;
--
CREATE SEQUENCE news_piece_table_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: product; Type: TABLE;
--
CREATE TABLE product (
    id integer NOT NULL,
    barcode text NOT NULL,
    vegan_status smallint,
    vegan_status_source smallint,
    creator_user_id uuid,
    moderator_vegan_choice_reason smallint,
    moderator_vegan_sources_text text,
    moderator_vegan_choice_reasons text
);

--
-- Name: product_at_shop; Type: TABLE;
--
CREATE TABLE product_at_shop (
    id integer NOT NULL,
    product_id integer NOT NULL,
    shop_id integer NOT NULL,
    creation_time bigint NOT NULL,
    creator_user_id uuid,
    source smallint DEFAULT 1 NOT NULL
);

--
-- Name: product_at_shop_id_seq; Type: SEQUENCE;
--
CREATE SEQUENCE product_at_shop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: product_change; Type: TABLE;
--
CREATE TABLE product_change (
    id integer NOT NULL,
    barcode text NOT NULL,
    editor_id uuid NOT NULL,
    old_product_json text NOT NULL,
    new_product_json text NOT NULL,
    "time" bigint NOT NULL
);

--
-- Name: product_change_id_seq; Type: SEQUENCE;
--
CREATE SEQUENCE product_change_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: product_id_seq; Type: SEQUENCE;
--
CREATE SEQUENCE product_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: product_like_table; Type: TABLE;
--
CREATE TABLE product_like_table (
    id integer NOT NULL,
    user_id uuid NOT NULL,
    barcode text NOT NULL,
    "time" bigint NOT NULL
);

--
-- Name: product_like_table_id_seq; Type: SEQUENCE;
--
CREATE SEQUENCE product_like_table_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: product_presence_vote; Type: TABLE;
--
CREATE TABLE product_presence_vote (
    id integer NOT NULL,
    product_id integer NOT NULL,
    shop_id integer NOT NULL,
    voted_user_id uuid NOT NULL,
    vote_time bigint NOT NULL,
    vote_val smallint NOT NULL
);

--
-- Name: product_presence_vote_id_seq; Type: SEQUENCE;
--
CREATE SEQUENCE product_presence_vote_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
--
-- Name: product_scan; Type: TABLE;
--
CREATE TABLE product_scan (
    id integer NOT NULL,
    barcode text NOT NULL,
    user_id uuid NOT NULL,
    "time" bigint NOT NULL
);

--
-- Name: product_scan_id_seq; Type: SEQUENCE;
--
CREATE SEQUENCE product_scan_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
--
-- Name: shop; Type: TABLE;
--
CREATE TABLE shop (
    id integer NOT NULL,
    osm_id text NOT NULL,
    creation_time bigint NOT NULL,
    created_new_osm_node boolean DEFAULT false NOT NULL,
    creator_user_id uuid NOT NULL,
    products_count integer DEFAULT 0 NOT NULL,
    lat double precision,
    lon double precision,
    last_auto_validation_time bigint,
    deleted boolean DEFAULT false NOT NULL
);

--
-- Name: shop_id_seq; Type: SEQUENCE;
--
CREATE SEQUENCE shop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
--
-- Name: shops_validation_queue; Type: TABLE;
--
CREATE TABLE shops_validation_queue (
    id integer NOT NULL,
    shop_id integer NOT NULL,
    enqueuing_time bigint NOT NULL,
    source_user_id uuid NOT NULL,
    reason smallint NOT NULL
);

--
-- Name: shops_validation_queue_id_seq; Type: SEQUENCE;
--
CREATE SEQUENCE shops_validation_queue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: user; Type: TABLE;
--
CREATE TABLE "user" (
    id uuid NOT NULL,
    banned boolean DEFAULT false NOT NULL,
    google_id text,
    login_generation integer NOT NULL,
    creation_time bigint NOT NULL,
    name text NOT NULL,
    gender smallint,
    birthday text,
    eats_milk boolean,
    eats_eggs boolean,
    eats_honey boolean,
    user_rights_group smallint DEFAULT 1 NOT NULL,
    apple_id text,
    langs_prioritized text,
    self_description text,
    has_avatar boolean DEFAULT false NOT NULL,
    avatar_id uuid
);

--
-- Name: user_contribution; Type: TABLE;
--
CREATE TABLE user_contribution (
    id integer NOT NULL,
    user_id uuid NOT NULL,
    barcode text,
    shop_uid text,
    "time" bigint NOT NULL,
    type smallint NOT NULL
);

--
-- Name: user_contribution_id_seq; Type: SEQUENCE;
--
CREATE SEQUENCE user_contribution_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: user_quiz; Type: TABLE;
--
CREATE TABLE user_quiz (
    id integer NOT NULL,
    question text NOT NULL,
    answer text NOT NULL,
    user_id uuid NOT NULL,
    "time" bigint NOT NULL
);

--
-- Name: user_quiz_id_seq; Type: SEQUENCE;
--
CREATE SEQUENCE user_quiz_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: moderator_task id; Type: DEFAULT;
--
ALTER TABLE ONLY moderator_task ALTER COLUMN id SET DEFAULT nextval('moderator_task_id_seq'::regclass);

--
-- Name: news_piece_product_at_shop id; Type: DEFAULT;
--
ALTER TABLE ONLY news_piece_product_at_shop ALTER COLUMN id SET DEFAULT nextval('news_piece_product_at_shop_id_seq'::regclass);

--
-- Name: news_piece_table id; Type: DEFAULT;
--
ALTER TABLE ONLY news_piece_table ALTER COLUMN id SET DEFAULT nextval('news_piece_table_id_seq'::regclass);

--
-- Name: product id; Type: DEFAULT;
--
ALTER TABLE ONLY product ALTER COLUMN id SET DEFAULT nextval('product_id_seq'::regclass);
--
-- Name: product_at_shop id; Type: DEFAULT;
--
ALTER TABLE ONLY product_at_shop ALTER COLUMN id SET DEFAULT nextval('product_at_shop_id_seq'::regclass);
--
-- Name: product_change id; Type: DEFAULT;
--
ALTER TABLE ONLY product_change ALTER COLUMN id SET DEFAULT nextval('product_change_id_seq'::regclass);
--
-- Name: product_like_table id; Type: DEFAULT;
--
ALTER TABLE ONLY product_like_table ALTER COLUMN id SET DEFAULT nextval('product_like_table_id_seq'::regclass);
--
-- Name: product_presence_vote id; Type: DEFAULT;
--
ALTER TABLE ONLY product_presence_vote ALTER COLUMN id SET DEFAULT nextval('product_presence_vote_id_seq'::regclass);
--
-- Name: product_scan id; Type: DEFAULT;
--
ALTER TABLE ONLY product_scan ALTER COLUMN id SET DEFAULT nextval('product_scan_id_seq'::regclass);
--
-- Name: shop id; Type: DEFAULT;
--
ALTER TABLE ONLY shop ALTER COLUMN id SET DEFAULT nextval('shop_id_seq'::regclass);
--
-- Name: shops_validation_queue id; Type: DEFAULT;
--
ALTER TABLE ONLY shops_validation_queue ALTER COLUMN id SET DEFAULT nextval('shops_validation_queue_id_seq'::regclass);
--
-- Name: user_contribution id; Type: DEFAULT;
--
ALTER TABLE ONLY user_contribution ALTER COLUMN id SET DEFAULT nextval('user_contribution_id_seq'::regclass);
--
-- Name: user_quiz id; Type: DEFAULT;
--
ALTER TABLE ONLY user_quiz ALTER COLUMN id SET DEFAULT nextval('user_quiz_id_seq'::regclass);
--
-- Name: moderator_task_id_seq; Type: SEQUENCE SET;
--
SELECT pg_catalog.setval('moderator_task_id_seq', 3576, true);
--
-- Name: news_piece_product_at_shop_id_seq; Type: SEQUENCE SET;
--
SELECT pg_catalog.setval('news_piece_product_at_shop_id_seq', 732, true);
--
-- Name: news_piece_table_id_seq; Type: SEQUENCE SET;
--
SELECT pg_catalog.setval('news_piece_table_id_seq', 732, true);
--
-- Name: product_at_shop_id_seq; Type: SEQUENCE SET;
--
SELECT pg_catalog.setval('product_at_shop_id_seq', 1961, true);
--
-- Name: product_change_id_seq; Type: SEQUENCE SET;
--
SELECT pg_catalog.setval('product_change_id_seq', 2618, true);
--
-- Name: product_id_seq; Type: SEQUENCE SET;
--
SELECT pg_catalog.setval('product_id_seq', 1517, true);
--
-- Name: product_like_table_id_seq; Type: SEQUENCE SET;
--
SELECT pg_catalog.setval('product_like_table_id_seq', 53, true);
--
-- Name: product_presence_vote_id_seq; Type: SEQUENCE SET;
--
SELECT pg_catalog.setval('product_presence_vote_id_seq', 2914, true);
--
-- Name: product_scan_id_seq; Type: SEQUENCE SET;
--
SELECT pg_catalog.setval('product_scan_id_seq', 7908, true);
--
-- Name: shop_id_seq; Type: SEQUENCE SET;
--
SELECT pg_catalog.setval('shop_id_seq', 409, true);
--
-- Name: shops_validation_queue_id_seq; Type: SEQUENCE SET;
--
SELECT pg_catalog.setval('shops_validation_queue_id_seq', 37164, true);
--
-- Name: user_contribution_id_seq; Type: SEQUENCE SET;
--
SELECT pg_catalog.setval('user_contribution_id_seq', 4193, true);
--
-- Name: user_quiz_id_seq; Type: SEQUENCE SET;
--
SELECT pg_catalog.setval('user_quiz_id_seq', 1, false);
--
-- Name: moderator_task moderator_task_pkey; Type: CONSTRAINT;
--
ALTER TABLE ONLY moderator_task
    ADD CONSTRAINT moderator_task_pkey PRIMARY KEY (id);
--
-- Name: news_piece_product_at_shop news_piece_product_at_shop_pkey; Type: CONSTRAINT;
--
ALTER TABLE ONLY news_piece_product_at_shop
    ADD CONSTRAINT news_piece_product_at_shop_pkey PRIMARY KEY (id);
--
-- Name: news_piece_table news_piece_table_pkey; Type: CONSTRAINT;
--
ALTER TABLE ONLY news_piece_table
    ADD CONSTRAINT news_piece_table_pkey PRIMARY KEY (id);
--
-- Name: product_at_shop product_at_shop_pkey; Type: CONSTRAINT;
--
ALTER TABLE ONLY product_at_shop
    ADD CONSTRAINT product_at_shop_pkey PRIMARY KEY (id);
--
-- Name: product_at_shop product_at_shop_product_id_shop_id_unique; Type: CONSTRAINT;
--
ALTER TABLE ONLY product_at_shop
    ADD CONSTRAINT product_at_shop_product_id_shop_id_unique UNIQUE (product_id, shop_id);
--
-- Name: product product_barcode_unique; Type: CONSTRAINT;
--
ALTER TABLE ONLY product
    ADD CONSTRAINT product_barcode_unique UNIQUE (barcode);
--
-- Name: product_change product_change_pkey; Type: CONSTRAINT;
--
ALTER TABLE ONLY product_change
    ADD CONSTRAINT product_change_pkey PRIMARY KEY (id);
--
-- Name: product_like_table product_like_table_pkey; Type: CONSTRAINT;
--
ALTER TABLE ONLY product_like_table
    ADD CONSTRAINT product_like_table_pkey PRIMARY KEY (id);
--
-- Name: product_like_table product_like_table_user_id_barcode_unique; Type: CONSTRAINT;
--
ALTER TABLE ONLY product_like_table
    ADD CONSTRAINT product_like_table_user_id_barcode_unique UNIQUE (user_id, barcode);
--
-- Name: product product_pkey; Type: CONSTRAINT;
--
ALTER TABLE ONLY product
    ADD CONSTRAINT product_pkey PRIMARY KEY (id);
--
-- Name: product_presence_vote product_presence_vote_pkey; Type: CONSTRAINT;
--
ALTER TABLE ONLY product_presence_vote
    ADD CONSTRAINT product_presence_vote_pkey PRIMARY KEY (id);
--
-- Name: product_scan product_scan_pkey; Type: CONSTRAINT;
--
ALTER TABLE ONLY product_scan
    ADD CONSTRAINT product_scan_pkey PRIMARY KEY (id);
--
-- Name: shop shop_osm_id_unique; Type: CONSTRAINT;
--
ALTER TABLE ONLY shop
    ADD CONSTRAINT shop_osm_id_unique UNIQUE (osm_id);
--
-- Name: shop shop_pkey; Type: CONSTRAINT;
--
ALTER TABLE ONLY shop
    ADD CONSTRAINT shop_pkey PRIMARY KEY (id);
--
-- Name: shops_validation_queue shops_validation_queue_pkey; Type: CONSTRAINT;
--
ALTER TABLE ONLY shops_validation_queue
    ADD CONSTRAINT shops_validation_queue_pkey PRIMARY KEY (id);
--
-- Name: user user_pkey; Type: CONSTRAINT;
--
ALTER TABLE ONLY "user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);
--
-- Name: user_quiz user_quiz_pkey; Type: CONSTRAINT;
--
ALTER TABLE ONLY user_quiz
    ADD CONSTRAINT user_quiz_pkey PRIMARY KEY (id);
--
-- Name: moderator_task_assign_time; Type: INDEX;
--
CREATE INDEX moderator_task_assign_time ON moderator_task USING btree (assign_time);
--
-- Name: moderator_task_assignee; Type: INDEX;
--
CREATE INDEX moderator_task_assignee ON moderator_task USING btree (assignee);
--
-- Name: moderator_task_barcode; Type: INDEX;
--
CREATE INDEX moderator_task_barcode ON moderator_task USING btree (barcode);
--
-- Name: moderator_task_lang; Type: INDEX;
--
CREATE INDEX moderator_task_lang ON moderator_task USING btree (lang);
--
-- Name: moderator_task_news_piece_id; Type: INDEX;
--
CREATE INDEX moderator_task_news_piece_id ON moderator_task USING btree (news_piece_id);
--
-- Name: moderator_task_osmid; Type: INDEX;
--
CREATE INDEX moderator_task_osmid ON moderator_task USING btree ("osmId");
--
-- Name: moderator_task_resolution_time; Type: INDEX;
--
CREATE INDEX moderator_task_resolution_time ON moderator_task USING btree (resolution_time);
--
-- Name: moderator_task_resolver; Type: INDEX;
--
CREATE INDEX moderator_task_resolver ON moderator_task USING btree (resolver);
--
-- Name: moderator_task_task_source_user_id; Type: INDEX;
--
CREATE INDEX moderator_task_task_source_user_id ON moderator_task USING btree (task_source_user_id);
--
-- Name: moderator_task_task_type; Type: INDEX;
--
CREATE INDEX moderator_task_task_type ON moderator_task USING btree (task_type);
--
-- Name: news_piece_product_at_shop_barcode; Type: INDEX;
--
CREATE INDEX news_piece_product_at_shop_barcode ON news_piece_product_at_shop USING btree (barcode);
--
-- Name: news_piece_product_at_shop_news_piece_id; Type: INDEX;
--
CREATE INDEX news_piece_product_at_shop_news_piece_id ON news_piece_product_at_shop USING btree (news_piece_id);
--
-- Name: news_piece_product_at_shop_shop_uid; Type: INDEX;
--
CREATE INDEX news_piece_product_at_shop_shop_uid ON news_piece_product_at_shop USING btree (shop_uid);
--
-- Name: news_piece_table_creation_time; Type: INDEX;
--
CREATE INDEX news_piece_table_creation_time ON news_piece_table USING btree (creation_time);
--
-- Name: news_piece_table_creator_user_id; Type: INDEX;
--
CREATE INDEX news_piece_table_creator_user_id ON news_piece_table USING btree (creator_user_id);
--
-- Name: news_piece_table_lat; Type: INDEX;
--
CREATE INDEX news_piece_table_lat ON news_piece_table USING btree (lat);
--
-- Name: news_piece_table_lon; Type: INDEX;
--
CREATE INDEX news_piece_table_lon ON news_piece_table USING btree (lon);
--
-- Name: news_piece_table_type; Type: INDEX;
--
CREATE INDEX news_piece_table_type ON news_piece_table USING btree (type);
--
-- Name: product_at_shop_creation_time; Type: INDEX;
--
CREATE INDEX product_at_shop_creation_time ON product_at_shop USING btree (creation_time);
--
-- Name: product_at_shop_creator_user_id; Type: INDEX;
--
CREATE INDEX product_at_shop_creator_user_id ON product_at_shop USING btree (creator_user_id);
--
-- Name: product_at_shop_product_id; Type: INDEX;
--
CREATE INDEX product_at_shop_product_id ON product_at_shop USING btree (product_id);
--
-- Name: product_at_shop_shop_id; Type: INDEX;
--
CREATE INDEX product_at_shop_shop_id ON product_at_shop USING btree (shop_id);
--
-- Name: product_change_barcode; Type: INDEX;
--
CREATE INDEX product_change_barcode ON product_change USING btree (barcode);
--
-- Name: product_change_editor_id; Type: INDEX;
--
CREATE INDEX product_change_editor_id ON product_change USING btree (editor_id);
--
-- Name: product_creator_user_id; Type: INDEX;
--
CREATE INDEX product_creator_user_id ON product USING btree (creator_user_id);
--
-- Name: product_like_table_barcode; Type: INDEX;
--
CREATE INDEX product_like_table_barcode ON product_like_table USING btree (barcode);
--
-- Name: product_like_table_time; Type: INDEX;
--
CREATE INDEX product_like_table_time ON product_like_table USING btree ("time");
--
-- Name: product_like_table_user_id; Type: INDEX;
--
CREATE INDEX product_like_table_user_id ON product_like_table USING btree (user_id);
--
-- Name: product_presence_vote_product_id; Type: INDEX;
--
CREATE INDEX product_presence_vote_product_id ON product_presence_vote USING btree (product_id);
--
-- Name: product_presence_vote_shop_id; Type: INDEX;
--
CREATE INDEX product_presence_vote_shop_id ON product_presence_vote USING btree (shop_id);
--
-- Name: product_presence_vote_vote_time; Type: INDEX;
--
CREATE INDEX product_presence_vote_vote_time ON product_presence_vote USING btree (vote_time);
--
-- Name: product_presence_vote_voted_user_id; Type: INDEX;
--
CREATE INDEX product_presence_vote_voted_user_id ON product_presence_vote USING btree (voted_user_id);
--
-- Name: product_scan_barcode; Type: INDEX;
--
CREATE INDEX product_scan_barcode ON product_scan USING btree (barcode);
--
-- Name: product_scan_time; Type: INDEX;
--
CREATE INDEX product_scan_time ON product_scan USING btree ("time");
--
-- Name: product_scan_user_id; Type: INDEX;
--
CREATE INDEX product_scan_user_id ON product_scan USING btree (user_id);
--
-- Name: shop_creation_time; Type: INDEX;
--
CREATE INDEX shop_creation_time ON shop USING btree (creation_time);
--
-- Name: shop_creator_user_id; Type: INDEX;
--
CREATE INDEX shop_creator_user_id ON shop USING btree (creator_user_id);
--
-- Name: shop_last_auto_validation_time; Type: INDEX;
--
CREATE INDEX shop_last_auto_validation_time ON shop USING btree (last_auto_validation_time);
--
-- Name: shop_lat; Type: INDEX;
--
CREATE INDEX shop_lat ON shop USING btree (lat);
--
-- Name: shop_lon; Type: INDEX;
--
CREATE INDEX shop_lon ON shop USING btree (lon);
--
-- Name: shops_validation_queue_enqueuing_time; Type: INDEX;
--
CREATE INDEX shops_validation_queue_enqueuing_time ON shops_validation_queue USING btree (enqueuing_time);
--
-- Name: shops_validation_queue_reason; Type: INDEX;
--
CREATE INDEX shops_validation_queue_reason ON shops_validation_queue USING btree (reason);
--
-- Name: shops_validation_queue_shop_id; Type: INDEX;
--
CREATE INDEX shops_validation_queue_shop_id ON shops_validation_queue USING btree (shop_id);
--
-- Name: shops_validation_queue_source_user_id; Type: INDEX;
--
CREATE INDEX shops_validation_queue_source_user_id ON shops_validation_queue USING btree (source_user_id);
--
-- Name: user_contribution_barcode; Type: INDEX;
--
CREATE INDEX user_contribution_barcode ON user_contribution USING btree (barcode);
--
-- Name: user_contribution_shop_uid; Type: INDEX;
--
CREATE INDEX user_contribution_shop_uid ON user_contribution USING btree (shop_uid);
--
-- Name: user_contribution_time; Type: INDEX;
--
CREATE INDEX user_contribution_time ON user_contribution USING btree ("time");
--
-- Name: user_contribution_type; Type: INDEX;
--
CREATE INDEX user_contribution_type ON user_contribution USING btree (type);
--
-- Name: user_contribution_user_id; Type: INDEX;
--
CREATE INDEX user_contribution_user_id ON user_contribution USING btree (user_id);
--
-- Name: user_creation_time; Type: INDEX;
--
CREATE INDEX user_creation_time ON "user" USING btree (creation_time);
--
-- Name: user_quiz_question; Type: INDEX;
--
CREATE INDEX user_quiz_question ON user_quiz USING btree (question);
--
-- Name: user_quiz_user_id; Type: INDEX;
--
CREATE INDEX user_quiz_user_id ON user_quiz USING btree (user_id);
--
-- Name: user_user_rights_group; Type: INDEX;
--
CREATE INDEX user_user_rights_group ON "user" USING btree (user_rights_group);
--
-- Name: moderator_task fk_moderator_task_assignee_id; Type: FK CONSTRAINT;
--
ALTER TABLE ONLY moderator_task
    ADD CONSTRAINT fk_moderator_task_assignee_id FOREIGN KEY (assignee) REFERENCES "user"(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
--
-- Name: moderator_task fk_moderator_task_news_piece_id_id; Type: FK CONSTRAINT;
--
ALTER TABLE ONLY moderator_task
    ADD CONSTRAINT fk_moderator_task_news_piece_id_id FOREIGN KEY (news_piece_id) REFERENCES news_piece_table(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
--
-- Name: moderator_task fk_moderator_task_resolver_id; Type: FK CONSTRAINT;
--
ALTER TABLE ONLY moderator_task
    ADD CONSTRAINT fk_moderator_task_resolver_id FOREIGN KEY (resolver) REFERENCES "user"(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
--
-- Name: moderator_task fk_moderator_task_task_source_user_id_id; Type: FK CONSTRAINT;
--
ALTER TABLE ONLY moderator_task
    ADD CONSTRAINT fk_moderator_task_task_source_user_id_id FOREIGN KEY (task_source_user_id) REFERENCES "user"(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
--
-- Name: news_piece_product_at_shop fk_news_piece_product_at_shop_news_piece_id_id; Type: FK CONSTRAINT;
--
ALTER TABLE ONLY news_piece_product_at_shop
    ADD CONSTRAINT fk_news_piece_product_at_shop_news_piece_id_id FOREIGN KEY (news_piece_id) REFERENCES news_piece_table(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
--
-- Name: news_piece_table fk_news_piece_table_creator_user_id_id; Type: FK CONSTRAINT;
--
ALTER TABLE ONLY news_piece_table
    ADD CONSTRAINT fk_news_piece_table_creator_user_id_id FOREIGN KEY (creator_user_id) REFERENCES "user"(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
--
-- Name: product_at_shop fk_product_at_shop_creator_user_id_id; Type: FK CONSTRAINT;
--
ALTER TABLE ONLY product_at_shop
    ADD CONSTRAINT fk_product_at_shop_creator_user_id_id FOREIGN KEY (creator_user_id) REFERENCES "user"(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
--
-- Name: product_at_shop fk_product_at_shop_product_id_id; Type: FK CONSTRAINT;
--
ALTER TABLE ONLY product_at_shop
    ADD CONSTRAINT fk_product_at_shop_product_id_id FOREIGN KEY (product_id) REFERENCES product(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
--
-- Name: product_at_shop fk_product_at_shop_shop_id_id; Type: FK CONSTRAINT;
--
ALTER TABLE ONLY product_at_shop
    ADD CONSTRAINT fk_product_at_shop_shop_id_id FOREIGN KEY (shop_id) REFERENCES shop(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
--
-- Name: product_change fk_product_change_barcode_barcode; Type: FK CONSTRAINT;
--
ALTER TABLE ONLY product_change
    ADD CONSTRAINT fk_product_change_barcode_barcode FOREIGN KEY (barcode) REFERENCES product(barcode) ON UPDATE RESTRICT ON DELETE RESTRICT;
--
-- Name: product_change fk_product_change_editor_id_id; Type: FK CONSTRAINT;
--
ALTER TABLE ONLY product_change
    ADD CONSTRAINT fk_product_change_editor_id_id FOREIGN KEY (editor_id) REFERENCES "user"(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
--
-- Name: product fk_product_creator_user_id_id; Type: FK CONSTRAINT;
--
ALTER TABLE ONLY product
    ADD CONSTRAINT fk_product_creator_user_id_id FOREIGN KEY (creator_user_id) REFERENCES "user"(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
--
-- Name: product_like_table fk_product_like_table_user_id_id; Type: FK CONSTRAINT;
--
ALTER TABLE ONLY product_like_table
    ADD CONSTRAINT fk_product_like_table_user_id_id FOREIGN KEY (user_id) REFERENCES "user"(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
--
-- Name: product_presence_vote fk_product_presence_vote_product_id_id; Type: FK CONSTRAINT;
--
ALTER TABLE ONLY product_presence_vote
    ADD CONSTRAINT fk_product_presence_vote_product_id_id FOREIGN KEY (product_id) REFERENCES product(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
--
-- Name: product_presence_vote fk_product_presence_vote_shop_id_id; Type: FK CONSTRAINT;
--
ALTER TABLE ONLY product_presence_vote
    ADD CONSTRAINT fk_product_presence_vote_shop_id_id FOREIGN KEY (shop_id) REFERENCES shop(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
--
-- Name: product_presence_vote fk_product_presence_vote_voted_user_id_id; Type: FK CONSTRAINT;
--
ALTER TABLE ONLY product_presence_vote
    ADD CONSTRAINT fk_product_presence_vote_voted_user_id_id FOREIGN KEY (voted_user_id) REFERENCES "user"(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
--
-- Name: product_scan fk_product_scan_user_id_id; Type: FK CONSTRAINT;
--
ALTER TABLE ONLY product_scan
    ADD CONSTRAINT fk_product_scan_user_id_id FOREIGN KEY (user_id) REFERENCES "user"(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
--
-- Name: shop fk_shop_creator_user_id_id; Type: FK CONSTRAINT;
--
ALTER TABLE ONLY shop
    ADD CONSTRAINT fk_shop_creator_user_id_id FOREIGN KEY (creator_user_id) REFERENCES "user"(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
--
-- Name: shops_validation_queue fk_shops_validation_queue_shop_id_id; Type: FK CONSTRAINT;
--
ALTER TABLE ONLY shops_validation_queue
    ADD CONSTRAINT fk_shops_validation_queue_shop_id_id FOREIGN KEY (shop_id) REFERENCES shop(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
--
-- Name: shops_validation_queue fk_shops_validation_queue_source_user_id_id; Type: FK CONSTRAINT;
--
ALTER TABLE ONLY shops_validation_queue
    ADD CONSTRAINT fk_shops_validation_queue_source_user_id_id FOREIGN KEY (source_user_id) REFERENCES "user"(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
--
-- Name: user_contribution fk_user_contribution_user_id_id; Type: FK CONSTRAINT;
--
ALTER TABLE ONLY user_contribution
    ADD CONSTRAINT fk_user_contribution_user_id_id FOREIGN KEY (user_id) REFERENCES "user"(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
--
-- Name: user_quiz fk_user_quiz_user_id_id; Type: FK CONSTRAINT;
--
ALTER TABLE ONLY user_quiz
    ADD CONSTRAINT fk_user_quiz_user_id_id FOREIGN KEY (user_id) REFERENCES "user"(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
--
-- PostgreSQL database dump complete
--
