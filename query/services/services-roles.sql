begin;

insert into admin.modules (mod_id, mod_name) values ('services', 'Сервисы');

insert into admin.module_actions (mod_id, mact_id, mact_name) values ('services', 'view', 'Просматривать сервисы');

insert into admin.module_modifiers (mod_id, mmod_id, mmod_name) values ('services', 'all',   'Сервисы с любой сигнатурой');
insert into admin.module_modifiers (mod_id, mmod_id, mmod_name) values ('services', 'smart_planning',   'Сервис «Умное территориальное планирование»');
insert into admin.module_modifiers (mod_id, mmod_id, mmod_name) values ('services', 'forecasting_for_drugs', 'Сервис «Прогнозирование потребности в лекарственных препаратах»');
insert into admin.module_modifiers (mod_id, mmod_id, mmod_name) values ('services', 'prevent_defects', 'Сервис «Поддержка принятия решений по предотвращению возникновения дефектуры»');
insert into admin.module_modifiers (mod_id, mmod_id, mmod_name) values ('services', 'forecasting_capacity_utilization', 'Сервис «Прогнозирование загрузки мощностей»');
insert into admin.module_modifiers (mod_id, mmod_id, mmod_name) values ('services', 'monitoring_of_property', 'Сервис «Мониторинг имущества и основных средств»');
insert into admin.module_modifiers (mod_id, mmod_id, mmod_name) values ('services', 'drug_supply_planning', 'Сервис «Планирование лекарственного обеспечения»');
insert into admin.module_modifiers (mod_id, mmod_id, mmod_name) values ('services', 'monitoring_of_financial_activities', 'Сервис «Мониторинг финансово-хозяйственной деятельности»');
insert into admin.module_modifiers (mod_id, mmod_id, mmod_name) values ('services', 'availability_of_medical_care', 'Сервис «Фактическая доступность медицинской помощи»');
insert into admin.module_modifiers (mod_id, mmod_id, mmod_name) values ('services', 'staffing_management', 'Сервис «Управление кадровой обеспеченностью»');

insert into admin.permissions (mod_id, mact_id, mmod_id, perm_name) values ('services', 'view', 'all',  'Просматривать сервисы с любой сигнатурой');
insert into admin.permissions (mod_id, mact_id, mmod_id, perm_name) values ('services', 'view', 'smart_planning',  'Просматривать сервис «Умное территориальное планирование»');
insert into admin.permissions (mod_id, mact_id, mmod_id, perm_name) values ('services', 'view', 'forecasting_for_drugs',  'Просматривать сервис «Прогнозирование потребности в лекарственных препаратах»');
insert into admin.permissions (mod_id, mact_id, mmod_id, perm_name) values ('services', 'view', 'prevent_defects',  'Просматривать сервис «Поддержка принятия решений по предотвращению возникновения дефектуры»');
insert into admin.permissions (mod_id, mact_id, mmod_id, perm_name) values ('services', 'view', 'forecasting_capacity_utilization',  'Просматривать сервис «Прогнозирование загрузки мощностей»');
insert into admin.permissions (mod_id, mact_id, mmod_id, perm_name) values ('services', 'view', 'monitoring_of_property',  'Просматривать сервис «Мониторинг имущества и основных средств»');
insert into admin.permissions (mod_id, mact_id, mmod_id, perm_name) values ('services', 'view', 'drug_supply_planning',  'Просматривать сервис «Планирование лекарственного обеспечения»');
insert into admin.permissions (mod_id, mact_id, mmod_id, perm_name) values ('services', 'view', 'monitoring_of_financial_activities',  'Просматривать сервис «Мониторинг финансово-хозяйственной деятельности»');
insert into admin.permissions (mod_id, mact_id, mmod_id, perm_name) values ('services', 'view', 'availability_of_medical_care',  'Просматривать сервис «Фактическая доступность медицинской помощи»');
insert into admin.permissions (mod_id, mact_id, mmod_id, perm_name) values ('services', 'view', 'staffing_management',  'Просматривать сервис «Управление кадровой обеспеченностью»');


insert into admin.roles (role_id, role_name, role_description) values (-1, 'Сервисы: админ',  'Это роль администратора сервисов: она дает возможность доступа к сервисам с любой сигнатурой');
insert into admin.roles_permissions (role_id, perm_id)
    select -1, perm_id
    from admin.permissions where mod_id = 'services' and mact_id in ('view') and mmod_id in ('all');


-- insert into admin.roles_permissions (role_id, perm_id)
--     select 99, perm_id -- 99 это роль Admin
--     from admin.permissions where mod_id = 'services' and mact_id in ('view') and mmod_id in ('all');


insert into admin.roles (role_id, role_name, role_description) values (-2, 'Сервисы: common',  'Эта роль дает возможность доступа к сервисам «Умное территориальное планирование» и «Прогнозирование потребности в лекарственных препаратах»');
insert into admin.roles_permissions (role_id, perm_id)
    select -2, perm_id
    from admin.permissions where mod_id = 'services' and mact_id in ('view') and mmod_id in ('smart_planning', 'forecasting_for_drugs');

insert into admin.roles (role_id, role_name, role_description) values (-3, 'Сервисы: special',  'Эта роль дает возможность доступа к сервисам «Поддержка принятия решений по предотвращению возникновения дефектуры» и «Прогнозирование загрузки мощностей»');
insert into admin.roles_permissions (role_id, perm_id)
    select -3, perm_id
    from admin.permissions where mod_id = 'services' and mact_id in ('view') and mmod_id in ('prevent_defects', 'forecasting_capacity_utilization');


commit;