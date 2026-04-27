# Current Repository Context and Goals

## Goal 1: Memory Optimization
We are currently experiencing high RAM pressure on mid-tier devices (specifically Galaxy A55 series). We need to explore techniques like adaptive quantization or sparse models to reduce footprint during inference.

## Goal 2: On-Device Speed
Inference time for vision-language models needs to drop below 150ms on mobile NPUs. Current approaches are bottlenecked by cross-attention mechanisms.
