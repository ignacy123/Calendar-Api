CREATE SCHEMA IF NOT EXISTS test;
DROP TABLE IF EXISTS activities CASCADE;
CREATE TABLE activities (
    id                          serial NOT NULL,
    name                        varchar(40) NOT NULL,
    CONSTRAINT activity_id PRIMARY KEY (id)
);

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

DROP TABLE IF EXISTS single_events CASCADE;
CREATE TABLE single_events (
    id                          serial NOT NULL,
    email_id                    integer NOT NULL,
    activity_id                 integer NOT NULL,
    start_time                  timestamptz NOT NULL,
    end_time                    timestamptz NOT NULL,
    CONSTRAINT single_event_id PRIMARY KEY (id),
    CONSTRAINT fk_single_events_email FOREIGN KEY (email_id) REFERENCES email(id),
    CONSTRAINT fk_single_events_activities FOREIGN KEY (activity_id) REFERENCES activities(id),
    CONSTRAINT correct_single_event CHECK (start_time < end_time)
);
-- trigger to check if the activity in the event is email owner's favourite
CREATE OR REPLACE FUNCTION event_fav_check() RETURNS TRIGGER AS $event_fav_check$
DECLARE
BEGIN
IF NOT EXISTS (SELECT id FROM fav_activities WHERE email_id = NEW.email_id AND activity_id = NEW.activity_id)
    THEN RAISE EXCEPTION 'User cannot schedule an event with an activity that is not favourite.';
END IF;
RETURN NEW;
END;
$event_fav_check$ LANGUAGE plpgsql;
CREATE TRIGGER single_event_fav_check BEFORE INSERT OR UPDATE ON single_events
FOR EACH ROW EXECUTE PROCEDURE event_fav_check();

-- trigger to check for potential overlaps between single events
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

DROP FUNCTION IF EXISTS get_single_activities CASCADE;

CREATE OR REPLACE FUNCTION get_single_activities(timestamptz, integer)
    RETURNS TABLE (name varchar(40), start_time timestamptz, end_time timestamptz) AS
$func$
BEGIN
    RETURN QUERY 
    SELECT a.name, r.start_time, r.end_time FROM single_events AS r LEFT OUTER JOIN activities AS a ON r.activity_id = a.id WHERE (
    (r.end_time >= $1 AND r.end_time <= $1 + '1 day'::interval)
    OR ($1 + '1 day'::interval >= r.start_time AND $1 + '1 day'::interval <= r.end_time)
    )
    AND r.email_id = $2;
END
$func$ LANGUAGE plpgsql;

DROP TABLE IF EXISTS recurrent_events CASCADE;
CREATE TABLE recurrent_events (
    id                      serial NOT NULL,
    email_id                integer NOT NULL,
    activity_id             integer NOT NULL,
    start_time              timestamptz NOT NULL,
    end_time                timestamptz NOT NULL,
    type                    varchar(10),
    CONSTRAINT recurrent_event_id PRIMARY KEY (id),
    CONSTRAINT fk_recurrent_events_email FOREIGN KEY (email_id) REFERENCES email(id),
    CONSTRAINT fk_recurrent_events_activities FOREIGN KEY (activity_id) REFERENCES activities(id),
    CONSTRAINT correct_recurrent_event CHECK (start_time < end_time),
    CONSTRAINT correct_type CHECK (type IN ('DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY'))
);
-- trigger to check if the activity in the event is email owner's favourite
CREATE TRIGGER recurrent_event_fav_check BEFORE INSERT OR UPDATE ON recurrent_events
FOR EACH ROW EXECUTE PROCEDURE event_fav_check();

--trigger to perform sanity checks on recurrent activites - dailies can't be longer than 24 hours, weeklies than 7 days, monthlies than 28 days, yearlies than 365 days
CREATE OR REPLACE FUNCTION recurrent_event_check() RETURNS TRIGGER AS $recurrent_event_check$
DECLARE
BEGIN
IF NEW.type = 'DAILY' AND EXTRACT (epoch FROM NEW.end_time - NEW.start_time) >= 60*60*24
    THEN RAISE EXCEPTION 'Daily activity cannot be longer than 24 hours.';
