import sys
import tensorflow as tf
from PIL import Image, ImageDraw, ImageFont
from transformers import AutoTokenizer, TFBertForMaskedLM

# Pre-trained masked language model
MODEL = "bert-base-uncased"

# Number of top predictions to display
K = 3

# Constants for generating attention diagrams
FONT = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 28)
GRID_SIZE = 40
PIXELS_PER_WORD = 200


def main():
    """
    Main function to handle input text, model prediction, and visualization.
    """
    # Get input text from the user
    text = input("Text: ")

    # Tokenize input using the pre-trained model's tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    inputs = tokenizer(text, return_tensors="tf")

    # Find the index of the mask token in the input
    mask_token_index = get_mask_token_index(tokenizer.mask_token_id, inputs)
    if mask_token_index is None:
        sys.exit(f"Input must include mask token {tokenizer.mask_token}.")

    # Load the pre-trained model
    model = TFBertForMaskedLM.from_pretrained(MODEL)

    # Perform inference and get model outputs
    result = model(**inputs, output_attentions=True)

    # Extract logits for the mask token and identify top predictions
    mask_token_logits = result.logits[0, mask_token_index]
    top_tokens = tf.math.top_k(mask_token_logits, K).indices.numpy()

    # Display top K predictions
    for token in top_tokens:
        prediction = text.replace(tokenizer.mask_token, tokenizer.decode([token]))
        print(prediction)

    # Visualize attention weights
    visualize_attentions(inputs.tokens(), result.attentions)


def get_mask_token_index(mask_token_id, inputs):
    """
    Get the index of the mask token in the input IDs.

    Args:
        mask_token_id (int): The ID of the mask token.
        inputs (dict): Tokenized inputs with input IDs.

    Returns:
        int: The index of the mask token, or None if not present.
    """
    ids = inputs.input_ids.numpy().tolist()[0]
    return ids.index(mask_token_id) if mask_token_id in ids else None


def get_color_for_attention_score(attention_score):
    """
    Map an attention score to a grayscale color value.

    Args:
        attention_score (float): The attention score (range 0 to 1).

    Returns:
        tuple: A (R, G, B) tuple representing a shade of gray.
    """
    color_intensity = round(float(attention_score) * 255)
    return (color_intensity, color_intensity, color_intensity)


def visualize_attentions(tokens, attentions):
    """
    Generate and save visualizations of self-attention scores for each attention head.

    Args:
        tokens (list): List of tokens in the input.
        attentions (list): Attention scores from the model.
    """
    for layer_idx, layer_attention in enumerate(attentions):
        for head_idx, head_attention in enumerate(layer_attention[0]):
            generate_diagram(
                layer_number=layer_idx + 1,
                head_number=head_idx + 1,
                tokens=tokens,
                attention_weights=head_attention
            )


def generate_diagram(layer_number, head_number, tokens, attention_weights):
    """
    Create a diagram representing self-attention scores for a specific attention head.

    Args:
        layer_number (int): Layer number of the attention head.
        head_number (int): Head number within the layer.
        tokens (list): List of tokens in the input.
        attention_weights (np.array): Attention weights for the tokens.
    """
    # Calculate image size based on the number of tokens
    image_size = GRID_SIZE * len(tokens) + PIXELS_PER_WORD
    img = Image.new("RGBA", (image_size, image_size), "black")
    draw = ImageDraw.Draw(img)

    # Draw tokens as column headers and row labels
    for i, token in enumerate(tokens):
        # Draw token as a column header (rotated)
        token_image = Image.new("RGBA", (image_size, image_size), (0, 0, 0, 0))
        token_draw = ImageDraw.Draw(token_image)
        token_draw.text(
            (image_size - PIXELS_PER_WORD, PIXELS_PER_WORD + i * GRID_SIZE),
            token,
            fill="white",
            font=FONT
        )
        token_image = token_image.rotate(90)
        img.paste(token_image, mask=token_image)

        # Draw token as a row label
        _, _, width, _ = draw.textbbox((0, 0), token, font=FONT)
        draw.text(
            (PIXELS_PER_WORD - width, PIXELS_PER_WORD + i * GRID_SIZE),
            token,
            fill="white",
            font=FONT
        )

    # Fill the grid with attention scores
    for i in range(len(tokens)):
        y = PIXELS_PER_WORD + i * GRID_SIZE
        for j in range(len(tokens)):
            x = PIXELS_PER_WORD + j * GRID_SIZE
            color = get_color_for_attention_score(attention_weights[i][j])
            draw.rectangle((x, y, x + GRID_SIZE, y + GRID_SIZE), fill=color)

    # Save the generated image
    img.save(f"Attention_Layer{layer_number}_Head{head_number}.png")


if __name__ == "__main__":
    main()
