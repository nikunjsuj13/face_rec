import sqlite3

conn=sqlite3.connect('face_rec.db')
cursor=conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS registered_faces (name TEXT, image BLOB) """)
cursor.execute("""
DELETE FROM unknown_faces""")
cursor.execute("""
DELETE FROM detected_faces""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS unknown_faces (time TEXT, image BLOB) """)
cursor.execute("""
CREATE TABLE IF NOT EXISTS detected_faces (name TEXT, image BLOB) """)
conn.commit()
cursor.close()
conn.close()
