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

INSERT INTO email (email) VALUES ('ignacy.buczek@onet.pl');

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

INSERT INTO fav_activities (email_id, activity_id) VALUES
(1, 3),
(1, 4),
(1, 8),
(1, 12);

DROP TABLE IF EXISTS single_events CASCADE;
CREATE TABLE single_events (
    id                          serial NOT NULL,
    email_id                    integer NOT NULL,
    activity_id                 integer NOT NULL,
    start_time                  timestamp NOT NULL,
    end_time                    timestamp NOT NULL,
    CONSTRAINT event_id PRIMARY KEY (id),
    CONSTRAINT fk_events_email FOREIGN KEY (email_id) REFERENCES email(id),
    CONSTRAINT fk_events_activities FOREIGN KEY (activity_id) REFERENCES activities(id),
    CONSTRAINT correct_event CHECK (start_time < end_time)
);
-- trigger to check for potential overlaps
CREATE OR REPLACE FUNCTION single_event_check() RETURNS TRIGGER AS $single_event_check$
DECLARE
BEGIN
IF EXISTS ( SELECT * FROM single_events WHERE email_id = NEW.email_id AND ( (NEW.start_time <= start_time AND NEW.end_time  > start_time) OR (NEW.start_time > start_time AND NEW.start_time < end_time) ))
THEN RAISE EXCEPTION 'This user is busy at this time.';
END IF;
RETURN NEW;
END;
$single_event_check$ LANGUAGE plpgsql;
CREATE TRIGGER single_event_check BEFORE INSERT OR UPDATE ON single_events
FOR EACH ROW EXECUTE PROCEDURE single_event_check();

INSERT INTO single_events (email_id, activity_id, start_time, end_time) VALUES (1, 3, '2019-04-28 08:20:00', '2019-04-28 10:20:00');






