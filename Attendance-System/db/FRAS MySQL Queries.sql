/*-------------------- CREATE TABLES----------------*/
create table users(
	id int(11) not null auto_increment,
    first_name text,
    last_name text,
    email text,
    pass text,
    user_role text,
    created_at timestamp default current_timestamp,
    updated_at timestamp default current_timestamp on update current_timestamp,
    primary key (id)
);

create table courses(
	id int(11) not null auto_increment,
    user_id int(11),
    title_id text,
    title text,
    units int(11),
    start_dt datetime,
    end_dt datetime,
    created_at timestamp default current_timestamp,
    updated_at timestamp default current_timestamp on update current_timestamp,
    primary key (id),
    foreign key (user_id) references users(id)
);

create table students(
	id int(11) not null auto_increment,
    first_name text,
    last_name text,
    email text,
    created_at timestamp default current_timestamp,
    updated_at timestamp default current_timestamp on update current_timestamp,
    primary key (id)
);

create table course_dt_time(
	id int(11) not null auto_increment,
	course_id int(11) not null unique,
    days text,
    start_time text,
    end_time text,
    created_at timestamp default current_timestamp,
    foreign key (course_id) references courses(id),
	primary key (id)
);

create table attendants(
	id int(11) not null auto_increment,
    student_id int(11), 
    course_id int(11),
    student_status text default "absent",
    lec_date datetime,
    foreign key (student_id) references students(id),
    foreign key (course_id) references courses(id),
	primary key (id)
);

create table attendees(
	id int(11) not null auto_increment,
    student_id int(11), 
    course_id int(11),
    image text,
    created_at timestamp default current_timestamp,
    updated_at timestamp default current_timestamp on update current_timestamp,
    foreign key (student_id) references students(id),
    foreign key (course_id) references courses(id),
    primary key (id)
);


