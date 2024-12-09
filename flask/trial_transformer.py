from transformers import pipeline

# Global variable to store the pipeline
generator = None


def get_generator():
    """
    Initializes and retrieves the text generation pipeline.
    Ensures that the generator is only created once (singleton pattern).
    """
    global generator
    if generator is None:
        # Initialize the generator only once
        generator = pipeline('text-generation', model='gpt2')
    return generator


def generate_responses(prompt):
    """
    Generates a text response for the given prompt using the GPT-2 model.

    Args:
        prompt (str): The input text to generate a response for.

    Returns:
        str: The generated text response.
    """
    generator = get_generator()  # Ensure generator is initialized
    output = generator(prompt, max_length=100, num_return_sequences=1)
    print(f"Response for '{prompt}': {output[0]['generated_text']}")
    return output[0]['generated_text']
