drop schema if exists logs cascade;
create schema logs;

drop table if exists logs.users_sessions;
create table logs.users_sessions (
    user_id                 integer                 null,
    user_login              text                    not null,
    user_admin_allow        boolean                 null,
    user_regions            text[] null,
    user_roles_esia         text[] null,
    session_ip              inet                    not null,
    session_login_time      timestamp(0) without time zone not null,
    session_logout_time     timestamp(0) without time zone null,
    session_id              text,
    constraint logs_users_sessions_pkey primary key (user_id, session_login_time),
    constraint logs_users_sessions_admin_users_fkey foreign key (user_id)
        references admin.users (user_id) on delete set null on update cascade -- храним сессии даже после того, как удалили юзера
) partition by range (session_login_time);

CREATE TABLE logs.users_sessions_2024_01 PARTITION OF logs.users_sessions FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE INDEX ON logs.users_sessions_2024_01(user_login, session_login_time);
CREATE INDEX ON logs.users_sessions_2024_01(user_login);
CREATE TABLE logs.users_sessions_2024_02 PARTITION OF logs.users_sessions FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
CREATE INDEX ON logs.users_sessions_2024_02(user_login, session_login_time);
CREATE INDEX ON logs.users_sessions_2024_02(user_login);
CREATE TABLE logs.users_sessions_2024_03 PARTITION OF logs.users_sessions FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');
CREATE INDEX ON logs.users_sessions_2024_03(user_login, session_login_time);
CREATE INDEX ON logs.users_sessions_2024_03(user_login);
CREATE TABLE logs.users_sessions_2024_04 PARTITION OF logs.users_sessions FOR VALUES FROM ('2024-04-01') TO ('2024-05-01');
CREATE INDEX ON logs.users_sessions_2024_04(user_login, session_login_time);
CREATE INDEX ON logs.users_sessions_2024_04(user_login);
CREATE TABLE logs.users_sessions_2024_05 PARTITION OF logs.users_sessions FOR VALUES FROM ('2024-05-01') TO ('2024-06-01');
CREATE INDEX ON logs.users_sessions_2024_05(user_login, session_login_time);
CREATE INDEX ON logs.users_sessions_2024_05(user_login);
CREATE TABLE logs.users_sessions_2024_06 PARTITION OF logs.users_sessions FOR VALUES FROM ('2024-06-01') TO ('2024-07-01');
CREATE INDEX ON logs.users_sessions_2024_06(user_login, session_login_time);
CREATE INDEX ON logs.users_sessions_2024_06(user_login);
CREATE TABLE logs.users_sessions_2024_07 PARTITION OF logs.users_sessions FOR VALUES FROM ('2024-07-01') TO ('2024-08-01');
CREATE INDEX ON logs.users_sessions_2024_07(user_login, session_login_time);
CREATE INDEX ON logs.users_sessions_2024_07(user_login);
CREATE TABLE logs.users_sessions_2024_08 PARTITION OF logs.users_sessions FOR VALUES FROM ('2024-08-01') TO ('2024-09-01');
CREATE INDEX ON logs.users_sessions_2024_08(user_login, session_login_time);
CREATE INDEX ON logs.users_sessions_2024_08(user_login);
CREATE TABLE logs.users_sessions_2024_09 PARTITION OF logs.users_sessions FOR VALUES FROM ('2024-09-01') TO ('2024-10-01');
CREATE INDEX ON logs.users_sessions_2024_09(user_login, session_login_time);
CREATE INDEX ON logs.users_sessions_2024_09(user_login);
CREATE TABLE logs.users_sessions_2024_10 PARTITION OF logs.users_sessions FOR VALUES FROM ('2024-10-01') TO ('2024-11-01');
CREATE INDEX ON logs.users_sessions_2024_10(user_login, session_login_time);
CREATE INDEX ON logs.users_sessions_2024_10(user_login);
CREATE TABLE logs.users_sessions_2024_11 PARTITION OF logs.users_sessions FOR VALUES FROM ('2024-11-01') TO ('2024-12-01');
CREATE INDEX ON logs.users_sessions_2024_11(user_login, session_login_time);
CREATE INDEX ON logs.users_sessions_2024_11(user_login);
CREATE TABLE logs.users_sessions_2024_12 PARTITION OF logs.users_sessions FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');
CREATE INDEX ON logs.users_sessions_2024_12(user_login, session_login_time);
CREATE INDEX ON logs.users_sessions_2024_12(user_login);