/*-------------------- Populate Data----------------*/
insert ignore into students (first_name, last_name, email) values ('Anderson', 'Cushe', 'acushe0@army.mil');
insert ignore into students (first_name, last_name, email) values ('Blair', 'Tynewell', 'btynewell1@myspace.com');
insert ignore into students (first_name, last_name, email) values ('Jehu', 'Paddy', 'jpaddy2@go.com');
insert ignore into students (first_name, last_name, email) values ('Goldi', 'Beeden', 'gbeeden3@berkeley.edu');
insert ignore into students (first_name, last_name, email) values ('Jerome', 'Colleford', 'jcolleford4@ocn.ne.jp');
insert ignore into students (first_name, last_name, email) values ('Thedrick', 'Airlie', 'tairlie5@etsy.com');
insert ignore into students (first_name, last_name, email) values ('Ebonee', 'Robroe', 'erobroe6@buzzfeed.com');
insert ignore into students (first_name, last_name, email) values ('Tamra', 'Harpur', 'tharpur7@wunderground.com');
insert ignore into students (first_name, last_name, email) values ('Darci', 'Kimpton', 'dkimpton8@ehow.com');
insert ignore into students (first_name, last_name, email) values ('Merry', 'Mattschas', 'mmattschas9@timesonline.co.uk');
insert ignore into students (first_name, last_name, email) values ('Jennica', 'Alexandrou', 'jalexandroua@nih.gov');
insert ignore into students (first_name, last_name, email) values ('Edyth', 'Semon', 'esemonb@webeden.co.uk');
insert ignore into students (first_name, last_name, email) values ('Roddy', 'Suckling', 'rsucklingc@is.gd');
insert ignore into students (first_name, last_name, email) values ('Inglis', 'Joddens', 'ijoddensd@qq.com');
insert ignore into students (first_name, last_name, email) values ('Daron', 'De la Harpe', 'ddelaharpee@pcworld.com');
insert ignore into students (first_name, last_name, email) values ('Randell', 'Columbell', 'rcolumbellf@techcrunch.com');
insert ignore into students (first_name, last_name, email) values ('Ania', 'Iacopetti', 'aiacopettig@eventbrite.com');
insert ignore into students (first_name, last_name, email) values ('Alanna', 'Stango', 'astangoh@sina.com.cn');
insert ignore into students (first_name, last_name, email) values ('Luce', 'Maddox', 'lmaddoxi@ovh.net');
insert ignore into students (first_name, last_name, email) values ('Benedicta', 'Lawranson', 'blawransonj@domainmarket.com');
insert ignore into students (first_name, last_name, email) values ('Rickey', 'Clements', 'rclementsk@goo.gl');
insert ignore into students (first_name, last_name, email) values ('Donall', 'Rean', 'dreanl@addtoany.com');
insert ignore into students (first_name, last_name, email) values ('Quintus', 'Thickens', 'qthickensm@aol.com');
insert ignore into students (first_name, last_name, email) values ('Dominik', 'De la Feld', 'ddelafeldn@eepurl.com');
insert ignore into students (first_name, last_name, email) values ('Rudiger', 'Weathers', 'rweatherso@bigcartel.com');
insert ignore into students (first_name, last_name, email) values ('Waverly', 'Bohike', 'wbohikep@sakura.ne.jp');
insert ignore into students (first_name, last_name, email) values ('Obidiah', 'Stearns', 'ostearnsq@wired.com');
insert ignore into students (first_name, last_name, email) values ('Mickie', 'Samuel', 'msamuelr@yahoo.com');
insert ignore into students (first_name, last_name, email) values ('Bethanne', 'Lathey', 'blatheys@livejournal.com');
insert ignore into students (first_name, last_name, email) values ('Abba', 'Chooter', 'achootert@ox.ac.uk');
insert ignore into students (first_name, last_name, email) values ('Lorilee', 'Crookshanks', 'lcrookshanksu@mail.ru');
insert ignore into students (first_name, last_name, email) values ('Talyah', 'Sneden', 'tsnedenv@trellian.com');
insert ignore into students (first_name, last_name, email) values ('Standford', 'Klimp', 'sklimpw@usda.gov');
insert ignore into students (first_name, last_name, email) values ('Feodora', 'Braben', 'fbrabenx@mysql.com');
insert ignore into students (first_name, last_name, email) values ('Arni', 'Lugton', 'alugtony@miitbeian.gov.cn');
insert ignore into students (first_name, last_name, email) values ('Webb', 'McCaughren', 'wmccaughrenz@ibm.com');
insert ignore into students (first_name, last_name, email) values ('Paula', 'Howell', 'phowell10@blogger.com');
insert ignore into students (first_name, last_name, email) values ('Karlee', 'Wellsman', 'kwellsman11@google.com.hk');
insert ignore into students (first_name, last_name, email) values ('Tammi', 'Vasyunin', 'tvasyunin12@cloudflare.com');
insert ignore into students (first_name, last_name, email) values ('Menard', 'Arlott', 'marlott13@yolasite.com');
insert ignore into students (first_name, last_name, email) values ('Newton', 'Gynne', 'ngynne14@youtube.com');
insert ignore into students (first_name, last_name, email) values ('Katheryn', 'Camings', 'kcamings15@dell.com');
insert ignore into students (first_name, last_name, email) values ('Melessa', 'Cheake', 'mcheake16@cdbaby.com');
insert ignore into students (first_name, last_name, email) values ('Jackie', 'Beddon', 'jbeddon17@liveinternet.ru');
insert ignore into students (first_name, last_name, email) values ('Gradey', 'Coare', 'gcoare18@gnu.org');
insert ignore into students (first_name, last_name, email) values ('Thoma', 'Hartopp', 'thartopp19@sbwire.com');
insert ignore into students (first_name, last_name, email) values ('Teri', 'Tothacot', 'ttothacot1a@printfriendly.com');
insert ignore into students (first_name, last_name, email) values ('Hadleigh', 'Zuann', 'hzuann1b@blogs.com');
insert ignore into students (first_name, last_name, email) values ('Bunny', 'Isakowicz', 'bisakowicz1c@histats.com');
insert ignore into students (first_name, last_name, email) values ('Shannon', 'Grix', 'sgrix1d@whitehouse.gov');
insert ignore into students (first_name, last_name, email) values ('Brew', 'Landeaux', 'blandeaux1e@tinypic.com');
insert ignore into students (first_name, last_name, email) values ('Delano', 'Sambell', 'dsambell1f@nationalgeographic.com');
insert ignore into students (first_name, last_name, email) values ('Mommy', 'Scandrett', 'mscandrett1g@unesco.org');
insert ignore into students (first_name, last_name, email) values ('Jen', 'Sawers', 'jsawers1h@ow.ly');
insert ignore into students (first_name, last_name, email) values ('Louisa', 'Aitken', 'laitken1i@amazon.de');
insert ignore into students (first_name, last_name, email) values ('Giraud', 'Ramlot', 'gramlot1j@about.me');
insert ignore into students (first_name, last_name, email) values ('Beatrix', 'Brabham', 'bbrabham1k@bluehost.com');
insert ignore into students (first_name, last_name, email) values ('Bryn', 'Arnaudon', 'barnaudon1l@flavors.me');
insert ignore into students (first_name, last_name, email) values ('Ryan', 'Weighell', 'rweighell1m@imdb.com');
insert ignore into students (first_name, last_name, email) values ('Janella', 'Houldey', 'jhouldey1n@addtoany.com');
insert ignore into students (first_name, last_name, email) values ('Town', 'Frosch', 'tfrosch1o@google.es');
insert ignore into students (first_name, last_name, email) values ('Lind', 'Broadley', 'lbroadley1p@multiply.com');
insert ignore into students (first_name, last_name, email) values ('Cash', 'Dash', 'cdash1q@aol.com');
insert ignore into students (first_name, last_name, email) values ('Joannes', 'Tollfree', 'jtollfree1r@ask.com');
insert ignore into students (first_name, last_name, email) values ('Brynn', 'Sarsfield', 'bsarsfield1s@exblog.jp');
insert ignore into students (first_name, last_name, email) values ('Clark', 'Finlry', 'cfinlry1t@netlog.com');
insert ignore into students (first_name, last_name, email) values ('Brucie', 'Iannuzzelli', 'biannuzzelli1u@webeden.co.uk');
insert ignore into students (first_name, last_name, email) values ('Malachi', 'Slite', 'mslite1v@clickbank.net');
insert ignore into students (first_name, last_name, email) values ('Rhonda', 'Thaine', 'rthaine1w@51.la');
insert ignore into students (first_name, last_name, email) values ('Puff', 'Burdikin', 'pburdikin1x@berkeley.edu');
insert ignore into students (first_name, last_name, email) values ('Jacklyn', 'Caddan', 'jcaddan1y@tinyurl.com');
insert ignore into students (first_name, last_name, email) values ('Torrence', 'Bradbury', 'tbradbury1z@mapy.cz');
insert ignore into students (first_name, last_name, email) values ('Andy', 'Lambole', 'alambole20@nba.com');
insert ignore into students (first_name, last_name, email) values ('Celinka', 'Caudrelier', 'ccaudrelier21@jiathis.com');
insert ignore into students (first_name, last_name, email) values ('Edan', 'Hanlin', 'ehanlin22@nature.com');


