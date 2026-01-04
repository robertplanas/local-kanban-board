import os
from PIL import Image, ImageDraw


def draw_rounded_rectangle(draw, xy, corner_radius, fill):
    """
    Helper to draw a rounded rectangle (macOS icon shape standard).
    """
    x0, y0, x1, y1 = xy
    # Prevent corner radius from overlapping if image is very small
    if corner_radius * 2 > (x1 - x0):
        corner_radius = (x1 - x0) // 2

    draw.rectangle([(x0, y0 + corner_radius), (x1, y1 - corner_radius)], fill=fill)
    draw.rectangle([(x0 + corner_radius, y0), (x1 - corner_radius, y1)], fill=fill)
    draw.pieslice(
        [(x0, y0), (x0 + corner_radius * 2, y0 + corner_radius * 2)],
        180,
        270,
        fill=fill,
    )
    draw.pieslice(
        [(x1 - corner_radius * 2, y0), (x1, y0 + corner_radius * 2)],
        270,
        360,
        fill=fill,
    )
    draw.pieslice(
        [(x0, y1 - corner_radius * 2), (x0 + corner_radius * 2, y1)], 90, 180, fill=fill
    )
    draw.pieslice(
        [(x1 - corner_radius * 2, y1 - corner_radius * 2), (x1, y1)], 0, 90, fill=fill
    )


def create_kanban_image(size):
    """
    Draws a Kanban board concept at the specified pixel size.
    """
    width, height = size

    # Create a transparent canvas
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Background (macOS 'Squircle' style)
    bg_color = (40, 44, 52)
    corner_radius = int(width * 0.22)
    draw_rounded_rectangle(draw, [0, 0, width, height], corner_radius, bg_color)

    # 2. Columns (3 columns: To Do, In Progress, Done)
    col_count = 3
    padding = width * 0.15
    col_spacing = width * 0.05

    available_width = width - (padding * 2) - (col_spacing * (col_count - 1))
    col_width = available_width / col_count

    col_top = height * 0.2
    col_bottom = height * 0.85
    col_color = (60, 64, 72)

    # 3. Cards
    card_colors = [(255, 99, 71), (255, 215, 0), (60, 179, 113)]

    for i in range(col_count):
        x_start = padding + (i * (col_width + col_spacing))
        x_end = x_start + col_width

        # Ensure we don't draw negative shapes if calculations get too small
        if x_end > x_start:
            draw.rectangle([x_start, col_top, x_end, col_bottom], fill=col_color)

        # Draw "Cards" inside the column
        card_height = (col_bottom - col_top) * 0.15
        card_spacing = (col_bottom - col_top) * 0.05

        # FIX: Dynamic padding instead of hardcoded '2' pixels
        # Use 10% of column width as padding, or 0 if very small
        card_padding = max(0, (x_end - x_start) * 0.1)

        num_cards = 2 if i != 1 else 1

        for j in range(num_cards):
            card_y = col_top + card_spacing + (j * (card_height + card_spacing))

            # Card coordinates
            c_x0 = x_start + card_padding
            c_x1 = x_end - card_padding
            c_y0 = card_y
            c_y1 = card_y + card_height

            # Only draw if the card has positive dimensions
            if c_x1 > c_x0 and c_y1 > c_y0:
                draw.rectangle([c_x0, c_y0, c_x1, c_y1], fill=card_colors[i])

    return img


def main():
    icon_sizes = [
        (16, 16),
        (32, 32),
        (64, 64),
        (128, 128),
        (256, 256),
        (512, 512),
        (1024, 1024),
    ]

    images = []
    print("Generating icon layers...")

    for size in icon_sizes:
        print(f" - Drawing {size[0]}x{size[1]} px...")
        images.append(create_kanban_image(size))

    output_filename = "kanban_app.icns"
    if images:
        print(f"Saving to {output_filename}...")
        images[0].save(output_filename, format="ICNS", append_images=images[1:])
        print("Done! File created successfully.")


if __name__ == "__main__":
    main()
