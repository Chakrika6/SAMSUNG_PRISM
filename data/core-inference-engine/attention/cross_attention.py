import torch
import torch.nn as nn
import math

class MobileCrossAttention(nn.Module):
    """
    Highly optimized Cross-Attention mechanism for Vision-Language models on edge devices.
    Currently a major bottleneck due to O(N^2) memory complexity during the forward pass.
    """
    def __init__(self, embed_dim, num_heads):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        assert self.head_dim * num_heads == self.embed_dim, "embed_dim must be divisible by num_heads"

        self.q_proj = nn.Linear(embed_dim, embed_dim)
        self.k_proj = nn.Linear(embed_dim, embed_dim)
        self.v_proj = nn.Linear(embed_dim, embed_dim)
        self.out_proj = nn.Linear(embed_dim, embed_dim)

    def forward(self, query, key, value, attention_mask=None):
        """
        Computes cross-attention between vision and language modalities.
        Performance warning: High RAM consumption observed when sequence length > 1024.
        """
        B, tgt_len, _ = query.size()
        _, src_len, _ = key.size()

        q = self.q_proj(query).view(B, tgt_len, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(key).view(B, src_len, self.num_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(value).view(B, src_len, self.num_heads, self.head_dim).transpose(1, 2)

        # MatMul: High computational cost
        attn_weights = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.head_dim)

        if attention_mask is not None:
            attn_weights = attn_weights + attention_mask

        attn_probs = nn.functional.softmax(attn_weights, dim=-1)
        
        # FlashAttention could be applied here to reduce memory bandwidth
        attn_output = torch.matmul(attn_probs, v)

        attn_output = attn_output.transpose(1, 2).contiguous().view(B, tgt_len, self.embed_dim)
        return self.out_proj(attn_output)
