import torch
import torch.nn as nn
import torchvision.models as models

class OptimizedChestXRayResNet(nn.Module):
    def __init__(self, num_classes=14):  
        super(OptimizedChestXRayResNet, self).__init__()
        self.model = models.resnet50(pretrained=False)  
        in_features = self.model.fc.in_features
        self.model.fc = nn.Linear(in_features, num_classes)  

    def forward(self, x):
        return self.model(x)

torch.serialization.add_safe_globals([OptimizedChestXRayResNet])  
model = torch.load("resnet50model.pth", map_location="cpu", weights_only=False)  
model.eval()  
print(model)  
