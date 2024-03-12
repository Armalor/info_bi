-- статусы для контента
begin work;

insert into object_states (state_id, state_name, state_icon) values (1,   'Черновик',                    null);
insert into object_states (state_id, state_name, state_icon) values (2,   'Требует доработки',           null);
insert into object_states (state_id, state_name, state_icon) values (10,  'Ожидает проверки редактором', null);
insert into object_states (state_id, state_name, state_icon) values (100, 'Опубликовано',                null);

commit work;