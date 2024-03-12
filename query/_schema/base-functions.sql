--
-- Функции для работы с базовыми таблицами
--


--
-- обновление версий и времени изменения объектов
--

create or replace function objects_version()
returns trigger
as $_$
begin
    new.obj_version  := old.obj_version + 1;
    new.obj_added    := old.obj_added;
    new.obj_modified := current_timestamp;
    return new;
end;
$_$ language 'plpgsql' volatile called on null input security definer;

create trigger objects_version
before update on objects for each row
execute procedure objects_version();

--
-- получение идентификатора тега (ключевого слова)
--

create or replace function get_tag_id(in_text text)
returns integer
as $_$
declare
    tag record;
begin
    loop
        select tag_id into tag from tags where tag_text = in_text;

        if found then
            return tag.tag_id;
        else
            begin
                insert into tags (tag_text) values (in_text);
                return currval('tags_seq');
            exception when unique_violation then
                -- тег вставили в параллельной транзакции, на следующей
                -- итерации цикла его достанем
            end;
        end if;
    end loop;
end;
$_$ language 'plpgsql' volatile strict security definer;


--
-- Обновление прав доступа при добавлении нового "статуса"
--

create or replace function on_state_change()
returns trigger
as $_$
declare
begin
    if TG_OP = 'DELETE' then
        -- из остальных таблиц удалится за счёт внешних ключей
        delete from admin.module_modifiers where mod_id != 'rubric' and mmod_id = cast(OLD.state_id as varchar(32));
    elsif TG_OP = 'UPDATE' then
        -- никаких действий если название не меняется!
        if OLD.state_name <> NEW.state_name then
            update admin.module_modifiers set mmod_name = 'Со статусом "' || NEW.state_name || '"'
            where mod_id != 'rubric' and mmod_id = cast(NEW.state_id AS varchar(32));

            update admin.permissions
            set perm_name = admin.module_actions.mact_name || ' "' || NEW.state_name || '"'
            from admin.module_actions
            where admin.permissions.mod_id = admin.module_actions.mod_id and
                  admin.permissions.mact_id = admin.module_actions.mact_id and
                  admin.permissions.mmod_id = cast(NEW.state_id AS varchar(32)) and
                  admin.permissions.mod_id != 'rubric';
        end if;
    elsif TG_OP = 'INSERT' then
        insert into admin.module_modifiers (mod_id, mmod_id, mmod_name)
        select mod_id, cast(NEW.state_id AS varchar(32)), 'Со статусом "' || NEW.state_name || '"'
        from admin.module_actions
        where mact_id = 'state';

        insert into admin.permissions (mod_id, mact_id, mmod_id, perm_name)
        select ma.mod_id, ma.mact_id, cast(NEW.state_id AS varchar(32)),
               ma.mact_name || ' "' || NEW.state_name || '"'
        from admin.module_actions ma
        where mact_id in ('state', 'edit-state', 'delete-state') and
              mod_id in (
                  select mod_id
                  from admin.module_actions ma2
                  where ma2.mact_id = 'state'
              );
    end if;

    return null;
end;
$_$ language 'plpgsql' volatile called on null input security definer;

create trigger state_permissions
after insert or update or delete on object_states for each row
execute procedure on_state_change();


-- current_setting() вываливает ошибку, если значение не было определено.
-- а нам надо бы получать какое-то значение по умолчанию, причём по
-- возможности не ляпая его в postgresql.conf
create or replace function current_setting_with_default(setting_name text, default_value text)
returns text
as $_$
begin
    return current_setting(setting_name);
exception
    when syntax_error_or_access_rule_violation then
        perform set_config(setting_name, default_value, false);
        return default_value;
end;
$_$ language 'plpgsql' volatile called on null input security definer;



