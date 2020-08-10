--TODO: UPDATE TO USE GOOD DATABASE CONVENTIONS. SEE https://stackoverflow.com/questions/7662/database-table-and-column-naming-conventions
drop table if exists _Users;
drop table if exists _Sessions;
drop table if exists _Views;

create table _Users(
    _user_id integer primary key autoincrement,
    _ip_address text not null,
    _location text,
    unique(_ip_address)
);

--TODO: ADD _IS_COMPLETE (BOOL) ATTRIBUTE
--TODO: CLASSIFICATION ENUM (BOT, ME, OTHER)
--TODO: DEFAULT VALUES
create table _Sessions(
    _session_id integer primary key autoincrement,
    _user_id integer not null,
    _first_request_time date not null,
    _last_request_time date,
    _num_requests integer
    -- _is_bot boolean,
    -- _is_me boolean
);

create table _Views(
    _view_id integer primary key autoincrement,
    _session_id integer not null,
    _url text not null,
    _user_agent text not null
);