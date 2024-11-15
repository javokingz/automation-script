import boto3
import pandas as pd

def obtener_subnets():
    # Configura el cliente de EC2
    ec2_client = boto3.client('ec2')

    # Obtiene una lista de todas las subnets en la cuenta
    response = ec2_client.describe_subnets()

    # Inicializa una lista para almacenar los datos de las subnets
    subnet_data = []

    # Itera a través de las subnets
    for subnet in response['Subnets']:
        subnet_id = subnet['SubnetId']
        vpc_id = subnet['VpcId']

        # Comprueba si la subnet tiene un Internet Gateway asociado
        route_tables_response = ec2_client.describe_route_tables(Filters=[{'Name': 'association.subnet-id', 'Values': [subnet_id]}])
        has_internet_gateway = any(route_table.get('Routes') and any(route['GatewayId'] for route in route_table['Routes']) for route_table in route_tables_response['RouteTables'])

        subnet_data.append({
            'Subnet ID': subnet_id,
            'VPC ID': vpc_id,
            'Tiene Internet Gateway': has_internet_gateway
        })

    # Convierte la lista en un DataFrame de pandas
    df = pd.DataFrame(subnet_data)

    # Exporta el DataFrame a un archivo Excel
    df.to_excel('subnets.xlsx', index=False, engine='openpyxl')

    print("Datos de subnets exportados a subnets.xlsx")

# Llama a la función para obtener y exportar los datos
obtener_subnets()
