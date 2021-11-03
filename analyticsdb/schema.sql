drop table if exists _Users;
drop table if exists _Views;
drop table if exists _CachedSessions;

create table _Users(
    _user_id integer primary key autoincrement,
    _ip_address text not null,
    _hostname text,
    _domain text,
    _city text,
    _region text,
    _country text,
    _is_bot integer,
    _was_processed integer default 0,
    unique(_ip_address)
);
create index _UsersIndex on _Users(_ip_address);

-- TODO: MOVE 'USER_AGENT' INTO THE SESSIONS TABLE? / MAKE IT PART OF WHAT DEFINES A NEW SESSION?
-- TODO: DETERMINE OPERATING SYSTEM, WEB BROWSER, VERSION
create table _Views(
    _view_id integer primary key autoincrement,
    _user_id integer not null,
    _timestamp datetime not null,
    _url text not null,
    _user_agent text not null,
    _operating_system text,
    _browser text
);
create index _ViewsUserIndex on _View(_user_id);