import boto3
import pandas as pd

# Configura el cliente de RDS
rds_client = boto3.client('rds')

# Obtiene una lista de todas las bases de datos RDS en la cuenta
response = rds_client.describe_db_instances()

# Inicializa una lista para almacenar los datos de las bases de datos
database_data = []

# Itera a través de las bases de datos
for db_instance in response['DBInstances']:
    vpc_id = db_instance['DBSubnetGroup']['VpcId']
    subnet_id = db_instance['DBSubnetGroup']['Subnets'][0]['SubnetIdentifier']
    engine = db_instance['Engine']
    encrypted = db_instance['StorageEncrypted']

    database_data.append({
        'Nombre del RDS': db_instance['DBInstanceIdentifier'],
        'VPC': vpc_id,
        'Subnet': subnet_id,
        'Motor de Base de Datos': engine,
        'Encriptado': encrypted
    })

# Convierte la lista en un DataFrame de pandas
df = pd.DataFrame(database_data)

# Exporta el DataFrame a un archivo Excel
df.to_excel('bases_de_datos_rds.xlsx', index=False, engine='openpyxl')

print("Datos de bases de datos RDS exportados a bases_de_datos_rds.xlsx")
