import joblib
from pathlib import Path

class ModelLoader:
    def __init__(self):
        self.models_dir = Path(__file__).parent / "trained_models"
        self.models = {}
        
    def load_model(self, model_name: str):
        """Load a model from the models directory"""
        if model_name in self.models:
            return self.models[model_name]
            
        model_path = self.models_dir / f"{model_name}.joblib"
        if not model_path.exists():
            raise FileNotFoundError(f"Model {model_name} not found at {model_path}")
            
        try:
            model = joblib.load(model_path)
            self.models[model_name] = model
            return model
        except Exception as e:
            raise Exception(f"Error loading model {model_name}: {str(e)}")