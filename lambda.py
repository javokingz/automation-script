import boto3

# Configura el cliente de EC2
ec2_client = boto3.client('ec2')

# ID de la instancia que deseas obtener
instance_id = 'tu-instance-id-aqui'

# Obtiene información de la instancia
response = ec2_client.describe_instances(InstanceIds=[instance_id])

# Extrae las etiquetas de la instancia
tags = response['Reservations'][0]['Instances'][0]['Tags']

# Busca la etiqueta con clave "Name"
instance_name = None
for tag in tags:
    if tag['Key'] == 'Name':
        instance_name = tag['Value']
        break

# Imprime el nombre de la instancia si se encontró
if instance_name:
    print(f"El nombre de la instancia {instance_id} es: {instance_name}")
else:
    print(f"No se encontró un nombre para la instancia {instance_id}")
