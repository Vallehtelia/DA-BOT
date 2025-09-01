# GPT-OSS-20B Model Test Script

This is a simple test script to verify that you can run the GPT-OSS-20B model on your hardware before we proceed with building the main AI agent platform.

## Prerequisites

- Python 3.8 or higher
- At least 16GB of GPU memory (MXFP4 quantization allows this model to run on consumer hardware)
- CUDA-compatible GPU
- Stable internet connection

## Installation

1. **Create and activate a virtual environment** (recommended):
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (should see (venv) in prompt)
which python
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. **Important**: Update the model name in `test_gpt_oss.py`
   - Currently it's set to: `"openai/gpt-oss-20b"`
   - This should be the correct model name, but verify it exists on Hugging Face
   - If needed, replace with the actual GPT-OSS-20B model identifier

4. **To deactivate virtual environment when done**:
```bash
deactivate
```

## Usage

Run the test script:
```bash
python test_gpt_oss.py
```

The script will:
1. Load the model and tokenizer
2. Provide an interactive console interface
3. Allow you to type prompts and see responses
4. Type 'quit' or 'exit' to stop

## What to Test

1. **Model Loading**: Verify the model loads without errors
2. **Memory Usage**: Check that it fits in your GPU memory (should work with 16GB+ VRAM)
3. **Response Generation**: Test with simple prompts using harmony format
4. **Performance**: Note response generation speed
5. **Harmony Format**: Verify responses follow the required format

## Troubleshooting

- **Out of Memory**: Try reducing `max_length` in the script or use CPU offloading
- **Model Not Found**: Verify the model name exists on Hugging Face
- **Slow Loading**: This is normal for large models on first run

## Next Steps

Once you confirm the model works on your hardware, we'll proceed with building Phase 1 of the AI agent platform according to the project overview.

## Hardware Requirements

- **GPU**: NVIDIA GPU with at least 16GB VRAM (RTX 4080, RTX 4090, A100, H100, etc.)
- **RAM**: At least 32GB system RAM
- **Storage**: At least 50GB free space for model downloads (MXFP4 quantization reduces size)
