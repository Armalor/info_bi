drop schema if exists services cascade;
create schema services;

create type services.service_type as enum (
    'dashboard',
    'prototype' -- прототип, не отображается в списке, но к нему есть документы.
);

create table services.items_data (
    obj_id                  integer                 not null,
    item_type               services.service_type   not null default 'dashboard',
    item_signature          text                    not null default 'common', -- сигнатура сервиса (дашборда), позволяющая ориентировать роли
    item_title              text                    not null,
    item_description        text                    null,
    item_link               text                    null,
    constraint services_items_data_pkey primary key (obj_id),
    constraint services_items_data_objects_fkey foreign key (obj_id)
       references objects (obj_id) on delete cascade on update cascade
);

create or replace view services.items as
select
    objects.obj_id as item_id,
    objects.user_id,
    objects.state_id,
    objects.obj_added as item_added,
    objects.obj_modified as item_modified,
    objects.obj_version as item_version,
    objects.obj_comment as item_comment,
    items_data.item_type,
    items_data.item_signature,
    items_data.item_title,
    items_data.item_description,
    items_data.item_link
from objects
join services.items_data on (items_data.obj_id = objects.obj_id);


alter view services.items alter column item_id set default nextval('objects_seq');
alter view services.items alter column user_id set default nullif(current_setting_with_default('web.user_id', ''), '')::integer;
alter view services.items alter column item_added set default now();
alter view services.items alter column item_modified set default now();
alter view services.items alter column item_version set default 1;
alter view services.items alter column item_type set default 'dashboard';


create trigger items_dml_trigger
    instead of insert or update or delete on services.items
    for each row execute procedure objects_dml('services.items_data', 'item', 'item', 'item_title');