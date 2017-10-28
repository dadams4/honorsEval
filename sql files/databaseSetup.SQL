
drop table if exists checklist;

create table checklist (
    LastName text,
    FirstName text,
    ID text,
    email text,
    Admitted text,
    duPontCode text,
    Status text,
    Term text,
    CoCur1 text,
    Date1 text,
    FSEMHN text,
    FSEMDate text,
    HNcourse1 text,
    HN1Date text,
    HNcourse2 text,
    HN2Date text,
    HNcourse3 text,
    HN3Date text,
    HNcourse4 text,
    HN4Date text,
    HNcourse5 text,
    HN5Date text,
    ResearchCourse text,
    ResearchDate text,
    CapstoneCourse text,
    CapstoneDate text,
    HONR201 text,
    HONR201Date text,
    Leadership text,
    mentoring text,
    HONRPortfolio4 text,
    HONRPortfolio1 text,
    HONRPortfolio2 text,
    HONRPortfolio3 text,
    ExitInterview text
);

grant all on checklist to manager;

insert into checklist values ( 