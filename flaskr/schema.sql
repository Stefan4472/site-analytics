--TODO: UPDATE TO USE GOOD DATABASE CONVENTIONS. SEE https://stackoverflow.com/questions/7662/database-table-and-column-naming-conventions
drop table if exists Views;

create table Views (
    view_id integer primary key autoincrement,
    viewed_url text not null,
    ip_address text not null,
    user_agent text not null
);