from fastapi import APIRouter,Query
from pydantic import BaseModel
import pyodbc
import csv
import io
import os
import pandas as pd
import hashlib
from fastapi.encoders import jsonable_encoder
# import mysql.connector

router = APIRouter(
    prefix='/SQL MIS',
    tags=['Geting Data SQL MIS'],
    responses={404:{
        'message':'Not found'
    }}
)

# Define custom storage path for CSV files
custom_storage_path = "D:/DBTEST/"
# Connection details
server = 'KSSDB'
database = 'MIS'
trusted_connection = 'yes'

# Function to calculate hash of data
def calculate_hash(data):
    hasher = hashlib.md5()
    for row in data:
        for value in row:
            hasher.update(str(value).encode('UTF-8-sig'))
    return hasher.hexdigest()

# Function to update CSV with new data
def update_csv_with_new_data(table_name, new_data, column_names, csv_file_path):
    # Check if CSV file exists
    if os.path.exists(csv_file_path):
        # Read CSV data and compare with new data
        with open(csv_file_path, 'r', newline='', encoding='UTF-8-sig') as csvfile:
            csv_reader = csv.reader(csvfile)
            csv_data = [row for row in csv_reader]
        csv_hash = calculate_hash(csv_data)
        new_hash = calculate_hash(new_data)
        
        if csv_hash != new_hash:
            # Data has changed, delete the existing CSV file
            os.remove(csv_file_path)
        else:
            return
    
    # Create a new CSV file and write data
    with open(csv_file_path, 'w', newline='', encoding='UTF-8-sig') as csvfile:
        csv_writer = csv.writer(csvfile)
        
        # Write the column names as the header
        csv_writer.writerow(column_names)
        
        # Write the data rows
        csv_writer.writerows(new_data)

@router.get("/update_csv/{table_name}")
async def update_csv(table_name: str):
    # Establish SQL Server connection
    connection = pyodbc.connect(
        f'DRIVER=SQL Server;'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'Trusted_Connection={trusted_connection};'
    )
    cursor = connection.cursor()
    
    # Execute SQL query to fetch data from the table
    query = f"SELECT * FROM {table_name}"
    cursor.execute(query)
    
    # Fetch data from the executed query in chunks
    chunk_size = 10000
    chunks = []
    while True:
        rows = cursor.fetchmany(chunk_size)
        if not rows:
            break
        chunks.extend(rows)
    
    # Define CSV file path
    csv_file_path = os.path.join(custom_storage_path, f"{table_name}.csv")

    # Get column names from cursor description
    column_names = [column[0] for column in cursor.description]
    
    # Update CSV with new data
    update_csv_with_new_data(table_name, chunks,column_names, csv_file_path)
   
    
    return {"message": f"CSV updated at {csv_file_path}"}


@router.get("tables")
def get_table():
    connection = pyodbc.connect(
        f'DRIVER=SQL Server;'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'Trusted_Connection={trusted_connection};'
    )
    cursor = connection.cursor()
    tables = [row.table_name for row in cursor.tables(tableType='TABLE')]
     # Save table names to a CSV file
    csv_filename = f"{custom_storage_path}MIS.csv"
    with open(csv_filename, "w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Table Name"])
        csv_writer.writerows([[table_name] for table_name in tables])
    return {"message": f"CSV updated at {csv_filename}"}

@router.get("/relationships")
def get_table():
    connection = pyodbc.connect(
        f'DRIVER=SQL Server;'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'Trusted_Connection={trusted_connection};'
    )
    cursor = connection.cursor()

    tables = [row.table_name for row in cursor.tables(tableType='TABLE')]

    table_relationships = {}

    # Retrieve relationships for each table
    for table in tables:
        relationships = []
        for foreign_key in cursor.foreignKeys(table):
            relationships.append({
                "table": foreign_key[6],
                "column": foreign_key[7]
            })
        table_relationships[table] = relationships

    # Save table relationships to a CSV file
    csv_filename = f"{custom_storage_path}MIS_relationships.csv"
    with open(csv_filename, "w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Table Name", "Related Table", "Related Column"])
        for table, relationships in table_relationships.items():
            for rel in relationships:
                csv_writer.writerow([table, rel["table"], rel["column"]])

    return {"message": f"CSV updated at {csv_filename}"}


