from diagrams import Diagram, Cluster, Edge
from diagrams.aws.analytics import Glue, Redshift
from diagrams.aws.storage import S3
from diagrams.aws.compute import Lambda, ECS
from diagrams.aws.management import Cloudwatch, CloudwatchAlarm
from diagrams.aws.integration import SNS
from diagrams.aws.general import General

with Diagram("Metadata-Driven Batch Data Platform with Monitoring", show=True, direction="LR"):
    
    # Data Sources
    source = General("""Data Sources:
    DB / Files / APIs""")
    
    # Main pipeline components
    ingestion = Glue("Glue Batch Pipeline")
    raw_storage = S3("Landing Zone (S3)")
    metadata = Lambda("Extract Metadata")
    schema = Glue("""Schema
    Validation""")
    format_conv = Glue("""Format Conversion
    (Parquet/Delta)""")
    dq = ECS("DQ Checks")
    quarantine = S3("Quarantine Zone")
    modeling = Glue("Modeling & Business Logic")
    redshift = Redshift("Analytics & Reporting")
    monitoring_lambda = Lambda("Monitoring & Lineage")
    metadata_log = S3("Metadata Store (S3)")
    
    # Monitoring & Alerting cluster
    with Cluster("Monitoring & Alerting"):
        cloudwatch = Cloudwatch("CloudWatch Metrics")
        alarms = CloudwatchAlarm("Pipeline Alarms")
        sns_alerts = SNS("Alert Notifications")
        dashboard = Cloudwatch("Pipeline Dashboard")
    
    # Main data flow
    source >> ingestion >> raw_storage
    ingestion >> metadata
    raw_storage >> schema >> format_conv >> dq
    dq >> [quarantine, modeling]
    modeling >> redshift
    metadata >> monitoring_lambda >> metadata_log
    
    # Monitoring flows (dotted lines to show monitoring relationships)
    ingestion >> Edge(style="dotted", color="orange") >> cloudwatch
    schema >> Edge(style="dotted", color="orange") >> cloudwatch
    format_conv >> Edge(style="dotted", color="orange") >> cloudwatch
    dq >> Edge(style="dotted", color="orange") >> cloudwatch
    modeling >> Edge(style="dotted", color="orange") >> cloudwatch
    metadata >> Edge(style="dotted", color="orange") >> cloudwatch
    monitoring_lambda >> Edge(style="dotted", color="orange") >> cloudwatch
    redshift >> Edge(style="dotted", color="orange") >> cloudwatch
    
    # Alert flow
    cloudwatch >> alarms >> sns_alerts
    cloudwatch >> dashboard