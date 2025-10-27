# Dynamic Certificate Positioning Guide

## Problem

The text placement (participant name and certificate number) may not appear in the correct position on your certificate template because:

1. Every certificate template has different dimensions
2. Design layouts vary (where you want the name, where the number should go)
3. Hard-coded positions don't work for all templates

## Solution: Database-Driven Dynamic Positioning

Store the X,Y coordinates in your **database** so you can configure positions per template without changing code!

---

## How It Works

### 1. Find the Correct Positions

Use the **Position Finder Tools** to determine where text should appear:

```bash
# Step 1: See coordinate system and suggestions
python find_certificate_positions.py

# Step 2: Test different positions interactively
python adjust_positions.py

# Or test specific coordinates quickly:
python adjust_positions.py 421 267 80 505
```

### 2. Test Generated Certificates

1. Run the position test
2. Open the generated PDF: `test_pos_N421x267_C80x505.pdf`
3. Check if text is in the right place
4. If not, adjust the coordinates:
   - **Move name LEFT**: decrease name X (e.g., 421 → 400)
   - **Move name RIGHT**: increase name X (e.g., 421 → 450)
   - **Move name UP**: decrease name Y (e.g., 267 → 200)
   - **Move name DOWN**: increase name Y (e.g., 267 → 300)
   - Same logic for certificate number positioning

### 3. Save to Database

Once you find the perfect positions, save them to your database:

```sql
-- Create/Update template with positioning data
INSERT INTO program_certificates (
    program_id,
    template_url,
    template_type,
    is_active
) VALUES (
    1,
    'https://your-cdn.com/certificates/kys_template.pdf',
    'pdf',
    1
);

-- Store content block positions (these make it DYNAMIC!)
INSERT INTO program_certificate_content_blocks (
    certificate_id,
    type,
    value,
    x,
    y,
    font_size,
    font_family,
    font_weight,
    text_align,
    color,
    is_active
) VALUES
-- Participant Name (adjust x, y to your findings)
(1, 'placeholder', '{{participant_name}}', 421, 267, 28, 'Times New Roman', 'bold', 'center', '#000000', 1),

-- Certificate Number (adjust x, y to your findings)
(1, 'placeholder', '{{certificate_number}}', 80, 505, 12, 'Arial', 'normal', 'left', '#000000', 1);
```

---

## PHP/CodeIgniter Dynamic Implementation

### Fetch Positions from Database

```php
<?php
public function generateCertificate($participantId, $certificateNumber)
{
    // 1. Get participant data
    $participantModel = new ParticipantModel();
    $participant = $participantModel->find($participantId);
    
    // 2. Get certificate template configuration
    $certificateModel = new ProgramCertificateModel();
    $template = $certificateModel
        ->where('program_id', $participant['program_id'])
        ->where('is_active', 1)
        ->first();
    
    if (!$template) {
        throw new \Exception('Certificate template not found');
    }
    
    // 3. Get content blocks (positions) from database - THIS IS THE KEY!
    $contentBlockModel = new ProgramCertificateContentBlockModel();
    $contentBlocks = $contentBlockModel
        ->where('certificate_id', $template['id'])
        ->where('is_active', 1)
        ->orderBy('id', 'ASC')
        ->findAll();
    
    // 4. Build certificate data with DYNAMIC positions
    $certificateData = [
        'participant' => [
            'id' => $participant['id'],
            'full_name' => $participant['full_name'],
            // ... other fields
        ],
        'program' => [
            'id' => $participant['program_id'],
            // ... program details
        ],
        'award' => [
            'id' => 1,
            'title' => 'Certificate of Participation',
            // ... award details
        ],
        'certificate_template' => [
            'id' => $template['id'],
            'template_url' => $template['template_url'],
            'template_type' => $template['template_type'],
            'issue_date' => date('Y-m-d'),
            'certificate_number' => $certificateNumber  // Pass the cert number
        ],
        // Use positions from database!
        'content_blocks' => array_map(function($block) {
            return [
                'id' => (int)$block['id'],
                'type' => $block['type'],
                'value' => $block['value'],
                'x' => (int)$block['x'],          // From database
                'y' => (int)$block['y'],          // From database
                'font_size' => (int)$block['font_size'],
                'font_family' => $block['font_family'],
                'font_weight' => $block['font_weight'],
                'text_align' => $block['text_align'],
                'color' => $block['color']
            ];
        }, $contentBlocks)
    ];
    
    // 5. Call Python API
    $certificateService = new CertificateService();
    return $certificateService->generateCertificate($certificateData);
}
```

---

## Benefits of Database-Driven Positioning

