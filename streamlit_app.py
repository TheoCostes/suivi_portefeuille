import logging
import sqlite3
import yaml
import os
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

import streamlit as st
from threading import Thread
import scheduler


def setup_user_auth():
    """Setup username and password"""
    if not os.path.isfile(os.path.join(".", "config_auth.yaml")):
        logging.debug("Creating config_auth.yaml")
        logging.debug(os.path.isfile(os.path.join(".", "config_auth.yaml")))
        data = {
            'credentials': {
                'usernames': {
                    "admin": {
                        "email": "tharic100@gmail.com",
                        "name": "admin",
                        "password": "admin",
                    },
                }
            },
            'cookie': {
                "expiry_days": 30,
                "key": "user",
                "name": "session_state"
            },
            'preauthorized': {
                "emails": "- tharic100@gmail.com"
            }
        }

        with open('./config_auth.yaml', 'w') as file:
            yaml.dump(data, file)


def setup_database():
    setup_user_auth()

    conn = sqlite3.connect('./data/db.sqlite3')
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS transaction_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,  
                  id_user VARCHAR,
                  date VARCHAR,
                  type_transaction VARCHAR,
                  type_actif1 VARCHAR,
                  token1 VARCHAR,
                  description1 VARCHAR,
                  amount1 REAL,
                  unit_price1 REAL,
                  value1 REAL,
                  type_actif2 VARCHAR,
                  token2 VARCHAR,
                  description2 VARCHAR,
                  amount2 REAL,
                  unit_price2 REAL,
                  value2 REAL)
            """)

    c.execute('''CREATE TABLE IF NOT EXISTS portefeuille_portefeuille
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      id_portefeuille INTEGER, 
                      id_user VARCHAR,
                      last_update VARCHAR,
                      type_actif VARCHAR,
                      token VARCHAR,
                      description VARCHAR,
                      amount REAL,
                      unit_price REAL,
                      value REAL)
                ''')

    c.execute('''CREATE TABLE IF NOT EXISTS transactions_token
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  id_user VARCHAR,
                  name VARCHAR, 
                  symbole VARCHAR,
                  type VARCHAR)
            ''')

    conn.commit()
    c.close()
    conn.close()

if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = None

st.title("Bienvenue sur l'app de suivie de portefeuille !")
setup_database()

with open('./config_auth.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

tabs1, tabs2 = st.tabs(["Login", "Register"])


def reset_password():
    global file, e
    if st.button('Reset password'):
        try:
            if authenticator.reset_password(st.session_state["username"], 'Reset password'):
                st.success('Password modified successfully')
                with open('./config_auth.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
        except Exception as e:
            st.error(e)





if st.session_state["authentication_status"]:
    authenticator.logout('Logout', 'main', key='unique_key')
    st.success(f'Connnexion Réussi ! Welcome *{st.session_state["name"]}*')
elif st.session_state["authentication_status"] is False:
    with tabs1:
        authenticator.login('Login', 'main')
        st.error('Username/password is incorrect')
        reset_password()
elif st.session_state["authentication_status"] is None:
    with tabs1:
        authenticator.login('Login', 'main')
        st.warning('Please enter your username and password')
        reset_password()



with tabs2:
    try:
        if authenticator.register_user('Register user', preauthorization=False):
            st.success('User registered successfully')
            with open('./config_auth.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
    except Exception as e:
        st.error(e)


# Fonction pour exécuter le planificateur dans un thread séparé
def run_scheduler():
    scheduler.run_scheduler()


# Lancez le planificateur dans un thread
scheduler_thread = Thread(target=run_scheduler)
scheduler_thread.start()
