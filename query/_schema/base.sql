drop schema if exists public cascade;
create sequence objects_seq;

create type enum_tg_op as enum (
    'INSERT',
    'UPDATE',
    'DELETE'
);




create table object_states (
    state_id             smallint             not null,
    state_name           text                 not null,
    state_icon           text                 null,
    constraint object_states_pkey primary key (state_id)
);


create table objects (
    obj_id               integer              not null default nextval('objects_seq'),
    user_id              integer              null,
    state_id             smallint             not null,
    obj_added            timestamp(0) with time zone not null default now(),
    obj_modified         timestamp(0) with time zone not null default now(),
    obj_version          smallint             not null default 1,
    obj_comment          text                 null,
    constraint objects_pkey primary key (obj_id),
    constraint objects_users_fkey foreign key (user_id)
       references admin.users (user_id) on delete set null on update cascade,
    constraint objects_states_fkey foreign key (state_id)
       references object_states (state_id) on delete restrict on update cascade
);

create index objects_owner_idx on objects (user_id) where user_id is not null;


create sequence tags_seq;
create table tags (
   tag_id               integer              not null default nextval('tags_seq'),
   tag_text             text                 not null,
   constraint tags_pkey primary key (tag_id),
   constraint tags_text_unique unique (tag_text)
);

create table objects_tags (
   obj_id               integer              not null,
   tag_id               integer              not null,
   constraint objects_tags_pkey primary key (obj_id, tag_id),
   constraint objects_tags_fkey foreign key (tag_id)
      references tags (tag_id) on delete cascade on update cascade,
   constraint tags_objects_fkey foreign key (obj_id)
      references objects (obj_id) on delete cascade on update cascade
);

create index objects_tags_tag_idx on objects_tags (tag_id);
