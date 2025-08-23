import torch
import torchvision.transforms as transforms
from PIL import Image
import io

# Placeholder for a pre-trained model (e.g., ResNet18)
# In a real scenario, you would load your fine-tuned model here.
# For demonstration, we'll simulate a simple classification.

def load_model():
    # This is a placeholder. Replace with actual model loading.
    # Example: model = torchvision.models.resnet18(pretrained=False)
    # model.fc = torch.nn.Linear(model.fc.in_features, num_classes)
    # model.load_state_dict(torch.load('path/to/your/model.pth'))
    # model.eval()
    print("Simulating model loading...")
    return True # Simulate a loaded model

# Global model instance (load once)
_model = load_model()

def preprocess_image(image_file):
    # Define transformations for the model
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    
    # Open the image file using PIL
    img = Image.open(io.BytesIO(image_file.read())).convert('RGB')
    return preprocess(img).unsqueeze(0) # Add batch dimension

def analyze_document(document_file):
    """
    Simulates AI analysis of a document.
    Returns a tuple: (analysis_status, extracted_data_dict)
    """
    if not _model:
        return 'REJECTED', {'reason': 'Model not loaded'}

    try:
        # Simulate image preprocessing and model inference
        # input_tensor = preprocess_image(document_file)
        # with torch.no_grad():
        #     output = _model(input_tensor)
        #     # Simulate classification result
        #     _, predicted_idx = torch.max(output, 1)
        #     # Map predicted_idx to a status (e.g., 0: VERIFIED, 1: REJECTED, 2: UNREADABLE)
        
        # For now, simulate based on file size or type for demonstration
        file_size = document_file.size # Access size from InMemoryUploadedFile
        file_name = document_file.name

        if "id_front" in file_name.lower() or "id_back" in file_name.lower():
            if file_size > 100 * 1024: # Simulate a reasonable size for a clear ID
                return 'VERIFIED', {'type': 'ID', 'confidence': 0.95, 'extracted_text': 'Simulated ID text'}
            else:
                return 'UNREADABLE', {'type': 'ID', 'confidence': 0.3, 'reason': 'Simulated low quality'}
        elif "receipt" in file_name.lower():
            if file_size > 50 * 1024:
                return 'VERIFIED', {'type': 'RECEIPT', 'confidence': 0.8, 'extracted_amount': 123.45}
            else:
                return 'UNREADABLE', {'type': 'RECEIPT', 'confidence': 0.2, 'reason': 'Simulated low quality'}
        else:
            return 'PENDING', {'type': 'UNKNOWN', 'confidence': 0.5}

    except Exception as e:
        print(f"Error during document analysis simulation: {e}")
        return 'REJECTED', {'reason': f'Analysis failed: {str(e)}'}