@router.get("/update_csv/{table_name}")
async def update_csv(
    table_name: str,
    join_table_name: str = Query(..., description="Name of the table to join with"),
    common_column: str = Query(..., description="Common column for the join"),
    condition_column: str = Query(..., description="Column to apply condition"),
    # condition_value: str = Query(..., description="Value for the condition")
):
    try:
        conn = pyodbc.connect(
            f'DRIVER=SQL Server;'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'Trusted_Connection={trusted_connection};'
        )
        cursor = conn.cursor()
    
        # Define SQL query to join tables and fetch data
        query = f"""
        SELECT t1.*, t2.related_column
        FROM {table_name} t1
        INNER JOIN {join_table_name} t2 ON t1.{common_column} = t2.{common_column}
        """
        cursor.execute(query)
    
        # Fetch data from the executed query in chunks
        chunk_size = 10000
        chunks = []
        while True:
            rows = cursor.fetchmany(chunk_size)
            if not rows:
                break
            chunks.extend(rows)
    
        # Define CSV file path
        csv_file_path = os.path.join(custom_storage_path, f"{table_name}_join.csv")

        # Get column names from cursor description
        column_names = [column[0] for column in cursor.description]
    
        # Update CSV with new data
        update_csv_with_new_data(table_name, chunks, column_names, csv_file_path)
   
        cursor.close()
        conn.close()

        return {"message": f"CSV updated at {csv_file_path}"}
    except Exception as e:
        return {"error": str(e)}

@router.get("/extract_to_csv/{table_name}")
async def extract_to_csv(
    table_name: str,
    batch_size: int = Query(10000, description="Number of rows per batch")
):
    try:
        conn = pyodbc.connect(
            f'DRIVER=SQL Server;'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'Trusted_Connection={trusted_connection};'
        )
        cursor = conn.cursor()
    
        # Define SQL query to fetch data from the table
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
    
        # Define CSV file path
        csv_file_path = os.path.join(custom_storage_path, f"{table_name}_extracted.csv")
        
        # Define an asynchronous generator to stream data
        async def generate_csv_data():
            while True:
                rows = cursor.fetchmany(batch_size)
                if not rows:
                    break
                csv_buffer = io.StringIO()
                csv_writer = csv.writer(csv_buffer)
                for row in rows:
                    csv_writer.writerow(row)
                yield csv_buffer.getvalue()
        
        # Stream data and write to CSV
        with open(csv_file_path, "w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            
            # Write header row
            header = [column[0] for column in cursor.description]
            csv_writer.writerow(header)
            
            # Stream data and write to CSV using the asynchronous generator
            async for chunk in generate_csv_data():
                csv_file.write(chunk)
    
        cursor.close()
        conn.close()

        return {"message": f"Data extracted and saved to {csv_file_path}"}
    except Exception as e:
        return {"error": str(e)}


@router.get("/extract_to_csv/{table_name}")
async def extract_to_csv(
    table_name: str,
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)")
):
    try:
        conn = pyodbc.connect(
            f'DRIVER=SQL Server;'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'Trusted_Connection={trusted_connection};'
        )
        cursor = conn.cursor()
    
        # Define SQL query to fetch data from the table within the specified date range
        query = f"SELECT * FROM {table_name} WHERE DateColumn BETWEEN '{start_date}' AND '{end_date}'"
        cursor.execute(query)
    
        # Define CSV file path with start and end dates in the file name
        csv_file_name = f"{table_name}_{start_date}_{end_date}_extracted.csv"
        csv_file_path = os.path.join(custom_storage_path, csv_file_name)
        
        # Stream data and write to CSV
        with open(csv_file_path, "w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            
            # Write header row
            header = [column[0] for column in cursor.description]
            csv_writer.writerow(header)
            
            # Fetch all rows and write to CSV
            rows = cursor.fetchall()
            for row in rows:
                csv_writer.writerow(row)
    
        cursor.close()
        conn.close()

        return {"message": f"Data extracted and saved to {csv_file_path}"}
    except Exception as e:
        return {"error": str(e)}
