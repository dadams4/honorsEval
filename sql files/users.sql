

drop table if exists users;
create table users (

    username text,
    password text,
    firstname text,
    lastname text,
    primary key(username)

);

insert into users values ('dadams@umw.edu', crypt('password', gen_salt('bf')), 'Daniel','Adams');
insert into users values ('jhurnyak@umw.edu', crypt('password2', gen_salt('bf')), 'Adam','Hurnyak');
insert into users values ('adyke@mail.umw.edu', crypt('password1', gen_salt('bf')), 'Aaron', 'Dyke');
insert into users values ('awoodruf@umw.edu', crypt('drowssap', gen_salt('bf')), 'Andrew', 'Woodruff');
