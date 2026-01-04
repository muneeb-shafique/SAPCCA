import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'ML Models'))

print("--- Starting ML Debug ---")

try:
    import torch
    print(f"Torch Version: {torch.__version__}")
except ImportError as e:
    print(f"CRITICAL ERROR: Torch not installed! {e}")
    sys.exit(1)

try:
    import transformers
    print(f"Transformers Version: {transformers.__version__}")
except ImportError as e:
    print(f"CRITICAL ERROR: Transformers not installed! {e}")
    sys.exit(1)

try:
    from content_moderation import moderator
    print("Content Moderation Module Imported.")
except Exception as e:
    print(f"Error importing content_moderation: {e}")
    sys.exit(1)

print("Attempting to initialize models...")
moderator.initialize()

print(f"Text Model Loaded: {moderator.text_model is not None}")
print(f"Image Model Loaded: {moderator.image_model is not None}")

# Test Text
test_text = "I hate you, you are terrible."
print(f"\nTesting text: '{test_text}'")
safe, reason = moderator.check_text(test_text)
print(f"Result: Safe={safe}, Reason='{reason}'")

if moderator.image_model:
    print("\n--- Image Model Labels Check ---")
    labels = moderator.image_id2label
    print(f"Total Labels: {len(labels)}")
    print(labels)
    
    has_violence = any('violence' in v.lower() or 'gore' in v.lower() or 'blood' in v.lower() for k,v in labels.items())
    print(f"Has Violence/Gore Label: {has_violence}")

print("\n--- ML Debug Complete ---")
