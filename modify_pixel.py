from PIL import Image

# Step 1: Open the original image
img = Image.open("sample.png").convert("RGB")

# Step 2: Read the first pixel
pixel = img.getpixel((0, 0))

print("Original pixel:", pixel)

# Step 3: Modify the Red value
red = pixel[0]
new_red = red & 254

# Step 4: Create the modified pixel
new_pixel = (new_red, pixel[1], pixel[2])

# Step 5: Update the image
img.putpixel((0, 0), new_pixel)

# Step 6: Save the modified image
img.save("modified_image.png")

print("Modified pixel:", img.getpixel((0, 0)))
print("Modified image saved successfully!")