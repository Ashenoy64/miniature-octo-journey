import mysql.connector
import xml.etree.ElementTree as ET
import sys
import streamlit as st
import time
import threading


class Database:
    def __init__(self, databaseConfig):
        try:
            self.conn = mysql.connector.connect(**databaseConfig)
            print("Successfully connected to database")
        except:
            print("Failed to Connect to the database")
            sys.exit(0)

        self.cursor = self.conn.cursor(dictionary=True)
        self.dataParser = XMLParser()

    def ViewTables(self, tableName):
        try:
            st.subheader(tableName)
            self.cursor.execute(f"SELECT * FROM {tableName}")
            data = self.cursor.fetchall()
            if data == []:
                self.cursor.execute(f"desc {tableName}")
                columns = [{i["Field"]: "" for i in self.cursor.fetchall()}]
                st.table(columns)
            else:
                st.table(data)
        except Exception as e:
            print("Error fetching data from the database:", str(e))

    def InsertData(self, filename):
        try:

            self.dataParser.InitParser(filename)
            data = self.dataParser.ParseXML()
            for table_name, records in data.items():
                    for record in records:
                        columns = ', '.join(record.keys())
                        values = ', '.join([f"'{value}'" for value in record.values()])
                        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
                        self.cursor.execute(query)

            self.conn.commit()
            NotifyUser("Successfully Uploaded the data",'success')

        except Exception as e:
            self.conn.rollback()
            NotifyUser("Failed to Parse",'warn')
        except:
            self.conn.rollback()
            NotifyUser("Unable to Insert Data",'warn')
            

    def UpdateBook(self, filename):
        try:
            self.dataParser.InitParser(filename)
            data = self.dataParser.ParseXML()
            for book in data['Books']:
                book_id = book['BookID']
                new_quantity = book['Quantity']
                query = f"UPDATE Books SET Quantity = {new_quantity} WHERE BookID = {book_id};"
                self.cursor.execute(query)


            self.conn.commit()
            NotifyUser("Successfully Updated the data",'success')
        except Exception as e:
            self.conn.rollback()
            print(e)
            NotifyUser("Failed to Parse",'warn')
        except:
            self.conn.rollback()
            NotifyUser("Unable to Update Data",'warn')

    def DeleteCartEntry(self, cartID):
        try:
            query = f"DELETE FROM Carts WHERE CartID = {cartID};"
            self.cursor.execute(query)

            self.conn.commit()
            NotifyUser("Deleted the Cart item",'success')

        except Exception as e:
            self.conn.rollback()
            print(e)
            NotifyUser("Failed to delete the items",'warn')

    def CartID(self):
        try:
            self.cursor.execute("SELECT CartID from carts")
            return [i['CartID'] for i in self.cursor.fetchall()]
        except:
            NotifyUser("Failed to fetch cart details",'warn')
            return []

    def CloseConnection(self):
        self.cursor.close()
        self.conn.close()


class XMLParser:
    def __init__(self):
        self.xml_tree = None

    def InitParser(self, filePath):
        self.xml_tree = ET.parse(filePath)

    def ParseXML(self):
        xml_root = self.xml_tree.getroot()

        data = {}

        for child_element in xml_root:
            data[child_element.tag] = []
            for Entry in child_element:
                entry = {}
                for attributes in Entry:
                    entry[attributes.tag] = attributes.text
                data[child_element.tag].append(entry)

        return data




def ClearMessage(message, delay):
    print("Here", flush=True)
    time.sleep(delay)
    print("Deleted", flush=True)
    message.empty()


def NotifyUser(message, _type):
    msg = None
    if _type == "warn":
        msg = st.warning(message)
    elif _type == "success":
        msg = st.success(message)


def UploadFile(file,_type):
    if not file:
        NotifyUser("No File Uploaded", "warn")
        return
    if('db' in st.session_state):
        db = st.session_state.db
        if(_type == 'insert'):
            db.InsertData(file)
        else:
            db.UpdateBook(file)
    else:
        NotifyUser("Unable to connect to database", "warn")


def InsertDataUIHandler():
    file = st.file_uploader("Upload XML", type=["xml"])
    st.button("Upload", on_click=UploadFile, args=(file, "insert"))
    pass


def TableDisplayUIHanlder():
    tabels = ['Books','Users','Carts']
    if('db' in st.session_state):
        db = st.session_state.db
        for i in tabels:
            db.ViewTables(i)

    else:
        NotifyUser("Unable To Connect to Database")
        return
    pass


def UpdateUIHandler():
    file = st.file_uploader("Upload XML", type=["xml"])
    st.session_state.db.ViewTables('Books')
    st.button("Upload", on_click=UploadFile, args=(file, "update"))
    pass


def HandleDelete(cart_id,data):
    if cart_id not in data:
        NotifyUser("Invalid ID",'warn')
        return
    st.session_state.db.DeleteCartEntry(cart_id)
    

def DeleteUIHandler():
    data = st.session_state.db.CartID()
    print(data)
    cart_id = st.number_input("Enter CartID",min_value=min(data),max_value=max(data),step=1)
    st.session_state.db.ViewTables('Carts')
    st.button('Delete',on_click=HandleDelete,args=(cart_id,data))

if __name__ == "__main__":
    if "db" not in st.session_state:
        st.session_state.db = Database(
            {
                "host": "localhost",
                "user": "root",
                "password": "12345",
                "database": "OnlineBookstore",
            }
        )


    st.markdown(
        f"""<div style="text-align: center; font-size: 36px; font-weight:semi-bold;">Online Book Store Management</div>""",
        unsafe_allow_html=True,
    )
    options = st.selectbox(
        label="What you want to do",
        options=("", "Insert XMl file", "View All tables", "Update", "Delete"),
        index=0,
    )
    if options == "Insert XMl file":
        InsertDataUIHandler()
    elif options == "View All tables":
        TableDisplayUIHanlder()
    elif options == "Update":
        UpdateUIHandler()
    elif options=='Delete':
        DeleteUIHandler()
