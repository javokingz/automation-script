import boto3
import pandas as pd

# Establecer conexión a AWS
session = boto3.Session(profile_name='your_aws_profile')
rds = session.client('rds')

# Obtener la lista de bases de datos
databases = rds.describe_db_instances()

# Crear una lista para almacenar los datos
data = []

# Iterar a través de las bases de datos y recopilar la información
for db in databases['DBInstances']:
    db_name = db['DBInstanceIdentifier']
    db_tags = rds.list_tags_for_resource(ResourceName=db['DBInstanceArn'])['TagList']
    
    # Agregar los datos a la lista
    data.append({
        'DB Name': db_name,
        'Tags': str(db_tags)
    })

# Crear un DataFrame de Pandas con los datos
df = pd.DataFrame(data)

# Guardar el DataFrame en un archivo XLSX
df.to_excel('database_tags.xlsx', index=False)

print("La información se ha guardado en el archivo 'database_tags.xlsx'.")