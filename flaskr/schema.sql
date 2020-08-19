--TODO: UPDATE TO USE GOOD DATABASE CONVENTIONS. SEE https://stackoverflow.com/questions/7662/database-table-and-column-naming-conventions
drop table if exists _Users;
drop table if exists _Sessions;
drop table if exists _Views;
drop table if exists _CachedSessions;

--TODO: CLASSIFICATION ENUM (BOT, ME, OTHER)
create table _Users(
    _user_id integer primary key autoincrement,
    _ip_address text not null,
    _hostname text default "UNKOWN",
    _domain text default "UNKOWN",
    _city text default "UNKOWN",
    _region text default "UNKOWN",
    _country text default "UNKOWN",
    unique(_ip_address)
);

--TODO: ADD _IS_COMPLETE (BOOL) ATTRIBUTE
--TODO: DEFAULT VALUES
create table _Sessions(
    _session_id integer primary key autoincrement,
    _user_id integer not null,
    _first_request_time datetime not null,
    _last_request_time datetime,
    _num_requests integer default 0,
    -- _is_finished integer default 0,
    unique(_user_id, _first_request_time)
);

-- TODO: MOVE 'USER_AGENT' INTO THE SESSIONS TABLE? / MAKE IT PART OF WHAT DEFINES A NEW SESSION?
create table _Views(
    _view_id integer primary key autoincrement,
    _session_id integer not null,
    _timestamp datetime not null,
    _url text not null,
    _user_agent text not null
);

create table _CachedSessions(
    _session_id integer not null,
    _user_id integer not null,
    _certified_stale integer default 0,
    unique(_session_id, _user_id)
);