✅ **Different templates, different positions**: Each template can have unique coordinates
✅ **No code changes needed**: Adjust positions by updating database only
✅ **Multiple certificates per program**: Different awards can have different layouts
✅ **Easy updates**: Change positions without redeploying code
✅ **Template versioning**: Keep multiple versions with different layouts

---

## Example: Multiple Templates

### Template 1: Landscape Certificate
```sql
-- Template
INSERT INTO program_certificates (id, template_url, template_type) 
VALUES (1, 'https://cdn.com/landscape.pdf', 'pdf');

-- Positions for landscape
INSERT INTO program_certificate_content_blocks (certificate_id, value, x, y) VALUES
(1, '{{participant_name}}', 421, 267),  -- Center
(1, '{{certificate_number}}', 80, 505); -- Bottom-left
```

### Template 2: Portrait Certificate
```sql
-- Template
INSERT INTO program_certificates (id, template_url, template_type) 
VALUES (2, 'https://cdn.com/portrait.pdf', 'pdf');

-- DIFFERENT positions for portrait
INSERT INTO program_certificate_content_blocks (certificate_id, value, x, y) VALUES
(2, '{{participant_name}}', 297, 400),  -- Different position!
(2, '{{certificate_number}}', 100, 750); -- Different position!
```

**Same code, different results!** 🎉

---

## Coordinate System Reference

For **Landscape A4** (842 × 595 points):

```
(0,0) ────────────────────────────────── (842,0)
  │              TOP                        │
  │                                         │
  │      X=421 (horizontal center)          │
  │                                         │
  │  Y=267 (upper-middle) ← Name here      │
  │                                         │
  │              CENTER                     │
  │                                         │
  │                                         │
  │  Y=505 (near bottom) ← Number here     │
  │                                         │
  │             BOTTOM                      │
(0,595) ──────────────────────────────── (842,595)
```

### Quick Reference

| Location | X | Y (Landscape) | Y (Portrait) |
|----------|---|---------------|--------------|
| Top-Left | 50 | 50 | 50 |
| Top-Center | 421 (L) / 297 (P) | 50 | 50 |
| Center | 421 (L) / 297 (P) | 298 | 421 |
| Bottom-Left | 80 | 505 | 750 |
| Bottom-Center | 421 (L) / 297 (P) | 505 | 750 |

---

## Tools Provided

| Tool | Purpose | Usage |
|------|---------|-------|
| `find_certificate_positions.py` | Shows coordinate system and suggestions | `python find_certificate_positions.py` |
| `adjust_positions.py` | Interactive position testing | `python adjust_positions.py` |
| `adjust_positions.py` (CLI) | Quick position testing | `python adjust_positions.py 421 267 80 505` |

---

## Workflow Summary

1. **Design** your certificate template in Photoshop/Illustrator/Canva
2. **Upload** template to CDN (S3, CloudFront, etc.)
3. **Find positions** using the position finder tools
4. **Test** with `adjust_positions.py` until perfect
5. **Save** coordinates to database
6. **Generate** certificates using PHP code above
7. **Done!** All future certificates use database positions

---

## Advanced: Per-Award Positioning

Different awards can have different positions on the same template:

```sql
-- Winner Certificate (larger, centered name)
INSERT INTO program_certificate_content_blocks (certificate_id, award_id, value, x, y, font_size) VALUES
(1, 1, '{{participant_name}}', 421, 250, 32); -- Larger font, higher position

-- Participant Certificate (smaller, lower name)
INSERT INTO program_certificate_content_blocks (certificate_id, award_id, value, x, y, font_size) VALUES
(1, 2, '{{participant_name}}', 421, 300, 24); -- Regular font, lower position
```

Then filter by award_id when fetching content blocks!

---

## Troubleshooting

### Text too high on page
- **Increase Y value** (moves down)
- Example: Y=200 → Y=250

### Text too low on page
- **Decrease Y value** (moves up)
- Example: Y=400 → Y=350

### Text too far left
- **Increase X value** (moves right)
- Example: X=300 → X=350

### Text too far right
- **Decrease X value** (moves left)
- Example: X=500 → X=450

### Text not centered
- Use **X = template_width / 2** and `text_align = 'center'`
- Landscape A4: X=421
- Portrait A4: X=297

---

## Summary

🎯 **Key Takeaway**: Store X,Y coordinates in your **database**, not in code!

This makes positioning:
- ✅ **Configurable** per template
- ✅ **Adjustable** without code changes
- ✅ **Flexible** for multiple designs
- ✅ **Maintainable** through admin panel

**Use the tools provided to find your perfect positions, then save them to the database!** 🚀
