drop schema if exists datamarts cascade;
create schema datamarts;

create table datamarts.items_data (
    obj_id                  integer                 not null,
    item_signature          text                    not null default 'common', -- сигнатура витрины, позволяющая ориентировать роли
    item_title              text                    not null,
    item_description        text                    null,
    item_tables_cnt         int                     null,
    item_link_pg_admin      text                    null,
    item_link_saud          text                    null,
    constraint datamarts_items_data_pkey primary key (obj_id),
    constraint datamarts_items_data_objects_fkey foreign key (obj_id)
       references objects (obj_id) on delete cascade on update cascade
);

create or replace view datamarts.items as
select
    objects.obj_id as item_id,
    objects.user_id,
    objects.state_id,
    objects.obj_added as item_added,
    objects.obj_modified as item_modified,
    objects.obj_version as item_version,
    objects.obj_comment as item_comment,

    items_data.item_signature,
    items_data.item_title,
    items_data.item_description,
    items_data.item_tables_cnt,
    items_data.item_link_pg_admin,
    items_data.item_link_saud
from objects
join datamarts.items_data on (items_data.obj_id = objects.obj_id);


alter view datamarts.items alter column item_id set default nextval('objects_seq');
alter view datamarts.items alter column user_id set default nullif(current_setting_with_default('web.user_id', ''), '')::integer;
alter view datamarts.items alter column item_added set default now();
alter view datamarts.items alter column item_modified set default now();
alter view datamarts.items alter column item_version set default 1;


create trigger items_dml_trigger
    instead of insert or update or delete on datamarts.items
    for each row execute procedure objects_dml('datamarts.items_data', 'item', 'item', 'item_title');