import pandas as pd
import sqlite3
#this is the page where i imported pandas & sqlite 3
csv_file_path = "patient dataset kaggle.csv"
df = pd.read_csv(csv_file_path)

database_path = "patients.db" #connecting the code to my database folder
conn = sqlite3.connect(database_path)

table_name = "patients" #defining tablename

df.to_sql(table_name, conn, if_exists="replace", index=False)

print(f"Successfully uploaded the data'{table_name}' table in the database at {database_path}")

conn.close()


