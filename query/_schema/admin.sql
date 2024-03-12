drop schema if exists admin;
create schema admin;

create sequence admin.users_seq;
create table admin.users (
    user_id                 integer              not null default nextval('admin.users_seq'),
    user_login              varchar(128)         not null,
    user_password_hash      varchar(34)          null,
    user_outer              boolean              not null default false, -- «внешний» пользователь, из ЕСИА.
    user_registered         timestamp(0) without time zone not null default now(),
    user_comment            text                 null,
    user_admin_allow        boolean              not null default false,
    user_last_login_time    timestamp(0) without time zone not null default now(),
    user_regions            text[] null,
    user_roles_esia         text[] null,
    constraint admin_users_pkey primary key (user_id),
    constraint admin_users_login_uniq unique (user_login)
);

create table admin.modules (
    mod_id               varchar(64)          not null,
    mod_name             text                 not null,
    mod_description      text                 null,
    constraint admin_modules_pkey primary key (mod_id)
);

create table admin.module_modifiers (
    mod_id               varchar(64)          not null,
    mmod_id              varchar(64)          not null,
    mmod_name            text                 null,
    constraint admin_module_modifiers_pkey primary key (mmod_id, mod_id),
    constraint admin_module_modifiers_fkey foreign key (mod_id)
       references admin.modules (mod_id) on delete cascade on update cascade
);

create table admin.module_actions (
    mod_id               varchar(64)          not null,
    mact_id              varchar(64)          not null,
    mact_name            text                 not null,
    constraint admin_module_actions_pkey primary key (mod_id, mact_id),
    constraint admin_module_actions_fkey foreign key (mod_id)
       references admin.modules (mod_id) on delete cascade on update cascade
);

create sequence admin.roles_seq;
create table admin.roles (
    role_id              integer              not null default nextval('admin.roles_seq'),
    role_name            text                 not null,
    role_description     text                 null,
    constraint admin_roles_pkey primary key (role_id),
    constraint admin_roles_name_uniq unique (role_name)
);

create table admin.users_roles (
    user_id              integer              not null,
    role_id              integer              not null,
    ur_start             date                 null,
    ur_finish            date                 null,
    constraint admin_users_roles_pkey primary key (user_id, role_id),
    constraint admin_roles_admin_users_fkey foreign key (user_id)
        references admin.users (user_id) on delete cascade on update cascade,
    constraint admin_users_admin_roles_fkey foreign key (role_id)
       references admin.roles (role_id) on delete cascade on update cascade
);

create sequence admin.permissions_seq;
create table admin.permissions (
    perm_id              integer              not null default nextval('admin.permissions_seq'),
    mod_id               varchar(64)          not null,
    mmod_id              varchar(64)          not null,
    mact_id              varchar(64)          not null,
    perm_name            text                 not null,
    constraint admin_permissions_pkey primary key (perm_id),
    constraint admin_permissions_admin_actions_fkey foreign key (mod_id, mact_id)
       references admin.module_actions (mod_id, mact_id) on delete cascade on update cascade,
    constraint admin_permissions_admin_modifiers_fkey foreign key (mod_id, mmod_id)
       references admin.module_modifiers (mod_id, mmod_id) on delete cascade on update cascade
);

create index permissions_module_idx on admin.permissions (mod_id);
create index permissions_modifier_idx on admin.permissions (mmod_id);


create table admin.roles_permissions (
    role_id              integer              not null,
    perm_id              integer              not null,
    roleperm_allow       boolean              not null default true,
    constraint admin_roles_permissions_pkey primary key (role_id, perm_id),
    constraint admin_permissions_admin_roles_fkey foreign key (role_id)
       references admin.roles (role_id) on delete cascade on update cascade,
    constraint admin_roles_permissions_admin_permissions_fkey foreign key (perm_id)
       references admin.permissions (perm_id) on delete cascade on update cascade
);

create index roles_permissions_perm_idx on admin.roles_permissions (perm_id);

--
-- таблица для аккаунтинга
--
create table admin.accounting (
    object_type          varchar(20)          not null,
    object_id            integer              not null,
    object_owner         integer              null,
    acct_action          enum_tg_op           not null,
    acct_stamp           timestamp(0) with time zone not null default now(),
    acct_editor          integer              null,
    acct_ip              inet                 null,
    object_title         text                 not null
);

create index admin_accounting_objects_idx on admin.accounting (object_id, acct_stamp);
create index admin_accounting_deleted_idx on admin.accounting (object_type, acct_stamp) where acct_action = 'DELETE';