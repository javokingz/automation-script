import flet as ft
import boto3
import configparser
import os

class AWSResourceViewer:
    def __init__(self):
        self.profiles = self._get_aws_profiles()
        self.selected_profile = None
        self.selected_service = None
        self.session = None

    def _get_aws_profiles(self):
        config = configparser.ConfigParser()
        config.read(os.path.expanduser("~/.aws/credentials"))
        return config.sections()

    def main(self, page: ft.Page):
        page.title = "AWS Resource Viewer"
        page.window_width = 800
        page.window_height = 600
        page.padding = 20

        # Contenedor principal
        main_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("AWS Resource Viewer", size=24, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                ]
            ),
            padding=10
        )

        # Dropdown para seleccionar perfil
        profile_dropdown = ft.Dropdown(
            label="Seleccionar Perfil AWS",
            options=[ft.dropdown.Option(profile) for profile in self.profiles],
            width=300
        )

        # Dropdown para seleccionar servicio
        service_dropdown = ft.Dropdown(
            label="Seleccionar Servicio AWS",
            options=[
                ft.dropdown.Option("EC2"),
                ft.dropdown.Option("S3"),
                ft.dropdown.Option("VPC"),
                ft.dropdown.Option("Subnets")
            ],
            width=300
        )

        # Área de resultados
        results_text = ft.TextField(
            multiline=True,
            read_only=True,
            width=700,
            height=400,
            border=ft.InputBorder.OUTLINE
        )

        def update_session(e):
            self.selected_profile = profile_dropdown.value
            try:
                self.session = boto3.Session(profile_name=self.selected_profile)
                results_text.value = f"Conectado al perfil: {self.selected_profile}"
                page.update()
            except Exception as err:
                results_text.value = f"Error al conectar con el perfil: {str(err)}"
                page.update()

        def get_resources(e):
            if not self.session:
                results_text.value = "Por favor, seleccione primero un perfil AWS"
                page.update()
                return

            service = service_dropdown.value
            try:
                if service == "EC2":
                    ec2 = self.session.client('ec2')
                    instances = ec2.describe_instances()
                    output = []
                    for reservation in instances['Reservations']:
                        for instance in reservation['Instances']:
                            output.append(f"ID: {instance['InstanceId']}")
                            output.append(f"Tipo: {instance['InstanceType']}")
                            output.append(f"Estado: {instance['State']['Name']}")
                            output.append("-" * 50)
                    results_text.value = "\n".join(output)

                elif service == "S3":
                    s3 = self.session.client('s3')
                    buckets = s3.list_buckets()
                    output = ["Buckets S3:"]
                    for bucket in buckets['Buckets']:
                        output.append(f"- {bucket['Name']}")
                    results_text.value = "\n".join(output)

                elif service == "VPC":
                    ec2 = self.session.client('ec2')
                    vpcs = ec2.describe_vpcs()
                    output = ["VPCs:"]
                    for vpc in vpcs['Vpcs']:
                        output.append(f"ID: {vpc['VpcId']}")
                        output.append(f"CIDR: {vpc['CidrBlock']}")
                        output.append("-" * 50)
                    results_text.value = "\n".join(output)

                elif service == "Subnets":
                    ec2 = self.session.client('ec2')
                    subnets = ec2.describe_subnets()
                    output = ["Subnets:"]
                    for subnet in subnets['Subnets']:
                        output.append(f"ID: {subnet['SubnetId']}")
                        output.append(f"VPC: {subnet['VpcId']}")
                        output.append(f"CIDR: {subnet['CidrBlock']}")
                        output.append("-" * 50)
                    results_text.value = "\n".join(output)

            except Exception as err:
                results_text.value = f"Error al obtener recursos: {str(err)}"

            page.update()

        # Botones
        connect_button = ft.ElevatedButton(
            text="Conectar",
            on_click=update_session
        )

        get_resources_button = ft.ElevatedButton(
            text="Obtener Recursos",
            on_click=get_resources
        )

        # Añadir controles a la interfaz
        main_container.content.controls.extend([
            profile_dropdown,
            connect_button,
            ft.Divider(),
            service_dropdown,
            get_resources_button,
            ft.Divider(),
            results_text
        ])

        page.add(main_container)

if __name__ == "__main__":
    app = AWSResourceViewer()
    ft.app(target=app.main)