END IF;
RETURN NEW;
END;
$recurrent_event_check$ LANGUAGE plpgsql;
CREATE TRIGGER recurrent_event_check BEFORE INSERT OR UPDATE ON recurrent_events
FOR EACH ROW EXECUTE PROCEDURE recurrent_event_check();

DROP FUNCTION IF EXISTS get_dailies CASCADE;

CREATE OR REPLACE FUNCTION get_dailies(timestamptz, integer) 
    RETURNS TABLE (name varchar(40), start_time timestamptz, end_time timestamptz, type varchar(10)) AS
$func$
BEGIN
    RETURN QUERY 
    SELECT a.name, r.start_time, r.end_time, r.type FROM recurrent_events AS r LEFT OUTER JOIN activities AS a ON r.activity_id = a.id WHERE 
    r.start_time < $1 + '1 day'::interval
    AND r.type = 'DAILY'
    AND r.email_id = $2;
END
$func$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_weeklies(timestamptz) 
    RETURNS TABLE (name varchar(40), start_time timestamptz, end_time timestamptz, type varchar(10)) AS
$func$
BEGIN
    RETURN QUERY 
    SELECT a.name, r.start_time, r.end_time, r.type FROM recurrent_events AS r LEFT OUTER JOIN activities AS a ON r.activity_id = a.id WHERE (
    (EXTRACT (isodow FROM r.start_time) <= EXTRACT (isodow FROM $1) AND EXTRACT (isodow FROM r.end_time) >= EXTRACT (isodow FROM $1)) 
    OR
    (EXTRACT (isodow FROM r.start_time) <= EXTRACT (isodow FROM $1) AND EXTRACT (isodow FROM r.end_time) <= EXTRACT (isodow FROM $1) AND (EXTRACT (isodow FROM r.start_time) > EXTRACT (isodow FROM r.end_time)))
    OR
    (EXTRACT (isodow FROM r.start_time) >= EXTRACT (isodow FROM $1) AND EXTRACT (isodow FROM r.end_time) >= EXTRACT (isodow FROM $1) AND (EXTRACT (isodow FROM r.start_time) > EXTRACT (isodow FROM r.end_time)))
    )
    AND r.start_time < $1 + '1 day'::interval
    AND r.type = 'WEEKLY';
END
$func$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS get_weeklies CASCADE;

CREATE OR REPLACE FUNCTION get_weeklies(timestamptz, integer) 
    RETURNS TABLE (name varchar(40), start_time timestamptz, end_time timestamptz, type varchar(10)) AS
$func$
BEGIN
    RETURN QUERY 
    SELECT a.name, r.start_time, r.end_time, r.type FROM recurrent_events AS r LEFT OUTER JOIN activities AS a ON r.activity_id = a.id WHERE (
    (EXTRACT (isodow FROM r.start_time) <= EXTRACT (isodow FROM $1) AND EXTRACT (isodow FROM r.end_time) >= EXTRACT (isodow FROM $1)) 
    OR
    (EXTRACT (isodow FROM r.start_time) <= EXTRACT (isodow FROM $1) AND EXTRACT (isodow FROM r.end_time) <= EXTRACT (isodow FROM $1) AND (EXTRACT (isodow FROM r.start_time) > EXTRACT (isodow FROM r.end_time)))
    OR
    (EXTRACT (isodow FROM r.start_time) >= EXTRACT (isodow FROM $1) AND EXTRACT (isodow FROM r.end_time) >= EXTRACT (isodow FROM $1) AND (EXTRACT (isodow FROM r.start_time) > EXTRACT (isodow FROM r.end_time)))
    )
    AND r.start_time < $1 + '1 day'::interval
    AND r.type = 'WEEKLY'
    AND r.email_id = $2;
END
$func$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS get_monthlies CASCADE;

CREATE OR REPLACE FUNCTION get_monthlies(timestamptz, integer) 
    RETURNS TABLE (name varchar(40), start_time timestamptz, end_time timestamptz, type varchar(10)) AS
