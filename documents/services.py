import torch
import torchvision.transforms as transforms
import torchvision.models as models # Import models
from PIL import Image
import io

# Global model instance (load once)
_model = None # Initialize as None

def load_model():
    global _model
    if _model is None:
        print("Loading pre-trained ResNet18 model...")
        # Load a pre-trained ResNet18 model
        _model = models.resnet18(pretrained=True)
        _model.eval() # Set the model to evaluation mode
        print("ResNet18 model loaded.")
    return _model

# Load the model when the module is imported
load_model()

def preprocess_image(image_file):
    # Define transformations for the model
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    
    # Open the image file using PIL
    # image_file is a Django InMemoryUploadedFile, it needs to be read
    img = Image.open(io.BytesIO(image_file.read())).convert('RGB')
    return preprocess(img).unsqueeze(0) # Add batch dimension

def analyze_document(document_file):
    """
    Performs actual (basic) AI analysis of a document using a pre-trained model.
    Returns a tuple: (analysis_status, extracted_data_dict)
    """
    if _model is None:
        return 'REJECTED', {'reason': 'AI model not loaded'}

    try:
        input_tensor = preprocess_image(document_file)
        
        with torch.no_grad():
            output = _model(input_tensor)
            probabilities = torch.nn.functional.softmax(output[0], dim=0)
            
            # Get the top prediction and its confidence
            confidence, predicted_idx = torch.max(probabilities, 0)
            confidence = confidence.item() # Convert tensor to Python float

            # Simulate status based on confidence
            if confidence > 0.7: # High confidence, likely readable
                status = 'VERIFIED'
                reason = 'High confidence classification'
            elif confidence > 0.4: # Medium confidence, might be readable but uncertain
                status = 'PENDING'
                reason = 'Medium confidence, requires review'
            else: # Low confidence, likely unreadable or not what's expected
                status = 'UNREADABLE'
                reason = 'Low confidence classification'

            # For a real ID/receipt classification, you'd map predicted_idx to your custom classes
            # For this MVP, we're using confidence as a proxy for "validity/readability"
            
            return status, {'confidence': confidence, 'reason': reason}

    except Exception as e:
        print(f"Error during document analysis: {e}")
        return 'REJECTED', {'reason': f'Analysis failed: {str(e)}'}
