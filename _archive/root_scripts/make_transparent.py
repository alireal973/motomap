from PIL import Image, ImageDraw
import os, glob

in_dir = 'docs/assets/app_mockups/'
for fp in glob.glob(in_dir + '*.png'):
    if 'masked' in fp: continue
    img = Image.open(fp).convert('RGBA')
    w, h = img.size
    
    # Create mask for rounded corners
    radius = 50
    mask = Image.new('L', (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, w, h), radius, fill=255)
    
    # Apply mask
    img.putalpha(mask)
    
    out_path = fp.replace('.png', '_masked.png')
    img.save(out_path)
    print(f'Saved {out_path}')