$func$
BEGIN
    RETURN QUERY 
    SELECT a.name, r.start_time, r.end_time, r.type FROM recurrent_events AS r LEFT OUTER JOIN activities AS a ON r.activity_id = a.id WHERE (
    (EXTRACT (day FROM r.start_time) <= EXTRACT (day FROM $1) AND EXTRACT (day FROM r.end_time) >= EXTRACT (day FROM $1)) 
    OR
    (EXTRACT (day FROM r.start_time) <= EXTRACT (day FROM $1) AND EXTRACT (day FROM r.end_time) <= EXTRACT (day FROM $1) AND (EXTRACT (day FROM r.start_time) > EXTRACT (day FROM r.end_time)))
    OR
    (EXTRACT (day FROM r.start_time) >= EXTRACT (day FROM $1) AND EXTRACT (day FROM r.end_time) >= EXTRACT (day FROM $1) AND (EXTRACT (day FROM r.start_time) > EXTRACT (day FROM r.end_time)))
    )
    AND r.start_time < $1 + '1 day'::interval
    AND r.type = 'MONTHLY'
    AND r.email_id = $2;
END
$func$ LANGUAGE plpgsql;

-- returns timestamptz1 <= timestamptz2 ignoring the year and anything after the day (MM1-DD1 <= MM2-DD2)

DROP FUNCTION IF EXISTS cmp_timestamptz_soe CASCADE;

CREATE OR REPLACE FUNCTION cmp_timestamptz_soe (timestamptz, timestamptz) 
    RETURNS boolean AS
$func$
BEGIN
    IF (SELECT EXTRACT (month FROM $1) < EXTRACT (month from $2))
        THEN RETURN TRUE;
    END IF;
    IF (SELECT EXTRACT (month FROM $1) > EXTRACT (month from $2))
        THEN RETURN FALSE;
    END IF;
    IF (SELECT EXTRACT (day FROM $1) <= EXTRACT (day from $2))
        THEN RETURN TRUE;
    END IF;
    RETURN FALSE;
END
$func$ LANGUAGE plpgsql;

-- returns timestamptz1 < timestamptz2 ignoring the year and anything after the day (MM1-DD1 < MM2-DD2)

DROP FUNCTION IF EXISTS cmp_timestamptz_s CASCADE;

CREATE OR REPLACE FUNCTION cmp_timestamptz_s (timestamptz, timestamptz) 
    RETURNS boolean AS
$func$
BEGIN
    IF (SELECT EXTRACT (month FROM $1) < EXTRACT (month from $2))
        THEN RETURN TRUE;
    END IF;
    IF (SELECT EXTRACT (month FROM $1) > EXTRACT (month from $2))
        THEN RETURN FALSE;
    END IF;
    IF (SELECT EXTRACT (day FROM $1) < EXTRACT (day from $2))
        THEN RETURN TRUE;
    END IF;
    RETURN FALSE;
END
$func$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS get_yearlies CASCADE;

CREATE OR REPLACE FUNCTION get_yearlies(timestamptz, integer) 
    RETURNS TABLE (name varchar(40), start_time timestamptz, end_time timestamptz, type varchar(10)) AS
$func$
BEGIN
    RETURN QUERY 
    SELECT a.name, r.start_time, r.end_time, r.type FROM recurrent_events AS r LEFT OUTER JOIN activities AS a ON r.activity_id = a.id WHERE (
    (SELECT cmp_timestamptz_soe(r.start_time, $1) AND (SELECT cmp_timestamptz_soe($1, r.end_time))) 
    OR
    (SELECT cmp_timestamptz_soe(r.start_time, $1) AND (SELECT cmp_timestamptz_soe(r.end_time, $1)) AND (SELECT cmp_timestamptz_s(r.end_time, r.start_time)))
    OR
    (SELECT cmp_timestamptz_soe($1, r.start_time) AND (SELECT cmp_timestamptz_soe($1, r.end_time)) AND (SELECT cmp_timestamptz_s(r.end_time, r.start_time)))
    )
    AND r.start_time < $1 + '1 day'::interval
    AND r.type = 'YEARLY'
    AND r.email_id = $2;
END
$func$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS get_activities CASCADE;

CREATE OR REPLACE FUNCTION get_activities(timestamptz, integer) 
    RETURNS TABLE (name varchar(40), start_time timestamptz, end_time timestamptz, type varchar(10)) AS
