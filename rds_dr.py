import boto3

# Establecer conexión a AWS
session = boto3.Session(profile_name='your_aws_profile')
rds = session.client('rds')

# Obtener la lista de bases de datos
databases = rds.describe_db_instances()

# Iterar a través de las bases de datos y verificar la información de recuperación
problem_databases = []
for db in databases['DBInstances']:
    if 'DeletionProtection' not in db or not db['DeletionProtection']:
        problem_databases.append(db['DBInstanceIdentifier'])
    elif 'BackupRetentionPeriod' not in db or db['BackupRetentionPeriod'] == 0:
        problem_databases.append(db['DBInstanceIdentifier'])
    elif 'MultiAZ' not in db or not db['MultiAZ']:
        problem_databases.append(db['DBInstanceIdentifier'])

# Imprimir los resultados
if problem_databases:
    print("Las siguientes bases de datos tienen problemas con la información de recuperación:")
    for db in problem_databases:
        print(f"- {db}")
else:
    print("Todas las bases de datos tienen la información de recuperación definida.")