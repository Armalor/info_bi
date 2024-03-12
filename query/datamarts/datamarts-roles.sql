begin;

insert into admin.modules (mod_id, mod_name) values ('datamarts', 'Витрины данных');

insert into admin.module_actions (mod_id, mact_id, mact_name) values ('datamarts', 'view', 'Просматривать витрины данных');

insert into admin.module_modifiers (mod_id, mmod_id, mmod_name) values ('datamarts', 'all',   'Витрины данных с любой сигнатурой');
insert into admin.module_modifiers (mod_id, mmod_id, mmod_name) values ('datamarts', 'common',   'Витрины данных с общей сигнатурой: «common»');


insert into admin.permissions (mod_id, mact_id, mmod_id, perm_name) values ('datamarts', 'view', 'all',  'Просматривать витрины данных с любой сигнатурой');
insert into admin.permissions (mod_id, mact_id, mmod_id, perm_name) values ('datamarts', 'view', 'common',  'Просматривать витрины данных «common»');



insert into admin.roles (role_id, role_name, role_description) values (-11, 'Витрины данных: админ',  'Это роль администратора витрин данных: она дает возможность доступа к витринам с любой сигнатурой');
insert into admin.roles_permissions (role_id, perm_id)
    select -11, perm_id
    from admin.permissions where mod_id = 'datamarts' and mact_id in ('view') and mmod_id in ('all');


insert into admin.roles_permissions (role_id, perm_id)
    select 99, perm_id -- 99 это роль Admin
    from admin.permissions where mod_id = 'datamarts' and mact_id in ('view') and mmod_id in ('all');


insert into admin.roles (role_id, role_name, role_description) values (-12, 'Витрины данных: common',  'Эта роль дает возможность доступа к витринам «common»');
insert into admin.roles_permissions (role_id, perm_id)
    select -12, perm_id
    from admin.permissions where mod_id = 'datamarts' and mact_id in ('view') and mmod_id in ('common');

commit;