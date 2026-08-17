import os
import torch
import torch.nn as nn
from typing import Any

class OnnxableSB3Policy(nn.Module):
    """Wrapper to make Stable-Baselines3 actor-critic policies exportable to ONNX."""
    def __init__(self, mlp_extractor, action_net):
        super().__init__()
        self.mlp_extractor = mlp_extractor
        self.action_net = action_net

    def forward(self, observation):
        # Observation shape: [batch_size, window_size, n_features] or [batch_size, flat_features]
        batch_size = observation.shape[0]
        obs_flat = observation.view(batch_size, -1)
        latent_pi, _ = self.mlp_extractor(obs_flat)
        action_logits = self.action_net(latent_pi)
        # Return deterministic discrete action index: 0=Hold, 1=Buy, 2=Sell
        return torch.argmax(action_logits, dim=-1)

def export_model_to_onnx(
    model: Any,
    output_path: str,
    window_size: int = 20,
    n_features: int = 5
) -> str:
    """Export Stable-Baselines3 PPO/A2C model to ONNX file."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    policy = model.policy
    extractor = policy.mlp_extractor
    action_net = policy.action_net
    
    onnx_policy = OnnxableSB3Policy(extractor, action_net)
    onnx_policy.eval()
    
    dummy_input = torch.randn(1, window_size, n_features)
    
    torch.onnx.export(
        onnx_policy,
        dummy_input,
        output_path,
        opset_version=14,
        input_names=["observation"],
        output_names=["action"],
        dynamic_axes={
            "observation": {0: "batch_size"},
            "action": {0: "batch_size"}
        }
    )
    return output_path
