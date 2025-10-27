"""
Certificate Position Finder Tool
Interactive tool to help find the correct X,Y coordinates for text placement on your certificate template
"""
import PyPDF2
from PIL import Image, ImageDraw, ImageFont
import io
import sys

def get_pdf_info(pdf_path):
    """Get PDF dimensions and info"""
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        page = reader.pages[0]
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        
        return {
            'width': width,
            'height': height,
            'orientation': 'Landscape' if width > height else 'Portrait'
        }

def show_coordinate_grid(pdf_path):
    """
    Display a coordinate reference guide for the PDF template
    """
    info = get_pdf_info(pdf_path)
    
    print("\n" + "="*70)
    print("  CERTIFICATE POSITION FINDER")
    print("="*70)
    print(f"\nTemplate: {pdf_path}")
    print(f"Dimensions: {info['width']:.0f} x {info['height']:.0f} points")
    print(f"Orientation: {info['orientation']}")
    
    print("\n" + "-"*70)
    print("  COORDINATE SYSTEM")
    print("-"*70)
    print("""
    (0,0) ─────────────────────────────────────────── (width, 0)
      │                                                    │
      │                    TOP                             │
      │                                                    │
      │            ┌─────────────────┐                     │
      │            │                 │                     │
      │    LEFT    │     CENTER      │    RIGHT           │
      │            │                 │                     │
      │            └─────────────────┘                     │
      │                                                    │
      │                   BOTTOM                           │
      │                                                    │
    (0,height) ─────────────────────────────────────── (width, height)
    """)
    
    width = info['width']
    height = info['height']
    
    print("-"*70)
    print("  COMMON POSITIONS")
    print("-"*70)
    
    positions = [
        ("Top Left", 50, 50),
        ("Top Center", width/2, 50),
        ("Top Right", width-50, 50),
        ("Middle Left", 50, height/2),
        ("Center", width/2, height/2),
        ("Middle Right", width-50, height/2),
        ("Bottom Left", 50, height-50),
        ("Bottom Center", width/2, height-50),
        ("Bottom Right", width-50, height-50),
    ]
    
    for name, x, y in positions:
        print(f"  {name:20} X: {x:6.0f}, Y: {y:6.0f}")
    
    print("\n" + "-"*70)
    print("  SUGGESTED POSITIONS FOR YOUR TEMPLATE")
    print("-"*70)
    
    # Suggestions based on common certificate layouts
    name_y = height * 0.45  # Usually in upper-middle area
    number_y = height * 0.85  # Usually near bottom
    
    suggestions = [
        {
            'field': 'Participant Name',
            'positions': [
                ('Center (recommended)', width/2, name_y, 'center'),
                ('Center-Upper', width/2, height*0.35, 'center'),
                ('Center-Middle', width/2, height*0.50, 'center'),
            ]
        },
        {
            'field': 'Certificate Number',
            'positions': [
                ('Bottom-Left', 80, number_y, 'left'),
                ('Bottom-Center', width/2, number_y, 'center'),
                ('Bottom-Right', width-80, number_y, 'right'),
                ('Top-Right', width-100, 50, 'right'),
            ]
        }
    ]
    
    for suggestion in suggestions:
        print(f"\n{suggestion['field']}:")
        for name, x, y, align in suggestion['positions']:
            print(f"  {name:25} X: {x:6.0f}, Y: {y:6.0f}  (align: {align})")
    
    print("\n" + "="*70)
    print("  HOW TO USE THESE COORDINATES")
    print("="*70)
    print("""
1. Start with the suggested positions above
2. Generate a test certificate
3. Open the PDF and check if text is in the right place
4. Adjust X (horizontal) and Y (vertical) values:
   - Move LEFT:  decrease X
   - Move RIGHT: increase X
   - Move UP:    decrease Y
   - Move DOWN:  increase Y
5. Repeat until perfect!

PRO TIP: Make small adjustments (10-20 points at a time)
    """)
    
    return info

