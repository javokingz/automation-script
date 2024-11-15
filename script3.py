import boto3
import json

# Configura el cliente de ELBv2 (Elastic Load Balancing v2)
elbv2_client = boto3.client('elbv2')

# Configura el cliente de EC2
ec2_client = boto3.client('ec2')

# Obtiene todos los Application Load Balancers (ALB)
albs_response = elbv2_client.describe_load_balancers()

# Inicializa un diccionario para almacenar los datos
data = {"ALBs": []}

# Itera a través de los ALB
for alb in albs_response['LoadBalancers']:
    alb_name = alb['LoadBalancerName']
    alb_arn = alb['LoadBalancerArn']

    # Obtiene las instancias asociadas al ALB
    targets_response = elbv2_client.describe_target_health(TargetGroupArn=alb_arn)

    instances = []

    for target in targets_response['TargetHealthDescriptions']:
        instance_id = target['Target']['Id']
        instances.append({"Instance ID": instance_id})

    alb_data = {"ALB Name": alb_name, "Instances": instances}
    data["ALBs"].append(alb_data)

# Guarda los datos en un archivo JSON
with open('alb_instances.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)

print("Datos de instancias de EC2 conectadas a ALBs exportados a alb_instances.json")
