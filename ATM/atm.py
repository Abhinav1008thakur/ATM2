import streamlit as st
import sqlite3
from streamlit_option_menu import option_menu
import time as t
import pandas as p
def connectdb():
    conn=sqlite3.connect("atm.db")
    return conn
def createtable():
    with connectdb() as con:
        cur=con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS user (Username TEXT, password TEXT primary key, balance REAL NOT NULL DEFAULT 0)")
        con.commit()
def addrecord(us,ps,bal):
    with connectdb() as con:
        cur=con.cursor()
        cur.execute("SELECT * FROM user WHERE Username=?", (us,))
        existinguser = cur.fetchone()
        if existinguser:
            st.error("Username already exists! Please choose a different username.")
            return False
        if us.lower() in ps.lower():  # Make it case insensitive for better user experience
            st.error("Password cannot contain the username.")
            return False
        else:
            cur.execute("insert or replace into user(Username,password,balance)values(?,?,?)",(us,ps,bal))
            con.commit()
        return True
def valid(Username,password):
    with connectdb() as con:
        cur=con.cursor()
        cur.execute("SELECT * FROM user WHERE Username=? AND password=?", (Username, password))
        holder=cur.fetchone()
        con.commit()
        return holder
def display():
    with connectdb() as con:
        cur=con.cursor()
        cur.execute("SELECT * FROM user")
        result=cur.fetchall()
        df=p.DataFrame(result,columns=["Username","Password","Balance"])
        con.commit()
    return df
createtable()
with st.sidebar:
    select=option_menu("Select option",["Sign in","Sign up","Display","Withdrawl"])
if select=="Sign up":
    st.subheader("Create New Account")
    us=st.text_input("Enter username")
    ps=st.text_input("Enter password",type="password")
    bal=st.number_input("Initial Balance",min_value=0,value=1000)
    if st.button("Submit"):
        if us and ps:
            addrecord(us,ps,bal)
            st.success(f"Account Created Successfully! Initial Balnce $ {bal}")
        else:
            st.error("please fill all field !!")
elif select=="Sign in":
    st.subheader("Enter Your Credentials to Access Your Account")
    us=st.text_input("Enter username")
    ps=st.text_input("Enter password",type="password")
    if st.button("Login"):
        if us and ps:
            holder=valid(us,ps)
            if holder:
                st.success("Signed in Successfully")
                st.write(f"Balance: $ {holder[2]}")
            else:
                st.error("Invalid username or password.Pls try again.")
        else:
            st.warning("Enter username and password both")
elif select=="Withdrawl":
    st.subheader("Withdraw money")
    ps=st.text_input("Enter password",type="password")
    wit=st.number_input("Enter ammount")
    if st.button("Withdrawl"):
        if ps:
            with connectdb() as con:
                cur=con.cursor()
                cur.execute("SELECT balance FROM user WHERE password=?",(ps,))
                row=cur.fetchone()
                if row:
                    curr_bal=row[0]
                    if wit > curr_bal:
                        st.warning("NOt that much amount")
                    else:
                        with st.spinner(" "):
                            t.sleep(2)
                            st.success("Withdrawl succesfull")
                            new_bal=curr_bal-wit
                            cur.execute("UPDATE user SET balance = ? WHERE password = ?", (new_bal, ps))
                            con.commit()
                            st.success(f"Wihdrawl amount ${wit}")
                            st.markdown(f"## Balance=$ {new_bal}")
                            st.balloons()
        else:
            st.warning("Password is incorrect")
else:
    holder=display()
    if not holder.empty:
        st.subheader("Users details")
        st.dataframe(holder)
    else:
        st.write("no user found")