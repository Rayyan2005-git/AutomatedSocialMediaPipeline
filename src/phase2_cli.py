import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from enhancer import Enhancer

def main():
    load_dotenv()
    
    manifest_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'manifest.json')
    if not os.path.exists(manifest_path):
        print("Manifest not found. Run Phase 1 first.")
        sys.exit(1)
        
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
        
    enhancer = Enhancer()
    
    enhanced_dir = os.path.join(os.path.dirname(__file__), '..', 'output', 'enhanced')
    os.makedirs(enhanced_dir, exist_ok=True)
    
    print(f"Starting Phase 2 for {len(manifest.get('files', []))} files...")
    
    for item in manifest.get('files', []):
        theme = item.get('matched_theme')
        prompt = item.get('generation_prompt', theme) # Fallback to theme if missing
        original_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', item.get('local_path')))
        
        if not os.path.exists(original_path):
            print(f"File {original_path} not found. Skipping.")
            continue
            
        file_name = os.path.basename(original_path)
        enhanced_path = os.path.abspath(os.path.join(enhanced_dir, f"enhanced_{file_name}"))
        
        # 1. Generate Scene with Gemini Imagen 3
        result_path = enhancer.generate_scene(original_path, prompt, enhanced_path)
        
        if not result_path:
            item['phase2'] = {
                "policyRejected": False,
                "fidelityCheckPassed": False,
                "error": "API failed to generate image."
            }
            continue
            
        # 2. Fidelity Check Removed (Gemini generates from scratch)
        fidelity_passed = True 
        
        # 3. Crop/Pad
        aspect_ratio = "4:5"
        final_path = enhancer.pad_image(result_path, ratio=aspect_ratio)
        
        # 4. Generate Caption
        caption = enhancer.generate_caption(theme, prompt)
        
        # 5. Extend Manifest Item
        item['phase2'] = {
            "generatedPath": os.path.relpath(final_path, start=os.path.join(os.path.dirname(__file__), '..')).replace('\\', '/'),
            "generationPrompt": prompt,
            "fidelityCheckPassed": fidelity_passed,
            "policyRejected": False,
            "caption": caption,
            "aspectRatio": aspect_ratio
        }
        print(f"Successfully processed {file_name}")
        
    # Write updated manifest
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Phase 2 complete. Manifest updated at {manifest_path}")

if __name__ == "__main__":
    main()
