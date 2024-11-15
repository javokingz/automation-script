import boto3

# Configura el cliente de EC2
ec2_client = boto3.client('ec2')

# Obtiene todas las instancias de EC2
response = ec2_client.describe_instances()

# Itera a través de las reservas (reservations) para obtener las instancias
for reservation in response['Reservations']:
    for instance in reservation['Instances']:
        # Imprime información relevante sobre cada instancia
        print("ID de Instancia:", instance['InstanceId'])
        print("Tipo de Instancia:", instance['InstanceType'])
        print("Estado:", instance['State']['Name'])
        print("Dirección IP pública:", instance.get('PublicIpAddress', 'N/A'))
        print("Dirección IP privada:", instance.get('PrivateIpAddress', 'N/A'))
        print("------------------------------------------")