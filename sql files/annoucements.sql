drop table if exists announcements;

create table announcements (
    date date,
    time time,
    title text,
    message text
    
);

grant all on announcements to manager;

insert into announcements (date, time, title, message) values (now(), current_timestamp, 'This is a test annoucement!', 'This is the test text!');
insert into announcements (date, time, title, message) values (now(), current_timestamp, 'announcements are cool', 'ikr');
insert into announcements (date, time, title, message) values (now(), current_timestamp, 'message 3', 'tres');
insert into announcements (date, time, title,  message) values (now(), current_timestamp, 'message 4', 'quatro');
insert into announcements (date, time, title, message) values (now(), current_timestamp, 'message 5', 'cinco');
insert into announcements (date, time, title, message) values (now(), current_timestamp, 'message 6', 'seis');
insert into announcements (date, time, title, message) values (now(), current_timestamp, 'message 7', 'siete');