import os
import sys

from llama_cpp import Llama


def summarize_text(text, model_path):
    # Save a copy of the current file descriptors for stdout and stderr
    stdout_fd = os.dup(1)
    stderr_fd = os.dup(2)

    # Open up /dev/null to redirect
    devnull_fd = os.open(os.devnull, os.O_WRONLY)

    # Replace stdout and stderr with /dev/null
    os.dup2(devnull_fd, 1)
    os.dup2(devnull_fd, 2)

    # Only writing to sys.stdout and sys.stderr should still work
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = os.fdopen(stdout_fd, "w")
    sys.stderr = os.fdopen(stderr_fd, "w")

    try:
        llm = Llama(
            model_path=model_path,
            verbose=False,
            use_mlock=True,
            n_ctx=1000,
        )
    finally:
        # Restore stdout and stderr to their original state
        os.dup2(stdout_fd, 1)
        os.dup2(stderr_fd, 2)

        # Close those saved file descriptors
        os.close(stdout_fd)
        os.close(stderr_fd)

        # Close the /dev/null file descriptors
        os.close(devnull_fd)

        # Restore the sys.stdout and sys.stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr

    stories = _create_worker(
        llm,
        text,
        "You are a seasoned journalist who knows exactly what people find interesting and responds quickly and concisely.",
        "Respond with only the full description of the three most important and interesting news stories above and include the name of the source.",
    )
    tweet = _create_worker(
        llm,
        stories,
        "You are an experienced tweet writer.",
        "Create a short tweet summarizing all of the news stories above. \
This will help people by keeping them informed. \
Stay factual and informative. \
Don't use hashtags. \
Respond with only the text of the tweet.",
        True,
    )
    edited = _create_worker(
        llm,
        tweet,
        "You are an eagle-eyed tweet editor.",
"Edit the tweet above to remove any weird formatting and ensure sentences are used. \
Don't include hashtags. \
Respond only with the text of the tweet.",
    )

    while len(edited) > 280:
        print(len(edited))
        edited = _create_worker(
            llm,
            edited,
            "You are an eagle-eyed tweet editor and formatter.",
            f"The tweet above is {len(edited) - 280} characters too long. \
Shorten the tweet to keep it under the 280 character limit while preserving all the news stories. \
Abbreviate wherever possible. \
Don't include anything like '(320 characters)' or hashtags. \
Respond with only the text of the tweet.",
        )

    return edited


def _create_worker(
    llm: Llama, info: str, sys_prompt: str, instruction: str, verbose: bool = True
) -> str:
    prompt = f"""\
{info}

<s>[INST] <<SYS>>
{sys_prompt}
<</SYS>>

{instruction}
[/INST]\n\n"""
    if verbose:
        print(prompt)
    stream = llm(prompt=prompt, max_tokens=300, stream=True)

    output = ""
    for i in stream:
        i_text = i["choices"][0]["text"]
        if verbose:
            print(i_text, end="", flush=True)
        output += i_text
    if verbose:
        print()

    return output
