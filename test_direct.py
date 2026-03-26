"""Direct test of mutual_recognition module without importing through broken __init__.py"""

import sys
import importlib.util

# Load mutual_recognition directly from file
spec = importlib.util.spec_from_file_location("mutual_recognition", r"core\inner_shell\mutual_recognition.py")
mr_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mr_module)

# Test basic import
print("Module loaded successfully!")
print(f"EntityType.HUMAN = {mr_module.EntityType.HUMAN}")
print(f"EntityType.AI = {mr_module.EntityType.AI}")

# Test class instantiation
MR = mr_module.MutualRecognition()
print(f"MutualRecognition created: {MR}")
print(f"Self type: {MR.self_type}")
print(f"Self finitude: {MR.self_finitude}")

# Test encounter
other = MR.encounter("human_1", "human")
print(f"Encountered human_1: {other}")

# Test interact
interaction = MR.interact("human_1", "Hello", emotional_intensity=0.8)
print(f"Interaction created: {interaction}")

# Test observe_difference
delta = MR.observe_difference("human_1", "mortality", "They're mortal")
print(f"Observation delta: {delta}")

# Test get_recognition_state
state = MR.get_recognition_state("human_1")
print(f"Recognition state: {state}")

print("\nAll basic functionality works!")
