import psycopg2

try: 
  conn = psycopg2.connect(###################################)
  print("Conexão estabelecida.")
except:
  print("Não foi possível conectar a base de dados.")

def create_tables():
  tables = [
            """
            CREATE TABLE u_ser ( 
            u_id integer NOT NULL, 
            name varchar(50) NOT NULL, 
            email varchar(50) NOT NULL, 
            PRIMARY KEY (u_id)
            );
            """,
            """
            CREATE TABLE director (
              d_id integer NOT NULL,
              d_name varchar(50) NOT NULL,
              d_bday date NOT NULL,
              d_dday date,
              PRIMARY KEY (d_id)
            );
            """,
            """
            CREATE TABLE category (
              c_id integer NOT NULL,
              c_description varchar(200) NOT NULL,
              c_type varchar(100) NOT NULL,
              PRIMARY KEY (c_id)
            );
            """,
            """
            CREATE TABLE producer (
              p_id integer NOT NULL,
              p_name varchar(50) NOT NULL,
              p_con varchar(15) NOT NULL,
              p_web varchar(100) NOT NULL,
              p_adr varchar(100) NOT NULL,
              PRIMARY KEY(p_id)
            );
            """,
            """
            CREATE TABLE film (
              f_id integer NOT NULL,
              f_title varchar(100) NOT NULL,
              f_rday date NOT NULL,
              f_sinopse varchar(300) NOT NULL,
              f_length  int NOT NULL,
              PRIMARY KEY (f_id),
              p_id integer REFERENCES producer (p_id) NOT NULL,
              c_id integer REFERENCES category (c_id) NOT NULL,
              d_id integer REFERENCES director (d_id) NOT NULL
            );
            """,
            """
            CREATE TABLE serie (
              s_id integer NOT NULL,
              s_title varchar(100) NOT NULL,              
              s_sinopse varchar(300) NOT NULL,
              s_season_amount integer NOT NULL,
              PRIMARY KEY (s_id),
              p_id integer REFERENCES producer (p_id) NOT NULL,
              d_id integer REFERENCES director (d_id) NOT NULL,
              c_id integer REFERENCES category (c_id) NOT NULL
            );
            """,
            """
            CREATE TABLE season (
              season_id integer NOT NULL,
              s_description varchar(200) NOT NULL,
              s_ep_amount integer NOT NULL,
              PRIMARY KEY (season_id),
              s_id integer REFERENCES serie (s_id) NOT NULL
            );
            """,
            """
            CREATE TABLE episode (
              e_id integer NOT NULL,
              e_title varchar(50) NOT NULL,
              e_sinopse varchar(200) NOT NULL,
              e_length integer NOT NULL,
              PRIMARY KEY (e_id),
              season_id integer REFERENCES season (season_id) NOT NULL
            );
            """,
            """
            CREATE TABLE actor (
              a_id integer NOT NULL,
              a_name varchar(100) NOT NULL,
              a_bday date NOT NULL,
              a_dday date,
              PRIMARY KEY (a_id)
            );
            """,
            """
            CREATE TABLE watch_s (
              rating_s integer,
              u_id integer REFERENCES u_ser (u_id) NOT NULL,
              s_id integer REFERENCES serie (s_id) NOT NULL
            );
            """,
            """
            CREATE TABLE watch_f (
              rating_f integer,
              u_id integer REFERENCES u_ser (u_id) NOT NULL,
              f_id integer REFERENCES film (f_id) NOT NULL
            );
            """,

            """
            CREATE TABLE star_e (
              a_id integer REFERENCES actor (a_id) NOT NULL,
              e_id integer REFERENCES episode (e_id) NOT NULL
            );
            """,
            """
            CREATE TABLE star_f (
              a_id integer REFERENCES actor (a_id) NOT NULL,
              f_id integer REFERENCES film (f_id) NOT NULL
            );
            """
  ]
  
  return tables;

def create_functions():
  functions= [
              """
              CREATE OR REPLACE FUNCTION check_user() returns trigger as
              $BODY$
              BEGIN
              IF EXISTS (SELECT 1 FROM u_ser u WHERE u.email = NEW.email AND u.u_id != NEW.u_id ) THEN
              RETURN NULL;
              --RAISE EXCEPTION 'Esse e-mail já está em uso';
              ELSE
              RETURN NEW;
              END IF;
              END;
              $BODY$
              language plpgsql;
              """,
              """
              CREATE OR REPLACE FUNCTION check_film() returns trigger as
              $BODY$
              BEGIN
              IF NEW.f_length < 10 OR NEW.f_length > 225 THEN
              RETURN NULL;
              --RAISE EXCEPTION 'Duração de filme inválida';
              ELSIF NEW.f_rday < '2000-01-01' OR NEW.f_rday > '2020-12-31' THEN
              RETURN NULL;
              --RAISE EXCEPTION 'Data de lançamento inválida';
              ELSIF NOT EXISTS (SELECT 1 FROM category c WHERE c.c_id = NEW.c_id) OR
                    NOT EXISTS (SELECT 1 FROM director d WHERE d.d_id = NEW.d_id) OR
                    NOT EXISTS (SELECT 1 FROM producer p WHERE p.p_id = NEW.p_id) THEN
              RETURN NULL;
              --RAISE EXCEPTION 'Valor inválido para c_id,d_id, ou p_id';
              ELSE
              RETURN NEW;
              END IF;
              END;
              $BODY$
              language plpgsql;
              """,
              """
              CREATE OR REPLACE FUNCTION check_serie() returns trigger as
              $BODY$
              BEGIN
              IF NEW.s_season_amount > 31 OR NEW.s_season_amount < 0 THEN
              RETURN NULL;
              --RAISE EXCEPTION 'Quantidade de temporadas inválida';
              ELSIF NOT EXISTS (SELECT 1 FROM category c WHERE c.c_id = NEW.c_id) OR
                    NOT EXISTS (SELECT 1 FROM director d WHERE d.d_id = NEW.d_id) OR
                    NOT EXISTS (SELECT 1 FROM producer p WHERE p.p_id = NEW.p_id) THEN
              RETURN NULL;
              --RAISE EXCEPTION 'Valor inválido para c_id,d_id, ou p_id';
              ELSE
              RETURN NEW;
              END IF;
              END;
              $BODY$
              language plpgsql;
              """,
              """
              CREATE OR REPLACE FUNCTION check_season() returns trigger as
              $BODY$
              BEGIN
              IF NEW.s_ep_amount < 6 OR NEW.s_ep_amount > 30 THEN
              RETURN NULL;
              --RAISE EXCEPTION 'Quantidade de episódios inválida';
              ELSIF NOT EXISTS (SELECT 1 FROM serie s WHERE s.s_id = NEW.s_id) THEN
              RETURN NULL;
              --RAISE EXCEPTION 'Valor inválido para s_id';
              ELSE
              RETURN NEW;
              END IF;
              END;
              $BODY$
              language plpgsql;
              """,
              """
              CREATE OR REPLACE FUNCTION check_ep() returns trigger as
              $BODY$
              BEGIN
              IF NEW.e_length < 15 OR NEW.e_length > 90 THEN
              RETURN NULL;
              --RAISE EXCEPTION 'Duração de episódio inválida';
              ELSIF NOT EXISTS (SELECT 1 FROM season s WHERE s.season_id = NEW.season_id) THEN
              RETURN NULL;
              --RAISE EXCEPTION 'Valor inválido para season_id';
              ELSE
              RETURN NEW;
              END IF;
              END;
              $BODY$
              language plpgsql;
              """,
              """
              CREATE OR REPLACE FUNCTION check_director() returns trigger as
              $BODY$
              BEGIN
              IF NEW.d_bday > NEW.d_dday THEN
              RETURN NULL;
              --RAISE EXCEPTION 'Combinação de datas de nascimento e morte inválidas';
              ELSE
              RETURN NEW;
              END IF;
              END;
              $BODY$
              language plpgsql;
              """,
              """
              CREATE OR REPLACE FUNCTION check_actor() returns trigger as
              $BODY$
              BEGIN
              IF NEW.a_bday > NEW.a_dday THEN
              RETURN NULL;
              --RAISE EXCEPTION 'Combinação de datas de nascimento e morte inválidas';
              ELSE
              RETURN NEW;
              END IF;
              END;
              $BODY$
              language plpgsql;
              """,
              """
              CREATE OR REPLACE FUNCTION check_watch_f() returns trigger as
              $BODY$
              BEGIN
              IF NEW.rating_f < 0 OR NEW.rating_f > 5 THEN
              RETURN NULL;
              --RAISE EXCEPTION 'Valor de avaliação inválido';
              ELSIF NOT EXISTS (SELECT 1 FROM u_ser us WHERE us.u_id = NEW.u_id) OR
                    NOT EXISTS (SELECT 1 FROM film f WHERE f.f_id = NEW.f_id) THEN
              RETURN NULL;
              --RAISE EXCEPTION 'Valor de u_id ou f_id inválido';
              ELSE
              RETURN NEW;
              END IF;
              END;
              $BODY$
              language plpgsql;
              """
              ,
              """
              CREATE OR REPLACE FUNCTION check_watch_s() returns trigger as
              $BODY$
              BEGIN
              IF NEW.rating_s < 0 OR NEW.rating_s > 5 THEN
              RETURN NULL;
              --RAISE EXCEPTION 'Valor de avaliação inválido';
              ELSIF NOT EXISTS (SELECT 1 FROM u_ser us WHERE us.u_id = NEW.u_id) OR
                    NOT EXISTS (SELECT 1 FROM serie s WHERE s.s_id = NEW.s_id) THEN
              RETURN NULL;
              --RAISE EXCEPTION 'Valor de u_id ou s_id inválido';
              ELSE
              RETURN NEW;
              END IF;
              END;
              $BODY$
              language plpgsql;
              """,
              """
              CREATE OR REPLACE FUNCTION check_category() returns trigger as
              $BODY$
              BEGIN
              IF (NEW.c_type = 'Comédia' or 
                  NEW.c_type = 'Ação' or 
                  NEW.c_type = 'Terror' or 
                  NEW.c_type = 'Suspense' or 
                  NEW.c_type = 'Animação' or 
                  NEW.c_type = 'Curta Metragem' 
                  or NEW.c_type = 'Fantasia' 
                  or NEW.c_type = 'Romance') THEN
              RETURN NEW;
              ELSE
              RETURN NULL;
              --RAISE EXCEPTION 'Tipo inválido de categoria';
              END IF;
              END;
              $BODY$
              language plpgsql;
              """,
              """
              CREATE OR REPLACE FUNCTION check_star_e() returns trigger as
              $BODY$
              BEGIN
              IF NOT EXISTS (SELECT 1 FROM episode e WHERE e.e_id = NEW.e_id) OR
                 NOT EXISTS (SELECT 1 FROM actor ac WHERE ac.a_id = NEW.a_id) THEN
              RETURN NULL;
              RAISE EXCEPTION 'Valor inválido para e_id ou a_id';
              ELSE
              RETURN NEW;
              END IF;
              END;
              $BODY$
              language plpgsql;
              """,
              """
              CREATE OR REPLACE FUNCTION check_star_f() returns trigger as
              $BODY$
              BEGIN
              IF NOT EXISTS (SELECT 1 FROM film f WHERE f.f_id = NEW.f_id) OR
                 NOT EXISTS (SELECT 1 FROM actor ac WHERE ac.a_id = NEW.a_id) THEN
              RETURN NULL;
              RAISE EXCEPTION 'Valor inválido para f_id ou a_id';
              ELSE
              RETURN NEW;
              END IF;
              END;
              $BODY$
              language plpgsql;
              """
  ]
  return functions;

def create_triggers():
  triggers = [
              """
              CREATE TRIGGER user_trigger
              BEFORE INSERT OR UPDATE ON u_ser
              FOR EACH ROW EXECUTE PROCEDURE check_user();
              """,
              """
              CREATE TRIGGER film_trigger
              BEFORE INSERT OR UPDATE ON film
              FOR EACH ROW EXECUTE PROCEDURE check_film();
              """,
              """
              CREATE TRIGGER serie_trigger
              BEFORE INSERT OR UPDATE ON serie
              FOR EACH ROW EXECUTE PROCEDURE check_serie();
              """,
              """
              CREATE TRIGGER season_trigger
              BEFORE INSERT OR UPDATE ON season
              FOR EACH ROW EXECUTE PROCEDURE check_season();
              """,
              """
              CREATE TRIGGER episode_trigger
              BEFORE INSERT OR UPDATE ON episode
              FOR EACH ROW EXECUTE PROCEDURE check_ep();
              """,
              """
              CREATE TRIGGER actor_trigger
              BEFORE INSERT OR UPDATE ON actor
              FOR EACH ROW EXECUTE PROCEDURE check_actor();
              """,
              """
              CREATE TRIGGER director_trigger
              BEFORE INSERT OR UPDATE ON director
              FOR EACH ROW EXECUTE PROCEDURE check_director();
              """,
              """
              CREATE TRIGGER watch_f_trigger
              BEFORE INSERT OR UPDATE ON watch_f
              FOR EACH ROW EXECUTE PROCEDURE check_watch_f();
              """,
              """
              CREATE TRIGGER watch_s_trigger
              BEFORE INSERT OR UPDATE ON watch_s
              FOR EACH ROW EXECUTE PROCEDURE check_watch_s();
              """,
              """
              CREATE TRIGGER category_trigger
              BEFORE INSERT OR UPDATE ON category
              FOR EACH ROW EXECUTE PROCEDURE check_category();
              """,
              """
              CREATE TRIGGER star_f_trigger
              BEFORE INSERT OR UPDATE ON star_f
              FOR EACH ROW EXECUTE PROCEDURE check_star_f();
              """,
              """
              CREATE TRIGGER star_e_trigger
              BEFORE INSERT OR UPDATE ON star_e
              FOR EACH ROW EXECUTE PROCEDURE check_star_e();
              """
  ]
  return triggers;

def queries():
  queries = [
             """
             SELECT f_title FROM film
             WHERE film.f_rday > '2019/12/31' AND film.f_rday < '2020/12/31';
             """,
             """
             SELECT p_name FROM producer pr
             INNER JOIN film f ON f.p_id = pr.p_id
             INNER JOIN category ca on ca.c_id = f.c_id
             WHERE ca.c_type = 'Fantasia';
             """,
             """
             SELECT DISTINCT ac.a_name
             FROM actor ac, star_f f, star_e e
             WHERE
             NOT EXISTS(SELECT 1 FROM star_f f WHERE f.a_id = ac.a_id) AND
             NOT EXISTS(SELECT 1 FROM star_e e WHERE e.a_id = ac.a_id);
             """,
             """
             SELECT e_title, ser.s_title from episode e, season sea, serie ser, producer pr
             WHERE e.season_id = sea.season_id 
             AND sea.s_id = ser.s_id
             AND pr.p_id = ser.p_id AND pr.p_adr LIKE '%Brazil%';
             """,
             """
             SELECT us.u_id
             FROM u_ser us, watch_f w, film f, category c, producer p, actor ac, star_f s
             WHERE us.u_id = w.u_id 
             AND w.rating_f = 3 
             AND w.f_id = f.f_id 
             AND f.c_id = c.c_id 
             AND c.c_type='Comédia' 
             AND f.f_id = s.f_id 
             AND f.p_id = p.p_id 
             AND p.p_adr LIKE '%Estados Unidos%';
             """
  ]

  return queries;

try:
  cur = conn.cursor()
  
  # table = create_tables()
  # functions = create_functions()
  # triggers = create_triggers()
  queries = queries();

  # for item in table:
  #   cur.execute(item)
  
  # for func in functions:
  #   cur.execute(func)
  
  # for trigger in triggers:
  #   cur.execute(trigger)
 
  # u_ser = open('u_ser.txt', 'r')
  # director = open('director.txt', 'r')
  # category = open('category.txt', 'r')
  # producer = open('producer.txt', 'r')
  # film = open('film.txt', 'r')
  # serie = open('serie.txt', 'r')
  # season = open('season.txt', 'r')
  # episode = open('episode.txt', 'r')
  # actor = open('actor.txt', 'r')
  # watch_s = open('watch_s.txt', 'r')
  # watch_f = open('watch_f.txt', 'r')
  # star_e = open('star_e.txt', 'r')
  # star_f = open('star_f.txt', 'r')
  
  
  # files = [
  #          u_ser,
  #          director,
  #          category,
  #          producer,
  #          film,
  #          serie,
  #          season,
  #          episode,
  #          actor,
  #          watch_s,
  #          watch_f,
  #          star_e,
  #          star_f
  # ]

  # for file in files:
  #   for line in file:
  #     cur.execute(line)

  for query in queries:
    cur.execute(query)
    print(cur.fetchall())
  
  
  conn.commit()

  cur.close()
except (Exception, psycopg2.DatabaseError) as error:
  print(error)
finally:
  if conn is not None:
    conn.close()

