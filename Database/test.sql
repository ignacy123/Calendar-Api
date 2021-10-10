CREATE SCHEMA IF NOT EXISTS test;
DROP TABLE IF EXISTS activities CASCADE;
CREATE TABLE activities (
    id                          serial NOT NULL,
    name                        varchar(40) NOT NULL,
    CONSTRAINT activity_id PRIMARY KEY (id)
);

INSERT INTO activities (name) VALUES
('swimming'), 
('tennis'), 
('eating'),
('gokarts'),
('bowling'),
('squash'),
('jogging'),
('football'),
('yoga'),
('basketball'),
('volleyball'),
('gym');

DROP TABLE IF EXISTS email CASCADE;
CREATE TABLE email (
    id                          serial NOT NULL,
    email                       varchar(100) NOT NULL,
    CONSTRAINT email_id PRIMARY KEY (id)
);

DROP TABLE IF EXISTS fav_activities CASCADE;
CREATE TABLE fav_activities (
    id                          serial NOT NULL,
    email_id                    integer NOT NULL,
    activity_id                 integer NOT NULL,
    CONSTRAINT fav_id PRIMARY KEY (id),
    CONSTRAINT unique_pairs UNIQUE (email_id, activity_id),
    CONSTRAINT fk_fav_activities_email FOREIGN KEY (email_id) REFERENCES email(id),
    CONSTRAINT fk_fav_activities_reg_activities FOREIGN KEY (activity_id) REFERENCES activities(id)
);
