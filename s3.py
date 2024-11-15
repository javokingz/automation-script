import boto3
import pandas as pd

# Configura el cliente de S3
s3_client = boto3.client('s3')

# Obtiene una lista de todos los buckets de S3 en la cuenta
buckets = s3_client.list_buckets()

# Inicializa una lista para almacenar los datos de los buckets
bucket_data = []

# Itera a través de los buckets
for bucket in buckets['Buckets']:
    bucket_name = bucket['Name']
    
    # Obtiene información sobre el versionamiento del bucket
    versioning_response = s3_client.get_bucket_versioning(Bucket=bucket_name)
    versioning_status = versioning_response.get('Status', 'Disabled')

    # Obtiene el tamaño del almacenamiento en megabytes
    bucket_size_response = s3_client.list_objects_v2(Bucket=bucket_name)
    total_size_mb = sum(obj['Size'] / (1024 ** 2) for obj in bucket_size_response.get('Contents', []))

    # Obtiene información sobre la encriptación del bucket
    bucket_policy_response = s3_client.get_bucket_encryption(Bucket=bucket_name)
    is_encrypted = 'ServerSideEncryptionConfiguration' in bucket_policy_response

    bucket_data.append({
        'Bucket Name': bucket_name,
        'Versioning Enabled': versioning_status,
        'Storage Size (MB)': total_size_mb,
        'Encrypted': is_encrypted
    })

# Convierte la lista en un DataFrame de pandas
df = pd.DataFrame(bucket_data)

# Exporta el DataFrame a un archivo Excel
df.to_excel('buckets_s3.xlsx', index=False, engine='openpyxl')

print("Datos de buckets de S3 exportados a buckets_s3.xlsx")