$func$
BEGIN
    RETURN QUERY 
    SELECT g.name, g.start_time, g.end_time, NULL FROM get_single_activities($1, $2) AS g
    UNION
    SELECT g.name, g.start_time, g.end_time, g.type FROM get_dailies($1, $2) AS g
    UNION
    SELECT g.name, g.start_time, g.end_time, g.type FROM get_weeklies($1, $2) AS g
    UNION
    SELECT g.name, g.start_time, g.end_time, g.type FROM get_monthlies($1, $2) AS g
    UNION
    SELECT g.name, g.start_time, g.end_time, g.type FROM get_yearlies($1, $2) AS g
    ORDER BY 4;
END
$func$ LANGUAGE plpgsql;


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

INSERT INTO email (email) VALUES ('ignacy.buczek@onet.pl');

INSERT INTO fav_activities (email_id, activity_id) VALUES
(1, 1),
(1, 2),
(1, 3),
(1, 4),
(1, 5),
(1, 7),
(1, 8),
(1, 9),
(1, 10),
(1, 11),
(1, 12);

INSERT INTO single_events (email_id, activity_id, start_time, end_time) VALUES (1, 3, '2019-04-28 08:20:00', '2019-04-28 10:20:00');
INSERT INTO single_events (email_id, activity_id, start_time, end_time) VALUES (1, 12, '2021-10-14 08:20:00', '2021-10-16 10:20:00');
INSERT INTO single_events (email_id, activity_id, start_time, end_time) VALUES (1, 4, '2021-10-16 10:20:00', '2021-10-16 14:20:00');
INSERT INTO single_events (email_id, activity_id, start_time, end_time) VALUES (1, 4, '2021-10-17 23:58:00', '2021-10-18 10:20:00');
INSERT INTO single_events (email_id, activity_id, start_time, end_time) VALUES (1, 8, '2020-05-05 21:37:12', '2020-06-30 10:20:00');

INSERT INTO recurrent_events (email_id, activity_id, start_time, end_time, type) VALUES 
(1, 3, '2021-10-12 10:00:00', '2021-10-12 12:00:00', 'DAILY'),
(1, 1, '2019-01-05 10:00:00', '2019-01-05 15:00:00', 'DAILY'),
(1, 11, '2021-10-12 14:00:00', '2021-10-13 13:00:00', 'DAILY'),
(1, 4, '2021-10-13 16:00:00', '2021-10-13 18:00:00', 'WEEKLY'),
(1, 5, '2021-10-02 10:00:00', '2021-10-05 12:00:00', 'WEEKLY'),
(1, 5, '2021-10-04 10:00:00', '2021-10-08 12:00:00', 'WEEKLY'),
(1, 7, '2021-10-06 15:00:00', '2021-10-06 17:00:00', 'WEEKLY'),
(1, 9, '2021-10-13 15:00:00', '2021-10-13 17:00:00', 'WEEKLY'),
(1, 10, '2021-10-20 15:00:00', '2021-10-20 17:00:00', 'WEEKLY'),
(1, 8, '2021-10-14 14:00:00', '2021-10-14 15:00:00', 'MONTHLY'),
(1, 11, '2021-08-30 14:00:00', '2021-09-10 15:00:00', 'MONTHLY'),
(1, 2, '2021-08-17 14:00:00', '2021-08-17 16:00:00', 'MONTHLY'),
(1, 1, '2021-10-17 14:00:00', '2021-10-30 16:00:00', 'MONTHLY'),
(1, 5, '2021-09-20 10:00:00', '2021-09-20 16:00:00', 'MONTHLY'),
(1, 5, '2021-06-30 10:00:00', '2021-07-01 09:00:00', 'MONTHLY'),
(1, 12, '2021-10-15 20:00:00', '2021-10-15 21:00:00', 'YEARLY'),
(1, 3, '2020-01-07 20:00:00', '2021-08-31 21:00:00', 'YEARLY'),
(1, 11, '2020-12-10 20:00:00', '2021-03-11 21:00:00', 'YEARLY'),
(1, 11, '2020-07-09 20:00:00', '2021-01-10 21:00:00', 'YEARLY'),
(1, 11, '2020-05-05 20:00:00', '2020-05-05 21:00:00', 'YEARLY'),
(1, 4, '2020-03-03 20:00:00', '2021-07-07 21:00:00', 'YEARLY');
