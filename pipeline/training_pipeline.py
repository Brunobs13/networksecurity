from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.pipeline.training_pipeline import TrainingPipeline
import sys


if __name__ == "__main__":
    try:
        pipeline = TrainingPipeline()
        pipeline.run_pipeline()
        print("Training pipeline completed.")
    except Exception as e:
        raise NetworkSecurityException(e, sys)