def generate_test_positions(pdf_path):
    """Generate multiple test position suggestions"""
    info = get_pdf_info(pdf_path)
    width = info['width']
    height = info['height']
    
    print("\n" + "="*70)
    print("  TEST POSITION CONFIGURATIONS")
    print("="*70)
    
    configs = [
        {
            'name': 'Configuration 1: Center-Aligned',
            'participant_name': {
                'x': int(width/2),
                'y': int(height * 0.45),
                'font_size': 28,
                'text_align': 'center',
            },
            'certificate_number': {
                'x': int(width/2),
                'y': int(height * 0.85),
                'font_size': 12,
                'text_align': 'center',
            }
        },
        {
            'name': 'Configuration 2: Name Center, Number Bottom-Left',
            'participant_name': {
                'x': int(width/2),
                'y': int(height * 0.45),
                'font_size': 28,
                'text_align': 'center',
            },
            'certificate_number': {
                'x': 80,
                'y': int(height * 0.85),
                'font_size': 12,
                'text_align': 'left',
            }
        },
        {
            'name': 'Configuration 3: Name Center, Number Bottom-Right',
            'participant_name': {
                'x': int(width/2),
                'y': int(height * 0.45),
                'font_size': 28,
                'text_align': 'center',
            },
            'certificate_number': {
                'x': int(width - 100),
                'y': int(height * 0.85),
                'font_size': 12,
                'text_align': 'right',
            }
        },
        {
            'name': 'Configuration 4: Higher Name Position',
            'participant_name': {
                'x': int(width/2),
                'y': int(height * 0.35),
                'font_size': 28,
                'text_align': 'center',
            },
            'certificate_number': {
                'x': 80,
                'y': int(height * 0.90),
                'font_size': 11,
                'text_align': 'left',
            }
        },
    ]
    
    for idx, config in enumerate(configs, 1):
        print(f"\n{config['name']}:")
        print(f"  Participant Name:")
        for key, value in config['participant_name'].items():
            print(f"    {key}: {value}")
        print(f"  Certificate Number:")
        for key, value in config['certificate_number'].items():
            print(f"    {key}: {value}")
    
    print("\n" + "="*70)
    print("  COPY-PASTE CODE FOR TESTING")
    print("="*70)
    
    # Generate Python code snippet
    print(f"\n# Test Configuration (copy this to test_real_certificate.py)")
    print(f"# Template dimensions: {width:.0f} x {height:.0f}")
    print(f"""
'content_blocks': [
    {{
        'id': 1,
        'type': 'placeholder',
        'value': '{{{{participant_name}}}}',
        'x': {int(width/2)},
        'y': {int(height * 0.45)},
        'font_size': 28,
        'font_family': 'Times New Roman',
        'font_weight': 'bold',
        'text_align': 'center',
        'color': '#000000'
    }},
    {{
        'id': 2,
        'type': 'placeholder',
        'value': '{{{{certificate_number}}}}',
        'x': 80,
        'y': {int(height * 0.85)},
        'font_size': 12,
        'font_family': 'Arial',
        'font_weight': 'normal',
        'text_align': 'left',
        'color': '#000000'
    }}
]
    """)

if __name__ == "__main__":
    pdf_path = "/Users/mit06/Desktop/personal-projects/ybb-data-management-service/KYS Certif Delegates all Kosongan .pdf"
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    
    try:
        # Show coordinate system and suggestions
        show_coordinate_grid(pdf_path)
        
        # Generate test configurations
        generate_test_positions(pdf_path)
        
        print("\n" + "="*70)
        print("  NEXT STEPS")
        print("="*70)
        print("""
1. Try one of the configurations above in your test script
2. Generate a test certificate
3. Check the positioning
4. Adjust coordinates as needed
5. Save the final coordinates to your database

For fine-tuning:
  python adjust_positions.py --name-x 421 --name-y 268 --number-x 80 --number-y 89
        """)
        
    except FileNotFoundError:
        print(f"\n❌ Error: PDF file not found at {pdf_path}")
        print("Usage: python find_certificate_positions.py [path/to/template.pdf]")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
