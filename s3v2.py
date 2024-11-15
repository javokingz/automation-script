import boto3
import pandas as pd
import argparse
from datetime import datetime

def analyze_s3_buckets(profile_name=None):
    try:
        # Crear una sesión de AWS usando el perfil especificado
        session = boto3.Session(profile_name=profile_name)
        
        # Configura el cliente de S3 usando la sesión
        s3_client = session.client('s3')
        
        print(f"Conectado usando el perfil: {profile_name}")
        
        # Obtiene una lista de todos los buckets de S3 en la cuenta
        buckets = s3_client.list_buckets()
        
        # Inicializa una lista para almacenar los datos de los buckets
        bucket_data = []
        
        # Itera a través de los buckets
        total_buckets = len(buckets['Buckets'])
        print(f"Analizando {total_buckets} buckets...")
        
        for index, bucket in enumerate(buckets['Buckets'], 1):
            bucket_name = bucket['Name']
            print(f"Procesando bucket {index}/{total_buckets}: {bucket_name}")
            
            try:
                # Obtiene información sobre el versionamiento del bucket
                versioning_response = s3_client.get_bucket_versioning(Bucket=bucket_name)
                versioning_status = versioning_response.get('Status', 'Disabled')
                
                # Obtiene el tamaño del almacenamiento en megabytes
                bucket_size_response = s3_client.list_objects_v2(Bucket=bucket_name)
                total_size_mb = sum(
                    obj['Size'] / (1024 ** 2) 
                    for obj in bucket_size_response.get('Contents', [])
                )
                
                # Obtiene información sobre la encriptación del bucket
                try:
                    bucket_policy_response = s3_client.get_bucket_encryption(Bucket=bucket_name)
                    is_encrypted = 'ServerSideEncryptionConfiguration' in bucket_policy_response
                except s3_client.exceptions.ClientError:
                    is_encrypted = False
                
                # Obtiene la fecha de creación
                creation_date = bucket['CreationDate'].strftime('%Y-%m-%d %H:%M:%S')
                
                bucket_data.append({
                    'Bucket Name': bucket_name,
                    'Creation Date': creation_date,
                    'Versioning Enabled': versioning_status,
                    'Storage Size (MB)': round(total_size_mb, 2),
                    'Encrypted': is_encrypted
                })
                
            except Exception as e:
                print(f"Error procesando bucket {bucket_name}: {str(e)}")
                bucket_data.append({
                    'Bucket Name': bucket_name,
                    'Creation Date': bucket['CreationDate'].strftime('%Y-%m-%d %H:%M:%S'),
                    'Versioning Enabled': 'Error',
                    'Storage Size (MB)': 'Error',
                    'Encrypted': 'Error'
                })
        
        # Convierte la lista en un DataFrame de pandas
        df = pd.DataFrame(bucket_data)
        
        # Genera un nombre de archivo con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'buckets_s3_{profile_name}_{timestamp}.xlsx'
        
        # Exporta el DataFrame a un archivo Excel
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"\nDatos de buckets de S3 exportados a {filename}")
        
        return df
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(description='Analizar buckets de S3 con un perfil AWS específico')
    parser.add_argument('--profile', type=str, required=True, help='Nombre del perfil AWS a utilizar')
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Ejecutar el análisis
    analyze_s3_buckets(args.profile)