create or replace function objects_dml()
returns trigger
as
$body$
declare
    target    text := TG_ARGV[0];
    prefix    text := TG_ARGV[1];
    pkey      text := prefix || '_id';
    acct_type text := TG_ARGV[2];
    title     text := 'coalesce(($1).'
                      || array_to_string(
                            regexp_split_to_array(TG_ARGV[3], e'\\s*,\\s*'),
                            $$, '') || ' ' || coalesce(($1).$$
                      )
                      || $$, '')$$;

    -- теоретически это можно получать из метаданных, но зачем?
    objects_cols text[] := array['user_id', 'state_id', 'obj_added', 'obj_modified', 'obj_version', 'obj_comment'];

    obj_query    text;
    target_query text;
    acct_query   text;

    same_pkey    boolean;
    field        text;
    obj_field    text;

    obj_fields text[]    := array[]::text[];
    obj_values text[]    := array[]::text[];
    target_fields text[] := array[]::text[];
    target_values text[] := array[]::text[];
begin
    if TG_OP = 'DELETE' then
        execute $$delete from objects where obj_id = ($1).$$ || pkey using old;

    elsif TG_OP = 'INSERT' or TG_OP = 'UPDATE' then
        if TG_OP = 'UPDATE' then
            execute 'select ($1).' || pkey || ' = ($2).' || pkey into same_pkey using old, new;
            if not same_pkey then
                raise exception 'Changing primary key is disallowed for objects-based views';
            end if;
        end if;

        for field in select * from json_object_keys(row_to_json(new)) loop
            if field != pkey then
                obj_field := regexp_replace(field, '^' || prefix, 'obj');
                if obj_field = any(objects_cols) then
                    if TG_OP = 'UPDATE' then
                        obj_fields := array_append(obj_fields, obj_field || ' = ($1).' || field);
                    else
                        obj_fields := array_append(obj_fields, obj_field);
                        obj_values := array_append(obj_values, '($1).' || field);
                    end if;

                else
                    if TG_OP = 'UPDATE' then
                        target_fields := array_append(target_fields, field || ' = ($1).' || field);
                    else
                        target_fields := array_append(target_fields, field);
                        target_values := array_append(target_values, '($1).' || field);
                    end if;
                end if;
            end if;
        end loop;

        if TG_OP = 'UPDATE' then
            obj_query    := 'update objects set ' || array_to_string(obj_fields, ', ')
                            || ' where obj_id = ($1).' || pkey;
            target_query := 'update ' || target || ' set ' || array_to_string(target_fields, ', ')
                            || ' where obj_id = ($1).' || pkey;

        else
            obj_query   := 'insert into objects (obj_id, '
                            || array_to_string(obj_fields, ', ')
                            || ') values (($1).' || pkey || ', '
                            || array_to_string(obj_values, ', ')
                            || ')';

            target_query := 'insert into ' || target || ' (obj_id, '
                            || array_to_string(target_fields, ', ')
                            || ') values (($1).' || pkey || ', '
                            || array_to_string(target_values, ', ')
                            || ')';
        end if;

        execute obj_query using new;
        execute target_query using new;

    else
        raise exception 'Wut?';
    end if;

    acct_query := $$
    insert into admin.accounting
        (object_type, object_id, object_owner, acct_action, acct_editor, acct_ip, object_title)
    values
        ($2, ($1).$$ || pkey || $$, ($1).user_id, $3::enum_tg_op,
         nullif(current_setting_with_default('web.user_id', ''), '')::integer,
         nullif(current_setting_with_default('web.session_ip', ''), '')::inet,
 $$
        || title || ')';

    if TG_OP = 'DELETE' then
        execute acct_query using old, acct_type, TG_OP;
        return old;
    else
        execute acct_query using new, acct_type, TG_OP;
        return new;
    end if;
end;
$body$
language plpgsql
security definer
set search_path = pg_catalog, public;


comment on function objects_dml() is $$
Делает представления, связанные с objects, изменяемыми

В вызове CREATE TRIGGER для представления передаются следующие параметры:
 0: имя второй таблицы, на которой основано представление (например 'articles_data')
 1: префикс для полей в таблице (например 'article')
 2: тип контента для вставки в таблицу accounting (например опять 'article')
 3: поле, используемое как название записи в accounting (например 'article_title');
    если название надо сгенерировать по нескольким полям, то они передаются одной строкой
    через запятую, например 'employee_surname, employee_name'

Все параметры обязательные.
$$;
