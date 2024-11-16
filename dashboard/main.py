import streamlit as st
import boto3
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

def get_aws_profiles():
    """Obtiene los perfiles AWS configurados"""
    import configparser
    import os
    config = configparser.ConfigParser()
    config.read(os.path.expanduser("~/.aws/credentials"))
    return config.sections()

def get_ec2_instances(session):
    """Obtiene información de las instancias EC2"""
    ec2_client = session.client('ec2')
    cloudwatch = session.client('cloudwatch')
    pricing_client = session.client('pricing', region_name='us-east-1')
    
    instances = []
    response = ec2_client.describe_instances()
    
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            
            # Obtener métricas de CloudWatch
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=1)
            
            cpu_stats = cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Average']
            )
            
            # Calcular CPU promedio
            cpu_avg = sum(point['Average'] for point in cpu_stats['Datapoints']) / len(cpu_stats['Datapoints']) if cpu_stats['Datapoints'] else 0
            
            # Obtener información de precios
            try:
                pricing_response = pricing_client.get_products(
                    ServiceCode='AmazonEC2',
                    Filters=[
                        {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance['InstanceType']},
                        {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
                        {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'},
                        {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
                    ]
                )
                price_details = pricing_response['PriceList'][0]
                hourly_cost = float(list(eval(price_details)['terms']['OnDemand'].values())[0]['priceDimensions'].values()[0]['pricePerUnit']['USD'])
            except:
                hourly_cost = 0
            
            instances.append({
                'Instance ID': instance_id,
                'Type': instance['InstanceType'],
                'State': instance['State']['Name'],
                'CPU Utilization (%)': round(cpu_avg, 2),
                'Hourly Cost ($)': hourly_cost,
                'Monthly Cost Estimate ($)': round(hourly_cost * 24 * 30, 2)
            })
    
    return pd.DataFrame(instances)

def get_s3_buckets(session):
    """Obtiene información de los buckets S3"""
    s3_client = session.client('s3')
    cloudwatch = session.client('cloudwatch')
    
    buckets = []
    response = s3_client.list_buckets()
    
    for bucket in response['Buckets']:
        bucket_name = bucket['Name']
        
        # Obtener tamaño del bucket
        try:
            size_response = s3_client.list_objects_v2(Bucket=bucket_name)
            total_size_gb = sum(obj['Size'] for obj in size_response.get('Contents', [])) / (1024**3)
        except:
            total_size_gb = 0
        
        # Verificar encriptación
        try:
            encryption = s3_client.get_bucket_encryption(Bucket=bucket_name)
            is_encrypted = True
        except:
            is_encrypted = False
        
        # Calcular costo estimado (S3 Standard = $0.023 por GB)
        estimated_cost = total_size_gb * 0.023
        
        buckets.append({
            'Bucket Name': bucket_name,
            'Size (GB)': round(total_size_gb, 2),
            'Encrypted': is_encrypted,
            'Monthly Cost Estimate ($)': round(estimated_cost, 2)
        })
    
    return pd.DataFrame(buckets)

def main():
    st.set_page_config(page_title="AWS Resource Dashboard", layout="wide")
    
    # Título y descripción
    st.title("AWS Resource Dashboard")
    st.markdown("Monitor your AWS resources across different profiles")
    
    # Selector de perfil
    profiles = get_aws_profiles()
    selected_profile = st.sidebar.selectbox("Select AWS Profile", profiles)
    
    try:
        # Crear sesión de AWS
        session = boto3.Session(profile_name=selected_profile)
        st.sidebar.success(f"Connected to profile: {selected_profile}")
        
        # Selector de servicio
        service = st.sidebar.radio("Select AWS Service", ["EC2 Instances", "S3 Buckets"])
        
        if service == "EC2 Instances":
            st.header("EC2 Instances")
            
            # Obtener y mostrar datos de EC2
            with st.spinner("Loading EC2 data..."):
                ec2_df = get_ec2_instances(session)
                
                # Métricas principales
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Instances", len(ec2_df))
                with col2:
                    st.metric("Running Instances", len(ec2_df[ec2_df['State'] == 'running']))
                with col3:
                    st.metric("Total Monthly Cost ($)", round(ec2_df['Monthly Cost Estimate ($)'].sum(), 2))
                
                # Gráfico de utilización de CPU
                fig_cpu = px.bar(ec2_df, 
                                x='Instance ID', 
                                y='CPU Utilization (%)',
                                title='CPU Utilization by Instance')
                st.plotly_chart(fig_cpu)
                
                # Gráfico de costos
                fig_cost = px.pie(ec2_df, 
                                values='Monthly Cost Estimate ($)',
                                names='Instance ID',
                                title='Monthly Cost Distribution')
                st.plotly_chart(fig_cost)
                
                # Tabla detallada
                st.subheader("Instance Details")
                st.dataframe(ec2_df)
        
        else:  # S3 Buckets
            st.header("S3 Buckets")
            
            # Obtener y mostrar datos de S3
            with st.spinner("Loading S3 data..."):
                s3_df = get_s3_buckets(session)
                
                # Métricas principales
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Buckets", len(s3_df))
                with col2:
                    st.metric("Encrypted Buckets", len(s3_df[s3_df['Encrypted']]))
                with col3:
                    st.metric("Total Monthly Cost ($)", round(s3_df['Monthly Cost Estimate ($)'].sum(), 2))
                
                # Gráfico de tamaño de buckets
                fig_size = px.bar(s3_df,
                                x='Bucket Name',
                                y='Size (GB)',
                                title='Bucket Sizes')
                st.plotly_chart(fig_size)
                
                # Gráfico de costos
                fig_cost = px.pie(s3_df,
                                values='Monthly Cost Estimate ($)',
                                names='Bucket Name',
                                title='Monthly Cost Distribution')
                st.plotly_chart(fig_cost)
                
                # Tabla detallada
                st.subheader("Bucket Details")
                st.dataframe(s3_df)
    
    except Exception as e:
        st.error(f"Error connecting to AWS: {str(e)}")

if __name__ == "__main__":
    main()