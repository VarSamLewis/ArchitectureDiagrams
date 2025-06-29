from diagrams import Diagram, Cluster, Edge, Node
from diagrams.gcp.compute import Run, Functions
from diagrams.gcp.devtools import Build
from diagrams.gcp.ml import AIPlatform
from diagrams.gcp.storage import GCS
from diagrams.gcp.analytics import PubSub, BigQuery
from diagrams.gcp.operations import Logging, Monitoring
from diagrams.custom import Custom

with Diagram("GCP ML Pipeline Architecture with Monitoring", show=True, direction="LR"):

    with Cluster("Ingestion"):
        trigger = Build("Cloud Build Trigger")
        api = Run("tripdata_api (Cloud Run)")
        landing = GCS("Raw GCS Bucket")

    with Cluster("Data Warehouse"):
        raw_events = BigQuery("raw_events (Staging)")
        cleaned_events = BigQuery("cleaned_events (Validated)")
        training_data = BigQuery("training_features (Aggregated)")
        predictions = BigQuery("predictions_event_level")

    with Cluster("Training Pipeline"):
        scheduler = Functions("Trigger (Scheduler)")
        training = AIPlatform("Vertex AI Custom Job")
        model_bucket = GCS("Model Artifact (GCS)")
        registry = BigQuery("Model Registry (BQ)")

    with Cluster("Inference"):
        pubsub = PubSub("Pub/Sub: Events to Inference")
        inference_api = Run("inference_api (Cloud Run)")
        prediction_store = BigQuery("Prediction Results")

    with Cluster("Monitoring & Metadata"):
        logs = Logging("Cloud Logging")
        monitor = Monitoring("Model Monitoring")
        metadata_log = GCS("Training Metadata")

    # Colored ingestion flow
    trigger >> Edge(color="blue") >> api
    api >> Edge(color="blue") >> landing
    landing >> Edge(color="blue") >> raw_events >> cleaned_events >> training_data

    # Colored training flow
    scheduler >> Edge(color="green") >> training
    training >> Edge(color="green") >> model_bucket >> Edge(color="green") >> registry
    training >> Edge(color="green") >> metadata_log
    training >> Edge(style="green") >> metadata_log

    # Colored inference flow
    cleaned_events >> Edge(color="red") >> pubsub >> Edge(color="red") >> inference_api
    inference_api >> Edge(color="red") >> prediction_store
    registry >> Edge(style="red") >> monitor

    # Monitoring flows
    [api, training, inference_api] >> Edge(style="dotted") >> logs
    [training, inference_api] >> Edge(style="dotted") >> monitor
    
    
