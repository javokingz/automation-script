import boto3
import pandas as pd

# Configura el cliente de EC2
ec2_client = boto3.client('ec2')

# Obtiene todas las instancias de EC2
response = ec2_client.describe_instances()

# Inicializa una lista para almacenar los datos de las instancias
instancias_data = []

# Itera a través de las reservas (reservations) para obtener las instancias
for reservation in response['Reservations']:
    for instance in reservation['Instances']:
        instancia = {
            'ID de Instancia': instance['InstanceId'],
            'Tipo de Instancia': instance['InstanceType'],
            'Estado': instance['State']['Name'],
            'Dirección IP pública': instance.get('PublicIpAddress', 'N/A'),
            'Dirección IP privada': instance.get('PrivateIpAddress', 'N/A'),
            'vpc_id': instance['VpcId'],
            'subnet_id' : instance['SubnetId']
            
        }
        instancias_data.append(instancia)

# Convierte la lista en un DataFrame de pandas
df = pd.DataFrame(instancias_data)

# Exporta el DataFrame a un archivo Excel
df.to_excel('instancias_ec2.xlsx', index=False, engine='openpyxl')
print("Datos de instancias de EC2 exportados a instancias_ec2.xlsx")