create table logs.hits (
    hit_timestamp               timestamp without time zone not null,
    user_id                     integer                 null,
    user_login                  text                    null,
    user_ip                     inet                    null,
    user_admin_allow            boolean                 null,
    user_regions                text[] null,
    user_roles_esia             text[] null,
    request_method              varchar(16)             not null,
    request_path                text                    not null,
    response_status_code        int                     not null,
    response_content_type       text                    null
--     Для хитов не создаем внешние ключи, чтобы не создавать лишнюю нагрузку на базу при перестройке
--     constraint logs_users_sessions_admin_users_fkey foreign key (user_id)
--         references admin.users (user_id) on delete set null on update cascade
) partition by range (hit_timestamp);

CREATE TABLE logs.hits_2024_01 PARTITION OF logs.hits FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE INDEX ON logs.hits_2024_01(hit_timestamp);
CREATE INDEX ON logs.hits_2024_01(user_login);
CREATE TABLE logs.hits_2024_02 PARTITION OF logs.hits FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
CREATE INDEX ON logs.hits_2024_02(hit_timestamp);
CREATE INDEX ON logs.hits_2024_02(user_login);
CREATE TABLE logs.hits_2024_03 PARTITION OF logs.hits FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');
CREATE INDEX ON logs.hits_2024_03(hit_timestamp);
CREATE INDEX ON logs.hits_2024_03(user_login);
CREATE TABLE logs.hits_2024_04 PARTITION OF logs.hits FOR VALUES FROM ('2024-04-01') TO ('2024-05-01');
CREATE INDEX ON logs.hits_2024_04(hit_timestamp);
CREATE INDEX ON logs.hits_2024_04(user_login);
CREATE TABLE logs.hits_2024_05 PARTITION OF logs.hits FOR VALUES FROM ('2024-05-01') TO ('2024-06-01');
CREATE INDEX ON logs.hits_2024_05(hit_timestamp);
CREATE INDEX ON logs.hits_2024_05(user_login);
CREATE TABLE logs.hits_2024_06 PARTITION OF logs.hits FOR VALUES FROM ('2024-06-01') TO ('2024-07-01');
CREATE INDEX ON logs.hits_2024_06(hit_timestamp);
CREATE INDEX ON logs.hits_2024_06(user_login);
CREATE TABLE logs.hits_2024_07 PARTITION OF logs.hits FOR VALUES FROM ('2024-07-01') TO ('2024-08-01');
CREATE INDEX ON logs.hits_2024_07(hit_timestamp);
CREATE INDEX ON logs.hits_2024_07(user_login);
CREATE TABLE logs.hits_2024_08 PARTITION OF logs.hits FOR VALUES FROM ('2024-08-01') TO ('2024-09-01');
CREATE INDEX ON logs.hits_2024_08(hit_timestamp);
CREATE INDEX ON logs.hits_2024_08(user_login);
CREATE TABLE logs.hits_2024_09 PARTITION OF logs.hits FOR VALUES FROM ('2024-09-01') TO ('2024-10-01');
CREATE INDEX ON logs.hits_2024_09(hit_timestamp);
CREATE INDEX ON logs.hits_2024_09(user_login);
CREATE TABLE logs.hits_2024_10 PARTITION OF logs.hits FOR VALUES FROM ('2024-10-01') TO ('2024-11-01');
CREATE INDEX ON logs.hits_2024_10(hit_timestamp);
CREATE INDEX ON logs.hits_2024_10(user_login);
CREATE TABLE logs.hits_2024_11 PARTITION OF logs.hits FOR VALUES FROM ('2024-11-01') TO ('2024-12-01');
CREATE INDEX ON logs.hits_2024_11(hit_timestamp);
CREATE INDEX ON logs.hits_2024_11(user_login);
CREATE TABLE logs.hits_2024_12 PARTITION OF logs.hits FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');
CREATE INDEX ON logs.hits_2024_12(hit_timestamp);
CREATE INDEX ON logs.hits_2024_12(user_login);