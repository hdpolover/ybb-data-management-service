"""
Interactive Position Adjustment Tool
Quickly test different coordinate positions for certificate text placement
"""
import requests
import json
import base64
import os
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"
CERTIFICATE_BASE = f"{BASE_URL}/api/ybb/certificates"
TEMPLATE_PATH = "/Users/mit06/Desktop/personal-projects/ybb-data-management-service/KYS Certif Delegates all Kosongan .pdf"

def generate_with_positions(name_x, name_y, number_x, number_y, 
                            name_align='center', number_align='left',
                            name_size=24, number_size=12):
    """
    Generate a test certificate with specified positions
    """
    # Ensure template is in static folder
    static_dir = "static/templates"
    os.makedirs(static_dir, exist_ok=True)
    template_filename = "kys_certificate_template.pdf"
    static_template_path = os.path.join(static_dir, template_filename)
    
    if not os.path.exists(static_template_path):
        if os.path.exists(TEMPLATE_PATH):
            import shutil
            shutil.copy(TEMPLATE_PATH, static_template_path)
    
    template_url = f"{BASE_URL}/static/templates/{template_filename}"
    
    # Create certificate data with specified positions
    certificate_data = {
        "participant": {
            "id": 1,
            "full_name": "John Michael Anderson",
            "birthdate": "1995-01-01",
            "gender": "male",
            "nationality": "Indonesia",
            "nationality_code": "ID",
            "education_level": "bachelor",
            "major": "Business",
            "institution": "University",
            "occupation": "Student",
            "category": "fully_funded"
        },
        "program": {
            "id": 1,
            "name": "Youth Break the Boundaries 2025",
            "theme": "Leadership Development",
            "start_date": "2025-08-01",
            "end_date": "2025-08-15"
        },
        "award": {
            "id": 1,
            "title": "Certificate of Participation",
            "description": "Successfully completed the program",
            "award_type": "other",
            "order_number": 1
        },
        "certificate_template": {
            "id": 1,
            "template_url": template_url,
            "template_type": "pdf",
            "issue_date": datetime.now().strftime("%Y-%m-%d"),
            "certificate_number": "KYS/2025/001"
        },
        "content_blocks": [
            {
                "id": 1,
                "type": "placeholder",
                "value": "{{participant_name}}",
                "x": name_x,
                "y": name_y,
                "font_size": name_size,
                "font_family": "Times New Roman",
                "font_weight": "bold",
                "text_align": name_align,
                "color": "#000000"
            },
            {
                "id": 2,
                "type": "placeholder",
                "value": "{{certificate_number}}",
                "x": number_x,
                "y": number_y,
                "font_size": number_size,
                "font_family": "Arial",
                "font_weight": "normal",
                "text_align": number_align,
                "color": "#000000"
            }
        ],
        "assignment_info": {
            "assigned_by": 1,
            "assigned_at": datetime.now().isoformat(),
            "notes": "Position testing"
        }
    }
    
    print(f"\n{'='*70}")
    print(f"  TESTING POSITIONS")
    print(f"{'='*70}")
    print(f"Name Position:    X={name_x:4d}, Y={name_y:4d}, Align={name_align:6}, Size={name_size}pt")
    print(f"Number Position:  X={number_x:4d}, Y={number_y:4d}, Align={number_align:6}, Size={number_size}pt")
    print(f"{'='*70}")
    
    try:
        response = requests.post(
            f"{CERTIFICATE_BASE}/generate",
            json=certificate_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                cert_data = result['data']
                
                # Save with descriptive filename showing positions
                filename = f"test_pos_N{name_x}x{name_y}_C{number_x}x{number_y}.pdf"
                pdf_bytes = base64.b64decode(cert_data['file_data'])
                
                with open(filename, 'wb') as f:
                    f.write(pdf_bytes)
                
                print(f"\n✅ Certificate generated: {filename}")
                print(f"   Size: {len(pdf_bytes):,} bytes")
                print(f"\n📋 Open the file to check positioning!")
                return filename
            else:
                print(f"\n❌ Generation failed: {result.get('error', {}).get('message')}")
        else:
            print(f"\n❌ API error: {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    return None

def interactive_mode():
    """Interactive mode to test positions"""
    print("\n" + "🎯 "*30)
    print("  INTERACTIVE POSITION TESTER")
    print("🎯 "*30)
    print("\nThis tool helps you find the perfect X,Y coordinates for your text.")
    print("Generate test certificates and adjust positions until perfect!\n")
    
    # Default starting positions for landscape A4 (842 x 595)
    name_x = 421      # Center
    name_y = 268      # Middle-ish
    number_x = 80     # Left
    number_y = 505    # Lower (closer to bottom, adjusted from 89)
    
    while True:
        print("\n" + "-"*70)
        print("Current positions:")
        print(f"  Name:   X={name_x}, Y={name_y}")
        print(f"  Number: X={number_x}, Y={number_y}")
        print("-"*70)
        print("\nOptions:")
        print("  1. Generate test certificate with current positions")
        print("  2. Adjust name X position")
        print("  3. Adjust name Y position")
        print("  4. Adjust number X position")
        print("  5. Adjust number Y position")
        print("  6. Try suggested positions")
        print("  7. Save final positions (display code)")
        print("  0. Exit")
        
        choice = input("\nEnter option: ").strip()
        
        if choice == '0':
            print("\n👋 Goodbye!")
            break
        elif choice == '1':
            generate_with_positions(name_x, name_y, number_x, number_y)
        elif choice == '2':
            try:
                name_x = int(input(f"Enter new name X (current: {name_x}): ").strip())
            except ValueError:
                print("❌ Invalid number")
        elif choice == '3':
            try:
                name_y = int(input(f"Enter new name Y (current: {name_y}): ").strip())
            except ValueError:
                print("❌ Invalid number")
        elif choice == '4':
            try:
                number_x = int(input(f"Enter new number X (current: {number_x}): ").strip())
            except ValueError:
                print("❌ Invalid number")
        elif choice == '5':
            try:
                number_y = int(input(f"Enter new number Y (current: {number_y}): ").strip())
            except ValueError:
                print("❌ Invalid number")
        elif choice == '6':
            print("\n" + "="*70)
            print("  SUGGESTED POSITIONS (Landscape A4: 842 x 595)")
            print("="*70)
            configs = [
                ("Center Name, Bottom-Left Number", 421, 268, 80, 505),
                ("Center Name, Bottom-Center Number", 421, 268, 421, 505),
                ("Center Name, Bottom-Right Number", 421, 268, 762, 505),
                ("Higher Name, Bottom-Left Number", 421, 200, 80, 505),
                ("Lower Name, Bottom-Left Number", 421, 350, 80, 505),
            ]
            for idx, (desc, nx, ny, cx, cy) in enumerate(configs, 1):
                print(f"  {idx}. {desc}")
                print(f"     Name: X={nx}, Y={ny} | Number: X={cx}, Y={cy}")
            
            try:
                sel = int(input("\nSelect configuration (1-5): ").strip())
                if 1 <= sel <= len(configs):
                    _, name_x, name_y, number_x, number_y = configs[sel-1]
                    print(f"✅ Positions updated!")
            except ValueError:
                print("❌ Invalid selection")
        elif choice == '7':
            print("\n" + "="*70)
            print("  FINAL POSITIONS - SAVE THIS!")
            print("="*70)
            print(f"\nParticipant Name: X={name_x}, Y={name_y}")
            print(f"Certificate Number: X={number_x}, Y={number_y}")
            print("\n📋 Copy this code to your database or PHP application:")
            print("-"*70)
            print(f"""
// Participant Name Block
[
    'type' => 'placeholder',
    'value' => '{{{{participant_name}}}}',
    'x' => {name_x},
    'y' => {name_y},
    'font_size' => 24,
    'font_family' => 'Times New Roman',
    'font_weight' => 'bold',
    'text_align' => 'center',
    'color' => '#000000'
]

// Certificate Number Block
[
    'type' => 'placeholder',
    'value' => '{{{{certificate_number}}}}',
    'x' => {number_x},
    'y' => {number_y},
    'font_size' => 12,
    'font_family' => 'Arial',
    'font_weight' => 'normal',
    'text_align' => 'left',
    'color' => '#000000'
]
            """)
            print("-"*70)
            
            # Also show SQL for database
            print("\n📊 SQL for database (program_certificate_content_blocks):")
            print("-"*70)
            print(f"""
INSERT INTO program_certificate_content_blocks 
(certificate_id, type, value, x, y, font_size, font_family, font_weight, text_align, color, is_active)
VALUES
-- Participant Name
(1, 'placeholder', '{{{{participant_name}}}}', {name_x}, {name_y}, 24, 'Times New Roman', 'bold', 'center', '#000000', 1),
-- Certificate Number
(1, 'placeholder', '{{{{certificate_number}}}}', {number_x}, {number_y}, 12, 'Arial', 'normal', 'left', '#000000', 1);
            """)
            print("="*70)

def quick_test_mode(name_x, name_y, number_x, number_y):
    """Quick test mode from command line arguments"""
    print("\n🚀 Quick Test Mode")
    generate_with_positions(name_x, name_y, number_x, number_y)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 5:
        # Command line mode: python adjust_positions.py name_x name_y number_x number_y
        try:
            name_x = int(sys.argv[1])
            name_y = int(sys.argv[2])
            number_x = int(sys.argv[3])
            number_y = int(sys.argv[4])
            quick_test_mode(name_x, name_y, number_x, number_y)
        except ValueError:
            print("Usage: python adjust_positions.py <name_x> <name_y> <number_x> <number_y>")
            print("Example: python adjust_positions.py 421 268 80 505")
    else:
        # Interactive mode
        interactive_mode()
