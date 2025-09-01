#!/usr/bin/env python3
"""
Simple test script for GPT-OSS-20B model from Hugging Face.
This script loads the model and provides a simple console interface for testing.
Uses the harmony response format as required by GPT-OSS models.
"""

import torch
from transformers import pipeline
import sys

def load_model():
    """Load the GPT-OSS-20B model using the pipeline approach."""
    print("Loading GPT-OSS-20B model...")
    print("This may take a while depending on your hardware...")
    print("Note: This model requires the harmony response format.")
    
    try:
        model_id = "openai/gpt-oss-20b"
        
        print(f"Loading model from {model_id}...")
        print("Using pipeline with auto device mapping and torch dtype...")
        
        # Use pipeline approach as recommended in the model documentation
        pipe = pipeline(
            "text-generation",
            model=model_id,
            torch_dtype="auto",
            device_map="auto",
        )
        
        print("Model loaded successfully!")
        return pipe
        
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Please check:")
        print("1. You have enough GPU memory (at least 16GB recommended for MXFP4 quantization)")
        print("2. You have the correct model name")
        print("3. Your internet connection is stable")
        print("4. You have the 'kernels' package installed")
        return None

def generate_response(pipe, user_input, max_new_tokens=256):
    """Generate a response from the model using harmony format."""
    try:
        # Format messages in the harmony format as required by GPT-OSS
        messages = [
            {"role": "user", "content": user_input}
        ]
        
        print("Generating response with harmony format...")
        
        # Generate response using the pipeline
        outputs = pipe(
            messages,
            max_new_tokens=max_new_tokens,
        )
        
        # Extract the generated text
        response = outputs[0]["generated_text"][-1]
        return response
        
    except Exception as e:
        return f"Error generating response: {e}"

def main():
    """Main function for the interactive console."""
    print("=" * 60)
    print("GPT-OSS-20B Model Test Script")
    print("=" * 60)
    print("Using harmony response format as required by GPT-OSS models")
    print("=" * 60)
    
    # Load the model
    pipe = load_model()
    
    if pipe is None:
        print("Failed to load model. Exiting.")
        sys.exit(1)
    
    print("\nModel is ready! Type your prompts below.")
    print("Type 'quit' or 'exit' to stop.")
    print("-" * 60)
    
    # Interactive loop
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("Generating response...")
            
            # Generate response
            response = generate_response(pipe, user_input)
            
            print(f"\nAssistant: {response}")
            
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Exiting...")
            break
        except Exception as e:
            print(f"\nError: {e}")
            continue

if __name__ == "__main__":
    main()