insert ignore into attendees (student_id, course_id) values (69, 1);
insert ignore into attendees (student_id, course_id) values (2, 1);
insert ignore into attendees (student_id, course_id) values (2, 1);
insert ignore into attendees (student_id, course_id) values (64, 1);
insert ignore into attendees (student_id, course_id) values (68, 1);
insert ignore into attendees (student_id, course_id) values (50, 1);
insert ignore into attendees (student_id, course_id) values (62, 1);
insert ignore into attendees (student_id, course_id) values (38, 1);
insert ignore into attendees (student_id, course_id) values (11, 1);
insert ignore into attendees (student_id, course_id) values (52, 1);
insert ignore into attendees (student_id, course_id) values (43, 1);
insert ignore into attendees (student_id, course_id) values (38, 1);
insert ignore into attendees (student_id, course_id) values (59, 1);
insert ignore into attendees (student_id, course_id) values (55, 1);
insert ignore into attendees (student_id, course_id) values (61, 1);
insert ignore into attendees (student_id, course_id) values (8, 1);
insert ignore into attendees (student_id, course_id) values (31, 1);
insert ignore into attendees (student_id, course_id) values (3, 1);



set @email_instructor = "wkim@gmail.com", @title = "Senior Project", @course = "CMPE_195", @start_dt = '2021-1-20', @end_dt = '2021-5-20';
set @start_time = "18:00", @end_time = "20:45", @units = 3, @days = "W";
insert into courses (user_id, title, title_id, units, start_dt, end_dt) 
values ((select id from users where email = @email_instructor), @title, @course, @units, @start_dt, (select DATE_ADD(@end_dt, interval 1 day)));

insert into course_dt_time (course_id, days, start_time, end_time) 
values ((select id from courses where title_id = @course), @days, @start_time, @end_time);